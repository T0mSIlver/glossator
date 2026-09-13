"""The corpus side: chunk id to page and section, rebuilt offline from the vendored corpus."""

from __future__ import annotations

import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import structlog
from mistralai.search.toolkit.common.text import sanitize_text
from mistralai.search.toolkit.document import compute_char_locator, compute_id

from glossator.index.variants import ChunkStrategy
from glossator.ingest.chunker import PageFacts, build_chunker
from glossator.ingest.pages import iter_page_paths, load_page

logger = structlog.get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ChunkFacts:
    """Where one chunk sits in the corpus."""

    url: str
    anchor: str | None
    heading_path: tuple[str, ...]

    @property
    def heading_line(self) -> str:
        return " > ".join(self.heading_path)


@dataclass(frozen=True, slots=True)
class ChunkIndex:
    """Every chunk id one chunking of one corpus produces, with its page and section."""

    facts: Mapping[str, ChunkFacts]
    chunking: ChunkStrategy

    def page(self, chunk_id: str) -> str | None:
        found = self.facts.get(chunk_id)
        return found.url if found else None

    def resolves(self, chunk_ids: Iterable[str]) -> int:
        return sum(chunk_id in self.facts for chunk_id in chunk_ids)


@cache
def chunk_index(corpus_dir: Path, chunking: ChunkStrategy) -> ChunkIndex:
    """The chunk map for one corpus directory, built once per process.

    The body is sanitized exactly as the extractor sanitizes it before chunking,
    because the offsets the ids are built from index into the sanitized body.
    """
    started = time.perf_counter()
    chunker = build_chunker(chunking)
    facts: dict[str, ChunkFacts] = {}
    for path in iter_page_paths(corpus_dir):
        page = load_page(path)
        body = sanitize_text(page.body)
        page_facts = PageFacts(url=page.url, title=page.title, kind=page.kind, locale=page.locale)
        for spec in chunker.plan(body, page_facts):
            chunk_id = compute_id(page.url, compute_char_locator(spec.start, spec.end))
            facts[chunk_id] = ChunkFacts(
                url=page.url,
                anchor=spec.metadata.anchor,
                heading_path=tuple(spec.metadata.heading_path),
            )
    logger.info(
        "Built the chunk map",
        corpus=str(corpus_dir),
        chunking=str(chunking),
        chunks=len(facts),
        seconds=round(time.perf_counter() - started, 2),
    )
    return ChunkIndex(facts=facts, chunking=chunking)


@cache
def _pages_by_url(corpus_dir: Path) -> Mapping[str, Path]:
    return {load_page(path).url: path for path in iter_page_paths(corpus_dir)}


def gold_section_text(
    corpus_dir: Path, chunking: ChunkStrategy, url: str, anchor: str | None
) -> str:
    """The chunk text the dataset points at, for a judge that has to read it.

    A gold source with no anchor names the whole page, so the whole page body
    comes back; the anchored case returns the chunks that carry that anchor, in
    reading order.
    """
    path = _pages_by_url(corpus_dir).get(url)
    if path is None:
        return ""
    page = load_page(path)
    body = sanitize_text(page.body)
    if anchor is None:
        return body
    page_facts = PageFacts(url=page.url, title=page.title, kind=page.kind, locale=page.locale)
    parts = [
        body[spec.start : spec.end]
        for spec in build_chunker(chunking).plan(body, page_facts)
        if spec.metadata.anchor == anchor
    ]
    return "\n\n".join(parts) or body
