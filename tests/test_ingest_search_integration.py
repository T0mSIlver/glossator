"""The fixture corpus, ingested and searched end to end.

Everything before this point can be right in isolation and still not compose: the
chunker's metadata has to survive the store's metadata-to-root-field promotion, the
query builder has to accept the filter the config produces, and the hit has to come
back carrying the url and anchor a citation needs.

Needs Vespa (`make setup-vespa`) and `MISTRAL_API_KEY`; skips without either, so
`make test` stays runnable with nothing started. It embeds the fixture corpus,
which costs a fraction of a cent per run.

All of the I/O happens in one `asyncio.run`, including the navigation call: the
Vespa client binds its connections to the loop that opened it, so a hit obtained in
one loop cannot be navigated from another.
"""

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path

import pytest
from dotenv import load_dotenv
from mistralai.search.toolkit.search import VectorSearchQuery

from glossator.index import get_index, get_variant
from glossator.ingest.pipeline import ingest_corpus
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.context import restrict_to
from glossator.retrieval.engine import Hit, SearchEngine

load_dotenv(override=True)

VARIANT = get_variant("sec128")

# One query per fact the pipeline is supposed to preserve: a question whose wording
# does not match the page's, a cross-page question, and a bare identifier that only
# a lexical match can find.
STREAMING_QUERY = "how do I stream a chat completion"
CAPABILITY_QUERY = "which models support function calling"
IDENTIFIER_QUERY = "tool_call_id"
QUERIES = [STREAMING_QUERY, CAPABILITY_QUERY, IDENTIFIER_QUERY]

pytestmark = pytest.mark.skipif(
    not os.environ.get("MISTRAL_API_KEY"),
    reason="MISTRAL_API_KEY is not set; the integration test embeds real text",
)


@dataclass(frozen=True, slots=True)
class Indexed:
    """Everything the assertions need, gathered in one event loop."""

    chunks: int
    reingested_chunks: int
    hits: dict[str, list[Hit]]
    filtered: list[Hit]
    context: list[Hit]
    context_anchor: Hit


async def _skip_unless_vespa_ready() -> None:
    index = get_index(VARIANT)
    # A non-zero vector: cosine similarity against an all-zero query is NaN, which
    # Vespa serializes as a null relevance and the toolkit then fails to parse.
    probe = VectorSearchQuery(
        query="probe", embedding=[0.1] * VARIANT.embedding_dimensions, top_k=1
    )
    try:
        await index.search(probe, context=restrict_to(VARIANT.schema_name))
    except Exception as exc:  # noqa: BLE001 - any failure here means the backend is not ready
        pytest.skip(
            f"Vespa not ready for schema {VARIANT.schema_name!r} ({exc}); run `make setup-vespa` first"
        )


async def _ingest_and_search(corpus_dir: Path) -> Indexed:
    await _skip_unless_vespa_ready()

    report = await ingest_corpus(corpus_dir, VARIANT, concurrency=4)
    assert not report.failures, report.failures

    engine = SearchEngine(RetrievalConfig(variant=VARIANT.name, top_k=5))
    hits = {query: await engine.search(query) for query in QUERIES}

    filtered_engine = SearchEngine(
        RetrievalConfig(variant=VARIANT.name, top_k=5, kinds=frozenset({"api"}))
    )
    filtered = await filtered_engine.search("request body fields")

    anchor = hits[STREAMING_QUERY][0]
    assert anchor.navigation is not None
    context = await anchor.navigation.around(window=1)

    # Re-ingesting must replace rather than duplicate: chunk ids derive from the
    # page URL and the chunk's span, both unchanged.
    again = await ingest_corpus(corpus_dir, VARIANT, concurrency=4)

    return Indexed(
        chunks=report.chunks,
        reingested_chunks=again.chunks,
        hits=hits,
        filtered=filtered,
        context=context,
        context_anchor=anchor,
    )


@pytest.fixture(scope="module")
def indexed(corpus_dir: Path) -> Indexed:
    return asyncio.run(_ingest_and_search(corpus_dir))


def test_ingest_writes_a_chunk_per_section(indexed: Indexed) -> None:
    # Eight fixture pages, five to ten sections each.
    assert indexed.chunks > 30


def test_reingesting_is_idempotent(indexed: Indexed) -> None:
    assert indexed.reingested_chunks == indexed.chunks


def test_every_query_returns_scored_hits(indexed: Indexed) -> None:
    for query, results in indexed.hits.items():
        assert results, query
        assert all(hit.score > 0 for hit in results), query


def test_hits_carry_a_citation_target(indexed: Indexed) -> None:
    """The metadata the chunker stamped survives the round trip through Vespa."""
    results = indexed.hits[STREAMING_QUERY]
    for hit in results:
        assert hit.url.startswith("https://docs.mistral.ai/")
        assert hit.page_title
        assert hit.heading_path and hit.heading_path[0] == hit.page_title
        assert hit.locale == "en"
        assert hit.start_offset is not None and hit.end_offset is not None
    assert any(hit.anchor for hit in results)
    assert any("#" in hit.citation_url for hit in results)


def test_a_streaming_question_finds_the_streaming_section(indexed: Indexed) -> None:
    hits = indexed.hits[STREAMING_QUERY]
    assert any("stream" in hit.heading_line.lower() for hit in hits)


def test_a_capability_question_reaches_the_capability_matrix(indexed: Indexed) -> None:
    hits = indexed.hits[CAPABILITY_QUERY]
    assert any(
        "capability-matrix" in hit.url or "function-calling" in hit.url for hit in hits
    )


def test_an_identifier_query_finds_the_page_that_names_it(indexed: Indexed) -> None:
    """The lexical half of hybrid search: no paraphrase reaches a bare identifier."""
    hits = indexed.hits[IDENTIFIER_QUERY]
    assert any("tool_call_id" in hit.content for hit in hits)


def test_a_kind_filter_restricts_the_result_set(indexed: Indexed) -> None:
    assert indexed.filtered
    assert {hit.kind for hit in indexed.filtered} == {"api"}


def test_navigation_reads_around_a_hit(indexed: Indexed) -> None:
    """A hit exposes its neighbours, which is how the answer layer widens context."""
    assert any(
        hit.chunk_id == indexed.context_anchor.chunk_id for hit in indexed.context
    )
    assert all(
        hit.source_id == indexed.context_anchor.source_id for hit in indexed.context
    )
    offsets = [hit.start_offset for hit in indexed.context]
    assert offsets == sorted(offsets)
