"""YAML frontmatter split and render."""

from __future__ import annotations

from typing import Any

import yaml

_DELIMITER = "---"


def split(source: str) -> tuple[dict[str, Any], str]:
    """Split `---` frontmatter from the body. Missing or invalid frontmatter is `{}`."""
    text = source.lstrip("﻿")
    if not text.startswith(_DELIMITER):
        return {}, source
    lines = text.split("\n")
    for index in range(1, len(lines)):
        if lines[index].rstrip() == _DELIMITER:
            raw = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            try:
                data = yaml.safe_load(raw)
            except yaml.YAMLError:
                return {}, source
            return (data if isinstance(data, dict) else {}), body
    return {}, source


def render(data: dict[str, Any]) -> str:
    """Render frontmatter with stable key order and no line wrapping."""
    body = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=None,
        width=10_000,
    )
    return f"{_DELIMITER}\n{body}{_DELIMITER}\n"
