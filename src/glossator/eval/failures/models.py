"""Failure classes, sub-labels, and the rows a failure analysis writes."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from glossator.eval.agreement import CorrectnessLabel
from glossator.eval.providers.models import ProviderName, TokenUsage

ANSWER_EVAL_KIND = "answer_eval"
FAILURES_KIND = "failure_analysis"


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
