"""One candidate generated, checked, and turned into a record row."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from collections.abc import Sequence

import structlog

from glossator.eval.datasets import EvalQuestion, GoldSource, QuestionSource, QuestionType
from glossator.eval.generate.calls import (
    check_corpus_answers,
    check_page_alone,
    closed_book_probe,
    filter_candidate,
    foreign_vendors_named,
    generate_candidate,
)
from glossator.eval.generate.models import (
    DROP_PROVIDER_ERROR,
    AttemptOutcome,
    AttemptPlan,
    CandidateOutput,
    CapabilityOutput,
    CrossPageOutput,
    GenerationAttempt,
    GenerationContext,
    SourceContribution,
)
from glossator.eval.generate.prompts import PROMPT_HASHES, PROMPT_VERSION
from glossator.eval.providers.models import ProviderCallError
from glossator.eval.providers.scopes import candidate_scope

logger = structlog.get_logger(__name__)


def _capability_gold(plan: AttemptPlan, candidate: CandidateOutput) -> tuple[GoldSource, ...]:
    """Gold for a capability question: the matrix, plus the model card it names.

    The generator's ``names_single_model`` flag alone is not enough -- the card
    joins the gold only when the question actually writes that model's name.
    """
    gold = list(plan.gold)
    if not isinstance(candidate, CapabilityOutput) or not candidate.names_single_model:
        return tuple(gold)
    question = candidate.question.casefold()
    for source in plan.sources[1:]:
        names = [source.title, *_api_names(source.content)]
        if any(name.casefold() in question for name in names if name):
            gold.append(GoldSource(url=source.url))
    return tuple(gold)


_API_NAME_RE = re.compile(r"`([a-z0-9][a-z0-9.\-]{4,})`")


def _api_names(text: str) -> list[str]:
    return _API_NAME_RE.findall(text)


async def run_attempt(context: GenerationContext, plan: AttemptPlan) -> AttemptOutcome:
    """One candidate, generated and checked. Never raises on a provider failure."""
    outcome = AttemptOutcome(plan=plan, gold=plan.gold)
    with candidate_scope(plan.candidate_id):
        try:
            candidate = await generate_candidate(context, plan)
            outcome.candidate = candidate
            if isinstance(candidate, CrossPageOutput):
                outcome.contributions = [
                    SourceContribution(
                        url=plan.sources[0].url, contribution=candidate.page_a_contribution
                    ),
                    SourceContribution(
                        url=plan.sources[1].url, contribution=candidate.page_b_contribution
                    ),
                ]
            outcome.gold = (
                _capability_gold(plan, candidate)
                if plan.question_type == QuestionType.CAPABILITY
                else plan.gold
            )
            outcome.filter = await filter_candidate(context, plan, candidate, outcome.gold)
            if plan.question_type == QuestionType.CROSS_PAGE:
                outcome.page_alone = list(
                    await asyncio.gather(
                        check_page_alone(context, candidate, plan.documents[0], "Page A alone"),
                        check_page_alone(context, candidate, plan.documents[1], "Page B alone"),
                    )
                )
            if plan.question_type == QuestionType.UNANSWERABLE:
                outcome.corpus_check, outcome.consulted_sections = await check_corpus_answers(
                    context, candidate
                )
            if plan.question_type == QuestionType.POST_CUTOFF:
                outcome.closed_book_answer = await closed_book_probe(context, candidate)
        except ProviderCallError as error:
            # One unrecoverable call must cost one candidate, not the run.
            outcome.error = str(error)
            outcome.drop_reasons = [DROP_PROVIDER_ERROR]
            logger.info(
                "candidate_dropped_on_provider_error",
                question_type=plan.question_type.value,
                candidate_id=plan.candidate_id,
                error=str(error),
            )
            return outcome
    outcome.foreign_vendors = foreign_vendors_named(outcome.candidate.question)
    outcome.drop_reasons = _check_reasons(plan, outcome, outcome.candidate)
    return outcome


def _check_reasons(
    plan: AttemptPlan, outcome: AttemptOutcome, candidate: CandidateOutput
) -> list[str]:
    """Every reason this candidate fails, from the checks that were run."""
    reasons: list[str] = []
    verdict = outcome.filter
    if verdict is not None:
        if not verdict.standalone:
            reasons.append("not standalone")
        if not verdict.gold_condition_met:
            reasons.append("gold condition failed")
        if not verdict.not_answerable_from_title_alone:
            reasons.append("answerable from title alone")
        if not verdict.uses_every_gold_source:
            reasons.append("does not require every gold source")
        if not verdict.about_the_documented_product:
            reasons.append("not about the documented product")
    if outcome.foreign_vendors:
        reasons.append("names another vendor's product")
    expected_fully_answered = plan.question_type != QuestionType.UNANSWERABLE
    if candidate.fully_answered != expected_fully_answered:
        reasons.append("fully_answered conflicts with question type")
    if any(page.fully_answerable for page in outcome.page_alone):
        # One reason for every page, not one per page title: the title belongs on
        # the verdict in the record, and a reason that varies cannot be counted.
        reasons.append("answerable from one page alone")
    if outcome.corpus_check is not None and outcome.corpus_check.answered_by_corpus:
        reasons.append("the corpus answers it after all")
    return reasons


def finalize_attempt(
    context: GenerationContext, outcome: AttemptOutcome, *, still_needed: bool = True
) -> GenerationAttempt:
    """Turn an outcome into a record row, applying duplicate detection.

    Runs after the concurrent attempts of a wave have finished, so that two
    identical questions produced at the same time cannot both be accepted, and
    so that ``kept`` means what the dataset holds rather than what passed the
    checks: a wave overshoots on purpose, and the surplus is recorded as such.
    """
    plan = outcome.plan
    drop_reasons = list(outcome.drop_reasons)
    duplicate = False
    if outcome.candidate is not None:
        normalized = normalize_question(outcome.candidate.question)
        duplicate = normalized in context.seen
        if duplicate:
            drop_reasons.append("duplicate question")
        if not drop_reasons and not still_needed:
            drop_reasons.append("surplus, the type was already filled")
    kept = outcome.candidate is not None and not drop_reasons

    question: EvalQuestion | None = None
    if kept and outcome.candidate is not None:
        context.seen.add(normalize_question(outcome.candidate.question))
        question = EvalQuestion(
            id=_question_id(plan.question_type, outcome.candidate.question, outcome.gold),
            question=outcome.candidate.question.strip(),
            type=plan.question_type,
            gold=list(outcome.gold),
            reference_answer=outcome.candidate.reference_answer.strip(),
            language=plan.language,
            source=QuestionSource.GENERATED,
            generator=_generator_metadata(context, plan, outcome),
        )
    attempt = GenerationAttempt(
        candidate_id=plan.candidate_id,
        generator_type=plan.question_type.value,
        seed=[source.url for source in plan.sources],
        candidate=outcome.candidate,
        filter=outcome.filter,
        page_alone=outcome.page_alone,
        corpus_check=outcome.corpus_check,
        consulted_sections=outcome.consulted_sections,
        closed_book_answer=outcome.closed_book_answer,
        contributions=outcome.contributions,
        foreign_vendors=outcome.foreign_vendors,
        duplicate=duplicate,
        kept=kept,
        drop_reasons=drop_reasons,
        sampled_sources=list(plan.sources),
        question=question,
        error=outcome.error,
    )
    if context.recorder is not None:
        context.recorder.record_candidate(attempt)
    if not kept:
        logger.info(
            "generated_question_dropped",
            question_type=plan.question_type.value,
            reasons=drop_reasons,
        )
    return attempt


def _generator_metadata(
    context: GenerationContext, plan: AttemptPlan, outcome: AttemptOutcome
) -> dict[str, object]:
    metadata: dict[str, object] = {
        "model": context.model,
        "prompt_version": PROMPT_VERSION,
        "prompt_hashes": PROMPT_HASHES,
        "candidate_id": plan.candidate_id,
        "seed_section": [source.url for source in plan.sources],
    }
    if context.recorder is not None:
        metadata["run_dir"] = str(context.recorder.run_dir)
    if outcome.consulted_sections:
        metadata["sections_consulted"] = outcome.consulted_sections
    if outcome.closed_book_answer is not None:
        metadata["closed_book_answer"] = outcome.closed_book_answer
    if outcome.contributions:
        metadata["contributions"] = [item.model_dump(mode="json") for item in outcome.contributions]
    return metadata


def normalize_question(question: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", question.casefold()))


def _question_id(question_type: QuestionType, question: str, gold: Sequence[GoldSource]) -> str:
    material = {
        "type": question_type.value,
        "question": normalize_question(question),
        "gold": [source.model_dump() for source in gold],
    }
    digest = hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()[:16]
    return f"gen-{digest}"
