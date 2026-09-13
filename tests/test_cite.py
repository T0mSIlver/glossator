"""Quote-verification tests for `glossator.answer.cite`, on fixtures.

Covers a quote that verifies, one that verifies after
emphasis normalization, one fabricated, one across a chunk boundary, a marker
with no quote, and duplicate sources collapsing to one entry; plus the clamps
and the malformed-input shape.
"""

import asyncio

import pytest

from glossator.answer.citations import VERIFIED_AFTER_EMPHASIS
from glossator.answer.cite import (
    MAX_DRAFT_CHARS,
    MAX_QUOTES,
    CiteInputError,
    CiteQuote,
    cite_draft,
    dedupe_sources,
    split_url_anchor,
)
from glossator.retrieval.engine import Hit

URL = "https://docs.mistral.ai/page"
ANCHOR = "a-section"
OTHER_ANCHOR = "other-section"


def _hit(
    chunk_id: str,
    content: str,
    *,
    start: int,
    end: int,
    anchor: str | None = ANCHOR,
) -> Hit:
    return Hit(
        chunk_id=chunk_id,
        score=0.5,
        url=URL,
        anchor=anchor,
        heading_path=("Page", "A section"),
        page_title="Page",
        kind="doc",
        locale="en",
        section_index=1,
        content=content,
        source_id=URL,
        start_offset=start,
        end_offset=end,
    )


class _Navigation:
    def __init__(self, hits: list[Hit]) -> None:
        self.hits = hits

    async def read(
        self, start: int | None = None, end: int | None = None, top_k: int = 20
    ) -> list[Hit]:
        return self.hits[:top_k]


class _Engine:
    """Two adjacent chunks on one page; `missing` names an empty page."""

    def __init__(self, hits: list[Hit] | None = None) -> None:
        self.hits = (
            hits
            if hits is not None
            else [
                _hit("c1", "Streaming returns server-sent events as the model", start=0, end=50),
                _hit("c2", "produces them. Call client.chat.stream for deltas.", start=50, end=100),
            ]
        )

    async def get_chunk(self, chunk_id: str) -> Hit | None:
        return next((hit for hit in self.hits if hit.chunk_id == chunk_id), None)

    def navigation_at(
        self, source_id: str, start_offset: int = 0, end_offset: int = 0
    ) -> _Navigation:
        if source_id != URL:
            return _Navigation([])
        return _Navigation(self.hits)


def _run(draft: str, quotes: list[CiteQuote], engine: _Engine | None = None):  # type: ignore[no-untyped-def]
    return asyncio.run(cite_draft(draft, quotes, engine=engine or _Engine()))  # type: ignore[arg-type]


def test_a_quote_against_its_chunk_verifies_with_a_fragment_link() -> None:
    result = _run(
        "It streams [1].",
        [CiteQuote(n=1, chunk_id="c1", quote="server-sent events as the model")],
    )

    (item,) = result.quotes
    assert item.verified is True
    assert item.reason is None
    assert item.url == URL
    assert item.anchor == ANCHOR
    assert item.chunk_id == "c1"
    assert item.emphasis_normalized is False
    assert item.fragment_url is not None
    assert item.fragment_url.startswith(f"{URL}#{ANCHOR}:~:text=")
    assert result.unverified_markers == []
    assert result.next.startswith("every [n] in the draft verified")


def test_a_quote_without_the_source_emphasis_verifies_as_normalized() -> None:
    engine = _Engine([_hit("c1", "Maximum number of tools per request: **128**", start=0, end=20)])

    result = _run(
        "At most 128 tools [1].",
        [CiteQuote(n=1, chunk_id="c1", quote="Maximum number of tools per request: 128")],
        engine,
    )

    (item,) = result.quotes
    assert item.verified is True
    assert item.reason == VERIFIED_AFTER_EMPHASIS
    assert item.emphasis_normalized is True
    assert item.fragment_url is not None


