"""Answer evaluation: every question of a dataset, through every strategy.

Two kinds of number come out of a run, and they are kept apart on purpose (D-016).
The deterministic ones -- did a verified citation land on a gold URL, did the
quotes survive the verifier, was the refusal correct, what did it cost and how
long did it take -- carry no model dependency and are the primary report. The
judged ones -- correctness against the reference answer, groundedness of the
answer's claims in the cited text, whether each citation supports the sentence it
is attached to -- come from GLM through `glossator.eval.providers` (D-021) and are
reported beside them, never merged into them.

The judge never learns which strategy produced an answer: it sees the question,
the reference answer, the gold URLs, the answer, and the verified citations with
the cited passage quoted verbatim. That is the whole of its input, and it is
recorded verbatim with its raw output, because a judgement that cannot be re-read
cannot be argued with (D-023).
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import hashlib
import json
import math
import os
import statistics
import time
from collections.abc import Iterator, Mapping, Sequence
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import httpx
import structlog
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

from glossator.answer.citations import (
    VERIFIED_AFTER_EMPHASIS,
    Answer,
    Citation,
    RejectionReason,
    Trace,
)
from glossator.answer.config import MISTRAL_MEDIUM_3_5, PRICES, AnswerConfig, ModelPrice
from glossator.answer.llm import LLMCall, MistralLLM
from glossator.answer.llm import TokenUsage as AnswerTokenUsage
from glossator.answer.service import STRATEGIES, ask, build_client
from glossator.eval.charts import bar_chart, scatter
from glossator.eval.datasets import (
    EvalQuestion,
    QuestionType,
    dataset_hash,
    read_jsonl,
    stratified_subset,
)
from glossator.eval.providers import (
    OpenAICompatibleProvider,
    ProviderCallError,
    TokenUsage,
    call_scope,
    candidate_scope,
)
from glossator.eval.run_records import RUN_NAME_RE
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import SearchEngine

logger = structlog.get_logger(__name__)

RUNS_ROOT = Path("eval/runs")

DEFAULT_GENERATION_MODEL = "ministral-14b-2512"
"""The largest Mistral model this key can reach (D-017a): every `mistral-medium-*`,
`mistral-small-*` and `magistral-*` id answers HTTP 429 with a configured limit of
zero requests per minute, which no backoff can get through."""

DEFAULT_JUDGE_MODEL = "glm-5.3"

REFERENCE_PRICING_MODEL = MISTRAL_MEDIUM_3_5
"""Prices the recorded tokens a second time, at the shipped model's rates (D-017),
so the day the account is provisioned the budget question is already answered."""

UNPRICED_MODELS = frozenset({DEFAULT_GENERATION_MODEL})
"""Models with no published price on 2026-09-09. Their tokens are recorded and
their USD is reported as zero, which is a statement about the price list rather
than about the work; the reference column prices the same tokens at D-017 rates."""

EVAL_PRICES: dict[str, ModelPrice] = {
    **PRICES,
    DEFAULT_GENERATION_MODEL: ModelPrice(input_usd_per_mtok=0.0, output_usd_per_mtok=0.0),
}

ZAI_QUOTA_URL = "https://api.z.ai/api/monitor/usage/quota/limit"
QUOTA_CEILING_PERCENT = 80
"""D-028: pause before a batch when the five-hour token window is this full."""

QUESTION_TYPES: tuple[str, ...] = tuple(question_type.value for question_type in QuestionType)


# --------------------------------------------------------------------------- #
# Judge prompts. Versioned constants: a verdict is only comparable to another
# verdict written by the same words, so the version and the hashes are recorded
# with every run and a rewording is a new version, not an edit.
# --------------------------------------------------------------------------- #

JUDGE_VERSION = "answer-judge/v1"

JUDGE_SYSTEM = """You grade answers produced by a documentation question-answering system over Mistral AI's platform documentation.

You are given the question, a short reference answer written by the dataset, the gold source URLs, the answer under test, and the citations the answer carries. Each citation shows the passage it points at, quoted verbatim from the documentation the system read. You have no other access to the documentation: if a claim is not supported by a passage shown to you, it is not supported.

Grade three things, independently.

1. correctness: does the answer under test agree with the reference answer on the substance the question asks about? "correct" means a developer following it would be right; "partial" means it is right as far as it goes but leaves out something the reference answer states; "wrong" means it contradicts the reference answer, answers a different question, or invents a fact. Extra correct detail is not a penalty. Different wording is not a penalty. For a question the documentation cannot answer, the reference answer says so, and only an answer that declines to answer is correct.

2. groundedness: count the factual claims the answer makes -- statements about the product that could be checked, not pleasantries, headings, or restatements of the question -- and count how many of them are supported by the passages shown with the citations. Judge support against those passages alone, never against what you happen to know about Mistral.

3. citation relevance: for each citation, does the passage it points at support the sentence it is attached to in the answer? A citation that supports some other sentence, or nothing in the answer, is not relevant.

Be strict and be brief. Every reason is one sentence."""

JUDGE_USER = """QUESTION
{question}

REFERENCE ANSWER
{reference_answer}

GOLD SOURCES
{gold_urls}

ANSWER UNDER TEST
{answer_markdown}

CITATIONS IN THE ANSWER UNDER TEST
{citations}"""

JUDGE_NO_CITATIONS = "(the answer carries no verified citation)"

JUDGE_CITATION = """[{n}] {citation_url}
quoted by the answer: "{quote}"
passage the citation points at, verbatim:
{source_text}"""

JUDGE_PROMPT_HASHES = {
    name: hashlib.sha256(prompt.encode()).hexdigest()[:16]
    for name, prompt in {
        "judge_system": JUDGE_SYSTEM,
        "judge_user": JUDGE_USER,
        "judge_citation": JUDGE_CITATION,
    }.items()
}

JUDGE_TEMPERATURE = 0.0
JUDGE_MAX_TOKENS = 1200


class CitationVerdict(BaseModel):
    """Whether one citation supports the sentence it is attached to."""

    model_config = ConfigDict(frozen=True)

    n: int
    supports: bool
    reason: str = ""


class JudgeVerdict(BaseModel):
    """The judge's structured output (D-021)."""

    model_config = ConfigDict(frozen=True)

    correctness: Literal["correct", "partial", "wrong"]
    correctness_reason: str
    claims_total: int = 0
    claims_supported: int = 0
    groundedness_reason: str = ""
    citations: list[CitationVerdict] = Field(default_factory=list)

    @property
    def groundedness(self) -> float | None:
        """Supported claims over claims. None when the answer makes no claim,
        which is a different thing from making unsupported ones."""
        if self.claims_total <= 0:
            return None
        return min(self.claims_supported, self.claims_total) / self.claims_total

    @property
    def citation_relevance(self) -> float | None:
        if not self.citations:
            return None
        return sum(verdict.supports for verdict in self.citations) / len(self.citations)


