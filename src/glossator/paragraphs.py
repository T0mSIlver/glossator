"""Markdown text cut where the rendered page starts a new block (D-036c).

A browser matches a text fragment directive inside one block element only, so
every phrase put in a link has to be taken from one of these pieces."""

from __future__ import annotations

import re

_PARAGRAPH_BREAK = re.compile(r"\n[ \t>]*\n")
"""A blank line, or a blockquote line with nothing on it: the page renders a new
block either way."""
_LIST_ITEM = re.compile(r"^[ \t]*(?:[-*]|\d+\.)[ \t]", re.M)
"""A list item renders as its own ``<li>`` even with no blank line above it. The
space after the marker keeps ``**bold**`` at a line start from counting."""


def without_list_marker(block: str) -> str:
    """A block without its leading ``-``, ``*`` or ``1.``, which renders as a bullet
    or a number and never as text a directive can match."""
    block = block.lstrip("\n")
    marker = _LIST_ITEM.match(block)
    return block[marker.end() :] if marker else block


def paragraphs(text: str) -> list[str]:
    """The non-blank blocks of ``text``, in order, each with its own characters."""
    blocks: list[str] = []
    for paragraph in _PARAGRAPH_BREAK.split(text):
        cuts = [match.start() for match in _LIST_ITEM.finditer(paragraph)]
        for start, end in zip([0, *cuts], [*cuts, len(paragraph)], strict=True):
            if paragraph[start:end].strip():
                blocks.append(paragraph[start:end])
    return blocks
