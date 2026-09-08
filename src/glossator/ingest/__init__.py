"""Corpus pages -> sections -> chunks -> the Vespa index."""

from glossator.ingest.chunker import (
    CorpusChunker,
    PageChunker,
    SectionChunker,
    build_chunker,
)
from glossator.ingest.links import extract_links, page_links
from glossator.ingest.pipeline import IngestReport, build_pipeline, ingest_corpus
from glossator.ingest.sections import Section, parse_sections

__all__ = [
    "CorpusChunker",
    "IngestReport",
    "PageChunker",
    "Section",
    "SectionChunker",
    "build_chunker",
    "build_pipeline",
    "extract_links",
    "ingest_corpus",
    "page_links",
    "parse_sections",
]