def test_a_fabricated_quote_is_rejected_with_its_reason() -> None:
    result = _run(
        "Pixels stream [1].",
        [CiteQuote(n=1, chunk_id="c1", quote="pixels are delicious")],
    )

    (item,) = result.quotes
    assert item.verified is False
    assert item.reason == "quote is not in the cited source"
    assert item.fragment_url is None
    assert result.unverified_markers == [1]
    assert "search(query=" in result.next


def test_a_too_short_quote_is_rejected_as_too_short() -> None:
    result = _run(
        "Events [1].",
        [CiteQuote(n=1, chunk_id="c1", quote="events")],
    )

    (item,) = result.quotes
    assert item.verified is False
    assert item.reason == "quote is shorter than the minimum"


def test_an_unknown_chunk_id_is_no_such_source() -> None:
    result = _run(
        "It streams [1].",
        [CiteQuote(n=1, chunk_id="nope", quote="server-sent events as the model")],
    )

    (item,) = result.quotes
    assert item.verified is False
    assert item.reason is not None and "no source with that number" in item.reason


def test_a_quote_across_a_chunk_boundary_verifies_through_the_url_form() -> None:
    result = _run(
        "It streams [1].",
        [
            CiteQuote(
                n=1,
                url=f"{URL}#{ANCHOR}",
                quote="as the model produces them. Call client.chat.stream",
            )
        ],
    )

    (item,) = result.quotes
    assert item.verified is True
    assert item.url == URL
    assert item.fragment_url is not None


def test_an_unknown_page_url_is_no_such_source() -> None:
    result = _run(
        "It streams [1].",
        [CiteQuote(n=1, url="https://docs.mistral.ai/nope", quote="server-sent events")],
    )

    (item,) = result.quotes
    assert item.verified is False
    assert item.reason is not None and "no source with that number" in item.reason
    assert item.url == "https://docs.mistral.ai/nope"


def test_a_marker_with_no_quote_is_reported() -> None:
    result = _run(
        "It streams [1] and batches [2].",
        [CiteQuote(n=1, chunk_id="c1", quote="server-sent events as the model")],
    )

    assert [item.n for item in result.quotes if item.verified] == [1]
    assert result.unverified_markers == [2]


def test_markers_inside_code_are_not_markers() -> None:
    result = _run(
        "Use `choices[7]` for output [1].",
        [CiteQuote(n=1, chunk_id="c1", quote="server-sent events as the model")],
    )

    assert result.unverified_markers == []


def test_duplicate_sources_collapse_to_one_entry() -> None:
    result = _run(
        "It streams [1] and again [2] elsewhere [3].",
        [
            CiteQuote(n=1, chunk_id="c1", quote="server-sent events as the model"),
            CiteQuote(n=2, chunk_id="c1", quote="Streaming returns server-sent events"),
            CiteQuote(
                n=3,
                url=URL,
                quote="Call client.chat.stream for deltas.",
            ),
        ],
    )

    assert len(result.sources) == 1
    (entry,) = result.sources
    assert entry.url == URL
    assert entry.anchor == ANCHOR
    assert entry.citation_url == f"{URL}#{ANCHOR}"
    assert entry.numbers == [1, 2, 3]
    assert "[1][2][3] [" in result.sources_markdown


def test_the_sources_block_is_markdown_links_with_the_heading_and_the_quote() -> None:
    result = _run(
        "It streams [1].",
        [CiteQuote(n=1, chunk_id="c1", quote="Streaming returns server-sent events")],
        engine=_Engine([_hit("c1", "Streaming returns server-sent events here", start=0, end=20)]),
    )

    (line,) = result.sources_markdown.splitlines()[1:]
    assert line.startswith("[1] [")
    assert "](https://docs.mistral.ai/page#a-section:~:text=" in line
    assert line.endswith('— "Streaming returns server-sent events"')
    assert result.sources[0].heading


