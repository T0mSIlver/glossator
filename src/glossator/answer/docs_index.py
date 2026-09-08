"""The slice of retrieval the answer layer depends on.

Strategies need search plus in-page navigation and nothing else. Stating that as
a protocol keeps the dependency one-way -- the answer layer does not reach into
``SearchEngine``'s embedder, index or Vespa context -- and lets a test drive a
whole strategy with a hand-written index and no network.
"""

from typing import Protocol

from mistralai.search.toolkit.search import GrepMode

from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import Hit


class PageReader(Protocol):
    """Navigation bound to one page: what `open`, `grep` and `read` are built on."""

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

    def navigation_at(
        self, source_id: str, start_offset: int = 0, end_offset: int = 0
    ) -> PageReader: ...

    async def get_chunk(self, chunk_id: str) -> Hit | None: ...


__all__ = ["DocsIndex", "PageReader"]
