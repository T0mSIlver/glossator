"""What the engine does to a result set before it returns it.

The floors and the footing gate sit between Vespa and the caller, so they are
exercised with a retriever double: no index, no embedding call, and the arithmetic
is the whole subject.
"""

import asyncio
from pathlib import Path
from typing import Any

from mistralai.search.toolkit.document import ChunkType
from mistralai.search.toolkit.search import SearchResult, SearchResultChunk

from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import Hit, SearchEngine, SearchTrace

PAGE = "https://docs.mistral.ai/capabilities/function-calling"
FIXTURE_CORPUS = Path(__file__).parent / "fixtures" / "corpus"


class StubRetriever:
    """Fixed results and fixed similarities, with a count of what was asked."""

    def __init__(self, similarities: dict[str, float]) -> None:
        self.similarities = similarities
        self.embed_calls = 0
        self.similarity_calls = 0

    async def retrieve(self, query: str, **kwargs: Any) -> list[SearchResult]:
        return [
            SearchResult(
                chunk=SearchResultChunk(
                    id=chunk_id,
                    source_id=PAGE,
                    locator=f"chunk:{rank}",
                    start_offset=rank,
                    end_offset=rank + 1,
                    chunk_type=ChunkType.CONTENT,
                    content=f"body {rank}",
                    metadata={"url": PAGE, "anchor": f"anchor-{rank}", "page_title": "Tools"},
                ),
                score=10.0 - rank,
            )
            for rank, chunk_id in enumerate(self.similarities)
        ]

    async def embed_query(self, query: str, context: Any = None) -> list[float]:
        self.embed_calls += 1
        return [0.1, 0.2]

    async def cosine_similarities(
        self, embedding: list[float], chunk_ids: list[str], context: Any = None
    ) -> dict[str, float]:
        self.similarity_calls += 1
        return {chunk_id: self.similarities[chunk_id] for chunk_id in chunk_ids}


def engine(config: RetrievalConfig, similarities: dict[str, float]) -> SearchEngine:
    built = SearchEngine.__new__(SearchEngine)
    built.config = config
    built.navigation_index = None  # type: ignore[assignment]
    built.context = None  # type: ignore[assignment]
    built.retriever = StubRetriever(similarities)  # type: ignore[assignment]
    built._llm = None
    built._recorder = None
    built.vocabulary = None
    return built


SIMILARITIES = {"a": 0.85, "b": 0.80, "c": 0.72, "d": 0.55}


def search(config: RetrievalConfig, **kwargs: Any) -> tuple[list[Hit], SearchTrace]:
    built = engine(config, SIMILARITIES)
    return asyncio.run(built.search_with_trace("how do I call a tool?", **kwargs))


def test_without_a_floor_nothing_is_measured_or_dropped() -> None:
    built = engine(RetrievalConfig(top_k=10), SIMILARITIES)
    hits, trace = asyncio.run(built.search_with_trace("how do I call a tool?"))
    assert len(hits) == 4
    assert trace.best_similarity is None
    assert all(hit.similarity is None for hit in hits)
    retriever: Any = built.retriever
    assert retriever.similarity_calls == 0
    assert retriever.embed_calls == 0


def test_an_absolute_floor_drops_what_sits_below_it() -> None:
    hits, trace = search(RetrievalConfig(top_k=10, similarity_floor=0.75))
    assert [hit.chunk_id for hit in hits] == ["a", "b"]
    assert trace.dropped_by_floor == 2
    assert trace.considered == 4 and trace.kept == 2
    assert trace.best_similarity == 0.85


def test_a_margin_drops_what_falls_too_far_behind_the_best_hit() -> None:
    hits, trace = search(RetrievalConfig(top_k=10, similarity_margin=0.1))
    assert [hit.chunk_id for hit in hits] == ["a", "b"]
    assert trace.dropped_by_margin == 2
    assert trace.dropped_by_floor == 0


def test_the_two_gates_are_counted_separately() -> None:
    _hits, trace = search(RetrievalConfig(top_k=10, similarity_floor=0.6, similarity_margin=0.1))
    assert trace.dropped_by_floor == 1
    assert trace.dropped_by_margin == 1


def test_every_hit_carries_the_similarity_it_was_judged_on() -> None:
    hits, _trace = search(RetrievalConfig(top_k=10, similarity_floor=0.5))
    assert [hit.similarity for hit in hits] == [0.85, 0.80, 0.72, 0.55]


def test_a_hit_whose_similarity_could_not_be_read_is_kept() -> None:
    """The floor discards what is measurably far away, not what is unmeasured."""
    built = engine(RetrievalConfig(top_k=10, similarity_floor=0.75), SIMILARITIES)
    retriever: Any = built.retriever
    retriever.cosine_similarities = _partial_similarities
    hits, trace = asyncio.run(built.search_with_trace("how do I call a tool?"))
    assert [hit.chunk_id for hit in hits] == ["a", "c", "d"]
    assert trace.dropped_by_floor == 1


async def _partial_similarities(
    embedding: list[float], chunk_ids: list[str], context: Any = None
) -> dict[str, float]:
    return {"a": 0.85, "b": 0.10}


def test_a_supplied_embedding_saves_the_call_without_turning_the_floors_on() -> None:
    built = engine(RetrievalConfig(top_k=10), SIMILARITIES)
    hits, trace = asyncio.run(
        built.search_with_trace("how do I call a tool?", embedding=[0.1, 0.2])
    )
    retriever: Any = built.retriever
    assert retriever.embed_calls == 0
    assert retriever.similarity_calls == 0
    assert len(hits) == 4 and trace.dropped_by_floor == 0


def test_a_supplied_embedding_is_used_for_the_floors_rather_than_a_fresh_one() -> None:
    built = engine(RetrievalConfig(top_k=10, similarity_floor=0.75), SIMILARITIES)
    asyncio.run(built.search_with_trace("how do I call a tool?", embedding=[0.1, 0.2]))
    retriever: Any = built.retriever
    assert retriever.embed_calls == 0
    assert retriever.similarity_calls == 1


def test_the_trace_reports_footing_when_the_vocabulary_is_loaded() -> None:
    from glossator.retrieval.vocabulary import corpus_vocabulary

    built = engine(RetrievalConfig(top_k=10), SIMILARITIES)
    built.vocabulary = corpus_vocabulary(FIXTURE_CORPUS)
    _hits, trace = asyncio.run(built.search_with_trace("how do I call a tool?"))
    assert trace.lexical_footing is True

    _hits, junk = asyncio.run(built.search_with_trace("what causes feline hyperthyroidism"))
    assert junk.lexical_footing is False
    assert "hyperthyroidism" in junk.missing_terms


def test_footing_is_unknown_when_the_check_is_off() -> None:
    _hits, trace = search(RetrievalConfig(top_k=10))
    assert trace.lexical_footing is None
    assert trace.missing_terms == ()
