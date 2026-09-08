from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict

HEADING_RE = re.compile(
    r"^(?P<marks>#{1,6})\s+(?P<title>.*?)(?:\s+\{#(?P<anchor>[^}]+)\})\s*$",
    re.MULTILINE,
)
FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<yaml>.*?)\n---\s*\n", re.DOTALL)

PageKind = Literal["doc", "api", "model"]


class ManifestEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    path: str
    title: str
    kind: PageKind
    source_path: str
    source_commit: str
    sha256: str


class CorpusSection(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    page_title: str
    heading_path: list[str]
    anchor: str
    level: int
    body: str
    token_estimate: int


class CorpusPage(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    title: str
    breadcrumbs: list[str]
    kind: PageKind
    locale: Literal["en", "fr"]
    source_path: str
    source_commit: str
    path: Path
    markdown: str
    sections: list[CorpusSection]


def read_manifest(path: Path) -> list[ManifestEntry]:
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise TypeError(f"manifest must contain a list: {path}")
    return [ManifestEntry.model_validate(item) for item in data]


def read_corpus(root: Path) -> list[CorpusPage]:
    return [read_page(path) for path in sorted(root.rglob("*.md"))]


def read_page(path: Path) -> CorpusPage:
    raw = path.read_text()
    match = FRONTMATTER_RE.match(raw)
    if match is None:
        raise ValueError(f"page has no YAML frontmatter: {path}")
    frontmatter = yaml.safe_load(match.group("yaml"))
    if not isinstance(frontmatter, dict):
        raise TypeError(f"page frontmatter must be a mapping: {path}")
    markdown = raw[match.end() :]
    required = {
        "url",
        "title",
        "breadcrumbs",
        "kind",
        "locale",
        "source_path",
        "source_commit",
    }
    missing = required - frontmatter.keys()
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"page frontmatter is missing {names}: {path}")
    sections = _sections(
        markdown,
        url=str(frontmatter["url"]),
        page_title=str(frontmatter["title"]),
    )
    return CorpusPage(
        url=frontmatter["url"],
        title=frontmatter["title"],
        breadcrumbs=frontmatter["breadcrumbs"],
        kind=frontmatter["kind"],
        locale=frontmatter["locale"],
        source_path=frontmatter["source_path"],
        source_commit=frontmatter["source_commit"],
        path=path,
        markdown=markdown,
        sections=sections,
    )


def _sections(markdown: str, *, url: str, page_title: str) -> list[CorpusSection]:
    headings = list(HEADING_RE.finditer(markdown))
    heading_stack: list[tuple[int, str]] = []
    sections: list[CorpusSection] = []
    for index, heading in enumerate(headings):
        level = len(heading.group("marks"))
        anchor = heading.group("anchor")
        if anchor is None:
            raise ValueError(
                f"heading has no explicit anchor on {url}: {heading.group('title')}"
            )
        title = heading.group("title").strip()
        heading_stack = [item for item in heading_stack if item[0] < level]
        heading_stack.append((level, title))
        end = len(markdown)
        for later in headings[index + 1 :]:
            if len(later.group("marks")) <= level:
                end = later.start()
                break
        body = markdown[heading.end() : end].strip()
        sections.append(
            CorpusSection(
                url=url,
                page_title=page_title,
                heading_path=[item[1] for item in heading_stack],
                anchor=anchor,
                level=level,
                body=body,
                token_estimate=estimate_tokens(body),
            )
        )
    return sections


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)
