"""MCP tool, resource, response, and error-contract tests."""

import asyncio
import dataclasses
import importlib
import json
from typing import Any

import pytest
from fastmcp.exceptions import ToolError
from mistralai.search.toolkit.retrieval.errors import RetrieverException
from mistralai.search.toolkit.search.errors import SourceNotFoundError

from glossator.answer.citations import Answer, Citation, Trace, TracedSource
from glossator.answer.llm import TokenUsage
from glossator.retrieval.engine import Hit, SearchTrace

TOOLS = {"search", "open", "navigate", "read", "grep", "ask"}


@pytest.fixture
def mcp_server(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> Any:
    """Import `entrypoints.mcp_server` offline, with a placeholder key and dotenv disabled.

    The corpus directory points at the test fixture so the resources read real
    pages without the vendored corpus being present.
    """
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key-not-used")
    monkeypatch.setenv("GLOSSATOR_CORPUS_DIR", "tests/fixtures/corpus")

    import entrypoints.mcp_server as module

    return importlib.reload(module)


def _hit(chunk_id: str, content: str, *, anchor: str | None = "a-section") -> Hit:
    return Hit(
        chunk_id=chunk_id,
        score=0.5,
        url="https://docs.mistral.ai/page",
        anchor=anchor,
        heading_path=("Page", "A section"),
        page_title="Page",
        kind="doc",
        locale="en",
        section_index=1,
        content=content,
        source_id="https://docs.mistral.ai/page",
        start_offset=10,
        end_offset=20,
    )


class FakeNavigation:
    def __init__(self, hits: list[Hit], *, missing: bool = False) -> None:
        self.hits = hits
        self.missing = missing

    def _require_page(self) -> None:
        if self.missing:
            raise SourceNotFoundError("https://docs.mistral.ai/nope")

    async def around(self, window: int = 2) -> list[Hit]:
        self._require_page()
        return self.hits

    async def next(self, top_k: int = 1) -> list[Hit]:
        self._require_page()
        return self.hits[:top_k]

    async def previous(self, top_k: int = 1) -> list[Hit]:
        self._require_page()
        return []

    async def read(
        self, start: int | None = None, end: int | None = None, top_k: int = 20
    ) -> list[Hit]:
        self._require_page()
        return self.hits[:top_k]

    async def grep(self, pattern: str, mode: Any = None, top_k: int = 5) -> list[Hit]:
        self._require_page()
        return self.hits[:top_k]


class FakeEngine:
    """One page, two chunks; records what the tools forwarded."""

    def __init__(
        self,
        hits: list[Hit] | None = None,
        empty: bool = False,
        missing_page: bool = False,
    ) -> None:
        self.hits = hits if hits is not None else [_hit("c1", "alpha content"), _hit("c2", "beta")]
        self.empty = empty
        self.missing_page = missing_page
        self.search_calls: list[dict[str, Any]] = []

    async def search(
        self,
        query: str,
        exclude_ids: set[str] | None = None,
        top_k: int | None = None,
        kinds: frozenset[str] | None = None,
        locales: frozenset[str] | None = None,
    ) -> list[Hit]:
        self.search_calls.append(
            {"query": query, "exclude_ids": exclude_ids, "top_k": top_k, "kinds": kinds}
        )
        return [] if self.empty else self.hits[: top_k or 5]

    async def search_with_trace(
        self,
        query: str,
        exclude_ids: set[str] | None = None,
        top_k: int | None = None,
        kinds: frozenset[str] | None = None,
        locales: frozenset[str] | None = None,
    ) -> tuple[list[Hit], SearchTrace]:
        hits = await self.search(query, exclude_ids, top_k, kinds, locales)
        return hits, SearchTrace(
            query=query,
            variant="sec1024",
            considered=len(hits),
            kept=len(hits),
            latency_ms=1.0,
        )

    async def get_chunk(self, chunk_id: str) -> Hit | None:
        for hit in self.hits:
            if hit.chunk_id == chunk_id:
                anchor = _hit(chunk_id, hit.content)
                return dataclasses.replace(
                    anchor,
                    navigation=FakeNavigation(self.hits),  # type: ignore[arg-type]
                )
        return None

    def navigation_at(self, source_id: str, start: int = 0, end: int = 0) -> FakeNavigation:
        return FakeNavigation([] if self.empty else self.hits, missing=self.missing_page)

    async def document_count(self) -> int:
        return 4430


def _call(server: Any, name: str, arguments: dict[str, Any]) -> str:
    result = asyncio.run(server.mcp.call_tool(name, arguments))
    return str(result.content[0].text)


def _call_error(server: Any, name: str, arguments: dict[str, Any]) -> str:
    with pytest.raises(ToolError) as excinfo:
        asyncio.run(server.mcp.call_tool(name, arguments))
    return str(excinfo.value)


def test_the_tool_set_is_exactly_the_six_read_tools(mcp_server: Any) -> None:
    tools = asyncio.run(mcp_server.mcp.list_tools())

    assert {tool.name for tool in tools} == TOOLS
    # No write tool ever ships: the corpus is vendored and hash-checked (D-026).
    assert not {"ingest", "delete", "index"} & {tool.name for tool in tools}


def test_descriptions_are_bounded_with_a_complete_first_line(mcp_server: Any) -> None:
    tools = asyncio.run(mcp_server.mcp.list_tools())

    for tool in tools:
        words = len(tool.description.split())
        first_line = tool.description.splitlines()[0]
        assert words < 120, f"{tool.name}: {words} words"
        assert len(first_line) < 80, f"{tool.name}: first line {len(first_line)} chars"
        assert first_line.rstrip().endswith((".", "!", "?")), f"{tool.name}: not a clause"
        lowered = tool.description.lower()
        assert "use when" in lowered and "do not use" in lowered, tool.name
        assert "start with" in lowered, tool.name


def test_every_parameter_carries_a_description(mcp_server: Any) -> None:
    tools = asyncio.run(mcp_server.mcp.list_tools())

    for tool in tools:
        for param, spec in tool.parameters["properties"].items():
            assert spec.get("description"), f"{tool.name}.{param} has no description"


def test_instructions_name_the_flow_the_guide_and_the_sin(mcp_server: Any) -> None:
    instructions = mcp_server.mcp.instructions

    assert "Start with search" in instructions
    assert "glossator://guide" in instructions
    assert "never fabricate documentation URLs or anchors" in instructions


def test_search_happy_path_carries_per_unit_citations_and_next(mcp_server: Any) -> None:
    engine = FakeEngine()
    mcp_server._engine = engine

    out = _call(mcp_server, "search", {"query": "how do I stream"})

    assert "https://docs.mistral.ai/page#a-section" in out
    assert "[1] https://docs.mistral.ai/page#a-section" in out
    assert 'chunk id "c1"' in out
    assert out.rstrip().splitlines()[-1].startswith("next:")
    assert "ask(question=" in out


def test_search_full_page_prints_a_copy_pasteable_deeper_call(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(mcp_server, "search", {"query": "streaming", "top_k": 2})

    assert "Results: 2/2 kept/considered" in out
    assert 'exclude_ids=["c1", "c2"]' in out
    assert out.rstrip().splitlines()[-1].startswith("next:")


def test_search_clamps_and_announces_and_bounds_the_engine_call(mcp_server: Any) -> None:
    engine = FakeEngine()
    mcp_server._engine = engine

    out = _call(mcp_server, "search", {"query": "streaming", "top_k": 500})

    assert "note: clamped server-side: top_k=500 → 50" in out
    # The clamp bounds the query itself, so 500 never reaches the engine.
    assert engine.search_calls[0]["top_k"] == 50


def test_search_pagination_keeps_filters_and_prior_exclusions(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(
        mcp_server,
        "search",
        {
            "query": "streaming",
            "top_k": 2,
            "kinds": ["doc"],
            "locales": ["en"],
            "exclude_ids": ["old"],
        },
    )

    assert 'exclude_ids=["old", "c1", "c2"]' in out
    assert 'kinds=["doc"]' in out
    assert 'locales=["en"]' in out


def test_search_empty_says_which_kind_and_echoes_the_query(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine(empty=True)

    out = _call(mcp_server, "search", {"query": "quantum cookies"})

    assert 'Results: 0 sections matched for query "quantum cookies"' in out
    assert "corpus may lack the topic" in out
    assert out.rstrip().splitlines()[-1].startswith("next:")


def test_search_rejects_an_unknown_kind(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "search", {"query": "x", "kinds": ["tutorial"]})

    assert "E_BAD_PARAM" in text
    assert "tutorial" in text
    assert "next:" in text


def test_search_rejects_an_empty_query(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "search", {"query": "   "})

    assert "E_EMPTY_QUERY" in text
    assert "next:" in text


def test_unknown_parameters_are_rejected_naming_the_right_one(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "search", {"query": "x", "limit": 3})

    assert "E_BAD_PARAM" in text
    assert "limit=" in text
    assert "did you mean limit= → top_k=?" in text
    assert "search accepts:" in text


def test_unknown_parameters_with_no_close_match_list_the_schema(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "grep", {"source_id": "s", "pattern": "p", "banana": 1})

    assert "E_BAD_PARAM" in text
    assert "banana=" in text
    assert "grep accepts:" in text


def test_open_windows_around_the_chunk_and_marks_it(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(mcp_server, "open", {"chunk_id": "c1", "window": 1})

    assert "[1]* https://docs.mistral.ai/page#a-section" in out
    assert out.count("https://docs.mistral.ai/page#a-section") >= 2
    assert out.rstrip().splitlines()[-1].startswith("next:")


def test_open_clamps_the_window_and_announces_it(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(mcp_server, "open", {"chunk_id": "c1", "window": 99})

    assert "note: clamped server-side: window=99 → 10" in out


def test_open_truncation_names_a_read_call_that_accepts_every_parameter(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine(hits=[_hit("c1", "x" * 1500)])

    out = _call(mcp_server, "open", {"chunk_id": "c1"})

    assert (
        'read(source_id="https://docs.mistral.ai/page", start_offset=10, '
        "end_offset=20, top_k=1)" in out
    )


def test_open_unknown_chunk_is_a_typed_error(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    text = _call_error(mcp_server, "open", {"chunk_id": "nope"})

    assert "E_UNKNOWN_CHUNK" in text
    assert '"nope"' in text
    assert "exactly as a search or open result printed it" in text
    assert "next:" in text


def test_navigate_walks_forward_with_next(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(
        mcp_server,
        "navigate",
        {
            "source_id": "https://docs.mistral.ai/page",
            "start_offset": 10,
            "end_offset": 20,
            "direction": "next",
        },
    )

    assert "next 1 chunk(s)" in out
    assert "https://docs.mistral.ai/page#a-section" in out
    assert out.rstrip().splitlines()[-1].startswith("next:")


def test_navigate_at_the_end_of_a_page_says_so(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(
        mcp_server,
        "navigate",
        {
            "source_id": "https://docs.mistral.ai/page",
            "start_offset": 10,
            "end_offset": 20,
            "direction": "previous",
        },
    )

    assert "Results: 0 chunks previous" in out
    assert "nothing further in that direction" in out
    assert out.rstrip().splitlines()[-1].startswith("next:")


def test_navigate_rejects_a_bad_direction(mcp_server: Any) -> None:
    text = _call_error(
        mcp_server,
        "navigate",
        {
            "source_id": "s",
            "start_offset": 0,
            "end_offset": 1,
            "direction": "sideways",
        },
    )

    assert "E_BAD_PARAM" in text
    assert "next" in text


def test_navigate_unknown_page_is_a_typed_error(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine(missing_page=True)

    text = _call_error(
        mcp_server,
        "navigate",
        {
            "source_id": "https://docs.mistral.ai/nope",
            "start_offset": 0,
            "end_offset": 1,
            "direction": "next",
        },
    )

    assert "E_UNKNOWN_PAGE" in text
    assert "next:" in text


def test_read_returns_the_page_with_next(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(mcp_server, "read", {"source_id": "https://docs.mistral.ai/page"})

    assert "page: https://docs.mistral.ai/page" in out
    assert "Results: 2 chunks (the whole requested range)" in out
    assert out.rstrip().splitlines()[-1].startswith("next:")


def test_read_returns_long_chunk_content_without_truncating_it(mcp_server: Any) -> None:
    content = "first line\n" + "x" * 1400 + "\nlast line"
    mcp_server._engine = FakeEngine(hits=[_hit("c1", content)])

    out = _call(mcp_server, "read", {"source_id": "https://docs.mistral.ai/page"})

    assert content in out
    assert "[truncated" not in out


def test_read_unknown_page_is_a_typed_error(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine(missing_page=True)

    text = _call_error(mcp_server, "read", {"source_id": "https://docs.mistral.ai/nope"})

    assert "E_UNKNOWN_PAGE" in text
    assert "glossator://index" in text


def test_grep_matches_with_next(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(
        mcp_server, "grep", {"source_id": "https://docs.mistral.ai/page", "pattern": "alpha"}
    )

    assert 'matches for "alpha" (mode=phrase)' in out
    assert "Results: 2 chunks matched" in out
    assert out.rstrip().splitlines()[-1].startswith("next:")


def test_grep_empty_names_the_kind_of_empty(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine(empty=True)

    out = _call(
        mcp_server, "grep", {"source_id": "https://docs.mistral.ai/page", "pattern": "alpha"}
    )

    assert 'Results: 0 chunks on this page contain the phrase "alpha"' in out
    assert "The page is indexed; the words are not on it" in out
    assert out.rstrip().splitlines()[-1].startswith("next:")


def test_grep_rejects_a_bad_mode(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "grep", {"source_id": "s", "pattern": "p", "mode": "fuzzy"})

    assert "E_BAD_PARAM" in text
    assert '"phrase"' in text and '"term"' in text


def test_grep_rejects_an_empty_pattern(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "grep", {"source_id": "s", "pattern": ""})

    assert "E_EMPTY_QUERY" in text


def test_grep_unknown_page_is_a_typed_error(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine(missing_page=True)

    text = _call_error(
        mcp_server,
        "grep",
        {"source_id": "https://docs.mistral.ai/nope", "pattern": "alpha"},
    )

    assert "E_UNKNOWN_PAGE" in text
    assert "next:" in text


def _fake_answer(insufficient: bool = False) -> Answer:
    rejected = Citation(
        n=3,
        url="https://docs.mistral.ai/page",
        anchor="invented",
        quote="a paraphrase, not a quote",
        verified=False,
        reason="quote is not in the cited source",
    )
    trace = Trace(
        strategy="single_pass",
        variant="sec1024",
        prompt_version="v1",
        sources=(
            []
            if insufficient
            else [
                TracedSource(
                    n=1,
                    citation_url="https://docs.mistral.ai/page#a-section",
                    heading_path=["Page", "A section"],
                    chunk_ids=["c1"],
                    tokens=100,
                )
            ]
        ),
        unverified_citations=[] if insufficient else [rejected],
    )
    return Answer(
        question="how do I stream?",
        strategy="single_pass",
        model="mistral-medium-2604",
        answer_markdown="Use server-sent events [1] and set stream=true [3].",
        citations=(
            []
            if insufficient
            else [
                Citation(
                    n=1,
                    url="https://docs.mistral.ai/page",
                    anchor="a-section",
                    chunk_id="c1",
                    quote="alpha content",
                    verified=True,
                )
            ]
        ),
        insufficient_evidence=insufficient,
        trace=trace,
        usage=TokenUsage(prompt_tokens=500, completion_tokens=80),
        latency_ms=2400.0,
        cost_usd=0.0013,
    )


def test_ask_prints_sources_verification_and_next(mcp_server: Any, monkeypatch: Any) -> None:
    mcp_server._engine = FakeEngine()
    seen: list[dict[str, Any]] = []

    async def fake_ask(question: str, **kwargs: Any) -> Answer:
        seen.append({"question": question, **kwargs})
        return _fake_answer()

    monkeypatch.setattr(mcp_server.answer_service, "ask", fake_ask)

    out = _call(mcp_server, "ask", {"question": "how do I stream?"})

    assert "Use server-sent events [1]" in out
    assert "Sources (1 verified):" in out
    assert "[1] https://docs.mistral.ai/page#a-section | Page > A section" in out
    assert "citations verified: 1/2" in out
    assert 'next: open(chunk_id="c1")' in out
    # The rejected citation is a plain drop, never a link.
    assert "[3] dropped, no link" in out
    assert "https://docs.mistral.ai/page#invented" not in out
    # The server's engine is reused, not rebuilt per question.
    assert seen[0]["engine"] is mcp_server._engine


def test_ask_insufficient_evidence_points_at_the_next_strategy(
    mcp_server: Any, monkeypatch: Any
) -> None:
    mcp_server._engine = FakeEngine()

    async def fake_ask(question: str, **kwargs: Any) -> Answer:
        return _fake_answer(insufficient=True)

    monkeypatch.setattr(mcp_server.answer_service, "ask", fake_ask)

    out = _call(mcp_server, "ask", {"question": "what is the tool-call cap?"})

    assert "insufficient evidence" in out
    assert "(none)" in out
    assert 'strategy="outline"' in out


def test_ask_rejects_an_unknown_strategy(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "ask", {"question": "q", "strategy": "vibes"})

    assert "E_BAD_PARAM" in text
    assert "single_pass" in text
    assert "next:" in text


def test_busy_tells_the_caller_to_retry_the_identical_call(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    async def fill() -> None:
        for _ in range(mcp_server._ADMISSION_SLOTS):
            await mcp_server._admission.acquire()

    asyncio.run(fill())
    try:
        text = _call_error(mcp_server, "search", {"query": "x"})
    finally:
        for _ in range(mcp_server._ADMISSION_SLOTS):
            mcp_server._admission.release()

    assert "E_BUSY" in text
    assert "IDENTICAL" in text
    assert "do not reformulate" in text


def test_upstream_failure_is_typed_with_a_retry_hint(mcp_server: Any) -> None:
    class ExplodingEngine:
        config: Any = None

        async def search_with_trace(
            self, query: str, **kwargs: Any
        ) -> tuple[list[Hit], SearchTrace]:
            raise RetrieverException("vespa down")

    mcp_server._engine = ExplodingEngine()

    text = _call_error(mcp_server, "search", {"query": "x"})

    assert "E_UPSTREAM" in text
    assert "retry the identical call" in text


def _read_resource(server: Any, uri: str) -> str:
    result = asyncio.run(server.mcp.read_resource(uri))
    raw = result.contents[0]
    return str(raw.content)


def test_exactly_three_resources_exist(mcp_server: Any) -> None:
    resources = asyncio.run(mcp_server.mcp.list_resources())

    assert {str(resource.uri) for resource in resources} == {
        "glossator://guide",
        "glossator://index",
        "glossator://context",
    }


def test_the_guide_states_the_flow_the_limits_and_no_other_uris(mcp_server: Any) -> None:
    guide = _read_resource(mcp_server, "glossator://guide")

    assert "Never fabricate documentation URLs or anchors" in guide
    assert "There are no other URIs" in guide
    assert "glossator://index" in guide and "glossator://context" in guide
    assert "| `search.top_k` | 1-50 | 5 |" in guide
    assert "E_BAD_PARAM" in guide


def test_the_index_resource_lists_pages_one_per_line(mcp_server: Any) -> None:
    index = _read_resource(mcp_server, "glossator://index")

    lines = index.splitlines()
    assert lines[1] == "url\ttitle\tkind"
    assert "https://docs.mistral.ai/agents/conversations\tConversations\tdoc" in lines
    assert "# the url column is the source_id the tools take" in lines


def test_the_context_resource_publishes_limits_formats_and_counts(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    context = json.loads(_read_resource(mcp_server, "glossator://context"))

    assert context["corpus"]["source_commit"] == "2e094f7"
    assert context["corpus"]["pages"] == 9
    assert context["variant_served"] == "sec1024"
    assert context["variants"]["sec1024"]["documents"] == 4430
    assert context["limits"]["search.top_k"] == [1, 50]
    assert "chunk_id" in context["id_formats"]
    assert context["models"]["generation_default"] == "mistral-medium-2604"
    assert "ministral-14b-2512" in context["models"]["generation_available"]
    assert context["resources"] == [
        "glossator://guide",
        "glossator://index",
        "glossator://context",
    ]
