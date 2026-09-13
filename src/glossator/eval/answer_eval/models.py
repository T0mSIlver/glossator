"""The answer evaluation's records: one answer, its judge input and its verdicts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from glossator.answer.citations import Citation, Trace
from glossator.answer.llm import TokenUsage as AnswerTokenUsage
from glossator.eval.answer_eval.prompts import JUDGE_CITATION, JUDGE_NO_CITATIONS, JUDGE_USER
from glossator.eval.datasets import QuestionType
from glossator.eval.providers import ProviderName, TokenUsage

DEFAULT_GENERATION_MODEL = "ministral-14b-2512"
"""The largest Mistral model this key can reach (D-017a): every `mistral-medium-*`,
`mistral-small-*` and `magistral-*` id answers HTTP 429 with a configured limit of
zero requests per minute, which no backoff can get through."""

DEFAULT_JUDGE_MODEL = "glm-5.3"
DEFAULT_JUDGE_MODELS = "zai:glm-5.3"

QUESTION_TYPES: tuple[str, ...] = tuple(question_type.value for question_type in QuestionType)


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
    quote: str
    source_text: str


class JudgeInput(BaseModel):
    """Everything the judge is shown. It names no strategy and no model."""

    model_config = ConfigDict(frozen=True)

    question: str
    reference_answer: str
    answer_markdown: str
    citations: list[JudgedCitation]

    def render(self) -> str:
        citations = "\n\n".join(
            JUDGE_CITATION.format(
                n=citation.n,
                quote=citation.quote,
                source_text=citation.source_text,
            )
            for citation in self.citations
        )
        return JUDGE_USER.format(
            question=self.question,
            reference_answer=self.reference_answer,
            answer_markdown=self.answer_markdown or "(the system produced no text)",
            citations=citations or JUDGE_NO_CITATIONS,
        )


class JudgeRecord(BaseModel):
    """One judgement, complete enough to re-read without the model."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    model: str
    provider: ProviderName | None = None
    prompt_version: str
    input_text: str
    raw_output: str = ""
    verdict: JudgeVerdict | None = None
    error: str | None = None
    latency_ms: float = 0.0
    usage: TokenUsage = TokenUsage()


class JudgeModel(BaseModel):
    """A provider-qualified judge model from the command line."""

    model_config = ConfigDict(frozen=True)

    provider: ProviderName
    model: str

    @property
    def identifier(self) -> str:
        return f"{self.provider}:{self.model}"


def parse_judge_models(value: str) -> list[JudgeModel]:
    """Parse a comma-separated list and preserve its primary-first order."""
    judges: list[JudgeModel] = []
    seen: set[str] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        provider, separator, model = item.partition(":")
        if separator != ":" or provider not in ("zai", "mistral", "local") or not model.strip():
            raise ValueError(
                f"invalid judge model {item!r}; expected provider:model with provider "
                "zai, mistral or local"
            )
        judge = JudgeModel(provider=provider, model=model.strip())  # type: ignore[arg-type]
        if judge.identifier in seen:
            raise ValueError(f"duplicate judge model {judge.identifier}")
        judges.append(judge)
        seen.add(judge.identifier)
    if not judges:
        raise ValueError("at least one judge model is required")
    return judges


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
    cost_usd_v1: float | None = Field(default=None, exclude_if=lambda value: value is None)
    """The recorded cost before an existing run was repriced."""
    error: str | None = None
    judge: JudgeRecord | None = None
    judges: dict[str, JudgeRecord] = Field(default_factory=dict)
    judges_v1: dict[str, JudgeRecord] = Field(default_factory=dict)

    @property
    def key(self) -> tuple[str, str]:
        return (self.question_id, self.strategy)
