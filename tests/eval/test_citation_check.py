"""Resolving an answer's documentation links to the passages they point at."""

from __future__ import annotations

from pathlib import Path

from glossator.eval.consumer.citation_check import (
    MARK,
    Corpus,
    docs_links,
    marked_answer,
    resolve_passage,
)

PAGE = """---
url: https://docs.mistral.ai/studio/agents/introduction
title: Agents Introduction
breadcrumbs: [Studio, Agents]
kind: doc
locale: en
source_path: src/content/en/docs/studio/agents/introduction/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# What are AI agents?

Agents plan and use tools.

## FAQ {#faq}

### Which models are supported? {#which-models-are-supported}

Only `mistral-medium-latest` and `mistral-large-latest`.

## Cookbooks {#cookbooks}

Links only.
"""


def _corpus(tmp_path: Path) -> Corpus:
    page = tmp_path / "docs" / "studio" / "agents" / "introduction.md"
    page.parent.mkdir(parents=True)
    page.write_text(PAGE)
    return Corpus(tmp_path / "docs", None)


def test_an_anchor_resolves_to_its_section_with_subsections(tmp_path: Path) -> None:
    corpus = _corpus(tmp_path)
    _page, passage, anchor, resolution, truncated = resolve_passage(
        corpus, "https://docs.mistral.ai/studio/agents/introduction#faq"
    )
    assert (anchor, resolution, truncated) == ("faq", "section", False)
    assert "mistral-large-latest" in passage
    assert "Links only" not in passage
    assert passage.startswith("Agents Introduction > What are AI agents? > FAQ")


def test_a_missing_anchor_falls_back_to_the_page_and_says_so(tmp_path: Path) -> None:
    corpus = _corpus(tmp_path)
    _page, passage, _anchor, resolution, _truncated = resolve_passage(
        corpus, "https://docs.mistral.ai/studio/agents/introduction#handoffs"
    )
    assert resolution == "anchor_missing"
    assert "Links only" in passage


def test_a_page_outside_the_corpus_resolves_to_nothing(tmp_path: Path) -> None:
    corpus = _corpus(tmp_path)
    _page, passage, _anchor, resolution, _truncated = resolve_passage(
        corpus, "https://docs.mistral.ai/platform/agents"
    )
    assert (passage, resolution) == ("", "not_in_corpus")


def test_links_are_documentation_only_and_deduplicated_without_text_directives() -> None:
    links = [
        "https://docs.mistral.ai/studio/agents/introduction#faq",
        "https://docs.mistral.ai/studio/agents/introduction#faq:~:text=Only",
        "https://your-mcp-server.com/sse",
    ]
    assert docs_links("", links) == ["https://docs.mistral.ai/studio/agents/introduction#faq"]


def test_a_page_link_does_not_mark_the_anchored_links_it_prefixes() -> None:
    page = "https://docs.mistral.ai/studio/agents/introduction"
    answer = f"Agents plan [Intro]({page}). Only two models [FAQ]({page}#faq)."
    marked = marked_answer(answer, page)
    assert marked.count(MARK) == 1
    assert f"({page} {MARK})" in marked
    anchored = marked_answer(answer, f"{page}#faq")
    assert anchored.count(MARK) == 1
    assert f"#faq {MARK})" in anchored
