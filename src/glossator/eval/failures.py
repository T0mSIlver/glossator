"""Why an answer failed: retrieval, context, generation, refusal, or the question.

An answer evaluation says how often the pipeline is wrong. It does not say which
part of the pipeline was wrong, and that is the number that decides where the next
effort goes: a retrieval miss and a generation failure on the same question call
for opposite work, and on a small generator (Ministral 3 14B, D-017a) the
temptation is to blame the model for both.

This reads the records an answer evaluation already wrote (D-023) and assigns each
failed answer to one class, in a fixed order, from evidence that is in the record:
the chunk ids every retrieval round returned, the chunk ids the assembled context
carried, the citations and their verification, and the refusal flag. It makes no
model call, so it can be re-run on any past run for free and its numbers are
recomputable from `records.jsonl` alone.

The one thing the records do not carry is the page behind a retrieved chunk id.
Chunk ids are ``uuid5(NAMESPACE_DNS, "<page url>:char:<start>-<end>")`` -- the
toolkit's ``compute_id`` over the extractor's ``source_id``, which is the page URL
(``glossator.ingest.extractor``) -- and the chunker is deterministic and offline,
so the whole map is rebuilt from the vendored corpus in about a second without
Vespa, an index, or a network call. `metrics.json` records how many of the run's
recorded chunk ids the map resolved, so a corpus that has moved on since a run
shows up as an unresolved count rather than as a silently wrong class.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import time
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from functools import cache
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import structlog
from dotenv import load_dotenv
from mistralai.search.toolkit.common.text import sanitize_text
from mistralai.search.toolkit.document import compute_char_locator, compute_id
from pydantic import BaseModel, ConfigDict, Field

from glossator.answer.citations import Citation, Trace
from glossator.eval.agreement import (
    LABEL_SCORE,
    CorrectnessLabel,
    labels_for_run,
    read_human_labels,
)
from glossator.eval.answer_eval import (
    CORRECTNESS_SCORE,
    QuestionRecord,
    accepts_model_card,
    read_records,
)
from glossator.eval.charts import stacked_bar_chart
from glossator.eval.datasets import QuestionType
from glossator.eval.providers import (
    OpenAICompatibleProvider,
    ProviderCallError,
    ProviderName,
    TokenUsage,
    call_scope,
    candidate_scope,
)
from glossator.eval.run_records import RUN_NAME_RE
from glossator.index.variants import VARIANTS, ChunkStrategy
from glossator.ingest.chunker import PageFacts, build_chunker
from glossator.ingest.pages import iter_page_paths, load_page

logger = structlog.get_logger(__name__)

RUNS_ROOT = Path("eval/runs")
DEFAULT_CORPUS = Path("corpus/mistral-docs")
DEFAULT_LABELS = Path("eval/labels/dev60-rerank-human.jsonl")
ANSWER_EVAL_KIND = "answer_eval"
FAILURES_KIND = "failure_analysis"

EXAMPLES_PER_CLASS = 3
"""How many worked examples the README shows per class, per run."""

EVIDENCE_CHARS = 220
"""How much of a quoted reason or answer an evidence line carries. Long enough to
read the point, short enough that a table of them is still a table; the whole text
stays in the source run's records."""


class FailureClass(StrEnum):
    """Where an answer went wrong. One per failed answer, decided in this order."""

    RETRIEVAL_MISS = "retrieval_miss"
    CONTEXT_MISS = "context_miss"
    GENERATION = "generation_failure"
    REFUSAL = "refusal_failure"


CLASS_ORDER: tuple[FailureClass, ...] = (
    FailureClass.RETRIEVAL_MISS,
    FailureClass.CONTEXT_MISS,
    FailureClass.GENERATION,
    FailureClass.REFUSAL,
)

CLASS_TITLES: dict[FailureClass, str] = {
    FailureClass.RETRIEVAL_MISS: "retrieval miss",
    FailureClass.CONTEXT_MISS: "context miss",
    FailureClass.GENERATION: "generation failure",
    FailureClass.REFUSAL: "refusal failure",
}


class SubLabel(StrEnum):
    """What kind of failure of its class this is."""

    RERANKER_DROP = "reranker_drop"
    SEARCH_MISS = "search_miss"
    CANDIDATES_NOT_RECORDED = "candidates_not_recorded"
    DROPPED_FROM_CONTEXT = "dropped_from_context"
    OUTRANKED_IN_ASSEMBLY = "outranked_in_assembly"
    NO_CITATION_TO_GOLD = "no_citation_to_gold"
    UNVERIFIED_QUOTE_FROM_GOLD = "unverified_quote_from_gold"
    VERIFIED_QUOTE_FROM_GOLD = "verified_quote_from_gold"
    FALSE_REFUSAL = "false_refusal"
    MISSED_REFUSAL = "missed_refusal"


SUB_LABELS: dict[FailureClass, tuple[SubLabel, ...]] = {
    FailureClass.RETRIEVAL_MISS: (
        SubLabel.RERANKER_DROP,
        SubLabel.SEARCH_MISS,
        SubLabel.CANDIDATES_NOT_RECORDED,
    ),
    FailureClass.CONTEXT_MISS: (SubLabel.DROPPED_FROM_CONTEXT, SubLabel.OUTRANKED_IN_ASSEMBLY),
    FailureClass.GENERATION: (
        SubLabel.NO_CITATION_TO_GOLD,
        SubLabel.UNVERIFIED_QUOTE_FROM_GOLD,
        SubLabel.VERIFIED_QUOTE_FROM_GOLD,
    ),
    FailureClass.REFUSAL: (SubLabel.FALSE_REFUSAL, SubLabel.MISSED_REFUSAL),
}


class DefectSignal(StrEnum):
    """A deterministic hint that the question or its reference answer is at fault."""

    JUDGE_NAMES_THE_REFERENCE = "judge_names_the_reference"
    HUMAN_IS_MORE_LENIENT = "human_is_more_lenient"


_REFERENCE_MENTION = re.compile(r"\breference(?:s|d)?\b", re.IGNORECASE)
"""The judge's own words about the reference answer. `answer-judge/v2` shows the
judge the reference and asks it to grade against it, so a reason that names the
reference is the judge saying the two disagree *about the reference*, which is
where a bad reference shows itself."""


# --------------------------------------------------------------------------- #
# The corpus side: chunk id -> page and section
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ChunkFacts:
    """Where one chunk sits in the corpus."""

    url: str
    anchor: str | None
    heading_path: tuple[str, ...]

    @property
    def heading_line(self) -> str:
        return " > ".join(self.heading_path)


