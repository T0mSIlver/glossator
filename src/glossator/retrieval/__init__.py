"""Retrieval over one variant of the Vespa index."""

from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import Hit, Navigation, SearchEngine, get_chunk, search
from glossator.retrieval.retriever import DocsRetriever

__all__ = [
    "DocsRetriever",
    "Hit",
    "Navigation",
    "RetrievalConfig",
    "SearchEngine",
    "get_chunk",
    "search",
]
