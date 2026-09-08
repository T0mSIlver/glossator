"""The MCP surface keeps the shape the agent loop depends on.

The round-trip test covers storing and finding a document; this one covers the seam
the MCP server owns on top of that.

- The server is read-only. `ingest` and `delete` are deliberately absent: the index
  is built from a vendored, hash-checked corpus, and a chunk fed in from an
  arbitrary URL would carry no url, anchor or kind and could never be cited.
- `open(chunk_id, window)` -- "I have a chunk from search, show me context around
  it." The caller passes only the opaque chunk `id`; the server resolves its
  position and pulls in neighbours. If this silently reverts to taking raw offsets,
  the tool becomes indistinguishable from `read` and the distinction the docs teach
  stops being true.
- `read(source_id, start_offset, end_offset)` -- "I know the exact range, give me
  those chunks." Offset-addressed, no expansion.
- Every result carries a citation target, because an answer built on these tools has
  to cite one.

No backend and no API key are needed: the tools are exercised against a fake store
and a recording engine, and the schema is read off the registered tools.
`mcp_server` fails fast at import without `MISTRAL_API_KEY` and loads `.env` with
`override=True`, so the fixture neutralises the dotenv load and sets a placeholder
key -- it is never used to make a call.
"""

import asyncio
import importlib

import pytest
from mistralai.search.toolkit.document import ChunkType
from mistralai.search.toolkit.search import NavigationDirection
from mistralai.search.toolkit.search.models import SearchResult, SearchResultChunk

from glossator.retrieval.engine import Hit


@pytest.fixture
def mcp_server(monkeypatch: pytest.MonkeyPatch):
    """Import `entrypoints.mcp_server` offline, with a placeholder key and dotenv disabled.

    The module reads `.env` with `override=True` at import; a real key there would
    clobber the placeholder set here. Neutralising `load_dotenv` before (re)import
    lets the placeholder stand so the import-time fail-fast passes.
    """
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key-not-used")

    import entrypoints.mcp_server as module

    return importlib.reload(module)


def _result(chunk_id: str, start: int, end: int, content: str) -> SearchResult:
    chunk = SearchResultChunk(
        id=chunk_id,
        source_id="https://docs.mistral.ai/page",
        locator=f"char:{start}-{end}",
        content=content,
        start_offset=start,
        end_offset=end,
        chunk_type=ChunkType.CONTENT,
        metadata={
            "url": "https://docs.mistral.ai/page",
            "anchor": "a-section",
            "page_title": "Page",
            "heading_path": ["Page", "A section"],
            "kind": "doc",
            "locale": "en",
            "section_index": 1,
        },
    )
    return SearchResult(score=0.5, chunk=chunk)


class _FakeStore:
    """Minimal `NavigableIndex` stand-in: one chunk and one neighbour each way."""

    async def get_chunk(self, chunk_id: str, **_: object) -> SearchResult | None:
        return _result("c2", 10, 20, "anchor") if chunk_id == "c2" else None

    async def navigate(
        self,
        source_id: str,
        start: int,
        end: int,
        direction: NavigationDirection,
        *,
        top_k: int = 1,
        **_: object,
    ) -> list[SearchResult]:
        if direction == NavigationDirection.PREVIOUS:
            return [_result("c1", 0, 10, "before")]
        return [_result("c3", 20, 30, "after")]

    async def read(
        self, source_id: str, start: int | None, end: int | None, **_: object
    ) -> list[SearchResult]:
        return [_result("c2", 10, 20, "anchor")]

    async def grep(
        self, source_id: str, pattern: str, **_: object
    ) -> list[SearchResult]:
        return [_result("c2", 10, 20, "anchor")]


def _tool_fn(module, name: str):
    # `open` shadows the builtin; @mcp.tool() wraps every tool, so reach the
    # coroutine through `.fn`.
    tool = getattr(module, name)
    return getattr(tool, "fn", tool)