@dataclass(frozen=True, slots=True)
class ChunkIndex:
    """Every chunk id one chunking of one corpus produces, with its page and section."""

    facts: Mapping[str, ChunkFacts]
    chunking: ChunkStrategy

    def page(self, chunk_id: str) -> str | None:
        found = self.facts.get(chunk_id)
        return found.url if found else None

    def resolves(self, chunk_ids: Iterable[str]) -> int:
        return sum(chunk_id in self.facts for chunk_id in chunk_ids)


@cache
def chunk_index(corpus_dir: Path, chunking: ChunkStrategy) -> ChunkIndex:
    """The chunk map for one corpus directory, built once per process.

    The body is sanitized exactly as the extractor sanitizes it before chunking,
    because the offsets the ids are built from index into the sanitized body.
    """
    started = time.perf_counter()
    chunker = build_chunker(chunking)
    facts: dict[str, ChunkFacts] = {}
    for path in iter_page_paths(corpus_dir):
        page = load_page(path)
        body = sanitize_text(page.body)
        page_facts = PageFacts(url=page.url, title=page.title, kind=page.kind, locale=page.locale)
        for spec in chunker.plan(body, page_facts):
            chunk_id = compute_id(page.url, compute_char_locator(spec.start, spec.end))
            facts[chunk_id] = ChunkFacts(
                url=page.url,
                anchor=spec.metadata.anchor,
                heading_path=tuple(spec.metadata.heading_path),
            )
    logger.info(
        "Built the chunk map",
        corpus=str(corpus_dir),
        chunking=str(chunking),
        chunks=len(facts),
        seconds=round(time.perf_counter() - started, 2),
    )
    return ChunkIndex(facts=facts, chunking=chunking)


@cache
def _pages_by_url(corpus_dir: Path) -> Mapping[str, Path]:
    return {load_page(path).url: path for path in iter_page_paths(corpus_dir)}


def gold_section_text(
    corpus_dir: Path, chunking: ChunkStrategy, url: str, anchor: str | None
) -> str:
    """The chunk text the dataset points at, for a judge that has to read it.

    A gold source with no anchor names the whole page, so the whole page body
    comes back; the anchored case returns the chunks that carry that anchor, in
    reading order.
    """
    path = _pages_by_url(corpus_dir).get(url)
    if path is None:
        return ""
    page = load_page(path)
    body = sanitize_text(page.body)
    if anchor is None:
        return body
    page_facts = PageFacts(url=page.url, title=page.title, kind=page.kind, locale=page.locale)
    parts = [
        body[spec.start : spec.end]
        for spec in build_chunker(chunking).plan(body, page_facts)
        if spec.metadata.anchor == anchor
    ]
    return "\n\n".join(parts) or body


# --------------------------------------------------------------------------- #
# The record side: what one answer did
# --------------------------------------------------------------------------- #


def page_url(url: str) -> str:
    """A citation or gold URL without its fragment: the page a reader lands on."""
    return urlparse(url)._replace(fragment="").geturl()


def retrieved_chunk_ids(trace: Trace | None) -> list[str]:
    """Every chunk id any round of this answer saw, in the order it first appeared.

    Every event that returns chunks carries them: the seed retrieval, each tool
    search, open, grep and read of the loop, and the assembly. A chunk the loop
    found in round three is as retrieved as one the seed search found.
    """
    if trace is None:
        return []
    seen: dict[str, None] = {}
    for event in trace.events:
        for chunk_id in event.result_ids:
            seen.setdefault(chunk_id, None)
    return list(seen)


def context_chunk_ids(trace: Trace | None) -> list[str]:
    """The chunk ids of the sources the model was actually shown."""
    if trace is None:
        return []
    seen: dict[str, None] = {}
    for source in trace.sources:
        for chunk_id in source.chunk_ids:
            seen.setdefault(chunk_id, None)
    return list(seen)


def accepts_page(record: QuestionRecord, url: str) -> bool:
    """Whether this URL is one the dataset's gold accepts for this question.

    The gold URLs, plus the capability relaxation the answer evaluation already
    applies to citations (D-033): the card of a model the question names stands
    in for the ``/models`` matrix.
    """
    if page_url(url) in {page_url(gold) for gold in record.gold_urls}:
        return True
    return accepts_model_card(
        url,
        question=record.question,
        question_type=record.question_type,
        gold_urls=record.gold_urls,
    )


def accepts_section(record: QuestionRecord, url: str, anchor: str | None) -> bool:
    """Whether this (URL, anchor) pair is the section the dataset points at.

    A gold source with no anchor is matched by any section of that page: the
    dataset is saying the page is the answer, and most of the corpus's headings
    have no anchor to be more precise about (D-003a). Same convention as
    `answer_eval.gold_anchor_match`, so the two numbers stay comparable.
    """
    for gold_url, gold_anchor in zip(record.gold_urls, record.gold_anchors, strict=True):
        if page_url(url) == page_url(gold_url) and (gold_anchor is None or anchor == gold_anchor):
            return True
    return accepts_model_card(
        url,
        question=record.question,
        question_type=record.question_type,
        gold_urls=record.gold_urls,
    )


def is_answerable(record: QuestionRecord) -> bool:
    return record.question_type != QuestionType.UNANSWERABLE.value


def verdict_of(record: QuestionRecord) -> str | None:
    """The primary judge's correctness label, or None when nothing judged it."""
    if record.judge is None or record.judge.verdict is None:
        return None
    return record.judge.verdict.correctness


def refusal_correct(record: QuestionRecord) -> bool:
    return record.insufficient_evidence == (not is_answerable(record))


def is_failure(record: QuestionRecord) -> bool:
    """Whether this answer failed at all: a bad verdict, or a refusal in the wrong direction."""
    return verdict_of(record) in ("partial", "wrong") or not refusal_correct(record)


# --------------------------------------------------------------------------- #
# Reranker candidates, when the run recorded them
# --------------------------------------------------------------------------- #

_CANDIDATE_LINE = re.compile(r"^\[(?P<number>\d+)\] (?P<url>\S+) \| ", re.MULTILINE)


