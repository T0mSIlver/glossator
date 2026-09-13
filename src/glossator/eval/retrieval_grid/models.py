"""The grid as written in YAML, its rows, and the per-question records a run writes."""

from pathlib import Path
from typing import Any, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from glossator.retrieval.config import (
    DEFAULT_RERANK_CANDIDATES,
    DEFAULT_TOP_K,
    RERANK_MODEL,
    RetrievalConfig,
)

RUN_KIND = "retrieval-grid"
"""Written into config.json so `make eval-report` knows which README to render."""

DEFAULT_REQUEST_INTERVAL = 1.1
"""Seconds between model calls. The Mistral account is on the free tier and is
governed to about one request a second with retries rather than concurrency
(D-028); Vespa itself is local and is not the constraint."""


class GridSpec(BaseModel):
    """The grid as it is written in YAML."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = "retrieval-grid"
    top_k: int = DEFAULT_TOP_K
    weight_sets: dict[str, dict[str, float]] = Field(default_factory=dict)
    axes: dict[str, list[str]] = Field(default_factory=dict)
    exclude: list[dict[str, str]] = Field(default_factory=list)
    rerank: "RerankSpec" = Field(default_factory=lambda: RerankSpec())

    @model_validator(mode="after")
    def _validate(self) -> Self:
        unknown_axes = sorted(set(self.axes) - {"variant", "weights"})
        if unknown_axes:
            raise ValueError(f"unknown grid axis/axes {unknown_axes}; available: variant, weights")
        unknown_weights = sorted(set(self.axes.get("weights", [])) - set(self.weight_sets))
        if unknown_weights:
            raise ValueError(
                f"axes name weight set(s) with no definition: {unknown_weights}; "
                f"defined: {sorted(self.weight_sets)}"
            )
        return self

    @classmethod
    def load(cls, path: Path) -> "GridSpec":
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})


class RerankSpec(BaseModel):
    """Which rows get a reranker, on which model, and how many calls they may make."""

    model_config = ConfigDict(frozen=True, extra="forbid", protected_namespaces=())

    model: str = RERANK_MODEL
    temperature: float = 0.0
    candidates: int = DEFAULT_RERANK_CANDIDATES
    max_calls: int = 400
    configurations: list[str] = Field(default_factory=list)


class GridEntry(BaseModel):
    """One row of the grid: a name and the configuration it stands for."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    variant: str
    weights: str
    """The weight set's name, kept so a table can group rows by it."""

    config: RetrievalConfig

    @property
    def reranked(self) -> bool:
        return self.config.rerank

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "variant": self.variant,
            "weights": self.weights,
            "rerank": self.reranked,
            "config": self.config.model_dump(mode="json"),
        }


class HitRecord(BaseModel):
    """One ranked hit, complete enough to recompute any metric from."""

    model_config = ConfigDict(frozen=True)

    rank: int
    chunk_id: str
    url: str
    anchor: str | None
    heading_path: list[str]
    score: float
    retrieval_score: float | None = None
    rerank_score: float | None = None
    similarity: float | None = None


class GridRecord(BaseModel):
    """One question through one configuration."""

    model_config = ConfigDict(frozen=True)

    question_id: str
    question: str
    question_type: str
    language: str
    question_source: str
    reference_answer: str
    gold: list[dict[str, str | None]]
    configuration: str
    variant: str
    weights: str
    rerank: bool

    hits: list[HitRecord] = Field(default_factory=list)
    latency_ms: float = 0.0
    lexical_footing: bool | None = None
    considered: int = 0
    kept: int = 0
    rerank_attempted: bool = False
    """Whether a rerank call was actually made and paid for. A row of a reranked
    configuration has ``rerank`` set and this false when the call budget was
    already spent, and those rows are not fallbacks: nothing was sent."""

    reranked: bool = False
    """Whether the model's ranking was applied. Attempted and not reranked is a
    fallback -- the call happened and its answer could not be used."""

    rerank_error: str | None = None
    rerank_cost_usd: float = 0.0
    rerank_usage: dict[str, int] = Field(default_factory=dict)
    metrics: dict[str, dict[str, float | int | None]] = Field(default_factory=dict)
    error: str | None = None
