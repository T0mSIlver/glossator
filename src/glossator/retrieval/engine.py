"""Search: a query and a configuration in, citable hits out.

A ``Hit`` is what the rest of the product quotes and cites, so it carries the
citation target (url plus anchor), the span it occupies in the page body, and a
handle on the index's navigation operations -- reading around a hit within its
own page is how the answer layer gets context without a second global search.
"""

import time
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any

import structlog
from mistralai.search.toolkit.context import RetrievalContext
from mistralai.search.toolkit.embedding import Embedder, MistralEmbedder
from mistralai.search.toolkit.plugins.vespa.search.index import VespaSearchIndex
from mistralai.search.toolkit.search import (
    GrepMode,
    NavigableIndex,
    NavigationDirection,
    SearchResult,
)

from glossator.clients import chat_client, embedding_client
from glossator.index import get_index
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.context import restrict_to
from glossator.retrieval.retriever import DocsRetriever
from glossator.retrieval.vocabulary import load_vocabulary

if TYPE_CHECKING:
    from glossator.answer.llm import LLM, CallRecorder
    from glossator.retrieval.reranker import ListwiseReranker, RerankTrace

logger = structlog.get_logger(__name__)

CONTENT_PREVIEW_CHARS = 240

EMBEDDER_MAX_RETRY = 8


@dataclass(frozen=True, slots=True)
class Navigation:
    """The index's positional operations, bound to one hit's place in its page."""

    index: NavigableIndex
    source_id: str
    start_offset: int
    end_offset: int
    context: RetrievalContext
    """Carries the schema restriction every request to this application needs."""

    async def around(self, window: int = 2) -> list["Hit"]:
        """The hit's neighbours and the hit itself, in reading order.

        The hit is re-read from the index rather than passed in, so the window is
        one consistent view of the page even if the chunk was re-indexed since.
        """
        previous = await self.previous(top_k=window)
        anchor = await self.read(self.start_offset, self.end_offset, top_k=1)
        following = await self.next(top_k=window)
        return previous + anchor + following

    async def next(self, top_k: int = 1) -> list["Hit"]:
        return _hits(
            await self.index.navigate(
                self.source_id,
                self.start_offset,
                self.end_offset,
                NavigationDirection.NEXT,
                top_k=top_k,
                context=self.context,
            ),
            self.index,
            self.context,
        )

    async def previous(self, top_k: int = 1) -> list["Hit"]:
        return _hits(
            await self.index.navigate(
                self.source_id,
                self.start_offset,
                self.end_offset,
                NavigationDirection.PREVIOUS,
                top_k=top_k,
                context=self.context,
            ),
            self.index,
            self.context,
        )

    async def read(
        self, start: int | None = None, end: int | None = None, top_k: int = 20
    ) -> list["Hit"]:
        """Chunks fully inside an offset range of the same page."""
        return _hits(
            await self.index.read(self.source_id, start, end, top_k=top_k, context=self.context),
            self.index,
            self.context,
        )

    async def grep(
        self, pattern: str, mode: GrepMode = GrepMode.PHRASE, top_k: int = 5
    ) -> list["Hit"]:
        """Lexical matches for a phrase within the same page."""
        return _hits(
            await self.index.grep(
                self.source_id, pattern, mode=mode, top_k=top_k, context=self.context
            ),
            self.index,
            self.context,
        )


@dataclass(frozen=True, slots=True)
class Hit:
    """One retrieved chunk, ready to cite."""

    chunk_id: str
    score: float
    url: str
    anchor: str | None
    heading_path: tuple[str, ...]
    page_title: str
    kind: str
    locale: str
    section_index: int | None
    content: str
    source_id: str
    start_offset: int | None
    end_offset: int | None
    navigation: Navigation | None = field(default=None, repr=False)
    snapshot: str | None = None
    content_sha256: str | None = None

    rerank_score: float | None = None
    """Set by the reranker: the hit's position in the model's ordering, read as a
    score. ``None`` means no reranker ran, or one ran and fell back."""

    retrieval_score: float | None = None
    """The score Vespa produced, kept when ``score`` is overwritten by a reranker."""

    similarity: float | None = None
    """Cosine similarity to the query vector, measured only when a score floor or
    margin is configured (D-030). ``score`` is a blend and is not one."""

    @property
    def citation_url(self) -> str:
        """The URL a reader should follow: the page, deep-linked when possible."""
        return f"{self.url}#{self.anchor}" if self.anchor else self.url

    @property
    def heading_line(self) -> str:
        return " > ".join(self.heading_path)

    def preview(self, chars: int | None = CONTENT_PREVIEW_CHARS) -> str:
        """The collapsed content, cut to ``chars``; ``None`` cuts nothing.

        ``None`` is the loop's "full" preview size (D-035c): a value large
        enough that no preview is cut has to be maintained against the longest
        chunk, while no cut at all is a statement about intent.
        """
        collapsed = " ".join(self.content.split())
        if chars is None or len(collapsed) <= chars:
            return collapsed
        return f"{collapsed[:chars]}..."


