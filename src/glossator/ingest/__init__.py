"""Corpus pages -> sections -> chunks -> the Vespa index."""

from glossator.ingest.chunker import (
    CorpusChunker,
    PageChunker,
    SectionChunker,
    build_chunker,
)
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
    "ingest_corpus",
    "parse_sections",
]
