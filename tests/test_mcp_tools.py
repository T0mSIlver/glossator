"""MCP tool, resource, response, and error-contract tests."""

import asyncio
import dataclasses
import importlib
import json
from typing import Any

import pytest
from fastmcp.exceptions import ToolError
from fastmcp.exceptions import ValidationError as FastMcpValidationError
from mistralai.search.toolkit.retrieval.errors import RetrieverException
from mistralai.search.toolkit.search.errors import SourceNotFoundError

from glossator.answer.citations import Answer, Citation, Trace, TracedSource
from glossator.answer.llm import TokenUsage
from glossator.retrieval.engine import Hit, SearchTrace

TOOLS = {"search", "open", "navigate", "read", "grep", "ask", "cite", "history"}


def _reload_with(monkeypatch: pytest.MonkeyPatch, **env: str) -> Any:
    """Reload the server with extra environment set (allowlist, token)."""
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key-not-used")
    monkeypatch.setenv("GLOSSATOR_CORPUS_DIR", "tests/fixtures/corpus")
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    import entrypoints.mcp_server as module

    return importlib.reload(module)


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
    def __init__(
        self,
        hits: list[Hit],
        *,
        missing: bool = False,
        previous_hits: list[Hit] | None = None,
    ) -> None:
        self.hits = hits
        self.missing = missing
        self.previous_hits: list[Hit] | None = previous_hits

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
        if self.previous_hits is None:
            return []
        return self.previous_hits[:top_k]

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
            {
                "query": query,
                "exclude_ids": exclude_ids,
                "top_k": top_k,
                "kinds": kinds,
                "locales": locales,
            }
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


def test_the_tool_set_includes_history_and_the_existing_read_tools(mcp_server: Any) -> None:
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


def test_search_forwards_the_locale_filter(mcp_server: Any) -> None:
    engine = FakeEngine()
    mcp_server._engine = engine

    out = _call(
        mcp_server,
        "search",
        {"query": "streaming", "kinds": ["doc"], "locales": ["en"]},
    )

    call = engine.search_calls[0]
    assert call["kinds"] == frozenset({"doc"})
    assert call["locales"] == frozenset({"en"})
    assert "note: filtered to kinds=['doc'] locales=['en']" in out


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


def test_open_truncation_without_offsets_still_names_a_valid_read(mcp_server: Any) -> None:
    hit = dataclasses.replace(_hit("c1", "x" * 1500), start_offset=None, end_offset=None)
    mcp_server._engine = FakeEngine(hits=[hit])

    out = _call(mcp_server, "open", {"chunk_id": "c1"})

    assert 'read(source_id="https://docs.mistral.ai/page", top_k=1)' in out
    assert "start_offset=None" not in out


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
    assert "(top_k=1 was full; more may exist)" in out
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


def test_navigate_previous_walks_backward_with_results(mcp_server: Any) -> None:
    earlier = _hit("c0", "chunk before the anchor")

    class PreviousEngine(FakeEngine):
        def navigation_at(self, source_id: str, start: int = 0, end: int = 0) -> FakeNavigation:
            return FakeNavigation([earlier], previous_hits=[earlier])

    mcp_server._engine = PreviousEngine()

    out = _call(
        mcp_server,
        "navigate",
        {
            "source_id": "https://docs.mistral.ai/page",
            "start_offset": 10,
            "end_offset": 20,
            "direction": "previous",
            "top_k": 2,
        },
    )

    assert "previous 1 chunk(s)" in out
    assert "(every chunk in this direction)" in out
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
    assert "Results: 2 chunks (the whole requested range; none dropped)" in out
    assert out.rstrip().splitlines()[-1].startswith("next:")


