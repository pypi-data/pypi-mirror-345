import asyncio
import logging
import math
from typing import List, Optional

from ..model import BaseLLM
from ..schemas import EvaluationResult, ThoughtExpansion

logger = logging.getLogger(__name__)


class TreeOfThoughts:
    class _Node:
        __slots__ = ("children", "parent", "prior", "steps", "value_sum", "visits")

        def __init__(
            self,
            steps: List[str],
            parent: Optional["TreeOfThoughts._Node"] = None,
            prior: float = 1.0,
        ) -> None:
            self.steps = steps
            self.parent = parent
            self.children: List["TreeOfThoughts._Node"] = []
            self.visits = 0
            self.value_sum = 0.0
            self.prior = prior

        def value(self) -> float:
            return self.value_sum / self.visits if self.visits > 0 else 0.0

        def is_leaf(self) -> bool:
            return not self.children

        def __repr__(self) -> str:
            return f"Node(steps={len(self.steps)}, val={self.value():.2f}, visits={self.visits})"

    def __init__(
        self,
        llm: BaseLLM,
        max_depth: int = 3,
        num_branches: int = 5,
        sims: int = 16,
        c_puct: float = 1.0,
        expand_prompt: str = (
            "Generate {k} distinct reasoning steps or thoughts to continue solving the problem, given the context below. "
            "Return as a JSON object with a single key 'thoughts' containing a list of strings.\n\n"
            "Context:\n{ctx}\n"
            "Question: {question}\n\n"
            "JSON Output:"
        ),
        eval_prompt: str = (
            "Rate the quality of the reasoning steps below for solving the question on a scale of 1-10 "
            '(1=bad, 10=excellent). Return response as a JSON object with keys "score" (int) and "justification" (str).\n\n'
            "Question: {question}\n"
            "Steps:\n{steps}\n\n"
            "JSON Evaluation:"
        ),
        *,
        max_tokens: Optional[int] = 256,
        seed: Optional[int] = None,
    ) -> None:
        self.llm = llm
        self.max_depth = max_depth
        self.num_branches = num_branches
        self.sims = sims
        self.c_puct = c_puct
        self.expand_prompt = expand_prompt
        self.eval_prompt = eval_prompt
        self.max_tokens = max_tokens
        self.seed = seed

    def _select(self, node: _Node) -> _Node:
        while not node.is_leaf():
            total_visits = sum(child.visits for child in node.children)
            if total_visits == 0:
                return node.children[0] if node.children else node

            sqrt_total = math.sqrt(total_visits)
            ucb_scores = [
                child.value() + self.c_puct * child.prior * (sqrt_total / (1 + child.visits))
                for child in node.children
            ]
            best_idx = ucb_scores.index(max(ucb_scores))
            node = node.children[best_idx]
        return node

    def _expand(self, node: _Node, question: str, **kwargs) -> None:
        ctx = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(node.steps))
        prompt = self.expand_prompt.format(k=self.num_branches, ctx=ctx, question=question)
        try:
            local_kwargs = kwargs.copy()
            generated = self.llm.generate_json(
                prompt,
                response_model=ThoughtExpansion,
                max_tokens=local_kwargs.pop("max_tokens", self.max_tokens),
                seed=local_kwargs.pop("seed", self.seed),
                **local_kwargs,
            )
            if not isinstance(generated, ThoughtExpansion):
                logger.warning("Expansion did not return ThoughtExpansion: %s", type(generated))
                return
            thoughts = [str(t).strip() for t in generated.thoughts if str(t).strip()]
        except Exception as e:
            logger.error("Expansion JSON failed: %s", e, exc_info=True)
            return

        prior = 1.0 / len(thoughts) if thoughts else 1.0
        for thought in thoughts[: self.num_branches]:
            child = TreeOfThoughts._Node([*node.steps, thought], parent=node, prior=prior)
            node.children.append(child)

    async def _expand_async(
        self, node: _Node, question: str, semaphore: Optional[asyncio.Semaphore], **kwargs
    ) -> None:
        ctx = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(node.steps))
        prompt = self.expand_prompt.format(k=self.num_branches, ctx=ctx, question=question)
        try:
            local_kwargs = kwargs.copy()
            gen_args = {
                "response_model": ThoughtExpansion,
                "max_tokens": local_kwargs.pop("max_tokens", self.max_tokens),
                "seed": local_kwargs.pop("seed", self.seed),
                **local_kwargs,
            }
            if semaphore:
                async with semaphore:
                    generated = await self.llm.generate_json_async(prompt, **gen_args)
            else:
                generated = await self.llm.generate_json_async(prompt, **gen_args)

            if not isinstance(generated, ThoughtExpansion):
                logger.warning(
                    "Async expansion did not return ThoughtExpansion: %s", type(generated)
                )
                return
            thoughts = [str(t).strip() for t in generated.thoughts if str(t).strip()]
        except Exception as e:
            logger.error("Async expansion JSON failed: %s", e, exc_info=True)
            return

        prior = 1.0 / len(thoughts) if thoughts else 1.0
        for thought in thoughts[: self.num_branches]:
            child = TreeOfThoughts._Node([*node.steps, thought], parent=node, prior=prior)
            node.children.append(child)

    def _evaluate(self, node: _Node, question: str, **kwargs) -> float:
        steps_str = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(node.steps))
        prompt = self.eval_prompt.format(question=question, steps=steps_str)
        try:
            local_kwargs = kwargs.copy()
            result = self.llm.generate_json(
                prompt,
                response_model=EvaluationResult,
                max_tokens=local_kwargs.pop("max_tokens", self.max_tokens),
                seed=local_kwargs.pop("seed", self.seed),
                **local_kwargs,
            )
            if isinstance(result, EvaluationResult):
                raw = float(result.score)
                return max(0.0, min(1.0, (raw - 1.0) / 9.0))
        except Exception as e:
            logger.error("Eval JSON failed: %s", e, exc_info=True)
        return 0.0

    async def _evaluate_async(
        self, node: _Node, question: str, semaphore: Optional[asyncio.Semaphore], **kwargs
    ) -> float:
        steps_str = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(node.steps))
        prompt = self.eval_prompt.format(question=question, steps=steps_str)
        try:
            local_kwargs = kwargs.copy()
            gen_args = {
                "response_model": EvaluationResult,
                "max_tokens": local_kwargs.pop("max_tokens", self.max_tokens),
                "seed": local_kwargs.pop("seed", self.seed),
                **local_kwargs,
            }
            if semaphore:
                async with semaphore:
                    result = await self.llm.generate_json_async(prompt, **gen_args)
            else:
                result = await self.llm.generate_json_async(prompt, **gen_args)

            if isinstance(result, EvaluationResult):
                raw = float(result.score)
                return max(0.0, min(1.0, (raw - 1.0) / 9.0))
        except Exception as e:
            logger.error("Async eval JSON failed: %s", e, exc_info=True)
        return 0.0

    def _backpropagate(self, node: _Node, value: float) -> None:
        cur = node
        while cur is not None:
            cur.visits += 1
            cur.value_sum += value
            cur = cur.parent

    def run(self, question: str, **kwargs) -> str:
        root = TreeOfThoughts._Node(steps=[], parent=None, prior=1.0)

        for sim in range(self.sims):
            logger.debug("Simulation %d/%d", sim + 1, self.sims)
            leaf = self._select(root)

            to_eval = leaf
            if len(leaf.steps) < self.max_depth:
                self._expand(leaf, question, **kwargs)
                if leaf.children:
                    to_eval = leaf.children[0]

            value = self._evaluate(to_eval, question, **kwargs)
            self._backpropagate(to_eval, value)

        if not root.children:
            logger.warning("No thoughts were generated; answering directly.")
            final_prompt = f"Answer the question: {question}"
        else:
            node = root
            while node.children:
                best_child = max(node.children, key=lambda c: (c.visits, c.value()))
                node = best_child
            ctx = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(node.steps))
            final_prompt = f"Given reasoning steps:\n{ctx}\n\nAnswer the question: {question}"

        try:
            local_kwargs = kwargs.copy()
            return self.llm.generate(
                final_prompt,
                max_tokens=local_kwargs.pop("max_tokens", self.max_tokens),
                seed=local_kwargs.pop("seed", self.seed),
                **local_kwargs,
            ).strip()
        except Exception as e:
            logger.error("Final answer generation failed: %s", e, exc_info=True)
            return "Error generating final answer."

    async def run_async(
        self, question: str, semaphore: Optional[asyncio.Semaphore] = None, **kwargs
    ) -> str:
        root = TreeOfThoughts._Node(steps=[], parent=None, prior=1.0)

        for sim in range(self.sims):
            logger.debug("Async Simulation %d/%d", sim + 1, self.sims)
            leaf = self._select(root)

            eval_node = leaf
            if len(leaf.steps) < self.max_depth:
                await self._expand_async(leaf, question, semaphore, **kwargs)
                if leaf.children:
                    eval_node = leaf.children[0]

            value = await self._evaluate_async(eval_node, question, semaphore, **kwargs)
            self._backpropagate(eval_node, value)

        if not root.children:
            logger.warning("No thoughts were generated async; answering directly.")
            final_prompt = f"Answer the question: {question}"
        else:
            node = root
            while node.children:
                best_child = max(node.children, key=lambda c: (c.visits, c.value()))
                node = best_child
            ctx = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(node.steps))
            final_prompt = f"Given reasoning steps:\n{ctx}\n\nAnswer the question: {question}"

        try:
            local_kwargs = kwargs.copy()
            gen_args = {
                "max_tokens": local_kwargs.pop("max_tokens", self.max_tokens),
                "seed": local_kwargs.pop("seed", self.seed),
                **local_kwargs,
            }
            if semaphore:
                async with semaphore:
                    return (await self.llm.generate_async(final_prompt, **gen_args)).strip()
            else:
                return (await self.llm.generate_async(final_prompt, **gen_args)).strip()
        except Exception as e:
            logger.error("Final async answer generation failed: %s", e, exc_info=True)
            return "Error generating final async answer."
