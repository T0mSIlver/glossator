"""Recognising this server's tools among every name a harness reports."""

from __future__ import annotations

from glossator.eval.consumer.models import ToolCallRecord

NAMESPACED_TOOLS = (
    "mistral_docs_search",
    "mistral_docs_open_section",
    "mistral_docs_step",
    "mistral_docs_read_page",
    "mistral_docs_find_on_page",
    "mistral_docs_answer",
    "mistral_docs_verify_quotes",
    "mistral_docs_history",
)
"""Every tool name this server has served. The surface is three tools since
D-044; the other five stay here so runs recorded before then keep reading."""

LEGACY_TOOLS = ("search", "open", "navigate", "read", "grep", "ask", "cite", "history")
"""The names the tools had before they were namespaced, so recorded runs keep
reading the way they did when they were collected. Every harness has a built-in
called `read` or `websearch`, so these count only behind a server prefix."""

TOOL_SUFFIXES = NAMESPACED_TOOLS + LEGACY_TOOLS

SERVER_PREFIXES = ("glossator", "mistral-docs", "mistral_docs")
"""What the consumers' clients have called this server. A harness prefixes a
tool with the server's name -- `glossator_search`,
`mistral-docs__mistral_docs_search`, `mcp__mistral-docs__mistral_docs_search`
-- and that prefix is what separates our `search` from the harness's own."""

VERIFY_TOOLS = ("mistral_docs_verify_quotes",)
LEGACY_VERIFY_TOOLS = ("cite",)
VERIFY_SUFFIXES = VERIFY_TOOLS + LEGACY_VERIFY_TOOLS
"""The quote checker, under either name."""


def _names_this_server(name: str, tool: str, *, bare: bool) -> bool:
    """Whether one harness tool name names this server's ``tool``."""
    if name == tool:
        return bare
    if not name.endswith(tool):
        return False
    prefix = name[: -len(tool)]
    return prefix.endswith("__") or prefix.rstrip("_").endswith(SERVER_PREFIXES)


def is_server_tool(name: str) -> bool:
    """Whether one harness tool name is one of this server's tools."""
    return any(_names_this_server(name, tool, bare=True) for tool in NAMESPACED_TOOLS) or any(
        _names_this_server(name, tool, bare=False) for tool in LEGACY_TOOLS
    )


def is_verify_tool(name: str) -> bool:
    """Whether one harness tool name is the quote checker."""
    return any(_names_this_server(name, tool, bare=True) for tool in VERIFY_TOOLS) or any(
        _names_this_server(name, tool, bare=False) for tool in LEGACY_VERIFY_TOOLS
    )


def asked_for_rerank(call: ToolCallRecord) -> bool:
    """Whether a recorded pre-D-044 search requested the listwise reranker."""
    return is_server_tool(call.name) and call.arguments.get("rerank", "").casefold() == "true"


MCP_SERVER_NAME = "mistral-docs"
"""What the consumer's client calls this server. Harnesses prefix tool names
with it, and the name a consumer reads is the server's own."""

TOKEN_ENV_VAR = "GLOSSATOR_MCP_TOKEN"