def test_read_continues_from_the_last_end_offset(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(
        mcp_server,
        "read",
        {"source_id": "https://docs.mistral.ai/page", "top_k": 1},
    )

    assert "Results: 1 chunks (top_k=1; the page may have more)" in out
    assert (
        'next: read(source_id="https://docs.mistral.ai/page", start_offset=20, '
        "top_k=1) to continue after this page of chunks" in out
    )


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
    assert "Results: 2 chunks matched (every match on this page)" in out
    assert out.rstrip().splitlines()[-1].startswith("next:")


def test_grep_full_page_names_the_cap(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(
        mcp_server,
        "grep",
        {"source_id": "https://docs.mistral.ai/page", "pattern": "alpha", "top_k": 2},
    )

    assert "Results: 2 chunks matched (top_k=2 was full; more matches may exist)" in out


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
                    fragment_url=("https://docs.mistral.ai/page#a-section:~:text=alpha%20content"),
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
    # The source line prints the fragment link: it carries the anchor inside it
    # and scrolls a supporting browser to the quoted span.
    assert "[1] https://docs.mistral.ai/page#a-section:~:text=alpha%20content" in out
    assert " | Page > A section" in out
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
    assert 'strategy="search_loop"' in out
    assert "no citations were proposed" in out


def test_ask_rejects_an_unknown_strategy(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "ask", {"question": "q", "strategy": "vibes"})

    assert "E_BAD_PARAM" in text
    assert "single_pass" in text
    assert "next:" in text


def test_ask_reports_a_bad_model_env_as_a_bad_param(mcp_server: Any, monkeypatch: Any) -> None:
    # A bad GLOSSATOR_MODEL is deterministic misconfiguration; E_UPSTREAM's
    # "retry the identical call" would loop forever.
    monkeypatch.setenv("GLOSSATOR_MODEL", "not-a-priced-model")
    server: Any = importlib.reload(mcp_server)
    server._engine = FakeEngine()

    async def fake_ask(question: str, **kwargs: Any) -> Answer:
        raise AssertionError("the route must fail before calling the service")

    monkeypatch.setattr(server.answer_service, "ask", fake_ask)
    text = _call_error(server, "ask", {"question": "how do I stream?"})

    assert "E_BAD_PARAM" in text
    assert "GLOSSATOR_MODEL" in text
    assert "ministral-14b-2512" in text
    assert "E_UPSTREAM" not in text


def test_ask_maps_service_failures_to_upstream(mcp_server: Any, monkeypatch: Any) -> None:
    mcp_server._engine = FakeEngine()

    async def failing(question: str, **kwargs: Any) -> Answer:
        raise RuntimeError("generation failed after retries")

    monkeypatch.setattr(mcp_server.answer_service, "ask", failing)

    text = _call_error(mcp_server, "ask", {"question": "how do I stream?"})

    assert "E_UPSTREAM" in text
    assert "generation failed" in text
    assert "retry the identical call" in text


def test_a_known_parameter_with_a_wrong_type_fails_framework_validation(
    mcp_server: Any,
) -> None:
    # The guard only inspects names; a wrong-typed known name passes it and is
    # rejected by the framework's own validation, naming the field.
    with pytest.raises(FastMcpValidationError) as excinfo:
        asyncio.run(mcp_server.mcp.call_tool("search", {"query": "x", "top_k": "many"}))

    assert "top_k" in str(excinfo.value)


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


def test_a_failed_call_releases_its_admission_slot(mcp_server: Any) -> None:
    class ExplodingEngine:
        config: Any = None

        async def search_with_trace(
            self, query: str, **kwargs: Any
        ) -> tuple[list[Hit], SearchTrace]:
            raise RetrieverException("vespa down")

    mcp_server._engine = ExplodingEngine()
    first = _call_error(mcp_server, "search", {"query": "x"})
    assert "E_UPSTREAM" in first

    mcp_server._engine = FakeEngine()
    second = _call(mcp_server, "search", {"query": "x"})

    assert "E_BUSY" not in second
    assert "https://docs.mistral.ai/page#a-section" in second


def test_multiple_unknown_parameters_use_the_plural_grammar(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "search", {"query": "x", "limit": 3, "lang": ["en"]})

    assert "E_BAD_PARAM" in text
    assert "unknown parameters for search: limit=, lang=" in text
    assert "they were rejected, not applied" in text
    assert "did you mean limit= → top_k=, lang= → locales=?" in text
    assert "search accepts:" in text


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


def test_the_guide_limits_table_matches_the_published_limits(mcp_server: Any) -> None:
    guide = _read_resource(mcp_server, "glossator://guide")

    for name, (low, high, default) in mcp_server.LIMITS.items():
        assert f"| `{name}` | {low}-{high} | {default} |" in guide, name


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


def test_resources_survive_a_missing_manifest(
    mcp_server: Any, monkeypatch: Any, tmp_path: Any
) -> None:
    monkeypatch.setenv("GLOSSATOR_CORPUS_DIR", str(tmp_path / "nowhere"))
    server: Any = importlib.reload(mcp_server)
    server._engine = FakeEngine()

    index = _read_resource(server, "glossator://index")
    assert index.splitlines()[0].endswith("0 pages · docs commit 0 commits")
    assert "url\ttitle\tkind" in index

    context = json.loads(_read_resource(server, "glossator://context"))
    assert context["corpus"]["pages"] == 0
    assert context["corpus"]["source_commit"] is None
    assert context["models"]["generation_default"] == "mistral-medium-2604"


def test_cite_verifies_a_chunk_quote_and_prints_the_source_list(
    mcp_server: Any,
) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(
        mcp_server,
        "cite",
        {
            "draft": "Alpha says the thing [1].",
            "quotes": [{"n": 1, "chunk_id": "c1", "quote": "alpha content"}],
        },
    )

    assert "[1] verified:" in out
    assert "https://docs.mistral.ai/page#a-section" in out
    assert "[1] https://docs.mistral.ai/page#a-section" in out
    assert "markers with no verified quote" not in out
    assert "paste the source list as-is" in out
    assert out.rstrip().splitlines()[-1].startswith("next:")


def test_cite_verifies_through_a_page_url_and_rejects_a_fabrication(
    mcp_server: Any,
) -> None:
    mcp_server._engine = FakeEngine()

    out = _call(
        mcp_server,
        "cite",
        {
            "draft": "Alpha [1] and pixels [2] plus memory [3].",
            "quotes": [
                {
                    "n": 1,
                    "url": "https://docs.mistral.ai/page#a-section",
                    "quote": "alpha content",
                },
                {"n": 2, "chunk_id": "c1", "quote": "pixels are delicious"},
            ],
        },
    )

    assert "[1] verified:" in out
    assert "[2] NOT verified: quote is not in the cited source" in out
    assert "markers with no verified quote: [2], [3]" in out


def test_cite_rejects_a_quote_naming_neither_chunk_nor_url(
    mcp_server: Any,
) -> None:
    text = _call_error(
        mcp_server,
        "cite",
        {"draft": "Alpha [1].", "quotes": [{"n": 1, "quote": "alpha content"}]},
    )

    assert "E_BAD_PARAM" in text
    assert "chunk_id" in text
    assert "next:" in text


def test_cite_rejects_an_empty_draft(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "cite", {"draft": "   ", "quotes": []})

    assert "E_BAD_PARAM" in text


def test_cite_announces_its_clamps(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()
    quotes = [{"n": n, "chunk_id": "c1", "quote": "alpha content"} for n in range(1, 26)]

    out = _call(mcp_server, "cite", {"draft": "Alpha [1].", "quotes": quotes})

    assert "note: clamped server-side: quotes=25 → 20" in out


def test_ask_prints_one_entry_per_source(mcp_server: Any, monkeypatch: Any) -> None:
    """Two markers on one source collapse to one entry (D-027b)."""
    mcp_server._engine = FakeEngine()
    answer = _fake_answer()
    doubled = answer.model_copy(
        update={
            "answer_markdown": "Use server-sent events [1] and again [2].",
            "citations": [
                answer.citations[0],
                answer.citations[0].model_copy(update={"n": 2}),
            ],
            "trace": answer.trace.model_copy(
                update={
                    "sources": [
                        TracedSource(
                            n=1,
                            citation_url="https://docs.mistral.ai/page#a-section",
                            heading_path=["Page", "A section"],
                            chunk_ids=["c1"],
                            tokens=100,
                        ),
                        TracedSource(
                            n=2,
                            citation_url="https://docs.mistral.ai/page#a-section",
                            heading_path=["Page", "A section"],
                            chunk_ids=["c1"],
                            tokens=100,
                        ),
                    ]
                }
            ),
        }
    )

    async def fake_ask(question: str, **kwargs: Any) -> Answer:
        return doubled

    monkeypatch.setattr(mcp_server.answer_service, "ask", fake_ask)

    out = _call(mcp_server, "ask", {"question": "how do I stream?"})

    assert "[1], [2] https://docs.mistral.ai/page#a-section" in out
    assert out.count("https://docs.mistral.ai/page#a-section | Page > A section") == 1


def test_the_allowlist_registers_only_the_named_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOOLS="search,cite")
    tools = asyncio.run(server.mcp.list_tools())

    assert {tool.name for tool in tools} == {"search", "cite"}
    assert "cite" in server.mcp.instructions
    assert "ask" not in server.mcp.instructions


def test_the_allowlist_scopes_the_guide_to_registered_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOOLS="search,cite")

    guide = _read_resource(server, "glossator://guide")

    assert "| cite |" in guide
    assert "| ask |" not in guide
    assert "`cite.quotes`" in guide


def test_the_allowlist_ignores_unknown_names_with_a_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOOLS="search,bogus")
    tools = asyncio.run(server.mcp.list_tools())

    assert {tool.name for tool in tools} == {"search"}


