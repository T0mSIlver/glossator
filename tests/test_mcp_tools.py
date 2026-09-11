"""MCP tool, response and error-contract tests for the three-tool surface."""

import asyncio
import importlib
from typing import Any

import pytest
from fastmcp.exceptions import ToolError
from mistralai.search.toolkit.retrieval.errors import RetrieverException
from mistralai.search.toolkit.search.errors import SourceNotFoundError

from glossator.retrieval.engine import Hit

TOOLS = {"mistral_docs_search", "mistral_docs_read_page", "mistral_docs_history"}
PAGE = "https://docs.mistral.ai/page"


def _reload_with(monkeypatch: pytest.MonkeyPatch, **env: str) -> Any:
    """Reload the server offline with a placeholder key, the fixture corpus, and extra env."""
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key-not-used")
    monkeypatch.setenv("GLOSSATOR_CORPUS_DIR", "tests/fixtures/corpus")
    monkeypatch.delenv("GLOSSATOR_MCP_TOOLS", raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    import entrypoints.mcp_server as module

    return importlib.reload(module)


@pytest.fixture
def mcp_server(monkeypatch: pytest.MonkeyPatch) -> Any:
    return _reload_with(monkeypatch)


def _hit(
    chunk_id: str,
    content: str,
    *,
    anchor: str | None = "a-section",
    heading: str = "A section",
    url: str = PAGE,
) -> Hit:
    return Hit(
        chunk_id=chunk_id,
        score=0.5,
        url=url,
        anchor=anchor,
        heading_path=("Page", heading),
        page_title="Page",
        kind="doc",
        locale="en",
        section_index=1,
        content=f"Page > {heading}\n\n{content}",
        source_id=url,
        start_offset=10,
        end_offset=20,
    )


class FakeNavigation:
    def __init__(self, hits: list[Hit], *, missing: bool = False) -> None:
        self.hits = hits
        self.missing = missing

    async def read(
        self, start: int | None = None, end: int | None = None, top_k: int = 20
    ) -> list[Hit]:
        if self.missing:
            raise SourceNotFoundError("https://docs.mistral.ai/nope")
        return self.hits[:top_k]


class FakeEngine:
    def __init__(
        self, hits: list[Hit] | None = None, *, empty: bool = False, missing_page: bool = False
    ) -> None:
        self.hits = hits if hits is not None else [_hit("c1", "alpha content"), _hit("c2", "beta")]
        self.empty = empty
        self.missing_page = missing_page
        self.search_calls: list[dict[str, Any]] = []

    async def search(
        self,
        query: str,
        top_k: int | None = None,
        rerank: bool | None = None,
        kinds: frozenset[str] | None = None,
    ) -> list[Hit]:
        self.search_calls.append({"query": query, "top_k": top_k, "rerank": rerank, "kinds": kinds})
        return [] if self.empty else self.hits[: top_k or 5]

    def navigation_at(self, page_url: str, start: int = 0, end: int = 0) -> FakeNavigation:
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


def _tools(server: Any) -> dict[str, Any]:
    return {tool.name: tool for tool in asyncio.run(server.mcp.list_tools())}


def test_exactly_three_tools_are_registered(mcp_server: Any) -> None:
    assert set(_tools(mcp_server)) == TOOLS


def test_every_tool_is_annotated_read_only(mcp_server: Any) -> None:
    for tool in _tools(mcp_server).values():
        annotations = tool.annotations
        assert annotations is not None
        assert annotations.readOnlyHint is True
        assert annotations.destructiveHint is False
        assert annotations.idempotentHint is True
        assert annotations.openWorldHint is False


def test_descriptions_are_short_and_name_no_time_cost_or_ids(mcp_server: Any) -> None:
    banned = ("second", " ms", "cost", "USD", "price of", "chunk id", "rerank", "budget")
    for name, tool in _tools(mcp_server).items():
        description = tool.description or ""
        assert len(description.split()) <= 120, name
        assert description.splitlines()[0].rstrip().endswith("."), name
        for word in banned:
            assert word not in description, (name, word)


def test_search_parameters_are_q_max_hits_and_kind(mcp_server: Any) -> None:
    schema = _tools(mcp_server)["mistral_docs_search"].parameters
    assert set(schema["properties"]) == {"q", "max_hits", "kind"}
    assert schema.get("additionalProperties") is False


def test_read_page_parameters_are_page_url_and_section(mcp_server: Any) -> None:
    schema = _tools(mcp_server)["mistral_docs_read_page"].parameters
    assert set(schema["properties"]) == {"page_url", "section"}


def test_instructions_carry_the_scope_the_citation_rule_and_the_refusal_rule(
    mcp_server: Any,
) -> None:
    text = mcp_server._instructions()
    assert "pages of Mistral's documentation" in text
    assert "mistral_docs_search" in text
    assert "url#anchor" in text
    assert "say so" in text
    assert "nothing more" in text
    assert "do not retry" in text
    for word in ("second", "cost", "chunk id", "rerank"):
        assert word not in text


def test_the_allowlist_registers_only_the_named_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOOLS="mistral_docs_search")
    assert set(_tools(server)) == {"mistral_docs_search"}
    assert "mistral_docs_read_page" not in server._instructions()


