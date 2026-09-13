"""Where on docs.mistral.ai a tool argument points, whatever form the model wrote.

Models write the full URL, a ``site:`` form of it, the host with a path but no
scheme, or a bare path. The search, read and history tools share this one
reading, so a location one of them accepts is a location the others accept
(D-044a, D-046, D-049b).
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

DOCS_HOST = "docs.mistral.ai"
SITE = f"https://{DOCS_HOST}"

# The first segment of a scheme-less value is a host when it holds a dot: no
# documentation path starts with one, and a model writing
# ``docs.mistral.ai/studio/search`` means the host, not a folder of that name.
_FIRST_SEGMENT = re.compile(r"[/#?]")


def split_docs_location(value: str, name: str) -> tuple[str, str]:
    """The path and fragment ``value`` names on docs.mistral.ai.

    The path has no trailing slash, so the site root is ``""``. ``name`` is the
    argument the value came in, for the error a foreign host raises.
    """
    text = value.strip()
    if text.startswith("site:"):
        text = text[len("site:") :].strip()
    if "://" not in text:
        first = _FIRST_SEGMENT.split(text, maxsplit=1)[0]
        text = f"https://{text}" if "." in first else f"{SITE}/{text.lstrip('/')}"
    parsed = urlsplit(text)
    if parsed.netloc != DOCS_HOST:
        raise ValueError(f"{name} must be on {DOCS_HOST}")
    return parsed.path.rstrip("/"), parsed.fragment


def under_prefix(under: str) -> str:
    """The page URL an ``under`` argument names, with no trailing slash.

    The search and history tools both scope by it. A foreign host raises
    ``ValueError``, and so does an empty value: an empty prefix would silently
    widen the scope to the whole site.
    """
    if not under.strip():
        raise ValueError("under must contain a documentation path")
    path, _fragment = split_docs_location(under, "under")
    return SITE + path


__all__ = ["DOCS_HOST", "SITE", "split_docs_location", "under_prefix"]
