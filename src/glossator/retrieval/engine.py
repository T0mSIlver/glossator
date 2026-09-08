"""Search: a query and a configuration in, citable hits out.

A ``Hit`` is what the rest of the product quotes and cites, so it carries the
citation target (url plus anchor), the span it occupies in the page body, and a
handle on the index's navigation operations -- reading around a hit within its
own page is how the answer layer gets context without a second global search.
"""

import os
from dataclasses import dataclass, field
from typing import Any

import structlog
from mistralai.client import Mistral
from mistralai.search.toolkit.context import RetrievalContext
from mistralai.search.toolkit.embedding import Embedder, MistralEmbedder
from mistralai.search.toolkit.plugins.vespa.search.index import VespaSearchIndex
from mistralai.search.toolkit.search import (
    GrepMode,
    NavigableIndex,
    NavigationDirection,
    SearchResult,
)

from glossator.index import get_index
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.context import restrict_to
from glossator.retrieval.retriever import DocsRetriever

logger = structlog.get_logger(__name__)

CONTENT_PREVIEW_CHARS = 240


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

    @property
    def citation_url(self) -> str:
        """The URL a reader should follow: the page, deep-linked when possible."""
        return f"{self.url}#{self.anchor}" if self.anchor else self.url

    @property
    def heading_line(self) -> str:
        return " > ".join(self.heading_path)

    def preview(self, chars: int = CONTENT_PREVIEW_CHARS) -> str:
        collapsed = " ".join(self.content.split())
        return collapsed if len(collapsed) <= chars else f"{collapsed[:chars]}..."


class SearchEngine:
    """One configured view of the index, reusable across queries."""

    def __init__(self, config: RetrievalConfig, embedder: Embedder | None = None) -> None:
        self.config = config
        self.index: VespaSearchIndex = get_index(config.index_variant)
        self.navigation_index = _as_navigable(self.index)
        self.context = restrict_to(config.index_variant.schema_name)
        self.embedder = embedder or MistralEmbedder(
            client=Mistral(api_key=_api_key()),
            model_name=config.index_variant.embedding_model_name,
        )
        self.retriever = DocsRetriever(self.index, self.embedder, config)

    async def search(
        self,
        query: str,
        exclude_ids: set[str] | None = None,
        top_k: int | None = None,
    ) -> list[Hit]:
        """Hits for a query. ``top_k`` overrides the configured depth for one call."""
        results = await self.retriever.retrieve(
            query, top_k=top_k or self.config.top_k, exclude_ids=exclude_ids
        )
        logger.info("Search", variant=self.config.variant, query=query, hits=len(results))
        return _hits(results, self.navigation_index, self.context)

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


async def search(query: str, config: RetrievalConfig | None = None) -> list[Hit]:
    """Search one variant of the index. Builds a short-lived engine per call."""
    return await SearchEngine(config or RetrievalConfig()).search(query)


def _api_key() -> str:
    key = os.environ.get("MISTRAL_API_KEY", "")
    if not key:
        raise RuntimeError("MISTRAL_API_KEY is not set. Check your .env file.")
    return key


def _as_navigable(index: VespaSearchIndex) -> NavigableIndex:
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
        content=chunk.content,
        source_id=chunk.source_id,
        start_offset=start,
        end_offset=end,
        navigation=navigation,
    )


async def get_chunk(chunk_id: str, config: RetrievalConfig) -> Hit | None:
    """Resolve an opaque chunk id back to a hit, for an agent that kept only the id."""
    index = _as_navigable(get_index(config.index_variant))
    context = restrict_to(config.index_variant.schema_name)
    result = await index.get_chunk(chunk_id, context=context)
    return _hit(result, index, context) if result is not None else None


__all__ = [
    "CONTENT_PREVIEW_CHARS",
    "Hit",
    "Navigation",
    "SearchEngine",
    "get_chunk",
    "search",
]
