"""Generating a whole dataset, evenly across the generated question types."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Sequence

import structlog

from glossator.eval.corpus import CorpusDocument
from glossator.eval.datasets import EvalQuestion, QuestionType
from glossator.eval.generate.attempt import finalize_attempt, run_attempt
from glossator.eval.generate.models import (
    GENERATED_TYPES,
    GenerationAttempt,
    GenerationContext,
    TypeResult,
)
from glossator.eval.generate.planning import plan_attempts
from glossator.eval.lexical import LexicalIndex
from glossator.eval.providers.models import ChatProvider, ThinkingMode
from glossator.eval.run_records import RunRecorder

logger = structlog.get_logger(__name__)


async def generate_questions(
    provider: ChatProvider,
    documents: Sequence[CorpusDocument],
    *,
    n: int,
    model: str,
    seed: int,
    thinking: ThinkingMode | None = "disabled",
    attempts_per_question: int = 4,
    recorder: RunRecorder | None = None,
) -> tuple[list[EvalQuestion], list[GenerationAttempt], list[TypeResult]]:
    """Generate up to ``n`` questions, evenly across the six generated types.

    A type that cannot be filled does not fail the run: the dataset is written
    with what was accepted and the shortfall is reported.
    """
    if n < len(GENERATED_TYPES):
        raise ValueError(
            f"n must be at least {len(GENERATED_TYPES)} so every generated type is represented"
        )
    context = GenerationContext(
        provider=provider,
        model=model,
        thinking=thinking,
        documents=list(documents),
        index=LexicalIndex(documents),
        recorder=recorder,
    )
    rng = random.Random(seed)
    allocations = type_allocations(n)
    accepted: list[EvalQuestion] = []
    attempts: list[GenerationAttempt] = []
    results: list[TypeResult] = []

    for question_type in GENERATED_TYPES:
        target = allocations[question_type]
        budget = target * attempts_per_question
        plans = plan_attempts(documents, question_type, budget, rng)
        kept_here = 0
        used = 0
        while kept_here < target and used < len(plans):
            # Waves are sized to the remaining shortfall, doubled: at a high
            # acceptance rate the run pays for barely more than it needs, at a
            # low one it still finishes in a handful of round trips.
            wave = plans[used : used + min(len(plans) - used, max(1, (target - kept_here) * 2))]
            used += len(wave)
            outcomes = await asyncio.gather(*(run_attempt(context, plan) for plan in wave))
            for outcome in outcomes:
                attempt = finalize_attempt(context, outcome, still_needed=kept_here < target)
                attempts.append(attempt)
                if attempt.question is not None:
                    accepted.append(attempt.question)
                    kept_here += 1
        results.append(
            TypeResult(
                question_type=question_type,
                requested=target,
                accepted=kept_here,
                attempted=used,
            )
        )
        if kept_here < target:
            logger.warning(
                "question_type_short",
                question_type=question_type.value,
                accepted=kept_here,
                requested=target,
                attempted=used,
            )
    return accepted, attempts, results


def type_allocations(n: int) -> dict[QuestionType, int]:
    order = list(GENERATED_TYPES)
    allocations = {question_type: 1 for question_type in order}
    for index in range(n - len(order)):
        allocations[order[index % len(order)]] += 1
    return allocations
