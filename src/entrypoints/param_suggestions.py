"""Name suggestions for unknown request parameters, shared by both surfaces.

D-029 requires an unknown parameter to be rejected with ``E_BAD_PARAM`` naming
the right one. The alias table covers the names callers reach for by habit;
``difflib`` covers the near misses. Both the API's body validation and the MCP
server's tool-argument guard resolve their suggestions through this one module,
so the two surfaces never disagree about what a caller meant.
"""

import difflib
from collections.abc import Iterable

ALIASES: dict[str, tuple[str, ...]] = {
    "q": ("query",),
    "text": ("query",),
    "search": ("query",),
    "keyword": ("query",),
    "keywords": ("query",),
    "question": ("query",),
    "limit": ("top_k",),
    "k": ("top_k",),
    "n": ("top_k",),
    "num": ("top_k",),
    "max_results": ("top_k",),
    "id": ("chunk_id",),
    "chunk": ("chunk_id",),
    "chunkid": ("chunk_id",),
    "url": ("source_id",),
    "page": ("source_id",),
    "page_url": ("source_id",),
    "start": ("start_offset",),
    "end": ("end_offset",),
    "window_size": ("window",),
    "dir": ("direction",),
    "filter": ("kinds",),
    "lang": ("locales",),
    "language": ("locales",),
}


def suggest_field(name: str, known: Iterable[str]) -> str | None:
    """The parameter the caller probably meant, by alias first, then by closeness."""
    known_set = set(known)
    lowered = name.lower()
    for candidate in ALIASES.get(lowered, ()):
        if candidate in known_set:
            return candidate
    close = difflib.get_close_matches(lowered, sorted(known_set), n=1, cutoff=0.75)
    return close[0] if close else None


def suggest_fields(unknown: list[str], known: Iterable[str]) -> list[str]:
    """One suggestion line per unknown name, in the caller's own order."""
    return [
        f"{wrong}= → {right}=" if right else f"{wrong}= (no close match)"
        for wrong, right in ((wrong, suggest_field(wrong, known)) for wrong in unknown)
    ]


__all__ = ["ALIASES", "suggest_field", "suggest_fields"]
