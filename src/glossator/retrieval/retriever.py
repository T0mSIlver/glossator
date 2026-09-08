"""A retriever that can carry ranking weights, filters and exclusions at once.

The toolkit's ``VectorRetriever`` builds a plain ``VectorSearchQuery``, which has
no seam for a per-query filter or for ranking weights; and a named Vespa query
profile, the other way to set weights, makes ``exclude_ids`` and
``extra_yql_filter`` raise (D-014). So retrieval goes through the query-builder
path with a ``VespaSearchQuery`` of our own.
"""

from typing import override

import structlog
from mistralai.search.toolkit.context import RetrievalContext
from mistralai.search.toolkit.embedding import Embedder
from mistralai.search.toolkit.plugins.vespa.search.index import VespaSearchIndex
from mistralai.search.toolkit.plugins.vespa.search.query import VespaSearchQuery
from mistralai.search.toolkit.retrieval.errors import RetrieverException
from mistralai.search.toolkit.retrieval.retrievers.base import DEFAULT_TOP_K, Retriever
from mistralai.search.toolkit.search import SearchResult

from glossator.retrieval.config import RetrievalConfig, query_weights
from glossator.retrieval.context import with_restrict

logger = structlog.get_logger(__name__)


class DocsRetriever(Retriever):
    """Hybrid retrieval over one index variant.

    Hybrid happens inside Vespa: the generated YQL is ``userInput OR
    nearestNeighbor`` and the two-phase rank profile combines the lexical and
    vector features (D-013). There is no second retriever to fuse.
    """

    def __init__(
        self, index: VespaSearchIndex, embedder: Embedder, config: RetrievalConfig
    ) -> None:
        super().__init__()
        self.index = index
        self.embedder = embedder
        self.config = config
        self.schema_name = config.index_variant.schema_name

    @override
    async def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        include_metadata: bool = True,
        include_content: bool = True,
        context: RetrievalContext = RetrievalContext(),
        exclude_ids: set[str] | None = None,
    ) -> list[SearchResult]:
        # Every request has to name its schema or Vespa cannot resolve the query
        # embedding's type (see glossator.retrieval.context); the caller's own
        # context is kept and the restriction merged into it.
        request_context = with_restrict(context, self.schema_name)
        try:
            embedding = await self.embedder.embed_query(query, context=request_context)
            search_query = VespaSearchQuery(
                query=query,
                embedding=embedding,
                top_k=top_k,
                include_metadata=include_metadata,
                include_content=include_content,
                exclude_ids=exclude_ids or set(),
                # No query_profile: that is what keeps the two fields below usable.
                # The builder still attaches the schema's generated default profile,
                # so the migration's baked-in weights apply and these override them.
                ranking_weights=query_weights(self.config.ranking_weights),
                extra_yql_filter=self.config.yql_filter(),
            )
            results = await self.index.search(
                query=search_query, context=request_context
            )
        except Exception as exc:
            raise RetrieverException(
                f"retrieval failed for variant {self.config.variant!r}"
            ) from exc

        stamped = [
            result.model_copy(update={"retriever_id": self.retriever_id})
            for result in results
        ]
        stamped.sort(key=lambda result: result.score, reverse=True)
        logger.debug(
            "Retrieved", variant=self.config.variant, query=query, hits=len(stamped)
        )
        return stamped
