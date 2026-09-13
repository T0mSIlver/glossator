"""The tool names. Results print them in ``next:`` lines, so they belong to the
surface rather than to the MCP registration."""

SEARCH = "mistral_docs_search"
READ_PAGE = "mistral_docs_read_page"
HISTORY = "mistral_docs_history"
TOOL_ORDER = (SEARCH, READ_PAGE, HISTORY)

__all__ = ["HISTORY", "READ_PAGE", "SEARCH", "TOOL_ORDER"]
