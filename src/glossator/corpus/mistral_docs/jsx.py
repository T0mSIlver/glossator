"""A tolerant, fence-aware JSX scanner for MDX bodies.

Full MDX parsing needs a JavaScript parser; the docs only need enough structure to
find components, their attributes and their children. Anything that does not parse
as a tag stays literal text, which is what keeps `<MISTRAL_API_KEY>` and `List<T>`
intact instead of being swallowed as markup.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .fences import closes_fence, fence_opening

# JSX allows dots and dashes in element names (`Foo.Bar`, `my-element`); underscores
# are allowed too, which is why `<MISTRAL_API_KEY>` scans as a tag and then fails on
# the missing close, falling back to literal text.
_NAME = re.compile(r"[A-Za-z][A-Za-z0-9._:-]*")
_ATTR_NAME = re.compile(r"[A-Za-z_:][A-Za-z0-9_.:-]*")
_WS = " \t\r\n"

VOID_TAGS = frozenset({"br", "hr", "img", "input", "meta", "link", "source", "col"})


@dataclass(frozen=True)
class Fence:
    """A fenced code block, kept verbatim including its delimiters."""

    raw: str


@dataclass(frozen=True)
class Text:
    """Literal markdown text."""

    value: str


@dataclass(frozen=True)
class Element:
    """A JSX element.

    An attribute value of `None` is a valueless (boolean) attribute; a value still
    wrapped in `{...}` is a JavaScript expression rather than a literal.
    """

    name: str
    attrs: dict[str, str | None] = field(default_factory=dict)
    children: list[Node] = field(default_factory=list)

    def attr(self, name: str) -> str | None:
        return self.attrs.get(name)


Node = Fence | Text | Element


def parse(source: str) -> list[Node]:
    """Parse an MDX body into text, fenced code and element nodes."""
    nodes, index = _parse_nodes(source, 0, None)
    if index != len(source):  # pragma: no cover - _parse_nodes always consumes to EOF
        raise AssertionError("scanner stopped before end of input")
    return nodes


def _at_line_start(source: str, index: int) -> bool:
    return index == 0 or source[index - 1] == "\n"


def _line_end(source: str, index: int) -> int:
    end = source.find("\n", index)
    return len(source) if end == -1 else end


def _scan_fence(source: str, index: int) -> tuple[Fence, int] | None:
    """Consume a fenced block starting at `index`, which must be at a line start.

    Opening and closing are decided by `fences`, so the parser and every line-based
    rewrite agree on where code begins and ends.
    """
    end = _line_end(source, index)
    opening = fence_opening(source[index:end])
    if opening is None:
        return None
    cursor = min(end + 1, len(source))
    while cursor < len(source):
        stop = _line_end(source, cursor)
        if closes_fence(source[cursor:stop], opening):
            return Fence(source[index:stop]), stop
        cursor = stop + 1
    return Fence(source[index:]), len(source)


def _skip_ws(source: str, index: int) -> int:
    while index < len(source) and source[index] in _WS:
        index += 1
    return index


def _skip_braced(source: str, index: int) -> int | None:
    """Skip a `{...}` expression, respecting nested braces and string literals."""
    depth = 0
    while index < len(source):
        char = source[index]
        if char in "\"'`":
            index = _skip_string(source, index, char)
            if index < 0:
                return None
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return None


def _skip_string(source: str, index: int, quote: str) -> int:
    index += 1
    while index < len(source):
        if source[index] == "\\":
            index += 2
            continue
        if source[index] == quote:
            return index + 1
        index += 1
    return -1


def _parse_attributes(source: str, index: int) -> tuple[dict[str, str | None], bool, int] | None:
    attrs: dict[str, str | None] = {}
    while True:
        index = _skip_ws(source, index)
        if index >= len(source):
            return None
        if source.startswith("/>", index):
            return attrs, True, index + 2
        if source[index] == ">":
            return attrs, False, index + 1
        if source[index] == "{":
            end = _skip_braced(source, index)
            if end is None:
                return None
            index = end
            continue
        name_match = _ATTR_NAME.match(source, index)
        if name_match is None:
            return None
        name = name_match.group(0)
        index = name_match.end()
        after = _skip_ws(source, index)
        if after < len(source) and source[after] == "=":
            index = _skip_ws(source, after + 1)
            if index >= len(source):
                return None
            char = source[index]
            if char in "\"'":
                end = _skip_string(source, index, char)
                if end < 0:
                    return None
                attrs[name] = source[index + 1 : end - 1]
                index = end
            elif char == "{":
                end = _skip_braced(source, index)
                if end is None:
                    return None
                # Braces are kept so a caller can tell an expression from a string
                # literal: `src={diagram}` has no value this converter can resolve.
                attrs[name] = source[index:end]
                index = end
            else:
                end = index
                while end < len(source) and source[end] not in _WS + "/>":
                    end += 1
                attrs[name] = source[index:end]
                index = end
        else:
            attrs[name] = None
    # unreachable


def _try_parse_element(source: str, index: int) -> tuple[Element, int] | None:
    name_match = _NAME.match(source, index + 1)
    if name_match is None:
        return None
    name = name_match.group(0)
    parsed = _parse_attributes(source, name_match.end())
    if parsed is None:
        return None
    attrs, self_closing, cursor = parsed
    if self_closing or name.lower() in VOID_TAGS:
        return Element(name, attrs, []), cursor
    children, cursor = _parse_nodes(source, cursor, name)
    closing = f"</{name}"
    if not source.startswith(closing, cursor):
        return None
    end = source.find(">", cursor)
    if end == -1:
        return None
    return Element(name, attrs, children), end + 1


def _parse_nodes(source: str, index: int, stop_tag: str | None) -> tuple[list[Node], int]:
    nodes: list[Node] = []
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            nodes.append(Text("".join(buffer)))
            buffer.clear()

    while index < len(source):
        if _at_line_start(source, index):
            # Checked from the first column so an indented fence is still a fence.
            fenced = _scan_fence(source, index)
            if fenced is not None:
                flush()
                nodes.append(fenced[0])
                index = fenced[1]
                continue
        char = source[index]
        if char == "`":
            end = _scan_inline_code(source, index)
            if end is not None:
                buffer.append(source[index:end])
                index = end
                continue
        if char == "<":
            if source.startswith("<!--", index):
                end = source.find("-->", index)
                index = len(source) if end == -1 else end + 3
                continue
            if source.startswith("</", index):
                name_match = _NAME.match(source, index + 2)
                if name_match is not None and name_match.group(0) == stop_tag:
                    flush()
                    return nodes, index
                if name_match is not None and name_match.group(0).lower() in VOID_TAGS:
                    # `</br>` is a common typo for `<br/>`; the browser treats it as
                    # a break, so it must not survive as literal text in a table cell.
                    end = source.find(">", index)
                    if end != -1:
                        flush()
                        nodes.append(Element(name_match.group(0), {}, []))
                        index = end + 1
                        continue
                # A stray close tag: keep it as text rather than losing content.
                buffer.append(char)
                index += 1
                continue
            parsed = _try_parse_element(source, index)
            if parsed is not None:
                flush()
                nodes.append(parsed[0])
                index = parsed[1]
                continue
            buffer.append(char)
            index += 1
            continue
        if char == "{" and source.startswith("{/*", index):
            end = source.find("*/}", index)
            index = len(source) if end == -1 else end + 3
            continue
        buffer.append(char)
        index += 1

    flush()
    return nodes, index


def _scan_inline_code(source: str, index: int) -> int | None:
    """Consume an inline code span so backticked `<Foo>` is not read as markup."""
    start = index
    while index < len(source) and source[index] == "`":
        index += 1
    ticks = source[start:index]
    end = source.find(ticks, index)
    if end == -1 or "\n\n" in source[index:end]:
        return None
    return end + len(ticks)
