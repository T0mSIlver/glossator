"""Read the plain-data object literals in the docs repo's TypeScript schema files.

`src/schema/models/**` is data, not logic: object literals of strings, numbers,
arrays and one localizable `describe` arrow function. A tolerant reader is enough
and avoids a Node dependency; anything it cannot read raises so a changed file is
noticed instead of silently dropped.
"""

from __future__ import annotations

import re
from typing import Any

_IDENT = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
_NUMBER = re.compile(r"-?(?:0[xX][0-9a-fA-F]+|\d[\d_]*(?:\.\d+)?(?:[eE][-+]?\d+)?|\.\d+)")
_WS = " \t\r\n"
_MAX_CONST_DEPTH = 8

FUNCTION = object()
"""Marker for a value that is a function; the docs never read one as data."""


class TsParseError(ValueError):
    """A TypeScript literal could not be read."""


def parse_object_after(source: str, marker: str) -> dict[str, Any]:
    """Parse the object literal that follows `marker` (for example `export default`)."""
    start = source.find(marker)
    if start < 0:
        raise TsParseError(f"marker {marker!r} not found")
    reader = _Reader(source, start + len(marker))
    reader.skip_trivia()
    if reader.peek() != "{":
        raise TsParseError(f"expected an object literal after {marker!r}")
    value = reader.parse_value()
    if not isinstance(value, dict):  # pragma: no cover - guarded by the peek above
        raise TsParseError(f"{marker!r} is not an object literal")
    return value


def parse_named_const(source: str, name: str) -> dict[str, Any]:
    """Parse `export const <name> = { ... }`."""
    match = re.search(rf"\bconst\s+{re.escape(name)}\b[^=]*=", source)
    if match is None:
        raise TsParseError(f"const {name!r} not found")
    reader = _Reader(source, match.end())
    reader.skip_trivia()
    value = reader.parse_value()
    if not isinstance(value, dict):
        raise TsParseError(f"const {name!r} is not an object literal")
    return value