def test_an_entry_falls_back_to_the_canonical_link_without_a_fragment() -> None:
    from glossator.answer.cite import SourceEntry, SourceQuote, sources_markdown

    block = sources_markdown(
        [
            SourceEntry(
                url=URL,
                anchor=ANCHOR,
                citation_url=f"{URL}#{ANCHOR}",
                numbers=[1],
                quotes=[SourceQuote(n=1, fragment_url=None, text="a sentence")],
                heading="Streaming",
            )
        ]
    )

    assert block.splitlines()[1] == f'[1] [Streaming]({URL}#{ANCHOR}) — "a sentence"'


def test_sections_with_different_anchors_stay_separate() -> None:
    engine = _Engine(
        [
            _hit("c1", "Streaming returns server-sent events here", start=0, end=20),
            _hit(
                "c2", "Batching returns one response there", start=30, end=50, anchor=OTHER_ANCHOR
            ),
        ]
    )

    result = _run(
        "Streams [1]; batches [2].",
        [
            CiteQuote(n=1, chunk_id="c1", quote="server-sent events here"),
            CiteQuote(n=2, chunk_id="c2", quote="one response there"),
        ],
        engine,
    )

    assert [(entry.anchor, entry.numbers) for entry in result.sources] == [
        (ANCHOR, [1]),
        (OTHER_ANCHOR, [2]),
    ]


def test_quotes_clamp_to_twenty_with_a_note() -> None:
    quotes = [
        CiteQuote(n=n, chunk_id="c1", quote="server-sent events as the model")
        for n in range(1, MAX_QUOTES + 6)
    ]

    result = _run("It streams [1].", quotes)

    assert len(result.quotes) == MAX_QUOTES
    assert result.notes == [f"note: clamped server-side: quotes={MAX_QUOTES + 5} → {MAX_QUOTES}"]


def test_a_long_draft_clamps_with_a_note() -> None:
    draft = "It streams [1]." + " padding" * 5000
    assert len(draft) > MAX_DRAFT_CHARS

    result = _run(
        draft,
        [CiteQuote(n=1, chunk_id="c1", quote="server-sent events as the model")],
    )

    assert result.notes == [
        f"note: clamped server-side: draft={len(draft)} → {MAX_DRAFT_CHARS} chars"
    ]
    assert result.quotes[0].verified is True


def test_a_quote_naming_both_chunk_and_url_is_malformed() -> None:
    with pytest.raises(CiteInputError, match="exactly one"):
        _run(
            "It streams [1].",
            [CiteQuote(n=1, chunk_id="c1", url=URL, quote="server-sent events")],
        )


def test_a_quote_naming_neither_chunk_nor_url_is_malformed() -> None:
    with pytest.raises(CiteInputError, match="neither chunk_id nor url"):
        _run(
            "It streams [1].",
            [CiteQuote(n=1, quote="server-sent events")],
        )


def test_an_empty_draft_is_malformed() -> None:
    with pytest.raises(CiteInputError, match="draft is empty"):
        _run(
            "   ",
            [CiteQuote(n=1, chunk_id="c1", quote="server-sent events")],
        )


def test_a_whitespace_quote_is_malformed() -> None:
    with pytest.raises(CiteInputError, match="empty or only whitespace"):
        _run(
            "It streams [1].",
            [CiteQuote(n=1, chunk_id="c1", quote="   ")],
        )


def test_split_url_anchor() -> None:
    assert split_url_anchor("https://docs.mistral.ai/page#sec") == (
        "https://docs.mistral.ai/page",
        "sec",
    )
    assert split_url_anchor("https://docs.mistral.ai/page") == (
        "https://docs.mistral.ai/page",
        None,
    )


def test_dedupe_sources_ignores_unverified_quotes() -> None:
    from glossator.answer.cite import VerifiedQuote

    entries = dedupe_sources(
        [
            VerifiedQuote(n=1, verified=True, url=URL, anchor=ANCHOR),
            VerifiedQuote(n=2, verified=False, reason="x", url=URL, anchor=ANCHOR),
        ]
    )

    assert [entry.numbers for entry in entries] == [[1]]