CORRECTNESS_SCORE = {"correct": 1.0, "partial": 0.5, "wrong": 0.0}


class JudgedCitation(BaseModel):
    """One citation as the judge sees it: the quote and the passage behind it."""

    model_config = ConfigDict(frozen=True)

    n: int
    citation_url: str
    quote: str
    source_text: str


class JudgeInput(BaseModel):
    """Everything the judge is shown. It names no strategy and no model."""

    model_config = ConfigDict(frozen=True)

    question: str
    reference_answer: str
    gold_urls: list[str]
    answer_markdown: str
    citations: list[JudgedCitation]

    def render(self) -> str:
        citations = "\n\n".join(
            JUDGE_CITATION.format(
                n=citation.n,
                citation_url=citation.citation_url,
                quote=citation.quote,
                source_text=citation.source_text,
            )
            for citation in self.citations
        )
        return JUDGE_USER.format(
            question=self.question,
            reference_answer=self.reference_answer,
            gold_urls="\n".join(self.gold_urls) or "(none: the documentation does not cover this)",
            answer_markdown=self.answer_markdown or "(the system produced no text)",
            citations=citations or JUDGE_NO_CITATIONS,
        )


class JudgeRecord(BaseModel):
    """One judgement, complete enough to re-read without the model."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    model: str
    prompt_version: str
    input_text: str
    raw_output: str = ""
    verdict: JudgeVerdict | None = None
    error: str | None = None
    latency_ms: float = 0.0
    usage: TokenUsage = TokenUsage()


class QuestionRecord(BaseModel):
    """One (question, strategy) pair: the answer, its trace, and its judgement.

    This is the run's checkpoint as well as its evidence. A re-run reads the
    records back, skips the pairs already in them, and pays only for the rest.
    """

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    question_id: str
    question: str
    question_type: str
    language: str
    gold_urls: list[str] = Field(default_factory=list)
    gold_anchors: list[str | None] = Field(default_factory=list)
    reference_answer: str
    strategy: str
    variant: str
    model: str
    answer_markdown: str = ""
    citations: list[Citation] = Field(default_factory=list)
    unverified_citations: list[Citation] = Field(default_factory=list)
    insufficient_evidence: bool = False
    trace: Trace | None = None
    usage: AnswerTokenUsage = AnswerTokenUsage()
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    error: str | None = None
    judge: JudgeRecord | None = None

    @property
    def key(self) -> tuple[str, str]:
        return (self.question_id, self.strategy)


# --------------------------------------------------------------------------- #
# Reading a run's evidence back
# --------------------------------------------------------------------------- #


def source_texts(trace: Trace | None) -> dict[int, str]:
    """The text of each numbered source, cut out of the context the model saw.

    `Trace.context_text` is the assembled context verbatim, and every source in
    it opens with the line `[n] <citation url>`. Locating those lines in order
    recovers each source's passage without re-running retrieval, which is what
    lets the judge be shown the cited text rather than asked to trust a quote.

    The heading path line stays on the passage: it is what the model saw, and it
    is what tells a judge reading a chunk from the middle of a page what section
    the chunk is from.
    """
    if trace is None or not trace.context_text:
        return {}
    text = trace.context_text
    marks: list[tuple[int, int, int]] = []
    cursor = 0
    for source in trace.sources:
        marker = f"[{source.n}] {source.citation_url}\n"
        start = text.find(marker, cursor)
        if start < 0:
            continue
        marks.append((source.n, start, start + len(marker)))
        cursor = start + len(marker)
    passages: dict[int, str] = {}
    for index, (n, _start, body) in enumerate(marks):
        end = marks[index + 1][1] if index + 1 < len(marks) else len(text)
        passages[n] = text[body:end].strip()
    return passages


def judge_input(question: EvalQuestion, record: QuestionRecord) -> JudgeInput:
    """What the judge is shown for one answer."""
    passages = source_texts(record.trace)
    return JudgeInput(
        question=question.question,
        reference_answer=question.reference_answer,
        gold_urls=[gold.url for gold in question.gold],
        answer_markdown=record.answer_markdown,
        citations=[
            JudgedCitation(
                n=citation.n,
                citation_url=citation.citation_url,
                quote=citation.quote,
                source_text=passages.get(citation.n, "(the passage was not recorded)"),
            )
            for citation in record.citations
        ],
    )


# --------------------------------------------------------------------------- #
# Deterministic metrics
# --------------------------------------------------------------------------- #


def gold_url_match(record: QuestionRecord) -> bool:
    """A verified citation names one of the gold pages."""
    gold = set(record.gold_urls)
    return any(citation.url in gold for citation in record.citations)


def gold_anchor_match(record: QuestionRecord) -> bool:
    """A verified citation names a gold page *and* lands on the gold section.

    A gold source with no anchor is matched by any citation to that page: the
    dataset is saying the page is the answer, and 53% of the corpus's sections
    have no anchor to be more precise about (D-003a).
    """
    pairs = list(zip(record.gold_urls, record.gold_anchors, strict=True))
    return any(
        citation.url == url and (anchor is None or citation.anchor == anchor)
        for citation in record.citations
        for url, anchor in pairs
    )


def tool_calls(record: QuestionRecord) -> int:
    if record.trace is None:
        return 0
    return sum(event.kind == "tool" for event in record.trace.events)


def rounds(record: QuestionRecord) -> int:
    return record.trace.rounds if record.trace is not None else 0


def rejection_counts(record: QuestionRecord) -> tuple[int, int]:
    """Rejected citations split into fabricated and cosmetic.

    A model that invented a sentence and a model that dropped a pair of asterisks
    are different failures (D-027a); averaging them into one rate hides both. A
    citation naming a source number that does not exist counts as fabricated: the
    quote was never checkable against anything.
    """
    fabricated = 0
    cosmetic = 0
    for citation in record.unverified_citations:
        if citation.reason in RejectionReason.COSMETIC:
            cosmetic += 1
        else:
            fabricated += 1
    return fabricated, cosmetic


def question_metrics(record: QuestionRecord) -> dict[str, float | None]:
    """Every per-question number, or None where the question does not have one."""
    answerable = record.question_type != QuestionType.UNANSWERABLE.value
    emitted = len(record.citations) + len(record.unverified_citations)
    fabricated, cosmetic = rejection_counts(record)
    normalized = sum(citation.reason == VERIFIED_AFTER_EMPHASIS for citation in record.citations)
    verdict = record.judge.verdict if record.judge else None
    return {
        "cited_url_match": float(gold_url_match(record)) if answerable else None,
        "cited_anchor_match": float(gold_anchor_match(record)) if answerable else None,
        "citations_emitted": float(emitted),
        "citations_verified": float(len(record.citations)),
        "citations_fabricated": float(fabricated),
        "citations_cosmetic": float(cosmetic),
        "citations_normalized": float(normalized),
        "distinct_sources_cited": float(len({citation.n for citation in record.citations})),
        "unmatched_markers_per_answer": float(
            len(record.trace.unmatched_markers) if record.trace else 0
        ),
        "unverified_citations_per_answer": float(len(record.unverified_citations)),
        "refusal_correct": float(record.insufficient_evidence == (not answerable)),
        "insufficient_evidence": float(record.insufficient_evidence),
        "latency_ms": record.latency_ms,
        "tokens_in": float(record.usage.prompt_tokens),
        "tokens_out": float(record.usage.completion_tokens),
        "usd": record.cost_usd,
        "reference_usd": reference_cost_usd(record.usage),
        "tool_calls": float(tool_calls(record)),
        "rounds": float(rounds(record)),
        "errors": float(record.error is not None),
        "correctness": CORRECTNESS_SCORE[verdict.correctness] if verdict else None,
        "correct": float(verdict.correctness == "correct") if verdict else None,
        "partial": float(verdict.correctness == "partial") if verdict else None,
        "wrong": float(verdict.correctness == "wrong") if verdict else None,
        "groundedness": verdict.groundedness if verdict else None,
        "citation_relevance": verdict.citation_relevance if verdict else None,
    }


def reference_cost_usd(usage: AnswerTokenUsage) -> float:
    """What the same tokens would cost on the shipped model (D-017, D-017a)."""
    price = PRICES[REFERENCE_PRICING_MODEL]
    return (
        usage.prompt_tokens * price.input_usd_per_mtok
        + usage.completion_tokens * price.output_usd_per_mtok
    ) / 1_000_000


# Metrics whose cell value is a mean of the per-question values, and the number of
# decimals the tables print them with.
MEAN_METRICS: dict[str, int] = {
    "cited_url_match": 2,
    "cited_anchor_match": 2,
    "distinct_sources_cited": 2,
    "unmatched_markers_per_answer": 2,
    "unverified_citations_per_answer": 2,
    "refusal_correct": 2,
    "correctness": 2,
    "correct": 2,
    "partial": 2,
    "wrong": 2,
    "groundedness": 2,
    "citation_relevance": 2,
    "tokens_in": 0,
    "tokens_out": 0,
    "usd": 5,
    "reference_usd": 4,
    "tool_calls": 2,
    "rounds": 2,
}


def _mean(values: Sequence[float]) -> float | None:
    return statistics.fmean(values) if values else None


def _percentile(values: Sequence[float], fraction: float) -> float | None:
    """Nearest-rank percentile: the smallest value at or above the fraction.

    Not interpolated. A dozen questions per cell is too few for an interpolated
    percentile to mean anything more than the value it sits between, and a
    reported p95 that no answer actually took is worse than a blunt one.
    """
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def cell(records: Sequence[QuestionRecord]) -> dict[str, Any]:
    """Every aggregate number for one group of records."""
    per_question = [question_metrics(record) for record in records]

    def column(name: str) -> list[float]:
        return [row[name] for row in per_question if row[name] is not None]  # type: ignore[misc]

    emitted = sum(column("citations_emitted"))
    verified = sum(column("citations_verified"))
    latencies = column("latency_ms")
    aggregate: dict[str, Any] = {
        "questions": len(records),
        "errors": int(sum(column("errors"))),
        "citations_emitted": int(emitted),
        "citations_verified": int(verified),
        "citation_verification_rate": (verified / emitted) if emitted else None,
        "fabricated_per_answer": _mean(column("citations_fabricated")),
        "cosmetic_per_answer": _mean(column("citations_cosmetic")),
        "verified_after_normalization": int(sum(column("citations_normalized"))),
        "latency_p50_s": (None if not latencies else (_percentile(latencies, 0.5) or 0.0) / 1000),
        "latency_p95_s": (None if not latencies else (_percentile(latencies, 0.95) or 0.0) / 1000),
        "judged": sum(1 for row in per_question if row["correctness"] is not None),
    }
    for name in MEAN_METRICS:
        aggregate[name] = _mean(column(name))
    aggregate["tokens_in_total"] = int(sum(column("tokens_in")))
    aggregate["tokens_out_total"] = int(sum(column("tokens_out")))
    aggregate["usd_total"] = sum(column("usd"))
    aggregate["reference_usd_total"] = sum(column("reference_usd"))
    aggregate.update(judge_spend(records))
    return aggregate


def judge_spend(records: Sequence[QuestionRecord]) -> dict[str, Any]:
    """What judging cost, counted apart from what answering cost.

    The judge runs on the z.ai coding plan, which bills nothing against the
    Mistral budget (D-020), so its tokens would vanish if they were added to the
    answer totals. They are counted anyway: "free" is a statement about this
    month's plan, not about the work, and a Mistral judge would be priced from
    exactly these numbers.
    """
    judged = [record.judge for record in records if record.judge is not None]
    prompt = sum(judgement.usage.prompt_tokens for judgement in judged)
    completion = sum(judgement.usage.completion_tokens for judgement in judged)
    reasoning = sum(judgement.usage.reasoning_tokens for judgement in judged)
    price = PRICES[REFERENCE_PRICING_MODEL]
    return {
        "judge_calls": len(judged),
        "judge_failures": sum(1 for judgement in judged if judgement.verdict is None),
        "judge_tokens_in": prompt,
        "judge_tokens_out": completion,
        "judge_reasoning_tokens": reasoning,
        "judge_latency_s_mean": (_mean([judgement.latency_ms for judgement in judged]) or 0.0)
        / 1000,
        "judge_reference_usd_total": (
            prompt * price.input_usd_per_mtok + completion * price.output_usd_per_mtok
        )
        / 1_000_000,
    }


def aggregate(records: Sequence[QuestionRecord], config: Mapping[str, Any]) -> dict[str, Any]:
    """The metrics file: one cell per strategy and question type, plus totals."""
    strategies = [
        strategy
        for strategy in config.get("strategies", [])
        if any(record.strategy == strategy for record in records)
    ] or sorted({record.strategy for record in records})
    types = [
        question_type
        for question_type in QUESTION_TYPES
        if any(record.question_type == question_type for record in records)
    ]
    by_strategy: dict[str, Any] = {}
    for strategy in strategies:
        rows = [record for record in records if record.strategy == strategy]
        by_strategy[strategy] = {
            "all": cell(rows),
            "by_type": {
                question_type: cell([row for row in rows if row.question_type == question_type])
                for question_type in types
            },
        }
    return {
        "kind": "answer_eval",
        "model": config.get("model"),
        "judge_model": config.get("judge_model"),
        "variant": config.get("variant"),
        "dataset": config.get("dataset"),
        "dataset_sha256": config.get("dataset_sha256"),
        "strategies": strategies,
        "question_types": types,
        "questions": len({record.question_id for record in records}),
        "records": len(records),
        "by_strategy": by_strategy,
        "totals": cell(list(records)),
        "winners": winners(by_strategy),
    }


# Metrics the README names a winner for, and whether more is better.
WINNER_METRICS: tuple[tuple[str, bool], ...] = (
    ("cited_url_match", True),
    ("cited_anchor_match", True),
    ("citation_verification_rate", True),
    ("unverified_citations_per_answer", False),
    ("refusal_correct", True),
    ("correctness", True),
    ("groundedness", True),
    ("citation_relevance", True),
    ("latency_p50_s", False),
    ("usd", False),
    ("reference_usd", False),
)


def winners(by_strategy: Mapping[str, Any]) -> dict[str, str | None]:
    """The best strategy on each metric, over all question types."""
    result: dict[str, str | None] = {}
    for metric, higher_is_better in WINNER_METRICS:
        scored = [
            (strategy, cells["all"][metric])
            for strategy, cells in by_strategy.items()
            if cells["all"].get(metric) is not None
        ]
        if not scored:
            result[metric] = None
            continue
        best = (
            max(scored, key=lambda pair: pair[1])
            if higher_is_better
            else min(scored, key=lambda pair: pair[1])
        )
        result[metric] = best[0]
    return result


# --------------------------------------------------------------------------- #
# The run directory
# --------------------------------------------------------------------------- #

_scope: ContextVar[tuple[str, str] | None] = ContextVar("answer_eval_scope", default=None)


@contextlib.contextmanager
def answer_scope(question_id: str, strategy: str) -> Iterator[None]:
    """Tag the answer layer's calls with the pair they were made for."""
    token = _scope.set((question_id, strategy))
    try:
        yield
    finally:
        _scope.reset(token)


