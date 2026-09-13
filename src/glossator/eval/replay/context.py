"""Rebuilding the sources a recorded answer's model saw, from the vendored corpus."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from mistralai.search.toolkit.common.text import sanitize_text
from mistralai.search.toolkit.document import compute_char_locator, compute_id

from glossator.answer.citations import Trace
from glossator.answer.context import AssembledContext, Source, SourcePiece, _merged
from glossator.eval.answer_eval.judge import source_texts
from glossator.index.variants import ChunkStrategy
from glossator.ingest.chunker import PageFacts, build_chunker
from glossator.ingest.pages import iter_page_paths, load_page
from glossator.retrieval.engine import Hit


@dataclass(frozen=True, slots=True)
class _ChunkText:
    url: str
    anchor: str | None
    page_title: str
    heading_path: tuple[str, ...]
    content: str
    start: int
    end: int


@cache
def _chunk_texts(corpus_dir: Path, chunking: ChunkStrategy) -> Mapping[str, _ChunkText]:
    """Every chunk one chunking of the corpus produces, with its stored content.

    Same walk as `glossator.eval.failures.corpus.chunk_index`, keeping the text: the
    verifier needs each merged source's chunk boundaries to name the chunk a
    quote came from, and the run's trace stores chunk ids, not offsets.
    """
    chunker = build_chunker(chunking)
    texts: dict[str, _ChunkText] = {}
    for path in iter_page_paths(corpus_dir):
        page = load_page(path)
        body = sanitize_text(page.body)
        page_facts = PageFacts(url=page.url, title=page.title, kind=page.kind, locale=page.locale)
        for spec in chunker.plan(body, page_facts):
            chunk_id = compute_id(page.url, compute_char_locator(spec.start, spec.end))
            texts[chunk_id] = _ChunkText(
                url=page.url,
                anchor=spec.metadata.anchor,
                page_title=page.title,
                heading_path=tuple(spec.metadata.heading_path),
                content=spec.content,
                start=spec.start,
                end=spec.end,
            )
    return texts


def _split_url(citation_url: str) -> tuple[str, str | None]:
    url, _, anchor = citation_url.partition("#")
    return url, anchor or None


def rebuild_context(
    trace: Trace, *, corpus_dir: Path, chunking: ChunkStrategy
) -> tuple[AssembledContext, list[str]]:
    """The `AssembledContext` behind a recorded trace, and the notes of what
    could not be rebuilt exactly.

    The passage text comes from the recorded context, verbatim. The chunk
    boundaries inside a merged passage come from re-chunking the vendored
    corpus and stitching the source's chunks the way assembly did; when the
    stitched text is not the recorded passage, the source keeps one piece for
    its first chunk and the note says so.
    """
    passages = source_texts(trace)
    texts = _chunk_texts(corpus_dir, chunking)
    notes: list[str] = []
    sources: list[Source] = []
    for traced in trace.sources:
        passage = passages.get(traced.n)
        if passage is None:
            notes.append(f"source {traced.n}: passage not found in the recorded context")
            continue
        _heading, _, content = passage.partition("\n")
        url, anchor = _split_url(traced.citation_url)
        hits = [_hit(chunk_id, texts) for chunk_id in traced.chunk_ids]
        pieces: tuple[SourcePiece, ...] | None = None
        page_title = ""
        if all(hit is not None for hit in hits):
            stitched, stitched_pieces = _merged([hit for hit in hits if hit is not None])
            page_title = next(hit.page_title for hit in hits if hit is not None)
            # `source_texts` right-strips each passage; the stitched text keeps
            # the trailing newlines assembly wrote, so it is the exact content.
            if stitched.rstrip() == content.rstrip():
                content = stitched
                pieces = stitched_pieces
            else:
                notes.append(f"source {traced.n}: stitched chunks differ from the recorded passage")
        else:
            notes.append(f"source {traced.n}: a chunk id is not in the corpus chunking")
        if pieces is None:
            pieces = (
                SourcePiece(
                    chunk_id=traced.chunk_ids[0] if traced.chunk_ids else "",
                    score=traced.score,
                    start_offset=None,
                    end_offset=None,
                    text_start=0,
                    text_end=len(content),
                ),
            )
        sources.append(
            Source(
                n=traced.n,
                url=url,
                anchor=anchor,
                page_title=page_title,
                heading_path=tuple(traced.heading_path),
                source_id=url,
                content=content,
                pieces=pieces,
                score=traced.score,
                tokens=traced.tokens,
            )
        )
    return (
        AssembledContext(
            text=trace.context_text,
            sources=tuple(sources),
            tokens=trace.context_tokens,
            dropped_chunk_ids=tuple(trace.dropped_chunk_ids),
        ),
        notes,
    )


def _hit(chunk_id: str, texts: Mapping[str, _ChunkText]) -> Hit | None:
    chunk = texts.get(chunk_id)
    if chunk is None:
        return None
    return Hit(
        chunk_id=chunk_id,
        score=0.0,
        url=chunk.url,
        anchor=chunk.anchor,
        heading_path=chunk.heading_path,
        page_title=chunk.page_title,
        kind="",
        locale="",
        section_index=None,
        content=chunk.content,
        source_id=chunk.url,
        start_offset=chunk.start,
        end_offset=chunk.end,
    )
