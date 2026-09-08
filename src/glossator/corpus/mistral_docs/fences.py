"""Fence-aware line scanning.

Every rewrite in this adapter has to leave fenced code untouched: MDX code samples
contain `# comment` lines that look like headings and `<PLACEHOLDER>` tokens that look
like JSX. One scanner decides what is inside a fence, and everything else uses it.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator

# The prefix allows blockquote markers so a fence inside a converted `:::` callout
# is still recognized as code.
FENCE_RE = re.compile(r"^(?P<indent>[ \t]*(?:>[ \t]*)*)(?P<delim>`{3,}|~{3,})(?P<info>.*)$")


def iter_lines(text: str) -> Iterator[tuple[str, bool]]:
    """Yield `(line, in_fence)` for every line, fences included as `in_fence=True`.

    Both the opening and the closing fence lines count as inside, so a rewrite that
    skips fenced lines never rewrites an info string either.
    """
    open_delim: str | None = None
    open_indent = ""
    for line in text.split("\n"):
        match = FENCE_RE.match(line)
        if open_delim is None:
            if match is not None:
                open_delim = match.group("delim")
                open_indent = match.group("indent")
                yield line, True
                continue
            yield line, False
            continue
        # A closing fence is at most as indented as the opener and uses the same
        # character, at least as many times, with nothing after it.
        if (
            match is not None
            and match.group("delim")[0] == open_delim[0]
            and len(match.group("delim")) >= len(open_delim)
            and not match.group("info").strip()
            and len(match.group("indent")) <= len(open_indent) + 3
        ):
            open_delim = None
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