def _health_via_http(server: Any, headers: dict[str, str] | None = None) -> Any:
    """GET /health through the real HTTP app, lifespan included."""
    from starlette.testclient import TestClient

    with TestClient(server.build_http_app()) as client:
        return client.get("/health", headers=headers)


class _ProbeForHealth:
    def as_dict(self) -> dict[str, Any]:
        return {"variant": "sec1024", "model": "m", "dimensions": 128}


def _fake_probe(server: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    async def probe(variant: str) -> _ProbeForHealth:
        return _ProbeForHealth()

    monkeypatch.setattr(server, "check_embedding_once", probe)


def test_health_reports_variant_chunks_probe_and_tools(
    mcp_server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    mcp_server._engine = FakeEngine()
    _fake_probe(mcp_server, monkeypatch)

    response = _health_via_http(mcp_server)

    assert response.status_code == 200
    body = response.json()
    assert body["variant"] == "sec1024"
    assert body["chunks"] == 4430
    assert body["embedding_probe"]["passed"] is True
    assert body["tools"] == sorted(TOOLS)


def test_health_lists_only_allowlisted_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOOLS="search,cite")
    server._engine = FakeEngine()
    _fake_probe(server, monkeypatch)

    body = _health_via_http(server).json()

    assert body["tools"] == ["cite", "search"]


def _mcp_post_via_http(
    server: Any, payload: dict[str, Any], headers: dict[str, str] | None = None
) -> Any:
    from starlette.testclient import TestClient

    with TestClient(server.build_http_app()) as client:
        return client.post("/mcp", json=payload, headers=headers)


def test_bearer_token_is_required_on_the_http_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOKEN="secret-token")
    server._engine = FakeEngine()

    denied = _mcp_post_via_http(server, {"jsonrpc": "2.0", "id": 1, "method": "ping"})

    assert denied.status_code == 401
    assert "Authorization" in denied.json()["error"]["message"]

    # Health stays unauthenticated so the Debugger and the tunnel can check it.
    assert _health_via_http(server).status_code == 200

    allowed = _mcp_post_via_http(
        server,
        {"jsonrpc": "2.0", "id": 1, "method": "ping"},
        headers={"Authorization": "Bearer secret-token"},
    )
    assert allowed.status_code != 401