def rerank_candidates(run_dir: Path) -> dict[tuple[str, str], set[str]]:
    """The pages the reranker was offered, per (question, strategy), from `calls.jsonl`.

    The reranker prompt lists its candidates as ``[n] <citation url> | <heading>``
    (`glossator.retrieval.reranker.render_candidates`), so a recorded rerank call
    is the only surviving record of what ranked *before* the reranker cut the list
    to `top_k`. Runs made before reranker calls reached the ledger (D-023b) have
    none, and the caller reports that as an unknown rather than as a search miss.
    """
    calls = run_dir / "calls.jsonl"
    if not calls.exists():
        return {}
    offered: dict[tuple[str, str], set[str]] = {}
    with calls.open() as handle:
        for line in handle:
            # Parsing every row of a 14 MB ledger to find a call kind that most
            # runs do not have costs more than the whole analysis.
            if '"rerank"' not in line:
                continue
            row = json.loads(line)
            if row.get("purpose") != "rerank":
                continue
            key = (str(row.get("question_id")), str(row.get("strategy")))
            for message in row.get("messages") or []:
                if message.get("role") != "user":
                    continue
                for match in _CANDIDATE_LINE.finditer(str(message.get("content") or "")):
                    offered.setdefault(key, set()).add(page_url(match.group("url")))
    return offered


# --------------------------------------------------------------------------- #
# One classified failure
# --------------------------------------------------------------------------- #


class FailureRecord(BaseModel):
    """One failed answer, its class, and the evidence that decided the class."""

    model_config = ConfigDict(frozen=True)

    run: str
    run_dir: str
    strategy: str
    variant: str
    question_id: str
    question: str
    question_type: str
    language: str
    failure_class: FailureClass
    sub_label: SubLabel
    evidence: str

    verdict: str | None = None
    insufficient_evidence: bool = False
    refusal_correct: bool = True
    answerable: bool = True

    gold_urls: list[str] = Field(default_factory=list)
    gold_anchors: list[str | None] = Field(default_factory=list)
    gold_retrieved: bool = False
    gold_in_context: bool = False
    gold_section_in_context: bool = False
    gold_chunk_dropped: bool = False
    gold_page_reranked_in: bool | None = None

    retrieved_chunks: int = 0
    unresolved_chunks: int = 0
    context_chunks: int = 0
    context_tokens: int = 0
    retrieved_pages: list[str] = Field(default_factory=list)

    reference_defect_suspected: bool = False
    defect_signals: list[DefectSignal] = Field(default_factory=list)
    human_label: CorrectnessLabel | None = None
    judge_reason: str = ""
    answer_opening: str = ""
    error: str | None = None
    defect_judgement: DefectJudgement | None = None


class DefectVerdict(BaseModel):
    """The reference-defect judge's structured output."""

    model_config = ConfigDict(frozen=True)

    supported: Literal["yes", "partly", "no"]
    reason: str


class DefectJudgement(BaseModel):
    """One reference-defect judgement, complete enough to re-read without the model."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    model: str
    provider: ProviderName | None = None
    prompt_version: str
    input_text: str
    raw_output: str = ""
    verdict: DefectVerdict | None = None
    error: str | None = None
    latency_ms: float = 0.0
    usage: TokenUsage = TokenUsage()


FailureRecord.model_rebuild()


def _shorten(text: str, limit: int = EVIDENCE_CHARS) -> str:
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
    if verdict is not None and _REFERENCE_MENTION.search(verdict.correctness_reason):
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
    return f'{state} quote from the gold section: "{_shorten(citation.quote, 120)}"'


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
        "judge_reason": _shorten(verdict.correctness_reason) if verdict else "",
        "answer_opening": _shorten(record.answer_markdown, 160),
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
                    f'"{_shorten(record.answer_markdown, 120)}"'
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
            f'"{_shorten(record.answer_markdown, 120)}"'
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


# --------------------------------------------------------------------------- #
# Runs in, rows out
# --------------------------------------------------------------------------- #


class SkippedRun(BaseModel):
    """A directory that was named on the command line but holds no answers."""

    model_config = ConfigDict(frozen=True)

    run_dir: str
    kind: str
    reason: str


@dataclass(frozen=True, slots=True)
class AnalysedRun:
    """One answer-evaluation run: its configuration and its failures.

    The answer counts per strategy and per question type are carried here rather
    than re-read later: they are the denominators of every share in the README,
    and a failure row cannot supply them (a strategy whose answers all passed has
    no rows at all).
    """

    path: Path
    name: str
    config: Mapping[str, Any]
    answers: int
    judged: int
    errors: int
    failures: tuple[FailureRecord, ...]
    resolved_chunks: int
    recorded_chunks: int
    answers_by_strategy: Mapping[str, int]
    answers_by_question_type: Mapping[str, int]
    reference_answers: Mapping[tuple[str, str], str]
    passed_judged: int
    passed_naming_the_reference: int
    """How often an answer that *passed* has a judge reason naming the reference.

    The base rate of the defect flag's first signal. Without it a reader takes the
    flag for a defect rate; with it the flag can be read for what it is worth,
    which on `answer-judge/v2` -- a prompt that shows the judge the reference and
    tells it to grade against it -- is close to nothing.
    """

    @property
    def variant(self) -> str:
        return str(self.config.get("variant", "sec1024"))

    @property
    def strategies(self) -> tuple[str, ...]:
        return tuple(self.answers_by_strategy)


def analyse_run(
    run_dir: Path,
    *,
    corpus_dir: Path,
    labels_path: Path | None,
) -> AnalysedRun | SkippedRun:
    """Classify every failed answer of one run directory."""
    config = json.loads((run_dir / "config.json").read_text())
    kind = str(config.get("kind", "generate"))
    if kind != ANSWER_EVAL_KIND:
        return SkippedRun(
            run_dir=str(run_dir),
            kind=kind,
            reason=(
                f"a `{kind}` run holds no answers to classify; it is the run that "
                "produced a dataset, not one that answered its questions"
            ),
        )
    records = read_records(run_dir / "records.jsonl")
    variant = str(config.get("variant", "sec1024"))
    index = chunk_index(corpus_dir, VARIANTS[variant].chunking)
    reranked = rerank_candidates(run_dir)
    human = _human_labels(labels_path, run_dir, config)

    failures: list[FailureRecord] = []
    resolved = recorded = 0
    passed_judged = passed_naming = 0
    for record in records:
        ids = retrieved_chunk_ids(record.trace)
        recorded += len(ids)
        resolved += index.resolves(ids)
        classified = classify(
            record,
            index=index,
            run_name=run_dir.name,
            run_dir=run_dir,
            reranked=reranked,
            human=human.get((record.question_id, record.strategy)),
        )
        if classified is not None:
            failures.append(classified)
            continue
        verdict = record.judge.verdict if record.judge else None
        if verdict is not None:
            passed_judged += 1
            passed_naming += bool(_REFERENCE_MENTION.search(verdict.correctness_reason))
    return AnalysedRun(
        path=run_dir,
        name=run_dir.name,
        config=config,
        answers=len(records),
        judged=sum(verdict_of(record) is not None for record in records),
        errors=sum(record.error is not None for record in records),
        failures=tuple(failures),
        resolved_chunks=resolved,
        recorded_chunks=recorded,
        answers_by_strategy=Counter(record.strategy for record in records),
        answers_by_question_type=Counter(record.question_type for record in records),
        reference_answers={record.key: record.reference_answer for record in records},
        passed_judged=passed_judged,
        passed_naming_the_reference=passed_naming,
    )


def _human_labels(
    labels_path: Path | None, run_dir: Path, config: Mapping[str, Any]
) -> dict[tuple[str, str], CorrectnessLabel]:
    """The hand labels that belong to this run, if any were exported for it."""
    if labels_path is None or not labels_path.exists():
        return {}
    names = [str(run_dir), run_dir.name, str(config.get("name") or "")]
    return labels_for_run(read_human_labels(labels_path), [name for name in names if name])


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #


def _class_counts(failures: Sequence[FailureRecord]) -> dict[str, int]:
    counts = Counter(failure.failure_class.value for failure in failures)
    return {
        failure_class.value: counts.get(failure_class.value, 0) for failure_class in CLASS_ORDER
    }


def _shares(counts: Mapping[str, int], total: int) -> dict[str, float]:
    return {name: round(count / total, 4) if total else 0.0 for name, count in counts.items()}


def _sub_label_counts(failures: Sequence[FailureRecord]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for failure_class in CLASS_ORDER:
        counts = Counter(
            failure.sub_label.value
            for failure in failures
            if failure.failure_class is failure_class
        )
        out[failure_class.value] = {
            sub.value: counts.get(sub.value, 0) for sub in SUB_LABELS[failure_class]
        }
    return out


def _breakdown(failures: Sequence[FailureRecord], answers: int) -> dict[str, Any]:
    counts = _class_counts(failures)
    return {
        "answers": answers,
        "failures": len(failures),
        "failure_share": round(len(failures) / answers, 4) if answers else 0.0,
        "by_class": counts,
        "by_class_share": _shares(counts, answers),
        "sub_labels": _sub_label_counts(failures),
        "reference_defect_flagged": sum(failure.reference_defect_suspected for failure in failures),
        "defect_signals": {
            signal.value: sum(signal in failure.defect_signals for failure in failures)
            for signal in DefectSignal
        },
    }


def _grouped(
    failures: Sequence[FailureRecord], answers: Mapping[str, int], key: str
) -> dict[str, dict[str, Any]]:
    """Failures broken down by one field of the row, over that group's answer count."""
    groups = sorted({str(getattr(failure, key)) for failure in failures} | set(answers))
    return {
        group: _breakdown(
            [failure for failure in failures if str(getattr(failure, key)) == group],
            answers.get(group, 0),
        )
        for group in groups
    }


