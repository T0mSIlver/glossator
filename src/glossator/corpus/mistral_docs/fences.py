"""Fence-aware line scanning.

Every rewrite in this adapter has to leave fenced code untouched: MDX code samples
contain `# comment` lines that look like headings and `<PLACEHOLDER>` tokens that look
like JSX. One scanner decides what is inside a fence, and everything else uses it.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass

# The prefix allows blockquote markers so a fence inside a converted `:::` callout
# is still recognized as code.
_FENCE_RE = re.compile(r"^(?P<indent>[ \t]*(?:>[ \t]*)*)(?P<delim>`{3,}|~{3,})(?P<info>.*)$")

# How much further a closing fence may be indented than its opener before it stops
# closing it, per the CommonMark fenced-code rules.
_MAX_CLOSING_INDENT_DRIFT = 3


@dataclass(frozen=True)
class FenceOpening:
    """The delimiter and indentation a fenced block was opened with."""

    delim: str
    indent: str


def fence_opening(line: str) -> FenceOpening | None:
    """The opening this line would start, or `None` if it is not a fence line."""
    match = _FENCE_RE.match(line)
    if match is None:
        return None
    return FenceOpening(delim=match.group("delim"), indent=match.group("indent"))


def closes_fence(line: str, opening: FenceOpening) -> bool:
    """Whether this line closes `opening`.

    A closing fence uses the same character at least as many times, carries no info
    string, and is not indented far past its opener.
    """
    match = _FENCE_RE.match(line)
    if match is None:
        return False
    delim = match.group("delim")
    return (
        delim[0] == opening.delim[0]
        and len(delim) >= len(opening.delim)
        and not match.group("info").strip()
        and len(match.group("indent")) <= len(opening.indent) + _MAX_CLOSING_INDENT_DRIFT
    )


def iter_lines(text: str) -> Iterator[tuple[str, bool]]:
    """Yield `(line, in_fence)` for every line, fences included as `in_fence=True`.

    Both the opening and the closing fence lines count as inside, so a rewrite that
    skips fenced lines never rewrites an info string either.
    """
    opening: FenceOpening | None = None
    for line in text.split("\n"):
        if opening is None:
            opening = fence_opening(line)
            yield line, opening is not None
            continue
        if closes_fence(line, opening):
            opening = None
        yield line, True


def map_outside_fences(text: str, transform: Callable[[str], str]) -> str:
    """Apply `transform` to each line that is not inside a fenced code block."""
    return "\n".join(line if in_fence else transform(line) for line, in_fence in iter_lines(text))


def strip_fenced_lines(text: str) -> str:
    """Drop fenced code, keeping line count-independent prose for residue checks."""
    return "\n".join(line for line, in_fence in iter_lines(text) if not in_fence)


_INLINE_CODE = re.compile(r"(`+)(?:(?!\1).)*?\1")


def strip_inline_code(text: str) -> str:
    """Blank out inline code spans.

    Placeholder tokens such as `` `<PROVIDER>_API_KEY` `` are code, not markup, so a
    residue scan has to ignore them the same way it ignores fenced blocks.
    """
    return _INLINE_CODE.sub("", text)


def collapse_blank_lines(text: str) -> str:
    """Collapse runs of blank lines outside fences to a single blank line."""
    out: list[str] = []
    blank_run = 0
    for line, in_fence in iter_lines(text):
        if in_fence:
            blank_run = 0
            out.append(line)
            continue
        if line.strip():
            blank_run = 0
            out.append(line.rstrip())
            continue
        blank_run += 1
        if blank_run == 1:
            out.append("")
    while out and not out[0]:
        out.pop(0)
    while out and not out[-1]:
        out.pop()
    return "\n".join(out)
