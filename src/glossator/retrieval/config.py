"""What one retrieval call is configured with.

Everything that an eval row varies lives here, so a grid is a list of these and
nothing else in the retrieval path has to be reconfigured.
"""

import re
from pathlib import Path
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from glossator.index.variants import VARIANTS, IndexVariant, get_variant

DEFAULT_TOP_K = 10

DEFAULT_RERANK_CANDIDATES = 20

RERANK_MODEL = "mistral-small-2603"
"""Mistral Small 4's fixed id, spelled out rather than imported.

``glossator.answer.config`` owns the price table this id is resolved through, and
importing it here would close a cycle (answer imports the search engine, the
engine imports this module). The reranker checks the id against that table when
it is built, and a test pins the two spellings together."""

DEFAULT_CORPUS_DIR = Path("corpus/mistral-docs")
"""Where the lexical-footing vocabulary is read from. The vendored corpus is what
the index was built from (D-009), so its words are exactly the words a query can
match."""

# Ranking features the schema generates. A weight naming anything else is silently
# ignored by Vespa, so it is rejected here instead.
RANK1_FEATURES = frozenset(
    {
        "bm25_content",
        "bm25_page_title",
        "bm25_heading_path_max",
        "bm25_heading_path_avg",
        "content_embedding_closeness",
    }
)
RANK2_FEATURES = frozenset(
    {
        "match_content",
        "match_page_title",
        "match_heading_path",
        "content_embedding_cosine_similarity_score",
    }
)
RANKING_FEATURES = RANK1_FEATURES | RANK2_FEATURES

KINDS = frozenset({"doc", "api", "model"})

# Filter values are interpolated into YQL, so both vocabularies are closed: kinds
# by enumeration, locales by shape.
_LOCALE = re.compile(r"[a-z]{2,3}(-[A-Za-z]{2,4})?")


class RetrievalConfig(BaseModel):
    """One retrieval configuration: which index, how many hits, how to rank, what to keep."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    variant: str = "sec1024"
    top_k: Annotated[int, Field(ge=1, le=100)] = DEFAULT_TOP_K

    ranking_weights: dict[str, float] = Field(default_factory=dict)
    """Per-query overrides of the schema's baked-in default weights. Empty means
    "use the migration's defaults", which is what a normal query wants."""

    kinds: frozenset[str] = frozenset()
    """Restrict to these page kinds. Empty means no restriction."""

    locales: frozenset[str] = frozenset()
    """Restrict to these locales (D-008 is still open, so this defaults to open)."""

    rerank: bool = False
    """Reorder the candidates with one listwise model call before returning them."""

    rerank_candidates: Annotated[int, Field(ge=1, le=100)] = DEFAULT_RERANK_CANDIDATES
    """How deep retrieval goes when reranking. The reranker sees this many hits and
    the caller still gets ``top_k``, so reranking can promote a hit from rank 17."""

    rerank_model: str = RERANK_MODEL
    rerank_temperature: float = 0.0
    """Zero, because a ranking is a judgement to be reproduced, not a text to vary."""

    similarity_floor: float | None = Field(default=None, ge=-1.0, le=1.0)
    """Drop a hit whose cosine similarity to the query is below this (D-030).
    ``None`` until the calibration run has measured the corridor."""

    similarity_margin: float | None = Field(default=None, ge=0.0, le=2.0)
    """Drop a hit further than this below the query's own best cosine (D-030)."""

    check_lexical_footing: bool = False
    """Report in the trace whether any content word of the query occurs in the
    corpus at all. Off by default because it reads the corpus from disk."""

    corpus_dir: Path = DEFAULT_CORPUS_DIR

    @model_validator(mode="after")
    def _validate(self) -> Self:
        get_variant(self.variant)
        unknown = sorted(set(self.ranking_weights) - RANKING_FEATURES)
        if unknown:
            raise ValueError(
                f"unknown ranking feature(s) {unknown}; available: {sorted(RANKING_FEATURES)}"
            )
        if self.rerank and self.rerank_candidates < self.top_k:
            raise ValueError(
                f"rerank_candidates ({self.rerank_candidates}) must be at least "
                f"top_k ({self.top_k}): reranking fewer hits than are returned "
                "would truncate the result set instead of reordering it"
            )
        bad_kinds = sorted(self.kinds - KINDS)
        if bad_kinds:
            raise ValueError(f"unknown page kind(s) {bad_kinds}; available: {sorted(KINDS)}")
        bad_locales = sorted(locale for locale in self.locales if not _LOCALE.fullmatch(locale))
        if bad_locales:
            raise ValueError(
                f"malformed locale(s) {bad_locales}; expected forms like 'en' or 'pt-BR'"
            )
        return self

    @property
    def index_variant(self) -> IndexVariant:
        return get_variant(self.variant)

    @property
    def scores_similarity(self) -> bool:
        """Whether a hit's cosine similarity has to be measured before it is returned."""
        return self.similarity_floor is not None or self.similarity_margin is not None

    @property
    def candidate_depth(self) -> int:
        """How many hits retrieval asks Vespa for, before reranking cuts to ``top_k``."""
        return max(self.top_k, self.rerank_candidates) if self.rerank else self.top_k

    def yql_filter(self) -> str | None:
        """The metadata filter as a YQL predicate, or ``None`` when nothing is filtered.

        Values are interpolated rather than bound, so they are restricted to the
        closed vocabularies validated above; nothing user-supplied reaches the YQL.
        """
        clauses = [
            _in_clause("kind", sorted(self.kinds)),
            _in_clause("locale", sorted(self.locales)),
        ]
        present = [clause for clause in clauses if clause]
        if not present:
            return None
        return " and ".join(present)


