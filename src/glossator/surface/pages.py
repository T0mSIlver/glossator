"""What the tools know about the vendored pages without touching the index:
sizes, section keys, citation links, and which pages sit under a path."""

from dataclasses import dataclass
from pathlib import Path

from glossator.answer.context import chunk_body
from glossator.citing import SectionKey, citation_link, page_search_text, section_keys
from glossator.doc_paths import SITE
from glossator.ingest.pages import iter_page_paths, load_page
from glossator.ingest.sections import parse_sections
from glossator.retrieval.engine import Hit

LARGE_PAGE_CHARS = 32_000
"""A page this long is read by section: a hit on it says so, and read_page
without a section returns the first part with the remaining sections named."""


@dataclass(frozen=True, slots=True)
class Page:
    size: int
    title: str
    kind: str
    keys: list[SectionKey]
    """One entry per section, index-aligned with the chunker's ``section_index``."""
    haystack: str
    """The page text as ``citing.page_search_text`` renders it, for phrase uniqueness."""


class PageCatalog:
    """The vendored pages by URL, loaded once at startup."""

    def __init__(self, pages: dict[str, Page]) -> None:
        self.pages = pages
        self.sizes: dict[str, int] = {url: page.size for url, page in pages.items()}

    @classmethod
    def load(cls, corpus_dir: Path) -> "PageCatalog":
        pages: dict[str, Page] = {}
        if not corpus_dir.is_dir():
            return cls(pages)
        for path in iter_page_paths(corpus_dir):
            page = load_page(path)
            sections = parse_sections(page.body, page_title=page.title)
            pages[page.url] = Page(
                size=len(page.body),
                title=page.title,
                kind=page.kind,
                keys=section_keys(sections),
                haystack=page_search_text(page.body),
            )
        return cls(pages)

    def is_large(self, url: str) -> bool:
        return self.sizes.get(url, 0) >= LARGE_PAGE_CHARS

    def _section_info(self, hit: Hit) -> SectionKey | None:
        page = self.pages.get(hit.url)
        if page is None or hit.section_index is None or hit.section_index >= len(page.keys):
            return None
        return page.keys[hit.section_index]

    def section_key(self, hit: Hit) -> str:
        """The key the tools name this chunk's section by (D-047): from the vendored
        corpus when the page is known, else the anchor or the heading text."""
        info = self._section_info(hit)
        if info is not None:
            return info.key
        if hit.anchor:
            return hit.anchor
        return hit.heading_path[-1] if hit.heading_path else "top"

    def cite(self, hit: Hit) -> str:
        """The link to cite this chunk by: the anchor link, plus a text fragment when
        the chunk sits more than a screen below where that link lands (D-047)."""
        info = self._section_info(hit)
        page = self.pages.get(hit.url)
        if info is None or page is None or hit.start_offset is None:
            return hit.citation_url
        return citation_link(
            hit.url,
            info.anchor,
            landing=info.anchor_start,
            text_start=hit.start_offset,
            text=chunk_body(hit),
            haystack=page.haystack,
        )

    def section_header(self, hit: Hit, n: int | None = None) -> list[str]:
        """A numbered search hit line, or the ``## section:`` line a read prints."""
        key = self.section_key(hit)
        first = f"[{n}] {hit.url} | section: {key}" if n is not None else f"## section: {key}"
        lines = [first]
        if hit.heading_line:
            lines.append(f"    {hit.heading_line}")
        return lines

    def under(self, prefix: str) -> list[tuple[str, str]]:
        """The (url, title) of every page at or below ``prefix``, sorted by URL."""
        return sorted(
            (url, page.title)
            for url, page in self.pages.items()
            if url == prefix or url.startswith(prefix + "/")
        )

    def nearest_parent_with_pages(self, prefix: str) -> str | None:
        """The longest ancestor path that has pages, never the site root: a listing
        of every page is not an answer to "does this page exist"."""
        parent = prefix
        while parent.startswith(SITE + "/"):
            parent = parent.rsplit("/", 1)[0]
            if parent == SITE:
                return None
            if self.under(parent):
                return parent
        return None


__all__ = ["LARGE_PAGE_CHARS", "Page", "PageCatalog"]