class RunDirectory:
    """One run's files. Rows are appended as they are produced, so a run that is
    killed halfway still holds everything it paid for -- and is resumable."""

    def __init__(self, path: Path, config: dict[str, Any]) -> None:
        self.path = path
        self.config = config
        self.calls_path = path / "calls.jsonl"
        self.records_path = path / "records.jsonl"
        self.records: list[QuestionRecord] = []

    @classmethod
    def open(cls, path: Path, config: dict[str, Any]) -> RunDirectory:
        """Create the directory, or reopen one and read its records back."""
        resumed = path.exists()
        (path / "figures").mkdir(parents=True, exist_ok=True)
        run = cls(path, config)
        if resumed and run.records_path.exists():
            run.records = read_records(run.records_path)
        run.calls_path.touch()
        run.records_path.touch()
        run.config["resumed_records"] = len(run.records)
        (path / "config.json").write_text(json.dumps(run.config, indent=2, sort_keys=True) + "\n")
        return run

    @property
    def done(self) -> set[tuple[str, str]]:
        return {record.key for record in self.records}

    def record(self, record: QuestionRecord) -> None:
        self.records.append(record)
        self._append(self.records_path, json.loads(record.model_dump_json()))

    def append_call(self, source: str, row: Mapping[str, Any]) -> None:
        """One line in `calls.jsonl`, tagged with which client made the call."""
        self._append(self.calls_path, {"source": source, **row})

    def finalize(self, *, status: str, error: str | None) -> dict[str, Any]:
        metrics = aggregate(self.records, self.config)
        metrics["status"] = status
        metrics["error"] = error
        (self.path / "metrics.json").write_text(
            json.dumps(metrics, indent=2, sort_keys=True) + "\n"
        )
        (self.path / "README.md").write_text(render_readme(self.config, metrics))
        render_figures(metrics, self.path / "figures")
        return metrics

    @staticmethod
    def _append(path: Path, row: Mapping[str, Any]) -> None:
        with path.open("a") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


