"""One failed answer's class and sub-label, decided from the evidence in its record."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from glossator.answer.citations import Citation
from glossator.eval.agreement import LABEL_SCORE, CorrectnessLabel
from glossator.eval.answer_eval.models import CORRECTNESS_SCORE, QuestionRecord
from glossator.eval.failures.corpus import ChunkIndex
from glossator.eval.failures.evidence import (
    accepts_page,
    accepts_section,
    context_chunk_ids,
    is_answerable,
    is_failure,
    page_url,
    refusal_correct,
    retrieved_chunk_ids,
    verdict_of,
)
from glossator.eval.failures.models import DefectSignal, FailureClass, FailureRecord, SubLabel

EVIDENCE_CHARS = 220
"""How much of a quoted reason or answer an evidence line carries. Long enough to
read the point, short enough that a table of them is still a table; the whole text
stays in the source run's records."""

REFERENCE_MENTION = re.compile(r"\breference(?:s|d)?\b", re.IGNORECASE)
"""The judge's own words about the reference answer. `answer-judge/v2` shows the
judge the reference and asks it to grade against it, so a reason that names the
reference is the judge saying the two disagree *about the reference*, which is
where a bad reference shows itself."""


def shorten(text: str, limit: int = EVIDENCE_CHARS) -> str:
    """One line of at most `limit` characters, cut on a word where it can be."""
    flat = " ".join(text.split())
    if len(flat) <= limit:
        return flat
    cut = flat[:limit].rsplit(" ", maxsplit=1)[0]
    return f"{cut or flat[:limit]} [...]"


def _defect_signals(record: QuestionRecord, human: CorrectnessLabel | None) -> list[DefectSignal]:
    """Deterministic hints, in a fixed order. None of them decides anything."""
    signals: list[DefectSignal] = []
    verdict = record.judge.verdict if record.judge else None
    if verdict is not None and REFERENCE_MENTION.search(verdict.correctness_reason):
        signals.append(DefectSignal.JUDGE_NAMES_THE_REFERENCE)
    judged = CORRECTNESS_SCORE[verdict.correctness] if verdict else None
    if human is not None and judged is not None and LABEL_SCORE[human] > judged:
        signals.append(DefectSignal.HUMAN_IS_MORE_LENIENT)
    return signals


def _generation_sub_label(record: QuestionRecord) -> tuple[SubLabel, str]:
    """What the citations say about a wrong answer that had the right page in front of it."""
    verified = [
        citation
        for citation in record.citations
        if accepts_section(record, citation.url, citation.anchor)
    ]
    if verified:
        return SubLabel.VERIFIED_QUOTE_FROM_GOLD, _quote_evidence(verified[0], verified=True)
    rejected = [
        citation
        for citation in record.unverified_citations
        if accepts_section(record, citation.url, citation.anchor)
    ]
    if rejected:
        return SubLabel.UNVERIFIED_QUOTE_FROM_GOLD, _quote_evidence(rejected[0], verified=False)
    cited = (
        ", ".join(sorted({page_url(citation.url) for citation in record.citations})) or "nothing"
    )
    return SubLabel.NO_CITATION_TO_GOLD, f"cited {cited} instead of the gold section"


def _quote_evidence(citation: Citation, *, verified: bool) -> str:
    state = "verified" if verified else f"rejected ({citation.reason or 'no reason recorded'})"
    return f'{state} quote from the gold section: "{shorten(citation.quote, 120)}"'


