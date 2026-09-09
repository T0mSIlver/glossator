"""What the chunker must never get wrong.

A chunk is the unit the product cites, so the properties tested here are the ones
a citation depends on: the span maps back to the page body, the budget holds, a
table or a code fence survives intact, and the embedded text says which section it
came from.
"""

from itertools import pairwise

import pytest

from glossator.ingest.chunker import (
    ATOMIC_TOKEN_CEILING,
    EMBEDDER_TOKEN_LIMIT,
    SECTION_MAX_TOKENS,
    PageChunker,
    PageFacts,
    SectionChunker,
)
from glossator.ingest.pages import CorpusPage

FACTS = PageFacts(url="https://example.test/page", title="Page title", kind="doc", locale="en")


def _facts(page: CorpusPage) -> PageFacts:
    return PageFacts(url=page.url, title=page.title, kind=page.kind, locale=page.locale)


@pytest.fixture(scope="module")
def chunker() -> SectionChunker:
    return SectionChunker()


# --- offsets ---------------------------------------------------------------


def test_offsets_map_back_to_the_page_body(
    chunker: SectionChunker, corpus_pages: list[CorpusPage]
) -> None:
    """The located span is verbatim source, and the prefix is the only addition."""
    for page in corpus_pages:
        for spec in chunker.plan(page.body, _facts(page)):
            body_slice = page.body[spec.start : spec.end]
            assert spec.content.endswith(body_slice), page.url
            prefix = spec.content[: len(spec.content) - len(body_slice)]
            assert prefix == " > ".join(spec.metadata.heading_path) + "\n\n"


def test_chunks_stay_inside_their_page(
    chunker: SectionChunker, corpus_pages: list[CorpusPage]
) -> None:
    for page in corpus_pages:
        for spec in chunker.plan(page.body, _facts(page)):
            assert 0 <= spec.start < spec.end <= len(page.body)


def test_page_strategy_offsets_map_back_too(corpus_pages: list[CorpusPage]) -> None:
    page_chunker = PageChunker()
    for page in corpus_pages:
        for spec in page_chunker.plan(page.body, _facts(page)):
            assert spec.content == page.body[spec.start : spec.end]


# --- the context prefix ----------------------------------------------------


def test_every_chunk_is_prefixed_with_its_heading_path(
    chunker: SectionChunker, function_calling_page: CorpusPage
) -> None:
    specs = chunker.plan(function_calling_page.body, _facts(function_calling_page))
    for spec in specs:
        first_line, blank, _rest = spec.content.partition("\n")
        assert blank
        assert first_line == " > ".join(spec.metadata.heading_path)
        assert first_line.startswith(function_calling_page.title)


def test_a_nested_heading_shows_its_ancestors(
    chunker: SectionChunker, function_calling_page: CorpusPage
) -> None:
    specs = chunker.plan(function_calling_page.body, _facts(function_calling_page))
    nested = next(spec for spec in specs if spec.metadata.anchor == "parallel-tool-calls")
    assert nested.metadata.heading_path == [
        "Function calling",
        "The call loop",
        "Parallel tool calls",
    ]


# --- metadata --------------------------------------------------------------


def test_metadata_carries_the_citation_target(
    chunker: SectionChunker, corpus_pages: list[CorpusPage]
) -> None:
    for page in corpus_pages:
        for spec in chunker.plan(page.body, _facts(page)):
            assert spec.metadata.url == page.url
            assert spec.metadata.page_title == page.title
            assert spec.metadata.kind == page.kind
            assert spec.metadata.locale == page.locale
            assert spec.metadata.section_index >= 0


def test_the_page_strategy_records_no_anchor(corpus_pages: list[CorpusPage]) -> None:
    """The starter's splitter knows nothing about headings, so it cannot deep-link."""
    page_chunker = PageChunker()
    for page in corpus_pages:
        for spec in page_chunker.plan(page.body, _facts(page)):
            assert spec.metadata.anchor is None
            assert spec.metadata.own_anchor is None
            assert spec.metadata.heading_path == [page.title]


def test_an_anchorless_h3_uses_its_h2_anchor(chunker: SectionChunker) -> None:
    body = """# Page title

## Linkable section {#linkable}

Parent prose.

### Anchorless detail

Nested prose.
"""

    detail = next(
        spec
        for spec in chunker.plan(body, FACTS)
        if spec.metadata.heading_path[-1] == "Anchorless detail"
    )

    assert detail.metadata.anchor == "linkable"
    assert detail.metadata.own_anchor is None


# --- token budgets ---------------------------------------------------------


def test_chunks_respect_the_hard_token_cap(
    chunker: SectionChunker, corpus_pages: list[CorpusPage]
) -> None:
    for page in corpus_pages:
        for spec in chunker.plan(page.body, _facts(page)):
            assert chunker.count_tokens(spec.content) <= SECTION_MAX_TOKENS, page.url


def test_an_oversized_section_is_split_into_several_chunks(
    chunker: SectionChunker, function_calling_page: CorpusPage
) -> None:
    specs = chunker.plan(function_calling_page.body, _facts(function_calling_page))
    limits = [spec for spec in specs if spec.metadata.anchor == "limits"]
    assert len(limits) > 1
    assert all(chunker.count_tokens(spec.content) <= SECTION_MAX_TOKENS for spec in limits)
    # Split at a paragraph boundary, so no chunk starts mid-sentence.
    for spec in limits[1:]:
        body_start = function_calling_page.body[spec.start]
        assert body_start not in {" ", "\t"}