@dataclass(frozen=True, slots=True)
class SearchTrace:
    """Everything one search did that the hits alone do not show.

    Counts are printed as kept over considered rather than as a bare number
    (D-029): a caller that sees five hits cannot otherwise tell whether the index
    held five or the floor discarded forty-five.
    """

    query: str
    variant: str
    considered: int
    kept: int
    latency_ms: float
    lexical_footing: bool | None = None
    """``None`` when the check is off or the corpus is not on disk to check against."""

    missing_terms: tuple[str, ...] = ()
    """Content words of the query the corpus does not contain."""

    best_similarity: float | None = None
    dropped_by_floor: int = 0
    dropped_by_margin: int = 0
    rerank: "RerankTrace | None" = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "variant": self.variant,
            "considered": self.considered,
            "kept": self.kept,
            "latency_ms": round(self.latency_ms, 3),
            "lexical_footing": self.lexical_footing,
            "missing_terms": list(self.missing_terms),
            "best_similarity": self.best_similarity,
            "dropped_by_floor": self.dropped_by_floor,
            "dropped_by_margin": self.dropped_by_margin,
            "rerank": self.rerank.as_dict() if self.rerank is not None else None,
        }


class SearchEngine:
    """One configured view of the index, reusable across queries."""

    def __init__(
        self,
        config: RetrievalConfig,
        embedder: Embedder | None = None,
        llm: "LLM | None" = None,
        recorder: "CallRecorder | None" = None,
    ) -> None:
        self.config = config
        self.index: VespaSearchIndex = get_index(config.index_variant)
        self.navigation_index = as_navigable(self.index)
        self.context = restrict_to(config.index_variant.schema_name)
        self.embedder = embedder or MistralEmbedder(
            client=embedding_client(),
            model_name=config.index_variant.embedding_model_name,
            # The embedding API rate-limits on the free tier, and the toolkit's
            # three default retries are not enough for a batch of queries in a
            # row: a query that runs out of retries is a search that failed
            # (D-011a found the same thing on the ingest side).
            max_retry=EMBEDDER_MAX_RETRY,
        )
        self.retriever = DocsRetriever(self.index, self.embedder, config)
        self._llm = llm
        self._recorder = recorder
        # Built at construction, not per query: the walk over the corpus is the
        # expensive half and the answer is the same for every question asked of
        # this engine.
        self.vocabulary = (
            load_vocabulary(config.corpus_dir) if config.check_lexical_footing else None
        )

    async def search(
        self,
        query: str,
        exclude_ids: set[str] | None = None,
        top_k: int | None = None,
        *,
        rerank: bool | None = None,
        embedding: list[float] | None = None,
        kinds: frozenset[str] | None = None,
        locales: frozenset[str] | None = None,
    ) -> list[Hit]:
        """Hits for a query. ``top_k`` overrides the configured depth for one call."""
        hits, _trace = await self.search_with_trace(
            query,
            exclude_ids=exclude_ids,
            top_k=top_k,
            rerank=rerank,
            embedding=embedding,
            kinds=kinds,
            locales=locales,
        )
        return hits

    async def search_with_trace(
        self,
        query: str,
        exclude_ids: set[str] | None = None,
        top_k: int | None = None,
        *,
        rerank: bool | None = None,
        embedding: list[float] | None = None,
        kinds: frozenset[str] | None = None,
        locales: frozenset[str] | None = None,
    ) -> tuple[list[Hit], SearchTrace]:
        """The same search, with the record of what it did to the result set.

        Two callers want different things from one search: an answer strategy
        wants the hits, an evaluation wants why there are that many of them. The
        trace is built either way, so the two can never disagree.

        ``embedding`` is the query's vector when the caller already has it. A
        query's embedding depends on the model, not on the ranking weights, so an
        evaluation that runs one question through a dozen weight sets embeds it
        once and pays one request instead of a dozen.
        """
        started = time.perf_counter()
        depth = top_k or self.config.top_k
        reranking = self.config.rerank if rerank is None else rerank
        candidates = max(depth, self.config.rerank_candidates) if reranking else depth
        retriever = self._retriever_for(kinds, locales)

        if embedding is None and self.config.scores_similarity:
            embedding = await retriever.embed_query(query, context=self.context)
        results = await retriever.retrieve(
            query, top_k=candidates, exclude_ids=exclude_ids, embedding=embedding
        )
        hits = _hits(results, self.navigation_index, self.context)
        considered = len(hits)

        best_similarity: float | None = None
        dropped_floor = dropped_margin = 0
        if self.config.scores_similarity and embedding is not None and hits:
            hits, best_similarity, dropped_floor, dropped_margin = await self._apply_floors(
                embedding, hits, retriever
            )

        rerank_trace: RerankTrace | None = None
        if reranking and hits:
            outcome = await self._reranker().rerank(query, hits)
            hits, rerank_trace = outcome.hits, outcome.trace

        hits = hits[:depth]
        footing = self.vocabulary.has_footing(query) if self.vocabulary else None
        missing = tuple(self.vocabulary.missing_terms(query)) if self.vocabulary else ()
        trace = SearchTrace(
            query=query,
            variant=self.config.variant,
            considered=considered,
            kept=len(hits),
            latency_ms=(time.perf_counter() - started) * 1000,
            lexical_footing=footing,
            missing_terms=missing,
            best_similarity=best_similarity,
            dropped_by_floor=dropped_floor,
            dropped_by_margin=dropped_margin,
            rerank=rerank_trace,
        )
        logger.info(
            "Search",
            variant=self.config.variant,
            query=query,
            kept=trace.kept,
            considered=trace.considered,
            lexical_footing=footing,
        )
        return hits, trace

    def _retriever_for(
        self,
        kinds: frozenset[str] | None,
        locales: frozenset[str] | None,
    ) -> DocsRetriever:
        """Apply request filters without changing the engine shared by other callers."""
        if kinds is None and locales is None:
            return self.retriever
        values = self.config.model_dump()
        if kinds is not None:
            values["kinds"] = kinds
        if locales is not None:
            values["locales"] = locales
        config = RetrievalConfig.model_validate(values)
        return DocsRetriever(self.index, self.embedder, config)

    async def _apply_floors(
        self, embedding: list[float], hits: list[Hit], retriever: DocsRetriever | None = None
    ) -> tuple[list[Hit], float | None, int, int]:
        """Attach each hit's cosine similarity and drop the ones below the floors."""
        similarities = await (retriever or self.retriever).cosine_similarities(
            embedding, [hit.chunk_id for hit in hits], context=self.context
        )
        measured = [replace(hit, similarity=similarities.get(hit.chunk_id)) for hit in hits]
        known = [hit.similarity for hit in measured if hit.similarity is not None]
        best = max(known) if known else None

        floor = self.config.similarity_floor
        margin = self.config.similarity_margin
        kept: list[Hit] = []
        dropped_floor = dropped_margin = 0
        for hit in measured:
            # A hit whose similarity could not be read is kept: the floor exists to
            # discard what is measurably far away, not what is unmeasured.
            if hit.similarity is None:
                kept.append(hit)
                continue
            if floor is not None and hit.similarity < floor:
                dropped_floor += 1
                continue
            if margin is not None and best is not None and hit.similarity < best - margin:
                dropped_margin += 1
                continue
            kept.append(hit)
        return kept, best, dropped_floor, dropped_margin

    def _reranker(self) -> "ListwiseReranker":
        """The reranker, built on first use.

        Imported here rather than at module scope: the reranker reads the chat
        client out of ``glossator.clients`` through ``glossator.answer``, which
        imports this module back through its service layer.
        """
        from glossator.answer.llm import MistralLLM
        from glossator.retrieval.reranker import ListwiseReranker, rerank_llm_config

        if self._llm is None:
            self._llm = MistralLLM(
                rerank_llm_config(self.config), client=chat_client(), recorder=self._recorder
            )
        return ListwiseReranker(self.config, self._llm)

    def navigation_at(
        self, source_id: str, start_offset: int = 0, end_offset: int = 0
    ) -> Navigation:
        """Navigation bound to a position in a page.

        The offsets are the anchor ``next``/``previous`` step from; ``read`` and
        ``grep`` address the page directly and ignore them.
        """
        return Navigation(
            index=self.navigation_index,
            source_id=source_id,
            start_offset=start_offset,
            end_offset=end_offset,
            context=self.context,
        )

    async def get_chunk(self, chunk_id: str) -> Hit | None:
        """Resolve an opaque chunk id back to a hit, for a caller that kept only the id."""
        result = await self.navigation_index.get_chunk(chunk_id, context=self.context)
        return _hit(result, self.navigation_index, self.context) if result else None

    async def document_count(self) -> int:
        """Return the number of documents in this engine's index variant."""
        response = await self.index._client.query(  # noqa: SLF001 - toolkit has no count API
            {
                "yql": (
                    f"select * from {self.config.index_variant.schema_name} where true limit 0"
                ),
                "timeout": "3s",
            }
        )
        payload = response.json
        if not isinstance(payload, dict):
            return 0
        root = payload.get("root")
        if not isinstance(root, dict):
            return 0
        coverage = root.get("coverage")
        if not isinstance(coverage, dict):
            return 0
        documents = coverage.get("documents", 0)
        return int(documents) if isinstance(documents, int | float | str) else 0


