"""Section parsing: the heading structure a citation is built from.

These are the facts the rest of the pipeline relies on -- that a section's body is
a verbatim slice of the page, that its heading path names its ancestors, and that
a `#` inside a fenced code block is a comment and not a heading.
"""

from itertools import pairwise
from pathlib import Path

from glossator.ingest.pages import CorpusPage, parse_page
from glossator.ingest.sections import Section, parse_sections

PAGE = """---
url: https://example.test/page
title: Page title
kind: doc
locale: en
source_path: page.mdx
source_commit: abc1234
---

# Page title

Intro prose.

## First section {#first}

Body of the first section.

### Nested {#nested}

Nested body.

## Second section

```python
# Step 1: this is a comment, not a heading
value = 1
```

Trailing prose.
"""


def _sections(text: str = PAGE) -> tuple[CorpusPage, list[Section]]:
    page = parse_page(text, path=Path("page.md"))
    return page, parse_sections(page.body, page_title=page.title)


def test_every_section_body_is_a_verbatim_slice_of_the_page() -> None:
    page, sections = _sections()
    for section in sections:
        assert page.body[section.start_offset : section.end_offset] == section.body


def test_sections_tile_the_page_in_reading_order() -> None:
    page, sections = _sections()
    # Only whitespace may sit outside a section.
    assert page.body[: sections[0].start_offset].strip() == ""
    for earlier, later in pairwise(sections):
        assert earlier.end_offset == later.start_offset
    assert sections[-1].end_offset == len(page.body)


def test_heading_path_names_the_ancestors() -> None:
    _page, sections = _sections()
    by_heading = {section.heading: section for section in sections}
    assert by_heading["Nested"].heading_path == (
        "Page title",
        "First section",
        "Nested",
    )
    assert by_heading["Second section"].heading_path == ("Page title", "Second section")


def test_explicit_anchors_are_read_and_absent_ones_stay_none() -> None:
    _page, sections = _sections()
    by_heading = {section.heading: section for section in sections}
    assert by_heading["First section"].anchor == "first"
    assert by_heading["Second section"].anchor is None
    # The anchor marker is not part of the heading text.
    assert "{#" not in by_heading["First section"].heading


def test_a_hash_inside_a_fenced_block_is_not_a_heading() -> None:
    _page, sections = _sections()
    headings = [section.heading for section in sections]
    assert "Step 1: this is a comment, not a heading" not in headings
    second = next(
        section for section in sections if section.heading == "Second section"
    )
    assert "value = 1" in second.body


def test_the_fixture_corpus_parses_into_sections(
    corpus_pages: list[CorpusPage],
) -> None:
    for page in corpus_pages:
        sections = parse_sections(page.body, page_title=page.title)
        assert sections, page.url
        assert sections[0].heading_path[0] == page.title


def test_pages_without_anchors_still_parse(corpus_pages: list[CorpusPage]) -> None:
    """Most headings on the live site have no anchor at all (D-003 correction).

    Only headings converted from SectionTab, FAQ items and API operations carry
    one, so a section without an anchor is the common case, not an error: the
    citation degrades to page level and the heading path still names the section.
    """
    anchorless = [
        page
        for page in corpus_pages
        if not any(
            section.anchor
            for section in parse_sections(page.body, page_title=page.title)
        )
    ]
    assert anchorless, (
        "the fixture corpus should include pages whose headings carry no anchor"
    )
    for page in anchorless:
        for section in parse_sections(page.body, page_title=page.title):
            assert section.anchor is None
            assert section.heading_path