def test_consecutive_chunks_of_one_section_overlap_but_advance(
    chunker: SectionChunker, function_calling_page: CorpusPage
) -> None:
    specs = chunker.plan(function_calling_page.body, _facts(function_calling_page))
    limits = [spec for spec in specs if spec.metadata.anchor == "limits"]
    for earlier, later in pairwise(limits):
        assert later.start > earlier.start
        assert later.start <= earlier.end


def test_a_tighter_budget_produces_more_chunks(
    function_calling_page: CorpusPage,
) -> None:
    facts = _facts(function_calling_page)
    loose = SectionChunker().plan(function_calling_page.body, facts)
    tight = SectionChunker(target_tokens=120, max_tokens=200, overlap_tokens=20).plan(
        function_calling_page.body, facts
    )
    assert len(tight) > len(loose)


def test_the_budget_is_validated() -> None:
    with pytest.raises(ValueError, match="target_tokens"):
        SectionChunker(target_tokens=SECTION_MAX_TOKENS + 1, max_tokens=SECTION_MAX_TOKENS)
    with pytest.raises(ValueError, match="overlap_tokens"):
        SectionChunker(target_tokens=100, max_tokens=200, overlap_tokens=100)


# --- atomic blocks ---------------------------------------------------------


def _fence_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.lstrip().startswith("```"))


def test_no_chunk_ends_inside_a_fenced_code_block(
    chunker: SectionChunker, corpus_pages: list[CorpusPage]
) -> None:
    for page in corpus_pages:
        for spec in chunker.plan(page.body, _facts(page)):
            assert _fence_count(spec.content) % 2 == 0, f"{page.url}: {spec.metadata.heading_path}"


def test_a_large_table_is_not_split(chunker: SectionChunker, table_page: CorpusPage) -> None:
    """Half a table has no header row, so it is neither readable nor quotable."""
    tight = SectionChunker(target_tokens=80, max_tokens=120, overlap_tokens=0)
    for spec in tight.plan(table_page.body, _facts(table_page)):
        rows = [line for line in spec.content.splitlines() if line.startswith("|")]
        if not rows:
            continue
        # A table that appears at all appears whole: its header and delimiter rows
        # are present, and the run is not truncated at the chunk edge.
        assert rows[1].startswith("| ---")
        assert not spec.content.rstrip().endswith("|") or spec.content.rstrip().endswith(rows[-1])
    # The default chunker keeps each matrix table in one chunk.
    for spec in chunker.plan(table_page.body, _facts(table_page)):
        rows = [line for line in spec.content.splitlines() if line.startswith("|")]
        if rows:
            assert rows[1].startswith("| ---")


# --- determinism -----------------------------------------------------------


def test_chunking_is_deterministic(
    chunker: SectionChunker, function_calling_page: CorpusPage
) -> None:
    facts = _facts(function_calling_page)
    first = chunker.plan(function_calling_page.body, facts)
    second = chunker.plan(function_calling_page.body, facts)
    assert [(spec.start, spec.end, spec.content) for spec in first] == [
        (spec.start, spec.end, spec.content) for spec in second
    ]


def test_a_chunk_without_an_anchor_still_carries_its_heading_path(
    chunker: SectionChunker, corpus_pages: list[CorpusPage]
) -> None:
    """Most headings on the live site have no anchor; the citation degrades to page level."""
    anchorless = [
        spec
        for page in corpus_pages
        for spec in chunker.plan(page.body, _facts(page))
        if spec.metadata.anchor is None
    ]
    assert anchorless, "the fixture corpus should include sections whose headings carry no anchor"
    for spec in anchorless:
        assert spec.metadata.heading_path
        assert spec.metadata.url


# --- blocks that cannot fit -------------------------------------------------

_PAGE_HEAD = "# Page title\n\n## Big block\n\n"


def _fenced(rows: int) -> str:
    lines = "\n".join(f"value_{index} = {index}" for index in range(rows))
    return f"{_PAGE_HEAD}```python\n{lines}\n```\n"


def test_a_code_block_over_the_cap_but_under_the_ceiling_stays_whole(
    chunker: SectionChunker,
) -> None:
    body = _fenced(600)
    tokens = chunker.count_tokens(body)
    assert SECTION_MAX_TOKENS < tokens < ATOMIC_TOKEN_CEILING
    specs = [spec for spec in chunker.plan(body, FACTS) if "```" in spec.content]
    assert len(specs) == 1


def test_a_code_block_over_the_ceiling_is_split_so_it_can_be_embedded(
    chunker: SectionChunker,
) -> None:
    """An unembeddable chunk never reaches the index, which is worse than a cut one."""
    body = _fenced(4000)
    assert chunker.count_tokens(body) > ATOMIC_TOKEN_CEILING
    specs = chunker.plan(body, FACTS)
    assert len(specs) > 1
    for spec in specs:
        assert chunker.count_tokens(spec.content) <= EMBEDDER_TOKEN_LIMIT
    # Still a contiguous, verbatim cover of the section.
    assert specs[0].start == body.index("## Big block")
    assert specs[-1].end == len(body)
    for earlier, later in pairwise(specs):
        assert earlier.end == later.start


def test_the_atomic_ceiling_is_validated() -> None:
    with pytest.raises(ValueError, match="atomic_ceiling"):
        SectionChunker(atomic_ceiling=EMBEDDER_TOKEN_LIMIT + 1)
    with pytest.raises(ValueError, match="atomic_ceiling"):
        SectionChunker(max_tokens=1024, atomic_ceiling=512)