class AnswerCallRecorder:
    """The answer layer's `CallRecorder`, writing into the run's `calls.jsonl`.

    The two client libraries record different shapes, and flattening one into the
    other would lose fields that only one of them has (tool calls on one side,
    thinking mode and cache hits on the other). Both go into the same file with a
    `source` tag instead, so the file stays the run's whole call ledger (D-023).
    """

    def __init__(self, run_dir: RunDirectory) -> None:
        self.run_dir = run_dir

    def record(self, call: LLMCall) -> None:
        scope = _scope.get()
        self.run_dir.append_call(
            "answer",
            {
                "question_id": scope[0] if scope else None,
                "strategy": scope[1] if scope else None,
                **json.loads(call.model_dump_json()),
            },
        )


class JudgeCallRecorder:
    """The provider's `CallRecorder`, writing into the same `calls.jsonl`."""

    def __init__(self, run_dir: RunDirectory) -> None:
        self.run_dir = run_dir

    def record_call(self, **row: Any) -> None:
        self.run_dir.append_call(
            "judge", {"timestamp": datetime.now(UTC).isoformat(), **_jsonable(row)}
        )


def _jsonable(row: Mapping[str, Any]) -> dict[str, Any]:
    """The provider hands over pydantic models and sequences; JSON wants neither."""
    out: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, BaseModel):
            out[key] = value.model_dump(mode="json")
        elif key == "messages":
            out[key] = [dict(message) for message in value]
        else:
            out[key] = value
    return out


