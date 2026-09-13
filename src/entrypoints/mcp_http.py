"""The MCP server's HTTP transport pieces: bearer auth, the favicon, the landing page."""

import hmac
from collections.abc import Iterable

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

PUBLIC_PATHS = frozenset({"/", "/health", "/favicon.ico", "/favicon.svg"})

FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="12" fill="#1f1f1f"/>'
    '<rect x="14" y="14" width="36" height="36" rx="4" fill="#ff7000"/>'
    '<rect x="20" y="22" width="24" height="4" fill="#1f1f1f"/>'
    '<rect x="20" y="30" width="24" height="4" fill="#1f1f1f"/>'
    '<rect x="20" y="38" width="16" height="4" fill="#1f1f1f"/>'
    "</svg>"
)


class BearerAuthMiddleware:
    """One shared secret on the HTTP transport (D-037). The landing page, the
    health check and the favicon need no token."""

    def __init__(self, app: ASGIApp, token: str) -> None:
        self.app = app
        self.token = token

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return
        if scope["type"] != "http":
            if scope["type"] == "websocket":
                await send({"type": "websocket.close", "code": 1008})
            return
        if scope.get("path") in PUBLIC_PATHS:
            await self.app(scope, receive, send)
            return
        headers = {
            name.decode("latin-1").lower(): value.decode("latin-1")
            for name, value in scope.get("headers", [])
        }
        if not hmac.compare_digest(headers.get("authorization", ""), f"Bearer {self.token}"):
            response = JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "E_UNAUTHORIZED",
                        "message": "send 'Authorization: Bearer <token>'.",
                        "next": "retry with the GLOSSATOR_MCP_TOKEN value; GET /health needs none.",
                    }
                },
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


def landing_page(title: str, page_count: int, tools: Iterable[str], repository_url: str) -> str:
    items = "".join(f"<li><code>{name}</code></li>" for name in tools)
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        f"<title>{title}</title>"
        "<link rel='icon' type='image/svg+xml' href='/favicon.svg'>"
        "<style>body{font:16px/1.5 system-ui,sans-serif;max-width:40rem;margin:4rem auto;"
        "padding:0 1rem;color:#1f1f1f}code{background:#f2f2f2;padding:0 .3em}</style>"
        f"</head><body><h1>{title}</h1>"
        f"<p>An MCP server over {page_count} pages of docs.mistral.ai at a pinned commit. "
        "The endpoint is <code>/mcp</code> over Streamable HTTP with a bearer token; "
        "<code>/health</code> is open.</p>"
        f"<ul>{items}</ul>"
        f"<p><a href='{repository_url}'>Source and evaluation</a></p></body></html>"
    )


__all__ = ["FAVICON_SVG", "PUBLIC_PATHS", "BearerAuthMiddleware", "landing_page"]