async def search(query: str, config: RetrievalConfig | None = None) -> list[Hit]:
    """Search one variant of the index. Builds a short-lived engine per call."""
    return await SearchEngine(config or RetrievalConfig()).search(query)


def as_navigable(index: VespaSearchIndex) -> NavigableIndex:
    """Narrow the store to its navigation protocol.

    ``VespaSearchIndex`` is the shared base; only the DOCUMENT_PER_CHUNK
    implementation carries navigate/read/grep, and the protocol is
    runtime-checkable, so a schema built the wrong way fails here rather than at
    the first navigation call.
    """
    if not isinstance(index, NavigableIndex):
        raise TypeError(
            f"{type(index).__name__} does not support navigation; "
            "the schema must use IndexingMode.DOCUMENT_PER_CHUNK"
        )
    return index


def _hits(
    results: list[SearchResult],
    index: NavigableIndex | None,
    context: RetrievalContext,
) -> list[Hit]:
    return [_hit(result, index, context) for result in results]


def _hit(
    result: SearchResult,
    index: NavigableIndex | None,
    context: RetrievalContext,
) -> Hit:
    chunk = result.chunk
    metadata: dict[str, Any] = chunk.metadata or {}
    start, end = chunk.start_offset, chunk.end_offset
    navigation = (
        Navigation(
            index=index,
            source_id=chunk.source_id,
            start_offset=start,
            end_offset=end,
            context=context,
        )
        if index is not None and start is not None and end is not None
        else None
    )
    heading_path = metadata.get("heading_path") or []
    return Hit(
        chunk_id=chunk.id,
        score=result.score,
        # source_id is the page URL for every chunk this project writes, so a hit
        # always has somewhere to point even if the url metadata went missing.
        url=str(metadata.get("url") or chunk.source_id),
        anchor=metadata.get("anchor"),
        heading_path=tuple(str(part) for part in heading_path),
        page_title=str(metadata.get("page_title", "")),
        kind=str(metadata.get("kind", "")),
        locale=str(metadata.get("locale", "")),
        section_index=metadata.get("section_index"),
        snapshot=metadata.get("snapshot"),
        content_sha256=metadata.get("content_sha256"),
        content=chunk.content,
        source_id=chunk.source_id,
        start_offset=start,
        end_offset=end,
        navigation=navigation,
    )


async def get_chunk(chunk_id: str, config: RetrievalConfig) -> Hit | None:
    """Resolve an opaque chunk id back to a hit, for an agent that kept only the id."""
    index = as_navigable(get_index(config.index_variant))
    context = restrict_to(config.index_variant.schema_name)
    result = await index.get_chunk(chunk_id, context=context)
    return _hit(result, index, context) if result is not None else None


__all__ = [
    "CONTENT_PREVIEW_CHARS",
    "Hit",
    "Navigation",
    "SearchEngine",
    "SearchTrace",
    "get_chunk",
    "search",
]
