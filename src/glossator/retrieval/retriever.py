"""Retrieve with ranking weights, filters and exclusions in one Vespa query.

The toolkit query-builder path is required because named profiles reject
``exclude_ids`` and ``extra_yql_filter`` (D-014).
"""

import re
from typing import override

import structlog
from mistralai.search.toolkit.context import RetrievalContext
from mistralai.search.toolkit.embedding import Embedder
from mistralai.search.toolkit.plugins.vespa.search.index import VespaSearchIndex
from mistralai.search.toolkit.plugins.vespa.search.query import VespaSearchQuery
from mistralai.search.toolkit.retrieval.errors import RetrieverException
from mistralai.search.toolkit.retrieval.retrievers.base import DEFAULT_TOP_K, Retriever
from mistralai.search.toolkit.search import SearchResult

from glossator.retrieval.config import RetrievalConfig, cosine_only_weights, query_weights
from glossator.retrieval.context import with_restrict

logger = structlog.get_logger(__name__)

# Chunk ids are hex digits and dashes (the toolkit derives them with uuid5). The
# cosine read-out interpolates them into YQL, so the shape is checked rather than
# assumed, the same way the config's closed vocabularies are.
_CHUNK_ID = re.compile(r"[A-Za-z0-9_.:-]{1,128}")


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
        *,
        embedding: list[float] | None = None,
    ) -> list[SearchResult]:
        """Hits for one query. ``embedding`` skips the embedding call when the
        caller already has the query's vector and needs it for something else."""
        # Every request has to name its schema or Vespa cannot resolve the query
        # embedding's type (see glossator.retrieval.context); the caller's own
        # context is kept and the restriction merged into it.
        request_context = with_restrict(context, self.schema_name)
        try:
            if embedding is None:
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
            results = await self.index.search(query=search_query, context=request_context)
        except Exception as exc:
            raise RetrieverException(
                f"retrieval failed for variant {self.config.variant!r}"
            ) from exc

        stamped = [
            result.model_copy(update={"retriever_id": self.retriever_id}) for result in results
        ]
        stamped.sort(key=lambda result: result.score, reverse=True)
        logger.debug("Retrieved", variant=self.config.variant, query=query, hits=len(stamped))
        return stamped

    async def embed_query(
        self, query: str, context: RetrievalContext = RetrievalContext()
    ) -> list[float]:
        return await self.embedder.embed_query(
            query, context=with_restrict(context, self.schema_name)
        )

    async def cosine_similarities(
        self,
        embedding: list[float],
        chunk_ids: list[str],
        context: RetrievalContext = RetrievalContext(),
    ) -> dict[str, float]:
        """Each named chunk's cosine similarity to the query vector.

        A second Vespa round trip rather than a second embedding call: the ids are
        already known, so the query restricts itself to them and ranks them on the
        exact cosine term alone (see ``cosine_only_weights``). Restricting to the
        ids matters -- an unrestricted vector-only query is ordered by the HNSW
        index's euclidean distance and need not contain the hits being scored.
        """
        if not chunk_ids:
            return {}
        malformed = sorted(id_ for id_ in chunk_ids if not _CHUNK_ID.fullmatch(id_))
        if malformed:
            raise RetrieverException(f"chunk id(s) not of the expected shape: {malformed}")
        request_context = with_restrict(context, self.schema_name)
        quoted = ", ".join(f'"{chunk_id}"' for chunk_id in sorted(set(chunk_ids)))
        # No query text: the select is then vector-only, which is all this measures.
        search_query = VespaSearchQuery(
            query="",
            embedding=embedding,
            top_k=len(set(chunk_ids)),
            ranking_weights=query_weights(cosine_only_weights()),
            extra_yql_filter=f"id in ({quoted})",
        )
        try:
            results = await self.index.search(query=search_query, context=request_context)
        except Exception as exc:
            raise RetrieverException(
                f"cosine read-out failed for variant {self.config.variant!r}"
            ) from exc
        return {result.chunk.id: result.score for result in results}
