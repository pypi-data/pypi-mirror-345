import asyncio
import json
import logging
from typing import List, Literal, Optional, Tuple

from pydantic import ValidationError

from ..model import BaseLLM
from ..schemas import ExtractedAnswer, LTMDecomposition

logger = logging.getLogger(__name__)


class LeastToMost:
    def __init__(
        self,
        llm: BaseLLM,
        few_shot_examples: Optional[List[Tuple[str, List[str]]]] = None,
        *,
        intermediate_output_format: Literal["text", "json"] = "text",
        decompose_prompt_template: str = (
            "Decompose the main question into a sequence of simpler subquestions "
            "that must be answered sequentially to solve the main question. "
            "Return the result as a JSON object with a single key 'subquestions' containing a list of strings.\n\n"
            "Main Question: {question}\n\n"
            "JSON Output:"
        ),
        solve_prompt_template: str = (
            "Previous Context:\n{context}\n\n"
            "Current Subquestion: {subquestion}\n\n"
            "Answer the current subquestion using the context if necessary. "
            "Provide only the answer to the subquestion.\nAnswer:"
        ),
        final_answer_prompt_template: str = (
            "Based on the following sequential subquestions and their answers, "
            "answer the original main question.\n\n"
            "Subquestions and Answers:\n{solved_steps}\n"
            "Original Main Question: {question}\n\nFinal Answer:"
        ),
        max_subqs: int = 10,
        max_tokens: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> None:
        self.llm = llm
        self.intermediate_output_format = intermediate_output_format
        self.max_subqs = max_subqs

        if few_shot_examples is None:
            self.examples = [
                (
                    "There are 3 red balls and 4 blue balls in a bag. How many balls are there in total?",
                    [
                        "How many red balls are there?",
                        "How many blue balls are there?",
                        "What is the total number of balls?",
                    ],
                ),
                (
                    "Sarah has 5 apples and gives 2 to Tom. How many apples does she have left?",
                    [
                        "How many apples did Sarah start with?",
                        "How many apples did she give away?",
                        "How many apples remain with Sarah?",
                    ],
                ),
            ]
        else:
            self.examples = few_shot_examples

        self.decompose_prompt_template = decompose_prompt_template
        self.solve_prompt_template = solve_prompt_template
        self.final_answer_prompt_template = final_answer_prompt_template

        self.max_tokens = max_tokens
        self.seed = seed

    def _build_prefix(self) -> str:
        prefix = ""
        for ex_q, ex_subs in self.examples:
            prefix += f"Main Question: {ex_q}\nJSON Subquestions: {json.dumps(ex_subs)}\n\n"
        return prefix

    def decompose(self, question: str, **kwargs) -> List[str]:
        prompt = self._build_prefix() + self.decompose_prompt_template.format(question=question)
        logger.debug("LTM Decompose Prompt:\n%s", prompt)
        try:
            result = self.llm.generate_json(
                prompt,
                response_model=LTMDecomposition,
                max_tokens=kwargs.pop("max_tokens", self.max_tokens),
                seed=kwargs.pop("seed", self.seed),
                **kwargs,
            )
            arr = result.subquestions or []
        except (json.JSONDecodeError, ValidationError) as ve:
            logger.error(
                "Decomposition JSON validation/decode failed for question '%s': %s",
                question,
                ve,
                exc_info=True,
            )
            raise ValueError(
                f"Failed to decompose question due to LLM response error: {type(ve).__name__}"
            ) from ve
        except Exception as e:
            logger.error(
                "Decomposition LLM call failed for question '%s': %s", question, e, exc_info=True
            )
            raise ValueError(
                f"Failed to decompose question due to LLM error: {type(e).__name__}"
            ) from e

        subs = [s.strip() for s in arr if s and isinstance(s, str)]
        if not subs:
            raise ValueError("LLM returned empty subquestions list after validation.")
        return subs[: self.max_subqs]

    async def decompose_async(
        self, question: str, semaphore: Optional[asyncio.Semaphore] = None, **kwargs
    ) -> List[str]:
        prompt = self._build_prefix() + self.decompose_prompt_template.format(question=question)
        logger.debug("LTM Async Decompose Prompt:\n%s", prompt)

        local_kwargs = kwargs.copy()
        gen_args = {
            "response_model": LTMDecomposition,
            "max_tokens": local_kwargs.pop("max_tokens", self.max_tokens),
            "seed": local_kwargs.pop("seed", self.seed),
            **local_kwargs,
        }
        try:
            if semaphore:
                async with semaphore:
                    result = await self.llm.generate_json_async(prompt, **gen_args)
            else:
                result = await self.llm.generate_json_async(prompt, **gen_args)
            arr = result.subquestions or []
        except (json.JSONDecodeError, ValidationError) as ve:
            logger.error(
                "Async decomposition JSON validation/decode failed for question '%s': %s",
                question,
                ve,
                exc_info=True,
            )
            raise ValueError(
                f"Async decomposition failed due to LLM response error: {type(ve).__name__}"
            ) from ve
        except Exception as e:
            logger.error(
                "Async decomposition LLM call failed for question '%s': %s",
                question,
                e,
                exc_info=True,
            )
            raise ValueError(
                f"Async decomposition failed due to LLM error: {type(e).__name__}"
            ) from e

        subs = [s.strip() for s in arr if s and isinstance(s, str)]
        if not subs:
            raise ValueError("Async LLM returned empty subquestions list after validation.")
        return subs[: self.max_subqs]

    def solve(self, question: str, subqs: List[str], **kwargs) -> List[Tuple[str, str]]:
        solved: List[Tuple[str, str]] = []
        for i, sub in enumerate(subqs):
            context = (
                "Previously solved:\n" + "\n".join(f"Q: {q}\nA: {a}" for q, a in solved) + "\n"
                if solved
                else "None."
            )
            prompt = self.solve_prompt_template.format(context=context, subquestion=sub)
            logger.debug("LTM Solve Subquestion %d Prompt:\n%s", i + 1, prompt)

            try:
                local_kwargs = kwargs.copy()
                gen_args = {
                    "max_tokens": local_kwargs.pop("max_tokens", self.max_tokens),
                    "seed": local_kwargs.pop("seed", self.seed),
                    **local_kwargs,
                }
                if self.intermediate_output_format == "json":
                    json_p = (
                        prompt
                        + '\n\nReturn exactly one JSON object with key "final_answer" whose value is the answer.\n\nJSON Answer:'
                    )
                    parsed = self.llm.generate_json(
                        json_p, response_model=ExtractedAnswer, **gen_args
                    )
                    ans = str(parsed.final_answer).strip()
                else:
                    ans = self.llm.generate(prompt, **gen_args).strip()
                if not ans:
                    ans = "[No Answer Found]"
            except Exception as e:
                logger.error("Error solving '%s': %s", sub, e, exc_info=True)
                ans = "[Error]"
            solved.append((sub, ans))
        return solved

    async def solve_async(
        self,
        question: str,
        subqs: List[str],
        semaphore: Optional[asyncio.Semaphore] = None,
        **kwargs,
    ) -> List[Tuple[str, str]]:
        solved: List[Tuple[str, str]] = []

        async def one(i: int, sq: str, ctx: str) -> Tuple[int, str, str]:
            prompt = self.solve_prompt_template.format(context=ctx, subquestion=sq)
            logger.debug("LTM Async Solve Subquestion %d Prompt:\n%s", i + 1, prompt)
            ans = "[Error]"
            try:
                local_kwargs = kwargs.copy()
                gen_args = {
                    "max_tokens": local_kwargs.pop("max_tokens", self.max_tokens),
                    "seed": local_kwargs.pop("seed", self.seed),
                    **local_kwargs,
                }
                if self.intermediate_output_format == "json":
                    json_p = (
                        prompt
                        + '\n\nReturn exactly one JSON object with key "final_answer" whose value is the answer.\n\nJSON Answer:'
                    )
                    gen_args["response_model"] = ExtractedAnswer
                    if semaphore:
                        async with semaphore:
                            parsed = await self.llm.generate_json_async(json_p, **gen_args)
                    else:
                        parsed = await self.llm.generate_json_async(json_p, **gen_args)
                    ans = str(parsed.final_answer).strip()
                else:
                    if semaphore:
                        async with semaphore:
                            ans = await self.llm.generate_async(prompt, **gen_args)
                    else:
                        ans = await self.llm.generate_async(prompt, **gen_args)
                    ans = ans.strip()

                if not ans:
                    ans = "[No Answer Found]"
            except Exception as e:
                logger.error("Async error solving '%s': %s", sq, e, exc_info=True)
                ans = "[Error]"
            return i, sq, ans

        current_context = "None."
        for i, sq in enumerate(subqs):
            idx, sqr, ansr = await one(i, sq, current_context)
            solved.append((sqr, ansr))
            current_context = (
                "Previously solved:\n" + "\n".join(f"Q: {q}\nA: {a}" for q, a in solved) + "\n"
            )

        return solved

    def run(self, question: str, **kwargs) -> str:
        final_answer = "[Error: Processing failed]"
        try:
            subs = self.decompose(question, **kwargs)
            solved = self.solve(question, subs, **kwargs)

            steps = "\n".join(f"{i + 1}. Q: {q}\n   A: {a}" for i, (q, a) in enumerate(solved))
            prompt = self.final_answer_prompt_template.format(solved_steps=steps, question=question)
            logger.debug("LTM Final Answer Prompt:\n%s", prompt)

            local_kwargs = kwargs.copy()
            gen_args = {
                "max_tokens": local_kwargs.pop("max_tokens", self.max_tokens),
                "seed": local_kwargs.pop("seed", self.seed),
                **local_kwargs,
            }
            if self.intermediate_output_format == "json":
                json_p = (
                    prompt
                    + '\n\nReturn exactly one JSON object with key "final_answer" whose value is the answer.\n\nJSON Answer:'
                )
                parsed = self.llm.generate_json(json_p, response_model=ExtractedAnswer, **gen_args)
                final_answer = str(parsed.final_answer).strip()
            else:
                final_answer = self.llm.generate(prompt, **gen_args).strip()
        except Exception as e:
            logger.error(
                "Error during LTM answer generation for '%s': %s", question, e, exc_info=True
            )
            final_answer = f"[Error: {type(e).__name__}]"

        return final_answer

    async def run_async(
        self, question: str, semaphore: Optional[asyncio.Semaphore] = None, **kwargs
    ) -> str:
        final_answer = "[Error: Async processing failed]"
        try:
            subs = await self.decompose_async(question, semaphore, **kwargs)
            solved = await self.solve_async(question, subs, semaphore, **kwargs)

            steps = "\n".join(f"{i + 1}. Q: {q}\n   A: {a}" for i, (q, a) in enumerate(solved))
            prompt = self.final_answer_prompt_template.format(solved_steps=steps, question=question)
            logger.debug("LTM Async Final Answer Prompt:\n%s", prompt)

            local_kwargs = kwargs.copy()
            gen_args = {
                "max_tokens": local_kwargs.pop("max_tokens", self.max_tokens),
                "seed": local_kwargs.pop("seed", self.seed),
                **local_kwargs,
            }
            if self.intermediate_output_format == "json":
                json_p = (
                    prompt
                    + '\n\nReturn exactly one JSON object with key "final_answer" whose value is the answer.\n\nJSON Answer:'
                )
                gen_args["response_model"] = ExtractedAnswer
                if semaphore:
                    async with semaphore:
                        parsed = await self.llm.generate_json_async(json_p, **gen_args)
                else:
                    parsed = await self.llm.generate_json_async(json_p, **gen_args)
                final_answer = str(parsed.final_answer).strip()
            else:
                if semaphore:
                    async with semaphore:
                        ans = await self.llm.generate_async(prompt, **gen_args)
                else:
                    ans = await self.llm.generate_async(prompt, **gen_args)
                final_answer = ans.strip()
        except Exception as e:
            logger.error(
                "Error during LTM async answer generation for '%s': %s", question, e, exc_info=True
            )
            final_answer = f"[Error: {type(e).__name__}]"

        return final_answer
