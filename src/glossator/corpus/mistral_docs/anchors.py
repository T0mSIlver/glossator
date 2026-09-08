"""Heading anchors, ported from the docs site so emitted links resolve live.

Ports `src/lib/heading-utils.ts` (`slugify`, `uniqueHeadingId`) and the heading level
that `src/components/layout/section-tab/index.tsx` renders for a `<SectionTab>`.
"""

from __future__ import annotations

import re

# JavaScript's \w inside a character class is exactly [A-Za-z0-9_]; Python's \w is
# unicode-aware and would keep accented letters that the site strips.
_NON_WORD = re.compile(r"[^A-Za-z0-9_\s-]")
_SPACES = re.compile(r"\s+")
_DASHES = re.compile(r"-+")
_EDGE_DASH = re.compile(r"^-|-$")

FALLBACK_ANCHOR = "heading"


def slugify(text: str) -> str:
    """Port of `slugify` in `src/lib/heading-utils.ts`."""
    if not text:
        return FALLBACK_ANCHOR
    out = text.lower()
    out = _NON_WORD.sub("", out)
    out = out.strip()
    out = _SPACES.sub("-", out)
    out = _DASHES.sub("-", out)
    out = _EDGE_DASH.sub("", out)
    return out


class AnchorAllocator:
    """Port of `uniqueHeadingId`: `-1`, `-2`, ... suffixes for repeated slugs.

    One allocator per page; explicit ids (a `sectionId` prop) are reserved through
    `reserve` so a later generated slug cannot collide with them.
    """

    def __init__(self) -> None:
        self._used: set[str] = set()

    def reserve(self, anchor: str) -> str:
        self._used.add(anchor)
        return anchor

    def allocate(self, text: str) -> str:
        base = slugify(text) or FALLBACK_ANCHOR
        final = base
        counter = 0
        while final in self._used:
            counter += 1
            final = f"{base}-{counter}"
        self._used.add(final)
        return final


def section_tab_level(as_prop: str | None, variant: str | None) -> int:
    """Heading level a `<SectionTab>` renders as.

    Mirrors `semanticAs` in the SectionTab component: the secondary variant demotes
    h1/h2 to h3, and a plain h1 is demoted to h2 because the page title already owns
    the document's single h1.
    """
    as_value = as_prop if as_prop in {"h1", "h2", "h3", "h4", "h5", "h6"} else "h2"
    if variant == "secondary" and as_value in {"h1", "h2"}:
        return 3
    if as_value == "h1":
        return 2
    return int(as_value[1])
