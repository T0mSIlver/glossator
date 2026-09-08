"""MCP server exposing search and navigation over the indexed documentation.

Read-only on purpose. The corpus is vendored and indexed by `make ingest` from a
manifest whose hashes are checked, so every chunk in the index can be traced to a
committed page at a known upstream commit. A tool that let an agent push an
arbitrary URL or a page of OCR output into the same index would break that: those
chunks carry no url, anchor or kind, so they can never be cited or filtered, and
nothing downstream could tell them from documentation.
"""

import argparse
import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from mistralai.search.toolkit.search import GrepMode, NavigationDirection

from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import Hit, SearchEngine

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Startup — fail fast if the environment is misconfigured
# ---------------------------------------------------------------------------

if not os.environ.get("MISTRAL_API_KEY"):
    raise RuntimeError("MISTRAL_API_KEY is not set. Check your .env file.")

# Which index variant this server serves. Schema names are owned by the index
# package, so the environment names a variant rather than a Vespa collection.
_variant_name = os.environ.get("GLOSSATOR_VARIANT", "sec1024")

# Building the engine resolves the variant, matches the embedder to its model, and
# checks that the schema supports navigation — all before the first request.
_engine = SearchEngine(RetrievalConfig(variant=_variant_name))

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "Mistral documentation",
    instructions=(
        "Search and navigate Mistral's documentation.\n\n"
        "Retrieval loop: start with `search` to find relevant sections across the "
        "documentation, then drill into a promising hit *within its page* without "
        "re-running a global search:\n"
        "- `open`     — expand context around a chunk by its `id` (`window` controls the radius)\n"
        "- `grep`     — jump to an exact term or phrase in the same page\n"
        "- `navigate` — step sequentially through adjacent chunks\n"
        "- `read`     — fetch a known offset range directly (no context expansion)\n"
        "Then call `search` again with a query informed by what you have read to "
        "connect information across pages.\n\n"
        "Every result carries `citation_url` (the page, deep-linked to the section "
        "when it has an anchor) and `heading_path`; cite those, and quote only text "
        "that appears in `content`."
    ),
)


def _format_hits(hits: list[Hit]) -> list[dict]:
    """Serialise hits into the shape the agent loop drives.

    Includes the chunk `id` (pass to open()) and start_offset / end_offset (pass to
    navigate() / read()), plus the citation fields an answer has to carry.
    """
    return [
        {
            "id": hit.chunk_id,
            "score": hit.score,
            "citation_url": hit.citation_url,
            "url": hit.url,
            "anchor": hit.anchor,
            "page_title": hit.page_title,
            "heading_path": list(hit.heading_path),
            "kind": hit.kind,
            "content": hit.content,
            "source_id": hit.source_id,
            "start_offset": hit.start_offset,
            "end_offset": hit.end_offset,
        }
        for hit in hits
    ]


@mcp.tool()
async def search(
    query: str, top_k: int = 5, exclude_ids: list[str] | None = None
) -> list[dict]:
    """Search the documentation and return the most relevant sections.

    Args:
        query:       Natural-language search query.
        top_k:       Maximum number of results to return (default 5).
        exclude_ids: Chunk `id`s to skip at query time — e.g. chunks already
                     seen earlier in an agentic loop, so each search surfaces
                     fresh context instead of repeating hits.
    """
    hits = await _engine.search(
        query, exclude_ids=set(exclude_ids) if exclude_ids else None, top_k=top_k
    )
    return _format_hits(hits)


@mcp.tool()
async def open(chunk_id: str, window: int = 2) -> list[dict]:
    """Expand context around a chunk from search: return it plus adjacent chunks in reading order.

    Pass the `id` of a chunk from a search() result; the server resolves its
    position and pulls in `window` neighbouring chunks on each side. When you
    already know the exact offset range and want those chunks verbatim, use
    read() instead.

    Args:
        chunk_id: `id` of a chunk from a search() result.
        window:   Number of adjacent chunks to fetch in each direction (default 2).
    """
    anchor = await _engine.get_chunk(chunk_id)
    if anchor is None or anchor.navigation is None:
        raise ToolError(f"chunk not found: {chunk_id!r}")
    return _format_hits(await anchor.navigation.around(window=window))


@mcp.tool()
async def navigate(
    source_id: str,
    start_offset: int,
    end_offset: int,
    direction: str,
    top_k: int = 1,
) -> list[dict]:
    """Step forward or backward through a page from a known position.

    Args:
        source_id:    Source identifier from a search() or open() result.
        start_offset: start_offset of the current anchor chunk.
        end_offset:   end_offset of the current anchor chunk.
        direction:    "next" to move forward, "previous" to move backward.
        top_k:        Number of chunks to retrieve in the given direction (default 1).
    """
    navigation = _engine.navigation_at(source_id, start_offset, end_offset)
    if NavigationDirection(direction) == NavigationDirection.PREVIOUS:
        return _format_hits(await navigation.previous(top_k=top_k))
    return _format_hits(await navigation.next(top_k=top_k))


@mcp.tool()
async def read(
    source_id: str,
    start_offset: int | None = None,
    end_offset: int | None = None,
    top_k: int = 20,
) -> list[dict]:
    """Fetch chunks from a known offset range: direct access, no context expansion.

    Use when you already know the page and the exact range you want, and just
    want those chunks back as-is (unlike open(), which expands around a chunk).
    Pass None for start_offset to read from the beginning, or None for
    end_offset to read to the end of the page.

    Args:
        source_id:    Source identifier from a search() result.
        start_offset: Inclusive lower bound (None = start of page).
        end_offset:   Exclusive upper bound (None = end of page).
        top_k:        Maximum number of chunks to return (default 20).
    """
    navigation = _engine.navigation_at(source_id)
    return _format_hits(await navigation.read(start_offset, end_offset, top_k=top_k))


@mcp.tool()
async def grep(
    source_id: str,
    pattern: str,
    mode: str = "phrase",
    top_k: int = 5,
) -> list[dict]:
    """Lexical search for an exact term or phrase within a single page.

    Args:
        source_id: Source identifier from a search() result.
        pattern:   Text to search for.
        mode:      "phrase" (default) — terms must appear in exact order;
                   "term" — all terms must appear but in any order.
        top_k:     Maximum number of matching chunks to return (default 5).
    """
    navigation = _engine.navigation_at(source_id)
    return _format_hits(
        await navigation.grep(pattern, mode=GrepMode(mode), top_k=top_k)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the MCP server.")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Start in HTTP (streamable-HTTP) mode instead of the default stdio mode.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host (HTTP mode only, default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port (HTTP mode only, default: 8000).",
    )
    args = parser.parse_args()

    if args.http:
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()
