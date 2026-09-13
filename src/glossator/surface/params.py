"""Unknown parameter names: reject them, and name the parameter the caller meant."""

import difflib
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from glossator.surface.errors import SurfaceError, bad_param

_COUNTS = ("max_hits", "top_k")

ALIASES: dict[str, tuple[str, ...]] = {
    "q": ("query",),
    "text": ("query",),
    "search": ("query",),
    "keyword": ("query",),
    "keywords": ("query",),
    "question": ("query",),
    "limit": _COUNTS,
    "k": _COUNTS,
    "n": _COUNTS,
    "num": _COUNTS,
    "max_results": _COUNTS,
    "top_k": _COUNTS,
    "id": ("chunk_id",),
    "chunk": ("chunk_id",),
    "chunkid": ("chunk_id",),
    "url": ("page_url", "source_id"),
    "page": ("page_url", "source_id"),
    "page_url": ("source_id",),
    "source_id": ("page_url",),
    "start": ("start_offset",),
    "end": ("end_offset",),
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
    """Suggest a replacement for each name in input order."""
    return [
        f"{wrong}= → {right}=" if right else f"{wrong}= (no close match)"
        for wrong, right in ((wrong, suggest_field(wrong, known)) for wrong in unknown)
    ]


def guard_arguments(
    tool_name: str, arguments: Mapping[str, Any], known: Iterable[str]
) -> dict[str, Any]:
    """The arguments a tool runs with, or a typed error naming the likely parameter.

    Arguments whose name starts with an underscore belong to the host: Mistral
    Work sends `_confirmationReason` on the call that asks the user for
    approval (D-037b). They are dropped before validation.
    """
    cleaned = {key: value for key, value in arguments.items() if not key.startswith("_")}
    known_set = set(known)
    unknown = [key for key in cleaned if key not in known_set]
    if unknown:
        suggestions = suggest_fields(unknown, known_set)
        raise bad_param(
            f"unknown parameter(s) for {tool_name}: {', '.join(unknown)}; the call was not run.",
            ("did you mean " + ", ".join(suggestions) + "? " if suggestions else "")
            + f"{tool_name} accepts: {', '.join(sorted(known_set))}.",
        )
    return cleaned


def invalid_body(path: str, known: set[str], errors: Sequence[Mapping[str, Any]]) -> SurfaceError:
    """A request body that failed validation, as one error naming its fields;
    an unknown field name also gets the field the caller probably meant."""
    fields: list[str] = []
    suggestions: list[str] = []
    for error in errors:
        field = ".".join(str(part) for part in error["loc"][1:]) or str(error["loc"][0])
        if error["type"] == "extra_forbidden" and known:
            suggestions.append(suggest_fields([field], known)[0])
        fields.append(field)
    next_hint = "the response's 'message' names the fields; see /openapi.json for the schema"
    if suggestions:
        next_hint = (
            f"did you mean {'; '.join(suggestions)}? "
            f"{path} accepts: {', '.join(sorted(known))}; "
            "unknown names are rejected, not applied; see /openapi.json for the schema"
        )
    return bad_param(f"invalid request: {', '.join(fields)}", next_hint)


__all__ = ["ALIASES", "guard_arguments", "invalid_body", "suggest_field", "suggest_fields"]