class _Reader:
    def __init__(self, source: str, index: int, resolving: frozenset[str] = frozenset()) -> None:
        self.source = source
        self.index = index
        self.resolving = resolving

    def peek(self) -> str:
        return self.source[self.index] if self.index < len(self.source) else ""

    def skip_trivia(self) -> None:
        while self.index < len(self.source):
            char = self.source[self.index]
            if char in _WS:
                self.index += 1
                continue
            if self.source.startswith("//", self.index):
                end = self.source.find("\n", self.index)
                self.index = len(self.source) if end < 0 else end + 1
                continue
            if self.source.startswith("/*", self.index):
                end = self.source.find("*/", self.index)
                if end < 0:
                    raise TsParseError("unterminated block comment")
                self.index = end + 2
                continue
            return

    def expect(self, char: str) -> None:
        self.skip_trivia()
        if self.peek() != char:
            raise TsParseError(f"expected {char!r} at offset {self.index}")
        self.index += 1

    def parse_value(self) -> Any:
        self.skip_trivia()
        char = self.peek()
        if char == "":
            raise TsParseError("unexpected end of input")
        if char == "{":
            return self.parse_object()
        if char == "[":
            return self.parse_array()
        if char in "\"'`":
            return self.parse_string()
        if char == "(":
            return self.parse_function()
        if char == "-" or char.isdigit() or (char == "." and self.source[self.index + 1].isdigit()):
            match = _NUMBER.match(self.source, self.index)
            if match is None:
                raise TsParseError(f"bad number at offset {self.index}")
            self.index = match.end()
            text = match.group(0).replace("_", "")
            return float(text) if any(c in text for c in ".eE") else int(text)
        match = _IDENT.match(self.source, self.index)
        if match is None:
            raise TsParseError(f"unreadable value at offset {self.index}")
        self.index = match.end()
        word = match.group(0)
        if word == "true":
            return True
        if word == "false":
            return False
        if word in {"null", "undefined"}:
            return None
        self.skip_trivia()
        if self.peek() == "=" and self.source.startswith("=>", self.index):
            # A single-parameter arrow function written without parentheses.
            self.index += 2
            self.skip_arrow_body()
            return FUNCTION
        return self.resolve_identifier(word)

    def resolve_identifier(self, name: str) -> Any:
        """A bare identifier is only data if a `const` in this file defines it.

        Anything else — an import, a computed expression — has a value that is not in
        the text being read, and guessing `None` would erase a real field.
        """
        if name in self.resolving:
            raise TsParseError(f"const {name!r} refers to itself")
        if len(self.resolving) >= _MAX_CONST_DEPTH:
            raise TsParseError(f"const {name!r} nests too deeply to resolve")
        match = re.search(rf"\bconst\s+{re.escape(name)}\b[^=;]*=", self.source)
        if match is None:
            raise TsParseError(
                f"identifier {name!r} at offset {self.index} is not defined in this file"
            )
        inner = _Reader(self.source, match.end(), self.resolving | {name})
        return inner.parse_value()

    def parse_object(self) -> dict[str, Any]:
        self.expect("{")
        out: dict[str, Any] = {}
        while True:
            self.skip_trivia()
            char = self.peek()
            if char == "}":
                self.index += 1
                return out
            if char == ",":
                self.index += 1
                continue
            if char == ".":  # spread: `...base`
                while self.peek() == ".":
                    self.index += 1
                spread = self.parse_value()
                if not isinstance(spread, dict):
                    raise TsParseError(f"object spread at offset {self.index} is not an object")
                out.update(spread)
                continue
            key = self.parse_key()
            self.skip_trivia()
            if self.peek() == "(":
                # Method shorthand `describe(l) { ... }`.
                self.parse_function()
                out[key] = FUNCTION
                continue
            self.expect(":")
            out[key] = self.parse_value()

    def parse_key(self) -> str:
        self.skip_trivia()
        char = self.peek()
        if char in "\"'`":
            return str(self.parse_string())
        if char == "[":
            # Computed key: read it as its literal text, which is all we need.
            self.index += 1
            key = self.parse_value()
            self.expect("]")
            return str(key)
        match = _IDENT.match(self.source, self.index)
        if match is None:
            raise TsParseError(f"bad object key at offset {self.index}")
        self.index = match.end()
        return match.group(0)

    def parse_array(self) -> list[Any]:
        self.expect("[")
        out: list[Any] = []
        while True:
            self.skip_trivia()
            char = self.peek()
            if char == "]":
                self.index += 1
                return out
            if char == ",":
                self.index += 1
                continue
            if char == ".":
                while self.peek() == ".":
                    self.index += 1
                spread = self.parse_value()
                if not isinstance(spread, list):
                    raise TsParseError(f"array spread at offset {self.index} is not an array")
                out.extend(spread)
                continue
            out.append(self.parse_value())

    def parse_string(self, strict: bool = True) -> str:
        """Read a string literal. In `strict` mode the value must be fully known."""
        quote = self.source[self.index]
        start = self.index
        self.index += 1
        parts: list[str] = []
        while self.index < len(self.source):
            char = self.source[self.index]
            if char == "\\":
                text, self.index = _read_escape(self.source, self.index)
                parts.append(text)
                continue
            if char == quote:
                self.index += 1
                return "".join(parts)
            if quote == "`" and self.source.startswith("${", self.index):
                if strict:
                    raise TsParseError(
                        f"template substitution at offset {self.index} has no literal value"
                    )
                self.skip_substitution()
                continue
            parts.append(char)
            self.index += 1
        raise TsParseError(f"unterminated string at offset {start}")

    def skip_substitution(self) -> None:
        depth = 0
        while self.index < len(self.source):
            if self.source[self.index] == "{":
                depth += 1
            elif self.source[self.index] == "}":
                depth -= 1
                if depth == 0:
                    self.index += 1
                    return
            self.index += 1

    def parse_function(self) -> Any:
        self.skip_balanced("(", ")")
        self.skip_trivia()
        if self.source.startswith("=>", self.index):
            self.index += 2
            self.skip_arrow_body()
        elif self.peek() == "{":
            self.skip_balanced("{", "}")
        return FUNCTION

    def skip_arrow_body(self) -> None:
        self.skip_trivia()
        char = self.peek()
        if char == "{":
            self.skip_balanced("{", "}")
        elif char == "(":
            self.skip_balanced("(", ")")
        else:
            self.skip_expression()

    def skip_expression(self) -> None:
        """Skip past an expression without reading it as data."""
        depth = 0
        while self.index < len(self.source):
            char = self.peek()
            if char in "\"'`":
                self.parse_string(strict=False)
                continue
            if self.source.startswith("//", self.index) or self.source.startswith("/*", self.index):
                self.skip_trivia()
                continue
            if char in "([{":
                depth += 1
            elif char in ")]}":
                if depth == 0:
                    return
                depth -= 1
            elif char == "," and depth == 0:
                return
            self.index += 1

    def skip_balanced(self, opener: str, closer: str) -> None:
        self.skip_trivia()
        if self.peek() != opener:
            raise TsParseError(f"expected {opener!r} at offset {self.index}")
        depth = 0
        while self.index < len(self.source):
            char = self.source[self.index]
            if char in "\"'`":
                self.parse_string(strict=False)
                continue
            if self.source.startswith("//", self.index) or self.source.startswith("/*", self.index):
                self.skip_trivia()
                continue
            if char == opener:
                depth += 1
            elif char == closer:
                depth -= 1
                if depth == 0:
                    self.index += 1
                    return
            self.index += 1
        raise TsParseError(f"unbalanced {opener!r}")


_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}


def _read_escape(source: str, index: int) -> tuple[str, int]:
    """Decode the escape sequence starting at the backslash at `index`."""
    if index + 1 >= len(source):
        raise TsParseError(f"string ends on a backslash at offset {index}")
    char = source[index + 1]
    if char == "u":
        if source.startswith("{", index + 2):
            end = source.find("}", index + 3)
            if end < 0:
                raise TsParseError(f"unterminated unicode escape at offset {index}")
            return chr(int(source[index + 3 : end], 16)), end + 1
        return chr(int(source[index + 2 : index + 6], 16)), index + 6
    if char == "x":
        return chr(int(source[index + 2 : index + 4], 16)), index + 4
    if char == "\n":
        # A line continuation contributes nothing to the value.
        return "", index + 2
    return _ESCAPES.get(char, char), index + 2
