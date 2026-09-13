"""The one typed failure both entrypoints report: a code, a message, the next call."""

from typing import Literal

import structlog

from glossator.surface.names import SEARCH

logger = structlog.get_logger(__name__)

ErrorCode = Literal["E_BAD_PARAM", "E_UNKNOWN_PAGE", "E_BUSY", "E_UPSTREAM"]


class SurfaceError(Exception):
    """A failure the caller can act on. The MCP entrypoint prints it as tool text
    and the HTTP API picks a status code from ``code``; nothing else maps it."""

    def __init__(self, code: ErrorCode, message: str, next_hint: str) -> None:
        super().__init__(message)
        self.code: ErrorCode = code
        self.message = message
        self.next_hint = next_hint


def bad_param(message: str, next_hint: str) -> SurfaceError:
    return SurfaceError("E_BAD_PARAM", message, next_hint)


def unknown_page(page_url: str) -> SurfaceError:
    return SurfaceError(
        "E_UNKNOWN_PAGE",
        f'no indexed page has the URL "{page_url}".',
        f"pass a page URL exactly as a {SEARCH} hit printed it, without the #anchor.",
    )


def busy(slots: int) -> SurfaceError:
    return SurfaceError(
        "E_BUSY",
        f"the server is already running {slots} concurrent calls.",
        "retry the identical call; do not reformulate it.",
    )


def upstream(operation: str, cause: Exception, target: str = "the search index") -> SurfaceError:
    logger.warning("Upstream failure", operation=operation, error=str(cause))
    return SurfaceError(
        "E_UPSTREAM",
        f"{operation} failed against {target}: {cause}",
        "retry the identical call; if it repeats, say the documentation server is down.",
    )


__all__ = ["ErrorCode", "SurfaceError", "bad_param", "busy", "unknown_page", "upstream"]
