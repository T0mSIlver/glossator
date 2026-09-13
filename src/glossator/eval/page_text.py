"""What a browser can match a text fragment against: the page's visible text,
block by block, and the ``:~:text=`` directive parsed out of a link."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

_DIRECTIVE = ":~:text="
_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True, slots=True)
class FragmentText:
    start: str
    end: str | None = None

    @property
    def json_value(self) -> str | dict[str, str]:
        return self.start if self.end is None else {"start": self.start, "end": self.end}


_HIDDEN_TAGS = frozenset({"script", "style"})
_BLOCK_TAGS = frozenset(
    {
        *("p", "li", "td", "th", "pre", "blockquote", "div"),
        *("h1", "h2", "h3", "h4", "h5", "h6"),
        # Containers that hold blocks. Text rarely sits in them directly, but when
        # it does the browser still breaks the line there.
        *("ul", "ol", "dl", "dt", "dd", "table", "tr", "section", "article", "main"),
        *("header", "footer", "nav", "aside", "details", "summary", "figure", "figcaption"),
    }
)


class _VisibleBlocks(HTMLParser):
    """Visible text cut at block element boundaries. Opening and closing a block
    both end the current run, so text before a nested ``<p>`` inside an ``<li>``
    is a block of its own, as the browser lays it out."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[str] = []
        self._current: list[str] = []
        self._hidden = 0

    def _flush(self) -> None:
        text = _WHITESPACE.sub(" ", "".join(self._current)).strip()
        if text:
            self.blocks.append(text)
        self._current = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        name = tag.casefold()
        if name in _HIDDEN_TAGS:
            self._hidden += 1
        elif name in _BLOCK_TAGS:
            self._flush()

    def handle_endtag(self, tag: str) -> None:
        name = tag.casefold()
        if name in _HIDDEN_TAGS and self._hidden:
            self._hidden -= 1
        elif name in _BLOCK_TAGS:
            self._flush()

    def handle_data(self, data: str) -> None:
        if not self._hidden:
            self._current.append(data)

    def close(self) -> None:
        super().close()
        self._flush()


def visible_text(html: str) -> list[str]:
    """The page's visible text, one string per rendered block, whitespace collapsed."""
    parser = _VisibleBlocks()
    parser.feed(html)
    parser.close()
    return parser.blocks


def parse_fragment_url(url: str) -> tuple[str | None, FragmentText]:
    fragment = urlsplit(url).fragment
    anchor, separator, directive = fragment.partition(_DIRECTIVE)
    if not separator:
        raise ValueError(f"URL has no text fragment directive: {url}")
    values = directive.split(",", 1)
    start = unquote(values[0])
    end = unquote(values[1]) if len(values) == 2 else None
    return anchor or None, FragmentText(start=start, end=end)


def _fold(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip().casefold()


def fragment_found(blocks: Sequence[str], fragment: FragmentText) -> tuple[bool, str | None]:
    """Whether a browser would find the fragment on a page of these blocks.

    A plain directive, and each end of a ``start,end`` range, must sit inside one
    block: browsers do not match a phrase across a block boundary (D-036c). The
    range itself may span blocks, as long as the end follows the start. Passing
    the page joined into a single block gives the flat check D-036b measured."""
    folded = [_fold(block) for block in blocks]
    start = _fold(fragment.start)
    located = next(
        ((i, block.find(start)) for i, block in enumerate(folded) if start in block), None
    )
    if located is None:
        return False, _absent_reason(folded, start)
    if fragment.end is None:
        return True, None
    end = _fold(fragment.end)
    if not any(end in block for block in folded):
        return False, _absent_reason(folded, end)
    index, offset = located
    if end in folded[index][offset + len(start) :] or any(
        end in block for block in folded[index + 1 :]
    ):
        return True, None
    return False, "range order"


def _absent_reason(folded: Sequence[str], text: str) -> str:
    # Kept apart from "text absent" so the results show how many misses the
    # block rule adds over the flat check, rather than folding them in silently.
    return "across blocks" if text in " ".join(folded) else "text absent"


__all__ = ["FragmentText", "fragment_found", "parse_fragment_url", "visible_text"]