def test_the_allowlist_rejects_an_unknown_tool_and_requires_search(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(RuntimeError, match="unknown tools"):
        _reload_with(monkeypatch, GLOSSATOR_MCP_TOOLS="not_a_tool")
    with pytest.raises(RuntimeError, match="must include mistral_docs_search"):
        _reload_with(monkeypatch, GLOSSATOR_MCP_TOOLS="mistral_docs_history")


def test_search_prints_url_anchor_heading_snippet_and_next(mcp_server: Any) -> None:
    engine = FakeEngine()
    mcp_server._engine = engine
    text = _call(mcp_server, "mistral_docs_search", {"q": "alpha"})
    assert 'q: "alpha"' in text
    assert f"[1] {PAGE}#a-section" in text
    assert "Page > A section" in text
    assert "alpha content" in text
    assert "chunk id" not in text
    assert "rerank" not in text
    assert text.rstrip().endswith(
        f'next: mistral_docs_read_page(page_url="{PAGE}") to read hit 1 on its page'
    )
    assert engine.search_calls[0]["rerank"] is False


def test_search_collapses_chunks_of_one_section_into_one_hit(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine(
        [
            _hit("c1", "first half"),
            _hit("c2", "second half"),
            _hit("c3", "elsewhere", anchor="other", heading="Other"),
        ]
    )
    text = _call(mcp_server, "mistral_docs_search", {"q": "half", "max_hits": 5})
    assert text.count(f"[1] {PAGE}#a-section") == 1
    assert f"[2] {PAGE}#other" in text
    assert "[3]" not in text
    assert "Results: 2 hits" in text


def test_search_asks_the_engine_for_more_than_it_shows_so_sections_stay_distinct(
    mcp_server: Any,
) -> None:
    engine = FakeEngine()
    mcp_server._engine = engine
    _call(mcp_server, "mistral_docs_search", {"q": "alpha", "max_hits": 4})
    assert engine.search_calls[0]["top_k"] == 12


def test_search_clamps_max_hits_silently_to_the_ceiling(mcp_server: Any) -> None:
    engine = FakeEngine()
    mcp_server._engine = engine
    _call(mcp_server, "mistral_docs_search", {"q": "alpha", "max_hits": 999})
    assert engine.search_calls[0]["top_k"] == mcp_server.MAX_HITS * 3


def test_search_snippet_drops_the_heading_line_the_path_already_shows(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine([_hit("c1", "## A section {#a-section}\n\nbody text")])
    text = _call(mcp_server, "mistral_docs_search", {"q": "body"})
    assert "{#a-section}" not in text
    assert "body text" in text


def test_search_marks_a_hit_on_a_large_page_with_the_section_to_read(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()
    mcp_server._PAGE_SIZES[PAGE] = mcp_server.LARGE_PAGE_CHARS
    text = _call(mcp_server, "mistral_docs_search", {"q": "alpha"})
    assert f'large page: mistral_docs_read_page(page_url="{PAGE}", section="a-section")' in text
    assert text.rstrip().endswith(
        f'next: mistral_docs_read_page(page_url="{PAGE}", section="a-section") '
        "to read hit 1 on its page"
    )


def test_search_forwards_the_kind_filter(mcp_server: Any) -> None:
    engine = FakeEngine()
    mcp_server._engine = engine
    text = _call(mcp_server, "mistral_docs_search", {"q": "alpha", "kind": "api"})
    assert engine.search_calls[0]["kinds"] == frozenset({"api"})
    assert "kind: api" in text


def test_search_rejects_an_unknown_kind(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "mistral_docs_search", {"q": "alpha", "kind": "blog"})
    assert "E_BAD_PARAM" in text
    assert '"doc", "api" or "model"' in text


def test_search_rejects_an_empty_query(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "mistral_docs_search", {"q": "   "})
    assert "E_BAD_PARAM" in text
    assert "q is empty" in text


def test_search_empty_says_the_documentation_may_not_cover_it(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine(empty=True)
    text = _call(mcp_server, "mistral_docs_search", {"q": "nothing"})
    assert "Results: no section matched." in text
    assert "does not cover it" in text


def test_search_with_a_page_url_lists_the_pages_under_it_without_the_index(
    mcp_server: Any,
) -> None:
    engine = FakeEngine()
    mcp_server._engine = engine
    text = _call(mcp_server, "mistral_docs_search", {"q": "https://docs.mistral.ai/capabilities"})
    assert text.startswith("pages under https://docs.mistral.ai/capabilities")
    assert "- https://docs.mistral.ai/capabilities/embeddings\n    Embeddings" in text
    assert "- https://docs.mistral.ai/capabilities/function-calling" in text
    assert "docs.mistral.ai/fr/" not in text
    assert "Results: 2 pages; a page not listed does not exist at this commit." in text
    assert text.rstrip().endswith(
        'next: mistral_docs_read_page(page_url="https://docs.mistral.ai/capabilities/embeddings")'
        " reads the first one."
    )
    assert engine.search_calls == []


def test_search_accepts_site_and_bare_path_forms_and_keeps_the_kind_filter(
    mcp_server: Any,
) -> None:
    mcp_server._engine = FakeEngine()
    for q in ("site:docs.mistral.ai/models", "/models/", "https://docs.mistral.ai/models#x"):
        text = _call(mcp_server, "mistral_docs_search", {"q": q})
        assert "- https://docs.mistral.ai/models\n    Model capability matrix" in text
        assert "- https://docs.mistral.ai/models/mistral-medium" in text
        assert "Results: 2 pages" in text
    text = _call(mcp_server, "mistral_docs_search", {"q": "/models", "kind": "doc"})
    assert "Results: no page under https://docs.mistral.ai/models at this commit." in text


def test_search_with_a_prefix_no_page_has_names_the_nearest_parent(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()
    text = _call(
        mcp_server,
        "mistral_docs_search",
        {"q": "https://docs.mistral.ai/capabilities/evaluation/metrics"},
    )
    assert "Results: no page under https://docs.mistral.ai/capabilities/evaluation/metrics" in text
    assert text.rstrip().endswith(
        'next: mistral_docs_search(q="https://docs.mistral.ai/capabilities") lists the pages '
        "that do exist there."
    )
    text = _call(mcp_server, "mistral_docs_search", {"q": "https://docs.mistral.ai/nowhere"})
    assert "next: search with words from the question instead of a URL." in text


def test_search_with_words_still_reaches_the_index(mcp_server: Any) -> None:
    engine = FakeEngine()
    mcp_server._engine = engine
    _call(mcp_server, "mistral_docs_search", {"q": "capabilities embeddings"})
    assert len(engine.search_calls) == 1


def test_unknown_parameters_are_rejected_naming_the_right_one(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()
    text = _call_error(mcp_server, "mistral_docs_search", {"q": "alpha", "max_hit": 3})
    assert "E_BAD_PARAM" in text
    assert "max_hit" in text
    assert "did you mean max_hit= → max_hits=" in text
    assert "accepts: kind, max_hits, q" in text


def test_a_host_argument_is_dropped_before_validation(mcp_server: Any) -> None:
    engine = FakeEngine()
    mcp_server._engine = engine
    text = _call(
        mcp_server, "mistral_docs_search", {"q": "alpha", "_confirmationReason": "user asked"}
    )
    assert "Results: 1 hits" in text
    assert engine.search_calls[0]["query"] == "alpha"


def test_busy_tells_the_caller_to_retry_the_identical_call(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()
    slots = mcp_server._ADMISSION_SLOTS

    async def fill_and_call() -> str:
        for _ in range(slots):
            await mcp_server._admission.acquire()
        try:
            with pytest.raises(ToolError) as excinfo:
                await mcp_server.mcp.call_tool("mistral_docs_search", {"q": "alpha"})
            return str(excinfo.value)
        finally:
            for _ in range(slots):
                mcp_server._admission.release()

    text = asyncio.run(fill_and_call())
    assert "E_BUSY" in text
    assert "retry the identical call" in text


def test_upstream_failure_is_typed_with_a_retry_hint(mcp_server: Any) -> None:
    class Broken(FakeEngine):
        async def search(self, *args: Any, **kwargs: Any) -> list[Hit]:
            raise RetrieverException("vespa down")

    mcp_server._engine = Broken()
    text = _call_error(mcp_server, "mistral_docs_search", {"q": "alpha"})
    assert "E_UPSTREAM" in text
    assert "vespa down" in text
    assert "retry the identical call" in text
    assert not mcp_server._admission.locked()


def test_read_page_returns_the_whole_page_with_section_headers(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine(
        [_hit("c1", "alpha content"), _hit("c2", "beta", anchor="b", heading="B")]
    )
    text = _call(mcp_server, "mistral_docs_read_page", {"page_url": PAGE})
    assert text.startswith(f'page: {PAGE} | "Page"')
    assert f"## {PAGE}#a-section" in text
    assert f"## {PAGE}#b" in text
    assert "alpha content" in text and "beta" in text
    assert "chunk id" not in text
    assert text.rstrip().endswith("Results: 2 sections, the whole page.")


def test_read_page_strips_an_anchor_from_the_url(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine()
    text = _call(mcp_server, "mistral_docs_read_page", {"page_url": f"{PAGE}#a-section"})
    assert text.startswith(f'page: {PAGE} | "Page"')


def test_read_page_prints_one_header_per_section_not_per_chunk(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine([_hit("c1", "first half"), _hit("c2", "second half")])
    text = _call(mcp_server, "mistral_docs_read_page", {"page_url": PAGE})
    assert text.count(f"## {PAGE}#a-section") == 1
    assert "first half" in text and "second half" in text


def test_read_page_stops_at_the_budget_and_names_the_remaining_sections(
    mcp_server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    hits = [_hit(f"c{i}", "x" * 300, anchor=f"s{i}", heading=f"S{i}") for i in range(1, 6)]
    mcp_server._engine = FakeEngine(hits)
    monkeypatch.setattr(mcp_server, "READ_MAX_CHARS", 800)
    text = _call(mcp_server, "mistral_docs_read_page", {"page_url": PAGE})
    assert "Results: 2 of 5 sections; the page continues." in text
    assert f'next: mistral_docs_read_page(page_url="{PAGE}", section="s3")' in text
    assert "remaining sections: s3, s4, s5" in text


def test_read_page_section_returns_it_with_its_neighbours(mcp_server: Any) -> None:
    hits = [_hit(f"c{i}", f"text {i}", anchor=f"s{i}", heading=f"S{i}") for i in range(1, 6)]
    mcp_server._engine = FakeEngine(hits)
    text = _call(mcp_server, "mistral_docs_read_page", {"page_url": PAGE, "section": "s3"})
    assert "| section: s3" in text
    assert "text 2" in text and "text 3" in text and "text 4" in text
    assert "text 1" not in text and "text 5" not in text
    assert text.rstrip().endswith("Results: 3 sections, the whole section.")


def test_read_page_section_matches_a_heading_when_the_page_has_no_anchors(
    mcp_server: Any,
) -> None:
    hits = [
        _hit("c1", "intro", anchor=None, heading="Intro"),
        _hit("c2", "the batch rows", anchor=None, heading="Batch"),
    ]
    mcp_server._engine = FakeEngine(hits)
    text = _call(mcp_server, "mistral_docs_read_page", {"page_url": PAGE, "section": "batch"})
    assert "the batch rows" in text
    assert f"## {PAGE}\n    Page > Batch" in text


def test_read_page_unknown_section_lists_the_sections_the_page_has(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine(
        [_hit("c1", "alpha"), _hit("c2", "beta", anchor="b", heading="B")]
    )
    text = _call_error(mcp_server, "mistral_docs_read_page", {"page_url": PAGE, "section": "zzz"})
    assert "E_BAD_PARAM" in text
    assert 'no section "zzz"' in text
    assert "sections on this page: a-section, b" in text


def test_read_page_unknown_page_is_a_typed_error(mcp_server: Any) -> None:
    mcp_server._engine = FakeEngine(missing_page=True)
    text = _call_error(
        mcp_server, "mistral_docs_read_page", {"page_url": "https://docs.mistral.ai/nope"}
    )
    assert "E_UNKNOWN_PAGE" in text
    assert "exactly as a mistral_docs_search hit printed it" in text


def test_read_page_asks_the_index_for_the_whole_page_under_the_vespa_limit(mcp_server: Any) -> None:
    calls: list[int] = []

    class Recording(FakeNavigation):
        async def read(self, start: Any = None, end: Any = None, top_k: int = 20) -> list[Hit]:
            calls.append(top_k)
            return await super().read(start, end, top_k)

    class RecordingEngine(FakeEngine):
        def navigation_at(self, page_url: str, start: int = 0, end: int = 0) -> FakeNavigation:
            return Recording(self.hits)

    engine = RecordingEngine()
    mcp_server._engine = engine
    _call(mcp_server, "mistral_docs_read_page", {"page_url": PAGE})
    assert calls == [mcp_server.READ_TOP_K]
    assert mcp_server.READ_TOP_K <= 400


def test_history_requires_exactly_one_form(mcp_server: Any) -> None:
    text = _call_error(mcp_server, "mistral_docs_history", {})
    assert "exactly one of text, section or question" in text
    text = _call_error(mcp_server, "mistral_docs_history", {"text": "a", "section": "b"})
    assert "exactly one of" in text


def test_history_text_prints_first_last_and_count(
    mcp_server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake(text: str, manifest: Any) -> dict[str, Any]:
        return {
            "form": "text",
            "text": text,
            "first": {"snapshot": "2026-06-01", "page": PAGE, "fragment_url": PAGE},
            "last": {"snapshot": "2026-09-07", "page": PAGE, "fragment_url": PAGE},
            "snapshots_found": 8,
        }

    monkeypatch.setattr(mcp_server.history_service, "phrase_history", fake)
    text = _call(mcp_server, "mistral_docs_history", {"text": "a phrase"})
    assert f"first: 2026-06-01 | {PAGE}" in text
    assert f"last: 2026-09-07 | {PAGE}" in text
    assert "Results: present in 8 snapshots" in text


def test_history_section_renders_states_and_diffs(
    mcp_server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake(section: str, manifest: Any) -> dict[str, Any]:
        return {
            "form": "section",
            "section": section,
            "states": [
                {"snapshot": "2026-06-01", "state": "same", "page": PAGE, "anchor": "a"},
                {
                    "snapshot": "2026-06-15",
                    "state": "changed",
                    "page": PAGE,
                    "anchor": "a",
                    "diff": "-old\n+new",
                    "diff_truncated": False,
                },
            ],
        }

    monkeypatch.setattr(mcp_server.history_service, "section_history", fake)
    text = _call(mcp_server, "mistral_docs_history", {"section": f"{PAGE}#a"})
    assert f"2026-06-01: same | {PAGE}#a" in text
    assert "```diff\n-old\n+new\n```" in text
    assert "Results: 2 of 2 stored snapshots" in text


def test_history_stops_at_its_budget_and_names_the_next_call(
    mcp_server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake(section: str, manifest: Any) -> dict[str, Any]:
        return {
            "form": "section",
            "section": section,
            "states": [
                {"snapshot": f"2026-0{i}-01", "state": "changed", "page": PAGE, "diff": "x" * 500}
                for i in range(1, 6)
            ],
        }

    monkeypatch.setattr(mcp_server.history_service, "section_history", fake)
    monkeypatch.setattr(mcp_server, "HISTORY_MAX_CHARS", 1200)
    text = _call(mcp_server, "mistral_docs_history", {"section": PAGE})
    assert "Results: 2 of 5 stored snapshots" in text
    assert "after 2026-02-01 were not rendered" in text


def test_history_question_runs_without_the_reranker(mcp_server: Any) -> None:
    config = mcp_server.RetrievalConfig.shipped(variant="snap1024", snapshot="2026-06-01", top_k=1)
    assert config.rerank is True
    engine = mcp_server._snapshot_engine(config)
    assert engine.config.rerank is False


def test_health_lists_pages_chunks_and_the_three_tools(
    mcp_server: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    from starlette.testclient import TestClient

    mcp_server._engine = FakeEngine()

    class Probe:
        def as_dict(self) -> dict[str, Any]:
            return {"variant": "sec1024"}

    async def fake_probe(variant: str) -> Probe:
        return Probe()

    monkeypatch.setattr(mcp_server, "check_embedding_once", fake_probe)
    with TestClient(mcp_server.build_http_app()) as client:
        body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["chunks"] == 4430
    assert body["pages"] == len(mcp_server._PAGE_SIZES) > 0
    assert body["tools"] == [
        "mistral_docs_search",
        "mistral_docs_read_page",
        "mistral_docs_history",
    ]


def test_landing_and_favicon_need_no_token_but_the_endpoint_does(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from starlette.testclient import TestClient

    server = _reload_with(monkeypatch, GLOSSATOR_MCP_TOKEN="secret")
    server._engine = FakeEngine()
    with TestClient(server.build_http_app()) as client:
        landing = client.get("/")
        assert landing.status_code == 200
        assert "Mistral documentation search" in landing.text
        assert "/favicon.svg" in landing.text
        icon = client.get("/favicon.svg")
        assert icon.status_code == 200
        assert icon.headers["content-type"].startswith("image/svg+xml")
        assert client.get("/favicon.ico").status_code == 200
        denied = client.post("/mcp", json={})
        assert denied.status_code == 401
        assert denied.json()["error"]["code"] == "E_UNAUTHORIZED"
