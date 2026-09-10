"""Retrieval over one variant of the Vespa index."""

from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import (
    Hit,
    Navigation,
    SearchEngine,
    SearchTrace,
    search,
)
from glossator.retrieval.probe import EmbeddingProbeError, ProbeResult, probe_embedding
from glossator.retrieval.retriever import DocsRetriever
from glossator.retrieval.vocabulary import Vocabulary, load_vocabulary

__all__ = [
    "DocsRetriever",
    "EmbeddingProbeError",
    "Hit",
    "Navigation",
    "ProbeResult",
    "RetrievalConfig",
    "SearchEngine",
    "SearchTrace",
    "Vocabulary",
    "load_vocabulary",
    "probe_embedding",
    "search",
]
