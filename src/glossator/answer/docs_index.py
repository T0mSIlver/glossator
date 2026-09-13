"""Protocols for the search and page-reading operations used by answer strategies."""

from typing import Protocol

from mistralai.search.toolkit.search import GrepMode

from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import Hit, SearchTrace


class PageReader(Protocol):
    """Page operations available to the internal answer search loop."""

    async def around(self, window: int = 2) -> list[Hit]: ...

    async def read(
        self, start: int | None = None, end: int | None = None, top_k: int = 20
    ) -> list[Hit]: ...

    async def grep(
        self, pattern: str, mode: GrepMode = GrepMode.PHRASE, top_k: int = 5
    ) -> list[Hit]: ...


class DocsIndex(Protocol):
    """A searchable, navigable view of the documentation."""

    config: RetrievalConfig

    async def search(
        self,
        query: str,
        exclude_ids: set[str] | None = None,
        top_k: int | None = None,
    ) -> list[Hit]: ...

    async def search_with_trace(
        self,
        query: str,
        exclude_ids: set[str] | None = None,
        top_k: int | None = None,
    ) -> tuple[list[Hit], SearchTrace]: ...

    def navigation_at(
        self, source_id: str, start_offset: int = 0, end_offset: int = 0
    ) -> PageReader: ...

    async def get_chunk(self, chunk_id: str) -> Hit | None: ...


__all__ = ["DocsIndex", "PageReader"]
