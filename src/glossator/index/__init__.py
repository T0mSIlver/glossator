"""Handle on the deployed Vespa application: one schema per index variant."""

import os
from pathlib import Path

from mistralai.search.toolkit.plugins.vespa import VespaApp, VespaClientConfig
from mistralai.search.toolkit.plugins.vespa.search.index import VespaSearchIndex

from glossator.index.variants import VARIANTS, ChunkStrategy, IndexVariant, get_variant

app = VespaApp(Path(__file__).parent)


def vespa_endpoint() -> str:
    """Query API URL from VESPA_QUERY_PORT (or optional VESPA_ENDPOINT override)."""
    if url := os.environ.get("VESPA_ENDPOINT"):
        return url
    port = os.environ.get("VESPA_QUERY_PORT", "18080")
    return f"http://localhost:{port}"


def get_index(variant: IndexVariant | str) -> VespaSearchIndex:
    """Live index for a variant's schema.

    No query profile is passed on purpose: for DOCUMENT_PER_CHUNK the toolkit
    reads ``query_profile=None`` as "use the query builder", which is the only
    path on which ``exclude_ids`` and ``extra_yql_filter`` work (D-014). Ranking
    weights still apply -- the builder attaches the schema's generated default
    profile, whose weights the migration bakes in, and a query may override them
    per request through ``VespaSearchQuery.ranking_weights``.
    """
    resolved = get_variant(variant) if isinstance(variant, str) else variant
    return app.get_search_index(
        VespaClientConfig(endpoint=vespa_endpoint()),
        collection_name=resolved.schema_name,
    )


__all__ = [
    "VARIANTS",
    "ChunkStrategy",
    "IndexVariant",
    "app",
    "get_index",
    "get_variant",
    "vespa_endpoint",
]