def aggregate(
    runs: Sequence[AnalysedRun],
    skipped: Sequence[SkippedRun],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Every number the README and the figure are built from."""
    by_run: dict[str, Any] = {}
    for run in runs:
        by_run[run.name] = {
            "run_dir": str(run.path),
            "dataset": run.config.get("dataset"),
            "model": run.config.get("model"),
            "variant": run.variant,
            "rerank": run.config.get("rerank"),
            "strategies": list(run.strategies),
            "judged": run.judged,
            "unjudged": run.answers - run.judged,
            "errors": run.errors,
            "chunk_ids_recorded": run.recorded_chunks,
            "chunk_ids_resolved": run.resolved_chunks,
            "passed_judged": run.passed_judged,
            "passed_naming_the_reference": run.passed_naming_the_reference,
            **_breakdown(run.failures, run.answers),
            "by_strategy": _grouped(run.failures, run.answers_by_strategy, "strategy"),
            "by_question_type": _grouped(
                run.failures, run.answers_by_question_type, "question_type"
            ),
        }

    every = [failure for run in runs for failure in run.failures]
    answers = sum(run.answers for run in runs)
    return {
        "kind": FAILURES_KIND,
        "generated_at": datetime.now(UTC).isoformat(),
        "corpus": str(config.get("corpus")),
        "runs": [run.name for run in runs],
        "skipped_runs": [row.model_dump(mode="json") for row in skipped],
        "chunk_index": {
            variant: len(chunk_index(Path(str(config["corpus"])), VARIANTS[variant].chunking).facts)
            for variant in sorted({run.variant for run in runs})
        },
        "judge_model": config.get("judge_model"),
        "totals": {
            **_breakdown(every, answers),
            "runs": len(runs),
            "chunk_ids_recorded": sum(run.recorded_chunks for run in runs),
            "chunk_ids_resolved": sum(run.resolved_chunks for run in runs),
            "passed_judged": sum(run.passed_judged for run in runs),
            "passed_naming_the_reference": sum(run.passed_naming_the_reference for run in runs),
            "defect_judgements": sum(failure.defect_judgement is not None for failure in every),
        },
        "by_run": by_run,
    }


# --------------------------------------------------------------------------- #
# The reference-defect judge (optional, one call per flagged failure)
# --------------------------------------------------------------------------- #

DEFECT_VERSION = "reference-defect/v1"

DEFECT_SYSTEM = """You check evaluation data, not answers.

You are given a question, the reference answer a dataset stores for it, and the verbatim text of the documentation section the dataset names as the source of that reference answer. Decide one thing only: is the reference answer supported by that section text?

"yes" means every fact the reference answer states is in the section text. "partly" means some of it is and some of it is not. "no" means the section text does not support the reference answer at all, or contradicts it.

Judge against the section text alone, never against what you happen to know about Mistral. Do not grade the question's quality and do not answer the question yourself. Your reason is one sentence."""

DEFECT_USER = """QUESTION
{question}

REFERENCE ANSWER STORED BY THE DATASET
{reference_answer}

GOLD SECTION TEXT, VERBATIM
{section_text}"""

DEFECT_PROMPT_HASHES = {
    name: hashlib.sha256(prompt.encode()).hexdigest()[:16]
    for name, prompt in {"system": DEFECT_SYSTEM, "user": DEFECT_USER}.items()
}

DEFECT_MAX_TOKENS = 500
DEFECT_ATTEMPTS = 3
DEFECT_SECTION_CHARS = 12000
"""How much gold section text one judgement carries. A whole unanchored page can
run past a judge's context, and the reference answers this checks are two lines."""


def parse_judge_model(value: str) -> tuple[ProviderName, str]:
    """`provider:model` from the command line, with the same providers as the answer judge."""
    provider, separator, model = value.partition(":")
    if separator != ":" or provider not in ("zai", "mistral", "local") or not model.strip():
        raise ValueError(
            f"invalid judge model {value!r}; expected provider:model with provider "
            "zai, mistral or local"
        )
    return provider, model.strip()  # type: ignore[return-value]


def defect_input(failure: FailureRecord, reference_answer: str, section_text: str) -> str:
    return DEFECT_USER.format(
        question=failure.question,
        reference_answer=reference_answer,
        section_text=section_text[:DEFECT_SECTION_CHARS] or "(no gold section text was found)",
    )


async def judge_defect(
    failure: FailureRecord,
    *,
    reference_answer: str,
    section_text: str,
    provider: OpenAICompatibleProvider,
    model: str,
) -> DefectJudgement:
    """Ask one judge whether the dataset's reference answer is in the gold section."""
    rendered = defect_input(failure, reference_answer, section_text)
    started = time.perf_counter()
    scope = f"{failure.question_id}:{failure.strategy}"
    with candidate_scope(scope), call_scope("reference_defect"):
        for attempt in range(DEFECT_ATTEMPTS):
            try:
                completion = await provider.complete(
                    [
                        {"role": "system", "content": DEFECT_SYSTEM},
                        {"role": "user", "content": rendered},
                    ],
                    model=model,
                    temperature=0.0,
                    max_tokens=DEFECT_MAX_TOKENS,
                    response_schema=DefectVerdict,
                    thinking="disabled" if provider.name == "zai" else None,
                )
                break
            except ProviderCallError as error:
                if attempt == DEFECT_ATTEMPTS - 1 or "HTTP 429" not in str(error):
                    return DefectJudgement(
                        model=model,
                        provider=provider.name,
                        prompt_version=DEFECT_VERSION,
                        input_text=rendered,
                        error=str(error),
                        latency_ms=(time.perf_counter() - started) * 1000,
                    )
                await asyncio.sleep((5.0 if provider.name == "zai" else 20.0) * (attempt + 1))
    verdict = completion.parsed if isinstance(completion.parsed, DefectVerdict) else None
    return DefectJudgement(
        model=model,
        provider=provider.name,
        prompt_version=DEFECT_VERSION,
        input_text=rendered,
        raw_output=completion.text,
        verdict=verdict,
        error=None if verdict else "the judge's output did not validate",
        latency_ms=(time.perf_counter() - started) * 1000,
        usage=completion.usage,
    )


class DefectCallRecorder:
    """The provider's `CallRecorder`, writing into this run's `calls.jsonl` (D-023)."""

    def __init__(self, calls_path: Path) -> None:
        self.calls_path = calls_path

    def record_call(self, **row: Any) -> None:
        payload: dict[str, Any] = {"source": "judge", "timestamp": datetime.now(UTC).isoformat()}
        for key, value in row.items():
            if isinstance(value, BaseModel):
                payload[key] = value.model_dump(mode="json")
            elif key == "messages":
                payload[key] = [dict(message) for message in value]
            else:
                payload[key] = value
        with self.calls_path.open("a") as handle:
            handle.write(json.dumps(payload, sort_keys=True, default=str) + "\n")


async def judge_flagged(
    runs: Sequence[AnalysedRun],
    *,
    judge: tuple[ProviderName, str],
    calls_path: Path,
    corpus_dir: Path,
) -> list[AnalysedRun]:
    """Ask the judge about every flagged failure, one call each, all recorded."""
    provider_name, model = judge
    provider = OpenAICompatibleProvider(
        provider_name,
        asyncio.Semaphore({"zai": 4, "local": 2}.get(provider_name, 1)),
        caller_tag="eval.failures",
        recorder=DefectCallRecorder(calls_path),
        seed=0,
        minimum_interval=1.05 if provider_name == "mistral" else 0.0,
    )
    judged: list[AnalysedRun] = []
    try:
        for run in runs:
            chunking = VARIANTS[run.variant].chunking
            rows: list[FailureRecord] = []
            for failure in run.failures:
                if not failure.reference_defect_suspected or not failure.gold_urls:
                    rows.append(failure)
                    continue
                anchor = failure.gold_anchors[0] if failure.gold_anchors else None
                judgement = await judge_defect(
                    failure,
                    reference_answer=run.reference_answers.get(
                        (failure.question_id, failure.strategy), ""
                    ),
                    section_text=gold_section_text(
                        corpus_dir, chunking, page_url(failure.gold_urls[0]), anchor
                    ),
                    provider=provider,
                    model=model,
                )
                rows.append(failure.model_copy(update={"defect_judgement": judgement}))
            judged.append(replace(run, failures=tuple(rows)))
    finally:
        await provider.aclose()
    return judged


# --------------------------------------------------------------------------- #
# The run directory
# --------------------------------------------------------------------------- #


def resolve_run_directory(name: str, *, root: Path = RUNS_ROOT) -> Path:
    """A fresh directory named for the moment the analysis ran, in UTC."""
    safe_name = RUN_NAME_RE.sub("-", name.casefold()).strip("-")
    if not safe_name:
        raise ValueError("run name must contain a letter or digit")
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d-%H%M")
    candidate = root / f"{timestamp}-{safe_name}"
    suffix = 2
    while candidate.exists():
        candidate = root / f"{timestamp}-{safe_name}-{suffix}"
        suffix += 1
    return candidate


def write_run(
    run_dir: Path,
    runs: Sequence[AnalysedRun],
    skipped: Sequence[SkippedRun],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Write config, records, metrics, README and figures (D-023)."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "figures").mkdir(exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps(dict(config), indent=2, sort_keys=True) + "\n")
    rows = [failure for run in runs for failure in run.failures]
    (run_dir / "records.jsonl").write_text(
        "".join(
            json.dumps(failure.model_dump(mode="json"), sort_keys=True) + "\n" for failure in rows
        )
    )
    metrics = aggregate(runs, skipped, config)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_dir / "README.md").write_text(render_readme(config, metrics, rows))
    render_figures(metrics, run_dir / "figures")
    return metrics


def ordered_runs(metrics: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    """The runs in the order they were named on the command line.

    `metrics.json` is written with sorted keys, so `by_run` comes back off disk
    alphabetically; reading the order from the `runs` list keeps a regenerated
    README identical to the one the analysis wrote.
    """
    return [(name, metrics["by_run"][name]) for name in metrics["runs"]]


def render_figures(metrics: Mapping[str, Any], figures_dir: Path) -> list[Path]:
    """The one figure the README carries: what each run's failures are made of."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, Sequence[float]]] = [
        (
            name,
            tuple(float(run["by_class"][failure_class.value]) for failure_class in CLASS_ORDER),
        )
        for name, run in ordered_runs(metrics)
    ]
    path = figures_dir / "failure-classes.svg"
    path.write_text(
        stacked_bar_chart(
            "Failures by class, per run",
            rows,
            [CLASS_TITLES[failure_class] for failure_class in CLASS_ORDER],
        )
    )
    return [path]


def regenerate(run_dir: Path) -> dict[str, Any]:
    """Rebuild metrics, README and figures from this run's own records.

    The rows are the record, so the analysis is not re-run: a README regenerated
    a month later says exactly what the rows say, which is the point of D-023.
    """
    config = json.loads((run_dir / "config.json").read_text())
    previous = json.loads((run_dir / "metrics.json").read_text())
    rows = [
        FailureRecord.model_validate_json(line)
        for line in (run_dir / "records.jsonl").read_text().splitlines()
        if line.strip()
    ]
    metrics = dict(previous)
    metrics["by_run"] = _rebuild_by_run(previous, rows)
    metrics["totals"] = {
        **previous["totals"],
        **_breakdown(rows, int(previous["totals"]["answers"])),
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_dir / "README.md").write_text(render_readme(config, metrics, rows))
    render_figures(metrics, run_dir / "figures")
    return metrics


def _rebuild_by_run(previous: Mapping[str, Any], rows: Sequence[FailureRecord]) -> dict[str, Any]:
    """Recount every class from the rows, keeping the per-run facts that are not counts.

    The answer counts are the only thing the rows cannot supply, so they are read
    back out of the stored metrics and everything else is recomputed.
    """
    by_run: dict[str, Any] = {}
    for name, run in previous["by_run"].items():
        failures = [row for row in rows if row.run == name]
        by_run[name] = {
            **run,
            **_breakdown(failures, int(run["answers"])),
            "by_strategy": _grouped(failures, _answers_of(run["by_strategy"]), "strategy"),
            "by_question_type": _grouped(
                failures, _answers_of(run["by_question_type"]), "question_type"
            ),
        }
    return by_run


def _answers_of(groups: Mapping[str, Mapping[str, Any]]) -> dict[str, int]:
    return {name: int(group["answers"]) for name, group in groups.items()}


# --------------------------------------------------------------------------- #
# README
# --------------------------------------------------------------------------- #

RULES = f"""Every answer whose primary judge verdict is `partial` or `wrong`, or whose
refusal went the wrong way (it refused a question the dataset says is answerable,
or answered one the dataset marks unanswerable), is a failure and gets exactly one
class. The tests run in this order, and each one is only reached when the one
before it passed, so a class always means "everything upstream of it worked".

1. **{CLASS_TITLES[FailureClass.RETRIEVAL_MISS]}** -- no chunk of a gold page appears in
   `trace.events[].result_ids` for any round: not the seed retrieval, not any of the
   search loop's tool calls. Chunk ids are resolved to pages through the corpus, not
   through the run: a chunk id is `uuid5(NAMESPACE_DNS, "<page url>:char:<start>-<end>")`,
   so re-chunking the vendored corpus with the run's own chunker rebuilds the whole map
   offline. Sub-labels: `{SubLabel.RERANKER_DROP.value}` when a recorded reranker call
   shows the gold page among the candidates it was offered and it did not come back;
   `{SubLabel.SEARCH_MISS.value}` when the gold page was not among those candidates;
   `{SubLabel.CANDIDATES_NOT_RECORDED.value}` when the run has no recorded reranker call
   for that question, which is every run made before reranker calls reached the call
   ledger (D-023b), so search and reranker cannot be told apart there.
2. **{CLASS_TITLES[FailureClass.CONTEXT_MISS]}** -- a gold chunk came back from retrieval
   but no source in `trace.sources` came from a gold page, so the model never saw it.
   Sub-labels: `{SubLabel.DROPPED_FROM_CONTEXT.value}` when the gold chunk is in
   `trace.dropped_chunk_ids`, `{SubLabel.OUTRANKED_IN_ASSEMBLY.value}` otherwise.
3. **{CLASS_TITLES[FailureClass.GENERATION]}** -- a gold chunk was in the assembled
   context, the model answered rather than refusing, and the answer is still partial or
   wrong. Sub-labels say what the citations did with it:
   `{SubLabel.NO_CITATION_TO_GOLD.value}` (the answer cited something else),
   `{SubLabel.UNVERIFIED_QUOTE_FROM_GOLD.value}` (it cited the gold section but the quote
   failed verification), `{SubLabel.VERIFIED_QUOTE_FROM_GOLD.value}` (it quoted the gold
   section verbatim and answered wrong anyway, which is the strongest evidence of a model
   limit rather than a pipeline one).
4. **{CLASS_TITLES[FailureClass.REFUSAL]}** -- reported separately, because D-035b showed
   false refusals dominate under noise. `{SubLabel.FALSE_REFUSAL.value}`: the answer set
   `insufficient_evidence` on an answerable question *with a gold chunk in the context*.
   `{SubLabel.MISSED_REFUSAL.value}`: it answered a question the dataset marks
   unanswerable. A refusal that follows a retrieval or context miss is classed as that
   miss instead, because refusing when the evidence never arrived is the pipeline working,
   and an unanswerable question has no gold to retrieve, so tests 1 to 3 never apply to
   one.
5. **question or reference defect** -- *flagged, not decided*, and not a class: it is a
   column on the rows above and overlaps them. Two deterministic signals raise it, and
   neither is evidence on its own: `{DefectSignal.JUDGE_NAMES_THE_REFERENCE.value}`, the
   judge's one-sentence reason mentions the reference answer; and
   `{DefectSignal.HUMAN_IS_MORE_LENIENT.value}`, a hand label for that answer scores it
   higher than the judge did (D-021b found every primary-judge disagreement went the
   strict way). The first signal is reported with the rate at which answers that *passed*
   carry the same wording, because `answer-judge/v2` shows the judge the reference and
   tells it to grade against it, so naming it is the norm rather than a symptom. Deciding
   whether a reference is actually wrong needs a judge that reads the gold section text,
   which is what `--judge-model provider:model` runs and what this run did not do."""

BLIND_SPOTS = f"""- **A wrong gold link in the dataset looks like a retrieval miss.** The gold URL is
  taken as ground truth. If the dataset points at the wrong page, retrieval can have
  found the page that really answers the question and still be counted as having missed.
  This is the single largest source of error in the retrieval-miss column and the reason
  the defect flag exists.
- **A correct answer from a page that is not gold looks like a failure.** D-033 saw this
  on capability questions, where a model card carries the same fact as the `/models`
  matrix. The one relaxation the answer evaluation already applies is applied here too --
  the card of a model the question names counts as the gold page -- and nothing beyond it.
- **`{SubLabel.CANDIDATES_NOT_RECORDED.value}` hides the reranker.** Where a run has no
  recorded reranker call, a search that never found the page and a reranker that dropped
  it look the same.
- **Judged correctness is a floor.** The primary judge is stricter than a reader (D-021b:
  it never called an answer correct that the reader rejected, and called five partial or
  wrong that the reader accepted), so the failure counts here are an upper bound on what
  a reader would call a failure.
- **One class per answer.** An answer can fail for two reasons at once; it is counted
  under the first one in the order, which is the upstream one.
- **The context test is page-level.** A failure is a generation failure once *any* chunk
  of a gold page reaches the context, even when the exact gold section did not. The
  `gold_section_in_context` column on each row says which of the two happened."""


def _class_table(breakdowns: Mapping[str, Mapping[str, Any]], first_column: str) -> str:
    """A table of failure counts by class, with the share of all answers beside each."""
    header = (
        f"| {first_column} | answers | failures | "
        + " | ".join(CLASS_TITLES[failure_class] for failure_class in CLASS_ORDER)
        + " |"
    )
    divider = "|---" * (3 + len(CLASS_ORDER)) + "|"
    lines = [header, divider]
    for name, breakdown in breakdowns.items():
        answers = int(breakdown["answers"])
        cells = [
            f"{breakdown['by_class'][failure_class.value]} "
            f"({breakdown['by_class_share'][failure_class.value]:.0%})"
            for failure_class in CLASS_ORDER
        ]
        share = f"{breakdown['failure_share']:.0%}" if answers else "n/a"
        lines.append(
            f"| {name} | {answers} | {breakdown['failures']} ({share}) | "
            + " | ".join(cells)
            + " |"
        )
    return "\n".join(lines)


def _sub_label_table(breakdown: Mapping[str, Any]) -> str:
    lines = ["| class | sub-label | failures |", "|---|---|---|"]
    for failure_class in CLASS_ORDER:
        for sub, count in breakdown["sub_labels"][failure_class.value].items():
            if count:
                lines.append(f"| {CLASS_TITLES[failure_class]} | `{sub}` | {count} |")
    if len(lines) == 2:
        lines.append("| (none) | | 0 |")
    return "\n".join(lines)


def _examples(rows: Sequence[FailureRecord], run_name: str) -> str:
    """Up to three worked examples per class, one paragraph each."""
    blocks: list[str] = []
    for failure_class in CLASS_ORDER:
        chosen = _pick_examples(
            [row for row in rows if row.run == run_name and row.failure_class is failure_class]
        )
        if not chosen:
            blocks.append(f"**{CLASS_TITLES[failure_class]}** -- none in this run.")
            continue
        lines = [f"**{CLASS_TITLES[failure_class]}**", ""]
        for row in chosen:
            lines.append(
                f"- `{row.question_id}` ({row.question_type}, {row.strategy}, judged "
                f"{row.verdict or 'not judged'}, `{row.sub_label.value}`) --- "
                f'"{_shorten(row.question, 160)}"'
            )
            lines.append(f"  - what happened: {row.evidence}")
            if row.judge_reason:
                lines.append(f"  - the judge: {row.judge_reason}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _pick_examples(rows: Sequence[FailureRecord]) -> list[FailureRecord]:
    """One example of each sub-label first, then the rest, deterministically.

    Showing three failures that all say the same thing wastes the section; a
    reader wants the range the class covers.
    """
    ordered = sorted(rows, key=lambda row: (row.sub_label.value, row.question_id, row.strategy))
    chosen: list[FailureRecord] = []
    seen: set[str] = set()
    for row in ordered:
        if row.sub_label.value not in seen:
            chosen.append(row)
            seen.add(row.sub_label.value)
    for row in ordered:
        if len(chosen) >= EXAMPLES_PER_CLASS:
            break
        if row not in chosen:
            chosen.append(row)
    return chosen[:EXAMPLES_PER_CLASS]


def _run_section(name: str, run: Mapping[str, Any], rows: Sequence[FailureRecord]) -> str:
    resolved = run["chunk_ids_resolved"]
    recorded = run["chunk_ids_recorded"]
    coverage = (
        f"{resolved} of {recorded} recorded chunk ids resolved to a page through the corpus"
        if recorded
        else "the run recorded no chunk ids"
    )
    return f"""### `{name}`

Dataset `{run["dataset"]}`, generator `{run["model"]}`, index `{run["variant"]}`,
reranker {run["rerank"]}. {run["judged"]} of {run["answers"]} answers carry a primary
verdict ({run["unjudged"]} do not), {run["errors"]} ended in an error. {coverage}.

**By strategy**

{_class_table(run["by_strategy"], "strategy")}

**By question type**

{_class_table(run["by_question_type"], "question type")}

**Sub-labels**

{_sub_label_table(run)}

{_defect_line(run)}

**Examples**

{_examples(rows, name)}"""


def _defect_line(breakdown: Mapping[str, Any]) -> str:
    """The defect flag with the base rate that says what it is worth.

    The first signal fires on a judge reason that names the reference, and the
    judge prompt asks the judge to grade against the reference, so the same words
    appear in the reasons of answers that passed. Printing the flag without that
    comparison would read as a defect rate.
    """
    signals = breakdown["defect_signals"]
    passed = int(breakdown.get("passed_judged", 0))
    naming = int(breakdown.get("passed_naming_the_reference", 0))
    base = (
        f" For comparison, {naming} of the {passed} answers that passed carry the same "
        f"`{DefectSignal.JUDGE_NAMES_THE_REFERENCE.value}` wording "
        f"({naming / passed:.0%}), so that signal on its own separates nothing; "
        f"`{DefectSignal.HUMAN_IS_MORE_LENIENT.value}` is the discriminating one."
        if passed
        else ""
    )
    return (
        f"{breakdown['reference_defect_flagged']} of {breakdown['failures']} failures carry "
        f"the reference-defect flag: "
        + ", ".join(f"`{name}` {count}" for name, count in signals.items())
        + f" (a row can carry both).{base}"
    )


def render_readme(
    config: Mapping[str, Any], metrics: Mapping[str, Any], rows: Sequence[FailureRecord]
) -> str:
    """The run README (D-023). Every number in it comes from `records.jsonl`."""
    totals = metrics["totals"]
    skipped = metrics["skipped_runs"]
    skipped_lines = (
        "\n".join(f"- `{row['run_dir']}`: {row['reason']}" for row in skipped)
        if skipped
        else "- None: every directory named on the command line held answers."
    )
    judge_line = (
        f"The reference-defect judge ran on `{metrics['judge_model']}` and produced "
        f"{totals['defect_judgements']} judgement(s), one per flagged failure, all in `calls.jsonl`."
        if metrics.get("judge_model")
        else (
            "The reference-defect judge did not run: no `--judge-model` was given, so "
            "every reference-defect entry below is a flag raised by a deterministic "
            "signal and nothing more. Running it is one call per flagged failure and "
            "decides those flags."
        )
    )
    index_line = ", ".join(
        f"`{variant}` {count} chunks" for variant, count in metrics["chunk_index"].items()
    )
    run_sections = "\n\n".join(_run_section(name, run, rows) for name, run in ordered_runs(metrics))
    return f"""# Failure analysis: which part of the pipeline was wrong

**What this measures.** Not how often the pipeline fails --- the answer evaluations
already say that --- but *which part* failed each time. Every answer these runs
recorded that the judge scored `partial` or `wrong`, or that refused in the wrong
direction, is assigned one class: the retrieval never found the page, the context
never carried it, the model had it and still answered wrong, or the refusal went the
wrong way. A wrong answer with the right passage in front of the model and a wrong
answer whose page was never retrieved call for opposite work, and the generator here
is a small model (Ministral 3 14B, D-017a), which makes the split worth having before
anything is blamed on it.

No model was called to produce this run's classes. Every class is decided from the
records the answer evaluations already wrote, so it can be recomputed from
`records.jsonl` at any time.

## Configuration

- Runs analysed: {len(metrics["runs"])} --- {", ".join(f"`{name}`" for name in metrics["runs"])}
- Corpus: `{metrics["corpus"]}`; chunk map rebuilt offline: {index_line}
- Human labels: `{config.get("labels") or "none"}`
- Reference-defect judge: `{metrics.get("judge_model") or "not run"}` ({DEFECT_VERSION}, \
hashes {json.dumps(DEFECT_PROMPT_HASHES, sort_keys=True)})

Directories named but not analysed:

{skipped_lines}

## How each class is decided

{RULES}

## Known blind spots

{BLIND_SPOTS}

## Results

Across {len(metrics["runs"])} runs, {totals["failures"]} of {totals["answers"]} answers
failed ({totals["failure_share"]:.0%}). {totals["chunk_ids_resolved"]} of
{totals["chunk_ids_recorded"]} recorded chunk ids resolved to a page through the corpus;
an unresolved id is a chunk the current corpus no longer produces, and is counted on the
row it came from as `unresolved_chunks`.

{_class_table(dict(ordered_runs(metrics)), "run")}

{_defect_line(totals)} {judge_line}

{run_sections}

## Figures

`figures/` is regenerated from `metrics.json` by `make eval-report run={config.get("run_dir")}`.

- `failure-classes.svg`: what each run's failures are made of, one stacked bar per run

## Files

- `config.json` --- the runs analysed, the corpus, the labels, and the judge setting.
- `records.jsonl` --- one row per failed answer: its class, its sub-label, the evidence
  that decided the class, and every intermediate fact the decision used
  (`gold_retrieved`, `gold_in_context`, `gold_section_in_context`, `gold_chunk_dropped`,
  the retrieved pages, the defect signals). Every number in this README is a count over
  these rows.
- `metrics.json` --- every number in the tables above.

## What it feeds

D-016 (which checks the answer evaluation reports), D-034 and D-035 (whether the next
effort belongs in retrieval or in the answer layer) and D-021b (the reference-defect rate
the judge study reports beside its own numbers).
"""


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify the failed answers of one or more answer-evaluation runs"
    )
    parser.add_argument(
        "--run",
        action="append",
        default=[],
        dest="runs",
        type=Path,
        required=True,
        help="An answer-evaluation run directory to read; repeatable",
    )
    parser.add_argument("--name", required=True, help="Run name for the output directory")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument(
        "--labels",
        type=Path,
        default=DEFAULT_LABELS,
        help="Human correctness labels as JSONL; missing files are ignored",
    )
    parser.add_argument(
        "--judge-model",
        help=(
            "Ask this provider:model whether each flagged reference answer is "
            "supported by its gold section text; off by default, one call per flag"
        ),
    )
    parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    return parser.parse_args(argv)


async def _run(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    analysed: list[AnalysedRun] = []
    skipped: list[SkippedRun] = []
    for run_dir in args.runs:
        result = analyse_run(run_dir, corpus_dir=args.corpus, labels_path=args.labels)
        if isinstance(result, SkippedRun):
            logger.warning("Skipping a directory", run=str(run_dir), reason=result.reason)
            skipped.append(result)
        else:
            analysed.append(result)
    if not analysed:
        raise SystemExit("no answer-evaluation run was given")

    run_dir = resolve_run_directory(args.name, root=args.runs_root)
    run_dir.mkdir(parents=True, exist_ok=False)
    judge = parse_judge_model(args.judge_model) if args.judge_model else None
    if judge is not None:
        load_dotenv()
        analysed = await judge_flagged(
            analysed,
            judge=judge,
            calls_path=run_dir / "calls.jsonl",
            corpus_dir=args.corpus,
        )
    config = {
        "kind": FAILURES_KIND,
        "runs": [str(path) for path in args.runs],
        "corpus": str(args.corpus),
        "labels": str(args.labels) if args.labels and args.labels.exists() else None,
        "judge_model": f"{judge[0]}:{judge[1]}" if judge else None,
        "name": args.name,
        "run_dir": str(run_dir),
    }
    return run_dir, write_run(run_dir, analysed, skipped, config)


def main() -> None:
    args = _parse_args()
    run_dir, metrics = asyncio.run(_run(args))
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "runs": metrics["runs"],
                "answers": metrics["totals"]["answers"],
                "failures": metrics["totals"]["failures"],
                "by_class": metrics["totals"]["by_class"],
            }
        )
    )


if __name__ == "__main__":
    main()
