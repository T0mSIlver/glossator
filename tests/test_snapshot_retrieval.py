import asyncio
from typing import Any

from mistralai.search.toolkit.document import ChunkType
from mistralai.search.toolkit.embedding import EmbeddingResult
from mistralai.search.toolkit.search import SearchResult, SearchResultChunk

from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.retriever import DocsRetriever


class FakeEmbedder:
    model_name = "fake"

    async def embed(self, texts: list[str], context: object = None) -> EmbeddingResult:
        del context
        return EmbeddingResult(embeddings=[[1.0, 0.0] for _ in texts], total_tokens=0)

    async def embed_query(self, text: str, context: object = None) -> list[float]:
        del text, context
        return [1.0, 0.0]


class TwoSnapshotIndex:
    def __init__(self) -> None:
        self.query: Any = None

    async def search(self, query: Any, context: object = None) -> list[SearchResult]:
        del context
        self.query = query
        snapshots = ("2026-06-01", "2026-06-15")
        selected = [date for date in snapshots if date in (query.extra_yql_filter or "")]
        return [
            SearchResult(
                chunk=SearchResultChunk(
                    id=f"chunk-{date}",
                    source_id=f"page:{date}",
                    locator="0:4",
                    chunk_type=ChunkType.CONTENT,
                    content="same page",
                    start_offset=0,
                    end_offset=4,
                    metadata={
                        "url": "https://docs.mistral.ai/page",
                        "snapshot": date,
                    },
                ),
                score=1.0,
            )
            for date in selected
        ]


def test_same_page_from_another_snapshot_cannot_leak_into_results() -> None:
    index = TwoSnapshotIndex()
    config = RetrievalConfig.shipped(variant="snap1024", snapshot="2026-06-01", rerank=False)
    retriever = DocsRetriever(index, FakeEmbedder(), config)  # type: ignore[arg-type]

    results = asyncio.run(retriever.retrieve("same page"))

    assert [result.chunk.metadata["snapshot"] for result in results] == ["2026-06-01"]
    assert index.query.extra_yql_filter == 'snapshot in ("2026-06-01")'