class _RecordingEngine:
    """Captures the kwargs `search` forwards, returns one canned hit."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def search(self, query: str, **kwargs: object) -> list[Hit]:
        self.calls.append({"query": query, **kwargs})
        return [
            Hit(
                chunk_id="c1",
                score=0.5,
                url="https://docs.mistral.ai/page",
                anchor="a-section",
                heading_path=("Page", "A section"),
                page_title="Page",
                kind="doc",
                locale="en",
                section_index=1,
                content="hit",
                source_id="https://docs.mistral.ai/page",
                start_offset=0,
                end_offset=10,
            )
        ]


def test_the_server_exposes_no_write_tools(mcp_server) -> None:
    """A vendored, hash-checked index must not be writable from an agent loop."""
    tools = asyncio.run(mcp_server.mcp.list_tools())

    assert {tool.name for tool in tools} == {
        "search",
        "open",
        "navigate",
        "read",
        "grep",
    }


def test_search_exposes_exclude_ids(mcp_server) -> None:
    search_tool = asyncio.run(mcp_server.mcp.get_tool("search"))
    props = search_tool.parameters["properties"]

    assert "exclude_ids" in props
    # Only `query` is mandatory; exclude_ids stays optional.
    assert search_tool.parameters.get("required") == ["query"]


def test_search_forwards_exclude_ids_as_a_set(
    mcp_server, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _RecordingEngine()
    monkeypatch.setattr(mcp_server, "_engine", engine)

    asyncio.run(_tool_fn(mcp_server, "search")("q", exclude_ids=["a", "b", "a"]))

    assert engine.calls[0]["exclude_ids"] == {"a", "b"}


def test_search_defaults_exclude_ids_to_none(
    mcp_server, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _RecordingEngine()
    monkeypatch.setattr(mcp_server, "_engine", engine)

    asyncio.run(_tool_fn(mcp_server, "search")("q"))

    # Empty/absent stays None so the backend skips the filter entirely.
    assert engine.calls[0]["exclude_ids"] is None


def test_search_asks_the_engine_for_the_requested_depth(
    mcp_server, monkeypatch: pytest.MonkeyPatch
) -> None:
    """top_k reaches the query rather than truncating a fixed-size result list."""
    engine = _RecordingEngine()
    monkeypatch.setattr(mcp_server, "_engine", engine)

    asyncio.run(_tool_fn(mcp_server, "search")("q", top_k=25))

    assert engine.calls[0]["top_k"] == 25


def test_results_carry_a_citation_target(
    mcp_server, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(mcp_server, "_engine", _RecordingEngine())

    out = asyncio.run(_tool_fn(mcp_server, "search")("q"))

    assert out[0]["citation_url"] == "https://docs.mistral.ai/page#a-section"
    assert out[0]["heading_path"] == ["Page", "A section"]


def test_open_takes_a_chunk_id_and_read_stays_offset_addressed(mcp_server) -> None:
    open_tool = asyncio.run(mcp_server.mcp.get_tool("open"))
    read_tool = asyncio.run(mcp_server.mcp.get_tool("read"))

    assert set(open_tool.parameters["properties"]) == {"chunk_id", "window"}
    assert open_tool.parameters.get("required") == ["chunk_id"]

    read_props = read_tool.parameters["properties"]
    assert "start_offset" in read_props and "end_offset" in read_props
    assert "chunk_id" not in read_props


def test_open_resolves_the_chunk_and_windows_around_it(
    mcp_server, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(mcp_server._engine, "navigation_index", _FakeStore())

    out = asyncio.run(_tool_fn(mcp_server, "open")("c2", window=1))

    # Previous neighbour, the resolved anchor, then the next neighbour -- in reading order.
    assert [row["id"] for row in out] == ["c1", "c2", "c3"]
    assert [row["content"] for row in out] == ["before", "anchor", "after"]


def test_open_raises_when_the_chunk_id_is_unknown(
    mcp_server, monkeypatch: pytest.MonkeyPatch
) -> None:
    from fastmcp.exceptions import ToolError

    monkeypatch.setattr(mcp_server._engine, "navigation_index", _FakeStore())

    with pytest.raises(ToolError):
        asyncio.run(_tool_fn(mcp_server, "open")("does-not-exist"))
