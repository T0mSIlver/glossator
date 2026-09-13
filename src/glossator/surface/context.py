"""What one tool call runs against."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from glossator.retrieval.engine import SearchEngine
from glossator.surface.errors import busy
from glossator.surface.pages import PageCatalog


@dataclass(frozen=True, slots=True)
class Surface:
    """The engine, the page catalog, the admission gate, the enabled tools and
    the per-call budgets. The MCP entrypoint builds one per call from its module
    attributes, so a swapped engine or a lowered budget applies to the next call."""

    engine: SearchEngine
    pages: PageCatalog
    admission: asyncio.Semaphore
    admission_slots: int
    enabled: frozenset[str]
    read_max_chars: int
    history_max_chars: int
    snapshot_manifest: Path

    @asynccontextmanager
    async def admitted(self) -> AsyncIterator[None]:
        """A slot on the index, or E_BUSY at once when every slot is taken."""
        if self.admission.locked():
            raise busy(self.admission_slots)
        await self.admission.acquire()
        try:
            yield
        finally:
            self.admission.release()


__all__ = ["Surface"]
