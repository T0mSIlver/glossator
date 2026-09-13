"""One question reworded by one kind of noise, checked, and turned into a dataset row."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from glossator.eval.datasets import EvalQuestion
from glossator.eval.perturb.models import (
    CHECK_MAX_TOKENS,
    CHECK_TEMPERATURE,
    DROP_ADDS_FACTS,
    DROP_DIFFERENT_QUESTION,
    DROP_EMPTY,
    DROP_NO_SUBSTITUTION,
    DROP_PROVIDER_ERROR,
    DROP_TOO_SHORT,
    DROP_UNCHANGED,
    DROP_UNPARSED,
    GENERATION_MAX_TOKENS,
    GENERATION_TEMPERATURE,
    KINDS,
    TYPOS,
    WRONG_TERM,
    NoisyQuestion,
    PerturbationRow,
    SameQuestion,
    Substitution,
    WrongTermQuestion,
)
from glossator.eval.perturb.prompts import (
    FILTER_INSTRUCTIONS,
    KIND_INSTRUCTIONS,
    PROMPT_VERSION,
    SYSTEM,
)
from glossator.eval.perturb.typos import typo_variant
from glossator.eval.providers.models import ChatProvider, ProviderCallError, ThinkingMode
from glossator.eval.providers.scopes import call_scope, candidate_scope
from glossator.eval.run_records import RunRecorder


def assign_kinds(subset: Sequence[EvalQuestion]) -> list[tuple[EvalQuestion, str]]:
    """One noise kind per question, round-robin in subset order."""
    return [(question, KINDS[index % len(KINDS)]) for index, question in enumerate(subset)]


async def noisy_variant(
    provider: ChatProvider,
    question: EvalQuestion,
    kind: str,
    *,
    model: str,
    thinking: ThinkingMode | None = None,
) -> NoisyQuestion:
    """One model-written variant of ``kind``."""
    schema: type[NoisyQuestion] = WrongTermQuestion if kind == WRONG_TERM else NoisyQuestion
    user = (
        f"{KIND_INSTRUCTIONS[kind]}\n\n"
        f"Question: {question.question}\n"
        f"Return JSON with noisy_question"
        + (" , original_term and replacement_term.\n" if kind == WRONG_TERM else ".\n")
    )
    with candidate_scope(question.id), call_scope(f"perturb:{kind}"):
        completion = await provider.complete(
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
            model=model,
            temperature=GENERATION_TEMPERATURE,
            max_tokens=GENERATION_MAX_TOKENS,
            response_schema=schema,
            thinking=thinking,
            cache_nonce=None,
        )
    parsed = completion.parsed
    if not isinstance(parsed, NoisyQuestion):
        raise ValueError(DROP_UNPARSED)
    return parsed


async def check_variant(
    provider: ChatProvider,
    question: EvalQuestion,
    kind: str,
    variant: str,
    *,
    model: str,
    thinking: ThinkingMode | None = None,
) -> SameQuestion:
    """Whether the variant still asks what the question asked."""
    user = (
        f"{FILTER_INSTRUCTIONS}\n\n"
        f"Degradation applied: {kind}\n"
        f"Original: {question.question}\n"
        f"Degraded: {variant}\n"
    )
    with candidate_scope(question.id), call_scope("filter"):
        completion = await provider.complete(
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
            model=model,
            temperature=CHECK_TEMPERATURE,
            max_tokens=CHECK_MAX_TOKENS,
            response_schema=SameQuestion,
            thinking=thinking,
            cache_nonce=None,
        )
    parsed = completion.parsed
    if not isinstance(parsed, SameQuestion):
        raise ValueError(DROP_UNPARSED)
    return parsed


async def perturb_one(
    provider: ChatProvider,
    question: EvalQuestion,
    kind: str,
    *,
    model: str,
    seed: int,
    thinking: ThinkingMode | None = None,
) -> PerturbationRow:
    """One question, one kind of noise, checked. Never raises: a failure is a row."""
    row = PerturbationRow(
        candidate_id=f"{question.id}-{kind}",
        source_id=question.id,
        noise=kind,
        generator_type=kind,
        original_question=question.question,
        kept=False,
        drop_reasons=[],
    )
    substitution: Substitution | None = None
    try:
        if kind == TYPOS:
            variant = typo_variant(question.question, seed=seed, question_id=question.id)
            if variant is None:
                return row.model_copy(update={"drop_reasons": [DROP_TOO_SHORT]})
        else:
            generated = await noisy_variant(
                provider, question, kind, model=model, thinking=thinking
            )
            variant = generated.noisy_question.strip()
            if isinstance(generated, WrongTermQuestion):
                substitution = Substitution(
                    removed=generated.original_term.strip(),
                    inserted=generated.replacement_term.strip(),
                )
    except (ProviderCallError, ValueError) as error:
        return row.model_copy(
            update={"drop_reasons": [f"{DROP_PROVIDER_ERROR}: {type(error).__name__}: {error}"]}
        )

    row = row.model_copy(update={"variant": variant, "substitution": substitution})
    reasons = _mechanical_reasons(question, kind, variant, substitution)
    if reasons:
        return row.model_copy(update={"drop_reasons": reasons})

    try:
        verdict = await check_variant(
            provider, question, kind, variant, model=model, thinking=thinking
        )
    except (ProviderCallError, ValueError) as error:
        return row.model_copy(
            update={"drop_reasons": [f"{DROP_PROVIDER_ERROR}: {type(error).__name__}: {error}"]}
        )

    row = row.model_copy(update={"filter": verdict})
    if not verdict.asks_the_same_thing:
        return row.model_copy(update={"drop_reasons": [DROP_DIFFERENT_QUESTION]})
    if verdict.adds_facts:
        return row.model_copy(update={"drop_reasons": [DROP_ADDS_FACTS]})
    return row.model_copy(
        update={"kept": True, "question": noisy_question(question, kind, variant, substitution)}
    )


def _mechanical_reasons(
    question: EvalQuestion, kind: str, variant: str, substitution: Substitution | None
) -> list[str]:
    """What can be decided about a variant without asking a model."""
    reasons: list[str] = []
    if not variant:
        reasons.append(DROP_EMPTY)
    elif variant == question.question:
        reasons.append(DROP_UNCHANGED)
    if kind == WRONG_TERM and (
        substitution is None
        or not substitution.removed
        or not substitution.inserted
        or substitution.removed == substitution.inserted
    ):
        reasons.append(DROP_NO_SUBSTITUTION)
    return reasons


def noisy_question(
    question: EvalQuestion, kind: str, variant: str, substitution: Substitution | None
) -> EvalQuestion:
    """The dataset row: the noisy wording, the original gold and reference answer."""
    generator = dict(question.generator or {})
    generator.update(
        {
            "noise": kind,
            "perturbed_from": question.id,
            "perturbation_prompt": PROMPT_VERSION,
            "original_question": question.question,
        }
    )
    if substitution is not None:
        generator["noise_substitution"] = substitution.model_dump(mode="json")
    return question.model_copy(
        update={"id": f"{question.id}-{kind}", "question": variant, "generator": generator}
    )


async def perturb_all(
    provider: ChatProvider,
    pairs: Sequence[tuple[EvalQuestion, str]],
    *,
    recorder: RunRecorder,
    model: str,
    seed: int,
    thinking: ThinkingMode | None,
    concurrency: int,
) -> list[EvalQuestion]:
    """Every pair, in batches, recorded as each batch lands."""
    kept: list[EvalQuestion] = []
    for start in range(0, len(pairs), concurrency):
        batch = pairs[start : start + concurrency]
        rows = await asyncio.gather(
            *(
                perturb_one(provider, question, kind, model=model, seed=seed, thinking=thinking)
                for question, kind in batch
            )
        )
        # Recorded in subset order rather than completion order, so the same seed
        # writes the same file whatever the network did.
        for row in rows:
            recorder.record_candidate(row)
            if row.question is not None:
                kept.append(row.question)
    return kept
