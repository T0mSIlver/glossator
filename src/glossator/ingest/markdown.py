"""Line-level markdown scanning shared by the section parser and the chunker.

Only what both need: where each line starts, whether it is inside a fenced code
block, and how to recognise a heading or a table row. Everything here works on
character offsets into the page body, because those offsets are what a citation
ultimately points at.
"""

import re
from dataclasses import dataclass

# ATX heading with an optional trailing ``{#anchor}`` deep-link marker.
_HEADING = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*$")
_ANCHOR = re.compile(r"^(.*?)[ \t]*\{#([^}\s]+)\}$")
# Up to three leading spaces still counts as a fence or a table row in GFM.
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_TABLE_ROW = re.compile(r"^ {0,3}\|")


@dataclass(frozen=True, slots=True)
class Line:
    """One physical line, with its span in the page body."""

    text: str
    """Line content without its trailing newline."""

    start: int
    """Offset of the line's first character in the page body."""

    end: int
    """Offset just past the line's newline (or past the last character at EOF)."""

    in_fence: bool
    """True inside a fenced code block, including the two fence lines themselves."""

    @property
    def is_blank(self) -> bool:
        return not self.text.strip()


@dataclass(frozen=True, slots=True)
class Heading:
    """An ATX heading and its optional explicit anchor."""

    level: int
    text: str
    anchor: str | None


def scan_lines(text: str) -> list[Line]:
    """Split ``text`` into lines, marking the ones inside fenced code blocks.

    A fence is closed by a line opening with the same character repeated at least
    as many times; an unterminated fence runs to the end of the page, which is
    what a markdown renderer does too.
    """
    lines: list[Line] = []
    offset = 0
    open_fence: str | None = None
    for raw in text.splitlines(keepends=True):
        stripped = raw.rstrip("\n").rstrip("\r")
        fence = _FENCE.match(stripped)
        marker = fence.group(1) if fence else None
        if open_fence is None:
            in_fence = marker is not None
            if marker is not None:
                open_fence = marker
        else:
            in_fence = True
            # A closing fence uses the same character, at least as long, and no info string.
            if (
                marker is not None
                and marker[0] == open_fence[0]
                and len(marker) >= len(open_fence)
            ):
                assert fence is not None
                if not fence.group(2).strip():
                    open_fence = None
        lines.append(
            Line(text=stripped, start=offset, end=offset + len(raw), in_fence=in_fence)
        )
        offset += len(raw)
    return lines


def parse_heading(line: Line) -> Heading | None:
    """The heading this line declares, or ``None``. Lines inside a fence never are."""
    if line.in_fence:
        return None
    match = _HEADING.match(line.text)
    if not match:
        return None
    body = match.group(2)
    anchor: str | None = None
    if anchored := _ANCHOR.match(body):
        body, anchor = anchored.group(1), anchored.group(2)
    return Heading(level=len(match.group(1)), text=body.strip(), anchor=anchor)


def is_table_row(line: Line) -> bool:
    return not line.in_fence and bool(_TABLE_ROW.match(line.text))