def classify(
    record: QuestionRecord,
    *,
    index: ChunkIndex,
    run_name: str,
    run_dir: Path,
    reranked: Mapping[tuple[str, str], set[str]],
    human: CorrectnessLabel | None,
) -> FailureRecord | None:
    """One failed answer's class, or None when the answer did not fail.

    The order is the point. Each test is only reached when the one before it
    passed, so a class always means "everything upstream of this worked": a
    generation failure is a failure with the gold section in the context, not
    merely a wrong answer.
    """
    if not is_failure(record):
        return None

    answerable = is_answerable(record)
    retrieved = retrieved_chunk_ids(record.trace)
    context = context_chunk_ids(record.trace)
    dropped = set(record.trace.dropped_chunk_ids) if record.trace else set()

    gold_retrieved = any(
        (page := index.page(chunk_id)) is not None and accepts_page(record, page)
        for chunk_id in retrieved
    )
    gold_in_context = any(
        (page := index.page(chunk_id)) is not None and accepts_page(record, page)
        for chunk_id in context
    )
    gold_section_in_context = any(
        (facts := index.facts.get(chunk_id)) is not None
        and accepts_section(record, facts.url, facts.anchor)
        for chunk_id in context
    )
    gold_chunk_dropped = any(
        (page := index.page(chunk_id)) is not None and accepts_page(record, page)
        for chunk_id in dropped
    )

    offered = reranked.get((record.question_id, record.strategy))
    gold_page_reranked_in = (
        any(accepts_page(record, url) for url in offered) if offered is not None else None
    )

    signals = _defect_signals(record, human)
    verdict = record.judge.verdict if record.judge else None
    common: dict[str, Any] = {
        "run": run_name,
        "run_dir": str(run_dir),
        "strategy": record.strategy,
        "variant": record.variant,
        "question_id": record.question_id,
        "question": record.question,
        "question_type": record.question_type,
        "language": record.language,
        "verdict": verdict_of(record),
        "insufficient_evidence": record.insufficient_evidence,
        "refusal_correct": refusal_correct(record),
        "answerable": answerable,
        "gold_urls": list(record.gold_urls),
        "gold_anchors": list(record.gold_anchors),
        "gold_retrieved": gold_retrieved,
        "gold_in_context": gold_in_context,
        "gold_section_in_context": gold_section_in_context,
        "gold_chunk_dropped": gold_chunk_dropped,
        "gold_page_reranked_in": gold_page_reranked_in,
        "retrieved_chunks": len(retrieved),
        "unresolved_chunks": len(retrieved) - index.resolves(retrieved),
        "context_chunks": len(context),
        "context_tokens": record.trace.context_tokens if record.trace else 0,
        "retrieved_pages": _retrieved_pages(retrieved, index),
        "reference_defect_suspected": bool(signals),
        "defect_signals": signals,
        "human_label": human,
        "judge_reason": shorten(verdict.correctness_reason) if verdict else "",
        "answer_opening": shorten(record.answer_markdown, 160),
        "error": record.error,
    }

    if answerable:
        if not gold_retrieved:
            sub_label, evidence = _retrieval_sub_label(record, gold_page_reranked_in, common)
            return FailureRecord(
                failure_class=FailureClass.RETRIEVAL_MISS,
                sub_label=sub_label,
                evidence=evidence,
                **common,
            )
        if not gold_in_context:
            sub_label = (
                SubLabel.DROPPED_FROM_CONTEXT
                if gold_chunk_dropped
                else SubLabel.OUTRANKED_IN_ASSEMBLY
            )
            reason = (
                "the gold chunk is in trace.dropped_chunk_ids"
                if gold_chunk_dropped
                else "the gold chunk was retrieved but no source in the context came from it"
            )
            return FailureRecord(
                failure_class=FailureClass.CONTEXT_MISS,
                sub_label=sub_label,
                evidence=(
                    f"{reason}; {len(context)} sources and "
                    f"{common['context_tokens']} tokens were assembled"
                ),
                **common,
            )
        if record.insufficient_evidence:
            where = (
                "the gold section"
                if gold_section_in_context
                else "another section of the gold page"
            )
            return FailureRecord(
                failure_class=FailureClass.REFUSAL,
                sub_label=SubLabel.FALSE_REFUSAL,
                evidence=(
                    f"refused an answerable question with {where} in the context: "
                    f'"{shorten(record.answer_markdown, 120)}"'
                ),
                **common,
            )
        sub_label, evidence = _generation_sub_label(record)
        return FailureRecord(
            failure_class=FailureClass.GENERATION, sub_label=sub_label, evidence=evidence, **common
        )

    return FailureRecord(
        failure_class=FailureClass.REFUSAL,
        sub_label=SubLabel.MISSED_REFUSAL,
        evidence=(
            "answered a question the dataset marks unanswerable, citing "
            f"{len(record.citations)} verified source(s): "
            f'"{shorten(record.answer_markdown, 120)}"'
        ),
        **common,
    )


def _retrieval_sub_label(
    record: QuestionRecord, gold_page_reranked_in: bool | None, common: Mapping[str, Any]
) -> tuple[SubLabel, str]:
    pages = ", ".join(common["retrieved_pages"][:3]) or "nothing"
    gold = ", ".join(page_url(url) for url in record.gold_urls)
    if gold_page_reranked_in is True:
        return (
            SubLabel.RERANKER_DROP,
            f"the reranker was offered {gold} and did not return it; the answer saw {pages}",
        )
    if gold_page_reranked_in is False:
        return SubLabel.SEARCH_MISS, f"{gold} was not among the reranker's candidates; saw {pages}"
    return (
        SubLabel.CANDIDATES_NOT_RECORDED,
        f"no chunk of {gold} in any round; the answer saw {pages}",
    )


def _retrieved_pages(chunk_ids: Sequence[str], index: ChunkIndex) -> list[str]:
    """The distinct pages behind a list of chunk ids, in rank order."""
    pages: dict[str, None] = {}
    for chunk_id in chunk_ids:
        page = index.page(chunk_id)
        if page is not None:
            pages.setdefault(page, None)
    return list(pages)
