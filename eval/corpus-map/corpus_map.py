"""Emit the corpus as JSON: every page, its sections, and the chunks the shipped
chunker (sec1024) cuts from them, with the names the MCP server uses, plus
what each section and chunk is made of (prose, code, numeric noise)."""

import json
import re
import sys
from pathlib import Path
from typing import Any

from glossator.ingest.chunker import PageFacts, SectionChunker
from glossator.ingest.pages import iter_page_paths, load_page, read_manifest
from glossator.ingest.sections import parse_sections

READ_MAX_CHARS = 24_000
LARGE_PAGE_CHARS = 32_000
FENCE = re.compile(r"```.*?```", re.S)
FLOAT = re.compile(r"-?\d+\.\d{4,}")
LONG_LINE = 1500


def composition(text: str) -> dict[str, Any]:
    """Characters of fenced code, prose, and two noise signals: float literals
    with four or more decimals (embedding vectors) and lines over 1,500 chars
    (pasted JSON responses)."""
    code = 0
    blocks = 0
    for m in FENCE.finditer(text):
        blocks += 1
        code += len(m.group(0))
    floats = len(FLOAT.findall(text))
    long_lines = sum(1 for line in text.split("\n") if len(line) > LONG_LINE)
    return {
        "code_chars": code,
        "code_blocks": blocks,
        "floats": floats,
        "long_lines": long_lines,
        "noisy": floats >= 20 or long_lines >= 1,
    }


# The concrete class rather than build_chunker: the map reports token counts,
# which only the section chunker exposes, and sec1024 is the shipped strategy.
chunker = SectionChunker()
corpus = Path("corpus/mistral-docs")
pages: list[dict[str, Any]] = []
for path in iter_page_paths(corpus):
    page = load_page(path)
    facts = PageFacts(url=page.url, title=page.title, kind=page.kind, locale=page.locale)
    chunks = chunker.plan(page.body, facts)
    sections = parse_sections(page.body, page_title=page.title)
    per_section: list[list[dict[str, Any]]] = [[] for _ in sections]
    for n, chunk in enumerate(chunks):
        span = page.body[chunk.start : chunk.end]
        entry = {
            "n": n,
            "chars": len(span),
            "tokens": chunker.count_tokens(chunk.content),
            **composition(span),
        }
        for i, s in enumerate(sections):
            if s.start_offset <= chunk.start < s.end_offset:
                per_section[i].append(entry)
                break
    page_comp = composition(page.body)
    pages.append(
        {
            "url": page.url,
            "path": page.url.replace("https://docs.mistral.ai", "") or "/",
            "title": page.title,
            "kind": page.kind,
            "breadcrumbs": list(getattr(page, "breadcrumbs", []) or []),
            "chars": len(page.body),
            "tokens": sum(c["tokens"] for cs in per_section for c in cs),
            "chunks": len(chunks),
            "large": len(page.body) >= LARGE_PAGE_CHARS,
            "over_budget": len(page.body) > READ_MAX_CHARS,
            **page_comp,
            "sections": [
                {
                    "index": s.index,
                    "level": s.level,
                    "heading": s.heading,
                    "own_anchor": s.own_anchor,
                    "anchor": s.anchor,
                    "key": s.anchor or s.heading_path[-1],
                    "heading_path": list(s.heading_path),
                    "chars": len(s.body),
                    "empty": s.is_empty,
                    "chunks": per_section[i],
                    **composition(s.body),
                }
                for i, s in enumerate(sections)
            ],
        }
    )

pages.sort(key=lambda p: p["path"])
manifest = read_manifest(corpus)
commit = (
    next((e.get("source_commit") for e in manifest if e.get("source_commit")), None)
    if manifest
    else None
)
out = {
    "commit": commit,
    "read_max_chars": READ_MAX_CHARS,
    "large_page_chars": LARGE_PAGE_CHARS,
    "pages": pages,
}
with open(sys.argv[1], "w") as handle:
    json.dump(out, handle, ensure_ascii=False)
n_sections = sum(len(p["sections"]) for p in pages)
n_chunks = sum(p["chunks"] for p in pages)
noisy_sections = sum(1 for p in pages for s in p["sections"] if s["noisy"])
code_share = sum(p["code_chars"] for p in pages) / sum(p["chars"] for p in pages)
print(
    len(pages),
    "pages",
    n_sections,
    "sections",
    n_chunks,
    "chunks;",
    noisy_sections,
    "noisy sections;",
    f"code share {code_share:.2f}",
)
