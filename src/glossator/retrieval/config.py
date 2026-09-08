"""What one retrieval call is configured with.

Everything that an eval row varies lives here, so a grid is a list of these and
nothing else in the retrieval path has to be reconfigured.
"""

import re
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from glossator.index.variants import VARIANTS, IndexVariant, get_variant

DEFAULT_TOP_K = 10

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

    @model_validator(mode="after")
    def _validate(self) -> Self:
        get_variant(self.variant)
        unknown = sorted(set(self.ranking_weights) - RANKING_FEATURES)
        if unknown:
            raise ValueError(
                f"unknown ranking feature(s) {unknown}; available: {sorted(RANKING_FEATURES)}"
            )
        bad_kinds = sorted(self.kinds - KINDS)
        if bad_kinds:
            raise ValueError(
                f"unknown page kind(s) {bad_kinds}; available: {sorted(KINDS)}"
            )
        bad_locales = sorted(
            locale for locale in self.locales if not _LOCALE.fullmatch(locale)
        )
        if bad_locales:
            raise ValueError(
                f"malformed locale(s) {bad_locales}; expected forms like 'en' or 'pt-BR'"
            )
        return self

    @property
    def index_variant(self) -> IndexVariant:
        return get_variant(self.variant)

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


def _in_clause(field: str, values: list[str]) -> str | None:
    if not values:
        return None
    quoted = ", ".join(f'"{value}"' for value in values)
    return f"{field} in ({quoted})"


__all__ = [
    "KINDS",
    "RANK1_FEATURES",
    "RANK2_FEATURES",
    "RANKING_FEATURES",
    "VARIANTS",
    "RetrievalConfig",
    "query_weights",
]