def test_a_wrong_bearer_token_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOKEN="secret-token")
    server._engine = FakeEngine()

    response = _mcp_post_via_http(
        server,
        {"jsonrpc": "2.0", "id": 1, "method": "ping"},
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401


def test_the_token_is_compared_in_constant_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A byte-by-byte comparison leaks the token's prefix to anyone who can
    time the 401, so the check must go through `hmac.compare_digest`."""
    import hmac

    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOKEN="secret-token")
    server._engine = FakeEngine()
    seen: list[tuple[str, str]] = []
    real = hmac.compare_digest

    def spy(left: str, right: str) -> bool:
        seen.append((left, right))
        return real(left, right)

    monkeypatch.setattr(server.hmac, "compare_digest", spy)
    _mcp_post_via_http(
        server,
        {"jsonrpc": "2.0", "id": 1, "method": "ping"},
        headers={"Authorization": "Bearer secret-token"},
    )

    assert ("Bearer secret-token", "Bearer secret-token") in seen


def test_a_non_http_connection_does_not_bypass_the_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Startup passes through; anything else carries no header to check and is
    closed rather than handed to the app unauthenticated."""
    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOKEN="secret-token")
    reached: list[str] = []
    sent: list[dict[str, Any]] = []

    async def app(scope: Any, receive: Any, send: Any) -> None:
        reached.append(scope["type"])

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    guard = server._BearerAuthMiddleware(app, "secret-token")
    asyncio.run(guard({"type": "websocket", "path": "/mcp", "headers": []}, None, send))

    assert reached == []
    assert sent == [{"type": "websocket.close", "code": 1008}]

    asyncio.run(guard({"type": "lifespan"}, None, send))
    assert reached == ["lifespan"]


def test_hints_never_name_a_tool_the_allowlist_turned_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A `next:` line naming an unregistered tool is the same trap as one
    naming a parameter the tool lacks (D-029): the call fails with "unknown
    tool" and the model has nothing to act on."""
    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOOLS="search,cite")
    server._engine = FakeEngine()

    out = _call(server, "search", {"query": "streaming", "top_k": 2})

    hints = [line for line in out.splitlines() if line.startswith("next:")]
    assert hints
    for line in hints:
        assert "open(" not in line
        assert "ask(" not in line
        assert "read(" not in line
    assert "cite(" in hints[-1]


def test_a_truncation_marker_names_a_registered_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOOLS="search,open")
    long_hit = _hit("chunk-long", "word " * 400)

    block = server._hit_block(long_hit, 1, 50)

    assert "…[truncated; use " in block
    assert "read(" not in block
    assert 'open(chunk_id="chunk-long"' in block