def query_weights(weights: dict[str, float]) -> dict[str, float]:
    """Translate ranking feature names into the query inputs Vespa expects.

    The two toolkit APIs that set the same weights disagree about the name.
    ``set_default_ranking_weights`` in a migration takes the *feature* name
    (``bm25_content``) and appends the suffix itself; ``VespaSearchQuery.ranking_weights``
    is serialized verbatim into ``ranking.features.query(<key>)``, so it needs the
    *input* name (``bm25_content_weight``). A feature name passed there names an
    input that no rank expression reads: the override is accepted and silently
    ignored. One vocabulary is used everywhere in this package -- the feature name --
    and translated here.
    """
    return {f"{feature}_weight": weight for feature, weight in weights.items()}


def cosine_only_weights() -> dict[str, float]:
    """Ranking weights under which a hit's score *is* its cosine similarity.

    The generated profile's second phase is ``sum(weighted rank-2 terms) +
    firstPhase``, and the first phase is a weighted sum of the rank-1 terms. Zero
    every weight but the exact cosine term and the arithmetic collapses to
    ``cosine_similarity(query, chunk)``, which is the number D-030's floor is
    expressed in and the only way to read it out: the toolkit drops Vespa's
    ``matchfeatures`` when it builds a ``SearchResult``.
    """
    weights = dict.fromkeys(RANKING_FEATURES, 0.0)
    weights["content_embedding_cosine_similarity_score"] = 1.0
    return weights


def _in_clause(field: str, values: list[str]) -> str | None:
    if not values:
        return None
    quoted = ", ".join(f'"{value}"' for value in values)
    return f"{field} in ({quoted})"


__all__ = [
    "DEFAULT_CORPUS_DIR",
    "DEFAULT_RERANK_CANDIDATES",
    "DEFAULT_TOP_K",
    "KINDS",
    "RANK1_FEATURES",
    "RANK2_FEATURES",
    "RANKING_FEATURES",
    "RERANK_MODEL",
    "VARIANTS",
    "RetrievalConfig",
    "cosine_only_weights",
    "query_weights",
]