def read_records(path: Path) -> list[QuestionRecord]:
    return [
        QuestionRecord.model_validate_json(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def resolve_run_directory(name: str, *, root: Path = RUNS_ROOT) -> Path:
    """The directory for a run of this name: an existing one, or a fresh one.

    Resumption is by name rather than by path so that the command a run was
    started with is also the command that finishes it. The newest matching
    directory wins, because that is the run the operator just interrupted.
    """
    safe = RUN_NAME_RE.sub("-", name.casefold()).strip("-")
    if not safe:
        raise ValueError("run name must contain a letter or digit")
    existing = sorted(path for path in root.glob(f"*-{safe}") if path.is_dir())
    if existing:
        return existing[-1]
    return root / f"{datetime.now(UTC).strftime('%Y-%m-%d-%H%M')}-{safe}"


# --------------------------------------------------------------------------- #
# Running
# --------------------------------------------------------------------------- #


async def zai_headroom(client: httpx.AsyncClient | None = None) -> int | None:
    """Percent of the five-hour z.ai token window already used (D-028).

    None when the endpoint cannot be read: a quota check that fails is a reason
    to say so, not a reason to refuse to judge.
    """
    key = os.environ.get("ZAI_API_KEY")
    if not key:
        return None
    owned = client is None
    http = client or httpx.AsyncClient(timeout=20.0)
    try:
        response = await http.get(ZAI_QUOTA_URL, headers={"Authorization": f"Bearer {key}"})
        response.raise_for_status()
        limits = response.json()["data"]["limits"]
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
        logger.warning("z.ai quota unreadable", error=str(error))
        return None
    finally:
        if owned:
            await http.aclose()
    for limit in limits:
        if limit.get("type") == "TOKENS_LIMIT":
            return int(limit.get("percentage", 0))
    return None


async def wait_for_quota(ceiling: int = QUOTA_CEILING_PERCENT) -> int | None:
    """Poll the quota before a batch and pause while it is above the ceiling."""
    used = await zai_headroom()
    while used is not None and used >= ceiling:
        logger.warning("z.ai token window above the ceiling, pausing", used=used, ceiling=ceiling)
        await asyncio.sleep(300)
        used = await zai_headroom()
    return used


async def answer_one(
    question: EvalQuestion,
    strategy: str,
    *,
    variant: str,
    model: str,
    settings: AnswerConfig,
    engine: SearchEngine,
    llm: MistralLLM,
) -> QuestionRecord:
    """One (question, strategy) pair, whatever happens to it.

    A strategy that raises is recorded with its error rather than killing the
    run: a run of thirty-six answers must not be lost to one timeout, and an
    error that is not in the records is an error nobody can count.
    """
    base = QuestionRecord(
        question_id=question.id,
        question=question.question,
        question_type=question.type.value,
        language=question.language,
        gold_urls=[gold.url for gold in question.gold],
        gold_anchors=[gold.anchor for gold in question.gold],
        reference_answer=question.reference_answer,
        strategy=strategy,
        variant=variant,
        model=model,
    )
    started = time.perf_counter()
    with answer_scope(question.id, strategy):
        try:
            answer: Answer = await ask(
                question.question,
                strategy=strategy,
                variant=variant,
                model=model,
                config=settings,
                engine=engine,
                llm=llm,
            )
        except Exception as error:  # noqa: BLE001 - recorded, then the run goes on
            logger.warning(
                "Answer failed", question=question.id, strategy=strategy, error=str(error)
            )
            return base.model_copy(
                update={
                    "error": f"{type(error).__name__}: {error}",
                    "latency_ms": (time.perf_counter() - started) * 1000,
                }
            )
    return base.model_copy(
        update={
            "answer_markdown": answer.answer_markdown,
            "citations": answer.citations,
            "unverified_citations": answer.trace.unverified_citations,
            "insufficient_evidence": answer.insufficient_evidence,
            "trace": answer.trace,
            "usage": answer.usage,
            "latency_ms": answer.latency_ms,
            "cost_usd": answer.cost_usd,
        }
    )


async def judge_one(
    question: EvalQuestion,
    record: QuestionRecord,
    *,
    provider: OpenAICompatibleProvider,
    model: str,
) -> JudgeRecord:
    """Grade one answer. The judge never learns which strategy wrote it."""
    payload = judge_input(question, record)
    rendered = payload.render()
    started = time.perf_counter()
    with candidate_scope(f"{record.question_id}:{record.strategy}"), call_scope("judge"):
        try:
            completion = await provider.complete(
                [
                    {"role": "system", "content": JUDGE_SYSTEM},
                    {"role": "user", "content": rendered},
                ],
                model=model,
                temperature=JUDGE_TEMPERATURE,
                max_tokens=JUDGE_MAX_TOKENS,
                response_schema=JudgeVerdict,
                thinking="disabled",
            )
        except ProviderCallError as error:
            return JudgeRecord(
                model=model,
                prompt_version=JUDGE_VERSION,
                input_text=rendered,
                error=str(error),
                latency_ms=(time.perf_counter() - started) * 1000,
            )
    verdict = completion.parsed if isinstance(completion.parsed, JudgeVerdict) else None
    return JudgeRecord(
        model=model,
        prompt_version=JUDGE_VERSION,
        input_text=rendered,
        raw_output=completion.text,
        verdict=verdict,
        error=None if verdict else "the judge's output did not validate",
        latency_ms=(time.perf_counter() - started) * 1000,
        usage=completion.usage,
    )


async def run(
    questions: Sequence[EvalQuestion],
    *,
    strategies: Sequence[str],
    variant: str,
    model: str,
    judge_model: str | None,
    run_dir: RunDirectory,
    settings: AnswerConfig,
    quota_ceiling: int = QUOTA_CEILING_PERCENT,
) -> dict[str, Any]:
    """Every question through every strategy, judged, recorded, summarized.

    Questions run one at a time: the Mistral account is on the free tier, where
    concurrency buys 429s rather than throughput (D-028).
    """
    by_id = {question.id: question for question in questions}
    done = run_dir.done
    pending = [
        (question, strategy)
        for question in questions
        for strategy in strategies
        if (question.id, strategy) not in done
    ]
    logger.info("Answer eval", pending=len(pending), recorded=len(done), run_dir=str(run_dir.path))
    if judge_model:
        await wait_for_quota(quota_ceiling)

    engine = SearchEngine(RetrievalConfig(variant=variant, top_k=settings.top_k))
    llm = MistralLLM(settings, client=build_client(), recorder=AnswerCallRecorder(run_dir))
    provider = (
        OpenAICompatibleProvider(
            "zai",
            asyncio.Semaphore(1),
            caller_tag="eval.answer_eval",
            recorder=JudgeCallRecorder(run_dir),
            seed=0,
        )
        if judge_model
        else None
    )
    try:
        for question, strategy in pending:
            record = await answer_one(
                question,
                strategy,
                variant=variant,
                model=model,
                settings=settings,
                engine=engine,
                llm=llm,
            )
            if provider is not None and judge_model and record.error is None:
                judgement = await judge_one(
                    by_id[question.id], record, provider=provider, model=judge_model
                )
                record = record.model_copy(update={"judge": judgement})
            run_dir.record(record)
    finally:
        if provider is not None:
            await provider.aclose()
    return run_dir.finalize(status="complete", error=None)


# --------------------------------------------------------------------------- #
# The README and the figures
# --------------------------------------------------------------------------- #

FAMILIES: tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...] = (
    (
        "Citations against the gold sources",
        "Whether the answer's verified citations point at the pages the dataset "
        "says hold the answer. Unanswerable questions have no gold source, so they "
        "are left out of these two tables rather than counted as failures.",
        (
            ("cited_url_match", "a verified citation names a gold page"),
            ("cited_anchor_match", "a verified citation names the gold section"),
        ),
    ),
    (
        "Citation verification",
        "Whether the quotes the model wrote are in the sources it named. A "
        "fabricated rejection is a sentence that is not in the source at all; a "
        "cosmetic one is a quote too short to be evidence. The two are reported "
        "apart because averaging them hides both (D-027a). Distinct sources are "
        "counted beside the citations because an answer that cites `[1]` five "
        "times looks well cited and is not.",
        (
            ("citation_verification_rate", "verified citations over emitted citations"),
            ("unverified_citations_per_answer", "rejected citations per answer"),
            ("fabricated_per_answer", "fabricated rejections per answer"),
            ("cosmetic_per_answer", "cosmetic rejections per answer"),
            ("distinct_sources_cited", "different sources cited per answer"),
            ("unmatched_markers_per_answer", "`[n]` markers with no citation behind them"),
        ),
    ),
    (
        "Refusal",
        "`insufficient_evidence` should be set on exactly the questions the "
        "documentation cannot answer. This table scores both directions: a refused "
        "answerable question is as wrong as an answered unanswerable one.",
        (("refusal_correct", "the refusal flag matches the question"),),
    ),
    (
        "Judged quality",
        "GLM's verdicts (D-021), reported beside the deterministic numbers and "
        "never merged into them. Correctness scores correct as 1, partial as 0.5, "
        "wrong as 0. Groundedness is the fraction of the answer's factual claims "
        "the cited passages support. Citation relevance is the fraction of "
        "citations that support the sentence they are attached to.",
        (
            ("correctness", "correctness against the reference answer"),
            ("groundedness", "claims supported by the cited passages"),
            ("citation_relevance", "citations that support their sentence"),
        ),
    ),
    (
        "Effort",
        "What each strategy spent to get there.",
        (
            ("latency_p50_s", "median seconds per answer"),
            ("latency_p95_s", "95th percentile seconds per answer"),
            ("tokens_in", "prompt tokens per answer"),
            ("tokens_out", "completion tokens per answer"),
            ("usd", "USD per question, at this run's price table"),
            ("reference_usd", f"USD per question at {REFERENCE_PRICING_MODEL} prices"),
            ("tool_calls", "tool calls per answer"),
            ("rounds", "rounds per answer"),
        ),
    ),
)

_DECIMALS: dict[str, int] = {
    **MEAN_METRICS,
    "citation_verification_rate": 2,
    "fabricated_per_answer": 2,
    "cosmetic_per_answer": 2,
    "latency_p50_s": 1,
    "latency_p95_s": 1,
}


def _format(value: Any, metric: str) -> str:
    if value is None:
        return "--"
    if isinstance(value, float):
        return f"{value:.{_DECIMALS.get(metric, 2)}f}"
    return str(value)


def _metric_table(metrics: Mapping[str, Any], metric: str) -> str:
    """One metric, strategies as rows and question types as columns.

    The generation model is a column of every table: this run and a re-run on
    Mistral Medium 3.5 will sit side by side in the same README one day, and a
    number without its model is not a number (D-017a).
    """
    types = list(metrics["question_types"])
    header = "| strategy | model | " + " | ".join(types) + " | all |"
    divider = "|---" * (len(types) + 3) + "|"
    lines = [header, divider]
    for strategy, cells in metrics["by_strategy"].items():
        values = [
            _format(cells["by_type"][question_type].get(metric), metric) for question_type in types
        ]
        lines.append(
            f"| `{strategy}` | `{metrics['model']}` | "
            + " | ".join(values)
            + f" | **{_format(cells['all'].get(metric), metric)}** |"
        )
    return "\n".join(lines)


def _trade_off(metrics: Mapping[str, Any]) -> str:
    """One sentence naming the winners and what the best answer costs."""
    winner = metrics["winners"]
    quality = winner.get("correctness") or winner.get("cited_url_match")
    cheap = winner.get("usd") or winner.get("latency_p50_s")
    if not quality:
        return "No strategy produced a comparable number in this run."
    if quality == cheap:
        return (
            f"`{quality}` wins on quality and on cost, so there is no trade-off to "
            "make in this run."
        )
    strategies = metrics["by_strategy"]
    quality_cell = strategies[quality]["all"]
    cheap_cell = strategies[cheap]["all"] if cheap in strategies else quality_cell
    ratio = (
        quality_cell["tokens_in_total"] / cheap_cell["tokens_in_total"]
        if cheap_cell["tokens_in_total"]
        else 1.0
    )
    return (
        f"`{quality}` answers best and `{cheap}` is cheapest: the better answers "
        f"cost {ratio:.1f}x the prompt tokens of the cheaper strategy."
    )


def render_readme(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> str:
    """The run README (D-023). Every sentence in it is computed from the records."""
    totals = metrics["totals"]
    unpriced = metrics["model"] in UNPRICED_MODELS
    price_note = (
        f"\n\n`{metrics['model']}` has no published price, so the USD column of this "
        f"run is zero by construction. The row beside it prices the same recorded "
        f"tokens at {REFERENCE_PRICING_MODEL} rates (D-017), which is what the "
        "shipped configuration would have cost."
        if unpriced
        else ""
    )
    judged = (
        f"{totals['judged']} of {metrics['records']} answers were judged by "
        f"`{metrics['judge_model']}` with thinking disabled."
        if metrics.get("judge_model")
        else "The judge was skipped in this run, so only the deterministic tables below are filled."
    )
    winner_lines = [
        f"- `{metric}`: **{strategy}**"
        for metric, strategy in metrics["winners"].items()
        if strategy is not None
    ]
    # Notes are the one part of the README an operator writes, and they are
    # written on the command line so that the README stays fully generated: a
    # sentence typed into a rendered file is lost the next time it is rendered.
    judge_cost = (
        f"Judging spent {totals['judge_tokens_in']} prompt and "
        f"{totals['judge_tokens_out']} completion tokens over {totals['judge_calls']} "
        f"call(s) ({totals['judge_reasoning_tokens']} of them reasoning tokens, with "
        "thinking disabled), at a mean of "
        f"{totals['judge_latency_s_mean']:.1f} s per judgement and "
        f"{totals['judge_failures']} verdict(s) that did not validate. The z.ai coding "
        "plan bills nothing against the Mistral budget (D-020); the same judging on "
        f"{REFERENCE_PRICING_MODEL} would have cost "
        f"{totals['judge_reference_usd_total']:.4f} USD."
        if totals["judge_calls"]
        else "Nothing was judged in this run."
    )
    notes = "\n".join(f"- {note}" for note in config.get("notes") or [])
    notes_section = f"\n\n## Notes on this run\n\n{notes}" if notes else ""
    family_sections = []
    for title, blurb, metric_list in FAMILIES:
        tables = [
            f"**{metric}** -- {caption}\n\n{_metric_table(metrics, metric)}"
            for metric, caption in metric_list
        ]
        family_sections.append(f"### {title}\n\n{blurb}\n\n" + "\n\n".join(tables))

    return f"""# Answer evaluation: {", ".join(metrics["strategies"])} on `{metrics["variant"]}`

**What this measures.** Which way of gathering evidence produces the best cited
answer, and what each one costs. Every question of the dataset is run through
each strategy against the same index, and every answer is scored twice: once by
code that can be re-run without a model, and once by a judge.

The deterministic checks are the primary numbers (D-016). They ask whether a
verified citation landed on a page the dataset names as gold, whether the quotes
the model wrote survive the verifier, whether the answer refused exactly the
questions the documentation cannot answer, and what the run spent. None of them
depends on a model's opinion, so none of them moves when a judge is swapped.

The judge answers what code cannot: whether the answer is *right*, whether its
claims are actually in the passages it cites, and whether each citation supports
the sentence it hangs on. It is shown the question, the reference answer, the
gold URLs, the answer and the cited passages verbatim -- and never which strategy
wrote the answer, so it cannot prefer one.

## Configuration

- Generation model: `{metrics["model"]}`
- Judge model: `{metrics.get("judge_model") or "none (--skip-judge)"}` ({JUDGE_VERSION})
- Index variant: `{metrics["variant"]}`, top_k {config.get("top_k")}, context budget \
{config.get("context_token_budget")} tokens
- Dataset: `{metrics["dataset"]}`, sha256 `{metrics["dataset_sha256"]}`
- Questions: {metrics["questions"]}; strategies: {len(metrics["strategies"])}; \
records: {metrics["records"]}
- Judge prompt hashes: {json.dumps(JUDGE_PROMPT_HASHES, sort_keys=True)}

`config.json` holds every other parameter, including the price table the USD
columns were computed with.{notes_section}

## Results

{judged} {totals["errors"]} answer(s) ended in an error and are recorded with it.

{(chr(10) * 2).join(family_sections)}

## Cost and latency

The run made {metrics["records"]} answers over {metrics["questions"]} questions:
{totals["tokens_in_total"]} prompt and {totals["tokens_out_total"]} completion tokens,
{totals["usd_total"]:.4f} USD at this run's price table and
{totals["reference_usd_total"]:.4f} USD at {REFERENCE_PRICING_MODEL} prices. Median
answer latency was {_format(totals["latency_p50_s"], "latency_p50_s")} s, 95th
percentile {_format(totals["latency_p95_s"], "latency_p95_s")} s.{price_note}

{judge_cost}

## Winner per metric

{chr(10).join(winner_lines) or "- No metric had a comparable value."}

{_trade_off(metrics)}

## Figures

`figures/` is regenerated from `metrics.json` by `make eval-report run={config.get("run_dir")}`.

- `citation-match.svg`: gold URL and gold anchor match, per strategy
- `verification-rate.svg`: verified, fabricated and cosmetic citations, per strategy
- `correctness.svg`: correct, partial and wrong, per strategy
- `groundedness.svg`: groundedness and citation relevance, per strategy
- `latency-vs-correctness.svg`: what the better answers cost in seconds
- `cost-per-question.svg`: USD per question at {REFERENCE_PRICING_MODEL} prices

## Files

- `config.json` -- every parameter, including the judge prompt hashes and the price table.
- `calls.jsonl` -- every model call, verbatim. `source` is `answer` for the serving
  path's calls and `judge` for the judge's.
- `records.jsonl` -- one line per (question, strategy): the answer, its verified and
  rejected citations, the whole trace including the context the model saw, the judge's
  input and raw output, usage, latency and cost. These rows are also the run's
  checkpoint: re-running with the same name skips the pairs already in them.
- `metrics.json` -- every number in the tables above.

## What it feeds

D-016 (which deterministic checks and which judged ones the answer eval reports),
D-027 (which strategy the shipped `ask` defaults to) and D-017a (the generation
model column, so this run and a Mistral Medium 3.5 re-run stay comparable).
"""


def render_figures(metrics: Mapping[str, Any], figures_dir: Path) -> list[Path]:
    """The six charts the README links. Returns the files written."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    strategies = list(metrics["by_strategy"])

    def values(metric: str) -> list[tuple[str, tuple[float, ...]]]:
        return [
            (strategy, (float(metrics["by_strategy"][strategy]["all"].get(metric) or 0.0),))
            for strategy in strategies
        ]

    def pairs(*names: str) -> list[tuple[str, tuple[float, ...]]]:
        return [
            (
                strategy,
                tuple(
                    float(metrics["by_strategy"][strategy]["all"].get(name) or 0.0)
                    for name in names
                ),
            )
            for strategy in strategies
        ]

    written: list[Path] = []
    charts: tuple[tuple[str, str], ...] = (
        ("citation-match.svg", "citation"),
        ("verification-rate.svg", "verification"),
        ("correctness.svg", "correctness"),
        ("groundedness.svg", "groundedness"),
        ("cost-per-question.svg", "cost"),
    )
    bodies = {
        "citation": bar_chart(
            "Citations landing on a gold source",
            pairs("cited_url_match", "cited_anchor_match"),
            ("gold URL", "gold anchor"),
        ),
        "verification": bar_chart(
            "Citation verification",
            pairs("citation_verification_rate", "fabricated_per_answer", "cosmetic_per_answer"),
            ("verified rate", "fabricated/answer", "cosmetic/answer"),
        ),
        "correctness": bar_chart(
            "Judged correctness",
            pairs("correct", "partial", "wrong"),
            ("correct", "partial", "wrong"),
        ),
        "groundedness": bar_chart(
            "Groundedness and citation relevance",
            pairs("groundedness", "citation_relevance"),
            ("groundedness", "citation relevance"),
        ),
        "cost": bar_chart(
            f"USD per question at {REFERENCE_PRICING_MODEL} prices",
            values("reference_usd"),
            ("USD",),
        ),
    }
    for name, key in charts:
        path = figures_dir / name
        path.write_text(bodies[key])
        written.append(path)

    points = [
        (
            strategy,
            float(metrics["by_strategy"][strategy]["all"].get("latency_p50_s") or 0.0),
            float(metrics["by_strategy"][strategy]["all"].get("correctness") or 0.0),
        )
        for strategy in strategies
    ]
    scatter_path = figures_dir / "latency-vs-correctness.svg"
    scatter_path.write_text(
        scatter(
            "What the better answers cost in seconds",
            points,
            x_label="median seconds per answer",
            y_label="judged correctness",
        )
    )
    written.append(scatter_path)
    return written


def regenerate(run_dir: Path) -> dict[str, Any]:
    """Rebuild metrics.json, README.md and figures/ from the run's own rows."""
    config = json.loads((run_dir / "config.json").read_text())
    previous: dict[str, Any] = {}
    with contextlib.suppress(FileNotFoundError, ValueError):
        previous = json.loads((run_dir / "metrics.json").read_text())
    directory = RunDirectory(run_dir, config)
    directory.records = read_records(run_dir / "records.jsonl")
    return directory.finalize(
        status=previous.get("status", "complete"), error=previous.get("error")
    )


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a question dataset through the answer strategies and score it"
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument(
        "--strategies",
        default="single_pass,search_loop,outline",
        help="Comma-separated strategy names",
    )
    parser.add_argument("--variant", default="sec1024")
    parser.add_argument("--name", required=True, help="Run name; re-running it resumes the run")
    parser.add_argument(
        "--limit",
        type=int,
        help="Run a stratified subset of this many questions instead of the whole dataset",
    )
    parser.add_argument("--seed", type=int, default=0, help="Seed for --limit's sampler")
    parser.add_argument("--model", default=DEFAULT_GENERATION_MODEL)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--top-k", type=int, default=AnswerConfig().top_k)
    parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    parser.add_argument(
        "--note",
        action="append",
        default=[],
        dest="notes",
        help="A sentence of context to render in the run README; repeatable",
    )
    parser.add_argument(
        "--quota-ceiling",
        type=int,
        default=QUOTA_CEILING_PERCENT,
        help="Pause before judging while the z.ai token window is this full",
    )
    return parser.parse_args(argv)


async def _run(args: argparse.Namespace) -> None:
    strategies = [name.strip() for name in args.strategies.split(",") if name.strip()]
    unknown = sorted(set(strategies) - set(STRATEGIES))
    if unknown:
        raise SystemExit(f"unknown strategy {unknown}; available: {sorted(STRATEGIES)}")

    questions = read_jsonl(args.dataset)
    if args.limit is not None:
        questions = stratified_subset(questions, args.limit, args.seed)
    settings = AnswerConfig(model=args.model, top_k=args.top_k, prices=EVAL_PRICES)
    judge_model = None if args.skip_judge else args.judge_model

    run_path = resolve_run_directory(args.name, root=args.runs_root)
    config: dict[str, Any] = {
        "kind": "answer_eval",
        "name": args.name,
        "run_dir": str(run_path),
        "dataset": str(args.dataset),
        "dataset_sha256": dataset_hash(args.dataset),
        "questions": [question.id for question in questions],
        "limit": args.limit,
        "seed": args.seed,
        "variant": args.variant,
        "strategies": strategies,
        "model": args.model,
        "judge_model": judge_model,
        "judge_prompt_version": JUDGE_VERSION,
        "judge_prompt_hashes": JUDGE_PROMPT_HASHES,
        "judge_temperature": JUDGE_TEMPERATURE,
        "judge_max_tokens": JUDGE_MAX_TOKENS,
        "judge_thinking": "disabled",
        "judge_provider": "zai",
        "top_k": settings.top_k,
        "context_token_budget": settings.context_token_budget,
        "answer_config": settings.model_dump(mode="json"),
        "unpriced_models": sorted(UNPRICED_MODELS),
        "reference_pricing_model": REFERENCE_PRICING_MODEL,
        "notes": list(args.notes),
    }
    run_dir = RunDirectory.open(run_path, config)
    try:
        metrics = await run(
            questions,
            strategies=strategies,
            variant=args.variant,
            model=args.model,
            judge_model=judge_model,
            run_dir=run_dir,
            settings=settings,
            quota_ceiling=args.quota_ceiling,
        )
    except Exception as error:
        run_dir.finalize(status="failed", error=f"{type(error).__name__}: {error}")
        raise
    print(
        json.dumps(
            {
                "run_dir": str(run_path),
                "records": metrics["records"],
                "questions": metrics["questions"],
                "errors": metrics["totals"]["errors"],
                "tokens_in": metrics["totals"]["tokens_in_total"],
                "tokens_out": metrics["totals"]["tokens_out_total"],
                "usd": round(metrics["totals"]["usd_total"], 6),
                "reference_usd": round(metrics["totals"]["reference_usd_total"], 6),
                "winners": metrics["winners"],
            },
            indent=2,
        )
    )


def main() -> None:
    load_dotenv()
    asyncio.run(_run(_parse_args()))


if __name__ == "__main__":
    main()


__all__ = [
    "DEFAULT_GENERATION_MODEL",
    "DEFAULT_JUDGE_MODEL",
    "JUDGE_SYSTEM",
    "JUDGE_USER",
    "JUDGE_VERSION",
    "JudgeInput",
    "JudgeRecord",
    "JudgeVerdict",
    "QuestionRecord",
    "RunDirectory",
    "aggregate",
    "cell",
    "judge_input",
    "question_metrics",
    "regenerate",
    "render_figures",
    "render_readme",
    "resolve_run_directory",
    "run",
    "source_texts",
]
