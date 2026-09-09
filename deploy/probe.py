"""Health and bearer-token checks, run inside the MCP container.

``deploy.sh`` streams this file into ``docker compose exec -T mcp python -``, so
the deployment host needs no curl and no port has to be reachable from the
machine running the deploy. It prints the health JSON, then reports what the MCP
endpoint answers without a token and with one: anything but 401 then 200 means
the transport is not protecting itself (D-037).
"""

import json
import sys
import urllib.error
import urllib.request
from typing import Any

BASE = "http://127.0.0.1:8000"

INITIALIZE = json.dumps(
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "glossator-deploy", "version": "1"},
        },
    }
).encode()

JSON_RPC_HEADERS = {
    "content-type": "application/json",
    # Streamable HTTP negotiates a JSON body or an event stream; a client that
    # accepts only one of them is refused before authentication is even read.
    "accept": "application/json, text/event-stream",
}


def _status(request: urllib.request.Request) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return int(response.status), bytes(response.read())
    except urllib.error.HTTPError as error:
        return int(error.code), bytes(error.read())


def _initialize(token: str | None) -> int:
    headers: dict[str, str] = dict(JSON_RPC_HEADERS)
    if token:
        headers["authorization"] = f"Bearer {token}"
    code, _ = _status(urllib.request.Request(f"{BASE}/mcp", data=INITIALIZE, headers=headers))
    return code


def main(token: str) -> int:
    code, body = _status(urllib.request.Request(f"{BASE}/health"))
    if code != 200:
        print(f"health: HTTP {code}", file=sys.stderr)
        return 1
    health: Any = json.loads(body)
    print(json.dumps(health, indent=2))

    if not token:
        print(
            "GLOSSATOR_MCP_TOKEN is empty: the MCP transport is open to any client.",
            file=sys.stderr,
        )
        return 1

    anonymous = _initialize(None)
    authorized = _initialize(token)
    print(f"token check: without a token HTTP {anonymous}, with the token HTTP {authorized}")
    if anonymous != 401:
        print(
            f"an unauthenticated MCP call got HTTP {anonymous}; the token is not enforced",
            file=sys.stderr,
        )
        return 1
    if authorized != 200:
        print(f"the configured token got HTTP {authorized}", file=sys.stderr)
        return 1
    if health.get("status") != "ok":
        print(f"the server reports status {health.get('status')!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
