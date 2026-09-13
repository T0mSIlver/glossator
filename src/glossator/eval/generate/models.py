"""Generation settings, the structured outputs the model returns, and the rows a run records."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from glossator.eval.corpus import CorpusDocument
from glossator.eval.datasets import EvalQuestion, GoldSource, QuestionType
from glossator.eval.lexical import LexicalIndex
from glossator.eval.providers.models import ChatProvider, ThinkingMode
from glossator.eval.run_records import RunRecorder

GENERATED_TYPES: tuple[QuestionType, ...] = tuple(
    question_type for question_type in QuestionType if question_type is not QuestionType.HISTORY
)
"""Every type this generator fills. History questions are written by hand from
the snapshot labels and carry a date bound no page-level prompt can produce."""

# One truncation constant, applied once per page or section text handed to a
# model. Different limits in generation and filtering let the filter reject a
# fact the generator legitimately used.
MAX_SOURCE_CHARS = 8000

MIN_SECTION_TOKENS = 80

GENERATION_TEMPERATURE = 0.7
GENERATION_MAX_TOKENS = 700
CHECK_TEMPERATURE = 0.0
CHECK_MAX_TOKENS = 500
PROBE_MAX_TOKENS = 400

# How many corpus sections an unanswerable candidate is checked against.
UNANSWERABLE_CHECK_TOP_K = 5

DROP_PROVIDER_ERROR = "provider_error"

Language = Literal["en", "fr"]


class CandidateOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: str
    reference_answer: str
    fully_answered: bool

    @field_validator("reference_answer")
    @classmethod
    def answer_is_at_most_two_lines(cls, value: str) -> str:
        if len(value.splitlines()) > 2:
            raise ValueError("reference_answer must contain at most two lines")
        return value


class CrossPageOutput(CandidateOutput):
    page_a_contribution: str
    page_b_contribution: str


class CapabilityOutput(CandidateOutput):
    names_single_model: bool


class FilterOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    standalone: bool
    gold_condition_met: bool
    not_answerable_from_title_alone: bool
    uses_every_gold_source: bool
    about_the_documented_product: bool
    reasons: list[str]


class PageAloneOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    fully_answerable: bool
    reason: str


class PageAloneVerdict(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    title: str
    fully_answerable: bool
    reason: str


class CorpusCheckOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    answered_by_corpus: bool
    reason: str


class SampledSource(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    title: str
    anchor: str | None
    heading_path: list[str]
    content: str


class SourceContribution(BaseModel):
    """Which page supplies which half of a cross-page answer.

    Kept on the record only: the reference answer a judge scores against stays a
    natural answer, with no page labels to score formatting on.
    """

    model_config = ConfigDict(frozen=True)

    url: str
    contribution: str


class GenerationAttempt(BaseModel):
    """One row of ``records.jsonl``: every candidate, kept or not."""

    model_config = ConfigDict(frozen=True)

    candidate_id: str
    generator_type: str
    seed: list[str]
    candidate: CandidateOutput | None = None
    filter: FilterOutput | None = None
    page_alone: list[PageAloneVerdict] = []
    corpus_check: CorpusCheckOutput | None = None
    consulted_sections: list[str] = []
    closed_book_answer: str | None = None
    contributions: list[SourceContribution] = []
    foreign_vendors: list[str] = []
    duplicate: bool = False
    kept: bool
    drop_reasons: list[str]
    sampled_sources: list[SampledSource]
    question: EvalQuestion | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class AttemptPlan:
    """What one attempt will ask about, decided before any model is called."""

    question_type: QuestionType
    documents: tuple[CorpusDocument, ...]
    sources: tuple[SampledSource, ...]
    gold: tuple[GoldSource, ...]
    language: Language
    nonce: int

    @property
    def candidate_id(self) -> str:
        material = {
            "type": self.question_type.value,
            "sources": [(source.url, source.anchor) for source in self.sources],
            "nonce": self.nonce,
        }
        digest = hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()
        return f"cand-{digest[:16]}"


@dataclass(slots=True)
class AttemptOutcome:
    """What the model calls produced, before duplicate detection."""

    plan: AttemptPlan
    candidate: CandidateOutput | None = None
    filter: FilterOutput | None = None
    page_alone: list[PageAloneVerdict] = field(default_factory=list)
    corpus_check: CorpusCheckOutput | None = None
    consulted_sections: list[str] = field(default_factory=list)
    closed_book_answer: str | None = None
    contributions: list[SourceContribution] = field(default_factory=list)
    foreign_vendors: list[str] = field(default_factory=list)
    gold: tuple[GoldSource, ...] = ()
    drop_reasons: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass(slots=True)
class TypeResult:
    """Per-type outcome, including a shortfall the run does not abort on."""

    question_type: QuestionType
    requested: int
    accepted: int
    attempted: int

    @property
    def shortfall(self) -> int:
        return max(self.requested - self.accepted, 0)


@dataclass(slots=True)
class GenerationContext:
    provider: ChatProvider
    model: str
    thinking: ThinkingMode | None
    documents: list[CorpusDocument]
    index: LexicalIndex
    recorder: RunRecorder | None = None
    seen: set[str] = field(default_factory=set)
