"""The distribution arithmetic on a fixture, with a fake token counter.

The tokenizer download belongs to the run, not to the test suite: every number
here is produced from rows built by hand or measured with a counter that just
divides characters, which is enough to check the arithmetic that the real run
only feeds.
"""

from pathlib import Path

from glossator.eval.corpus_stats.figure import histogram_svg
from glossator.eval.corpus_stats.measure import (
    MARKERS,
    THRESHOLDS,
    PageStats,
    distribution,
    largest_pages,
    measure_page,
    percentile,
    read_page_fits,
    shares_under,
    summarize,
    totals_by_kind,
)
from glossator.eval.corpus_stats.report import render_readme
from glossator.index.variants import ChunkStrategy
from glossator.ingest.chunker import build_chunker
from glossator.ingest.pages import parse_page

FIXTURE_PAGE = """---
url: https://docs.mistral.ai/getting-started/quickstart
title: Quickstart
breadcrumbs:
  - Getting started
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstart/page.mdx
source_commit: 2e094f7
---

# Quickstart

Install the SDK and call the chat endpoint with your API key.

## Install

```bash
pip install mistralai
```

## First call

Send one message and read the answer in the response content.
"""


def _fake_counter(text: str) -> int:
    """One token per four characters: deterministic, no download."""
    return len(text) // 4


def row(url: str, tokens: int, *, kind: str = "doc", chunks: int = 1) -> PageStats:
    characters = tokens * 4
    return PageStats(
        url=url, kind=kind, locale="en", tokens=tokens, characters=characters, chunks=chunks
    )


ROWS = [
    row("https://docs.mistral.ai/a", 100),
    row("https://docs.mistral.ai/b", 500),
    row("https://docs.mistral.ai/c", 1_500),
    row("https://docs.mistral.ai/d", 2_500),
    row("https://docs.mistral.ai/e", 9_000, kind="api", chunks=9),
    row("https://docs.mistral.ai/f", 17_000, kind="model", chunks=20),
    row("https://docs.mistral.ai/g", 33_000, kind="model", chunks=40),
    row("https://docs.mistral.ai/h", 3_000),
]


def test_a_page_is_measured_with_the_injected_counter(tmp_path: Path) -> None:
    path = tmp_path / "quickstart.md"
    path.write_text(FIXTURE_PAGE, encoding="utf-8")
    page = parse_page(path.read_text(encoding="utf-8"), path=path)

    stats = measure_page(
        page, count_tokens=_fake_counter, chunker=build_chunker(ChunkStrategy.SECTION)
    )

    assert stats.url == page.url
    assert stats.kind == "doc"
    assert stats.locale == "en"
    assert stats.tokens == len(page.body) // 4
    assert stats.characters == len(page.body)
    # One section per heading, none oversized: the fixture's three prose sections.
    assert stats.chunks == 3


def test_percentile_interpolates_linearly() -> None:
    assert percentile([10, 20, 30, 40], 0.5) == 25.0
    assert percentile([10, 20], 0.25) == 12.5
    assert percentile([7], 0.99) == 7.0
    assert percentile([5, 1, 9], 0.0) == 1.0
    assert percentile([5, 1, 9], 1.0) == 9.0


def test_the_distribution_covers_the_requested_quantiles() -> None:
    values = [100, 200, 300, 400, 500]
    assert distribution(values) == {
        "n": 5,
        "min": 100,
        "p50": 300,
        "p75": 400,
        "p90": 460,
        "p95": 480,
        "p99": 496,
        "max": 500,
        "mean": 300,
    }


def test_shares_count_pages_under_each_threshold() -> None:
    shares = shares_under([1_500, 2_500, 9_000, 33_000], thresholds=THRESHOLDS)
    assert [threshold for threshold in THRESHOLDS] == [2_000, 4_000, 8_000, 16_000, 32_000]
    assert shares["2000"]["pages"] == 1
    assert shares["4000"]["pages"] == 2
    assert shares["8000"]["pages"] == 2
    assert shares["16000"]["pages"] == 3
    assert shares["32000"]["pages"] == 3
    assert shares["2000"]["share"] == 0.25


def test_read_page_budgets_are_derived_from_the_median() -> None:
    fits = read_page_fits([1_000, 2_000, 3_000, 8_000], budgets=(8_000, 16_000))
    assert fits["8000"]["pages_fitting_whole"] == 3
    assert fits["8000"]["share_fitting_whole"] == 0.75
    # Median 2,500: three pages of that size fit an 8,000 budget.
    assert fits["8000"]["median_sized_pages_per_call"] == 3
    assert fits["16000"]["median_sized_pages_per_call"] == 6


def test_totals_are_broken_down_by_kind() -> None:
    totals = totals_by_kind(ROWS)
    assert totals["doc"]["pages"] == 5
    assert totals["doc"]["tokens"] == 100 + 500 + 1_500 + 2_500 + 3_000
    assert totals["api"]["chunks"] == 9
    assert totals["model"]["token_share"] == round(
        (17_000 + 33_000) / sum(r.tokens for r in ROWS), 4
    )


def test_the_largest_pages_come_first_and_keep_order_on_ties() -> None:
    tied = [row("https://docs.mistral.ai/x", 5_000), row("https://docs.mistral.ai/a", 5_000)]
    largest = largest_pages(tied + ROWS, count=3)
    assert [page.tokens for page in largest] == [33_000, 17_000, 9_000]
    assert largest_pages([row("https://docs.mistral.ai/y", 100)], count=10)[0].tokens == 100


def test_the_summary_carries_every_table_the_readme_prints() -> None:
    metrics = summarize(ROWS, {"corpus_dir": "corpus/mistral-docs", "corpus_commit": "2e094f7"})
    assert metrics["totals"]["pages"] == len(ROWS)
    assert metrics["totals"]["chunks"] == sum(page.chunks for page in ROWS)
    assert len(metrics["largest_pages"]) == 8
    assert set(metrics["by_kind"]) == {"doc", "api", "model"}
    assert metrics["distribution"]["max"] == 33_000

    readme = render_readme(metrics)
    assert "Mistral Medium 3.5" in readme
    assert "`mistral-medium-2604`" in readme
    assert "not** the Medium 3.5 tokenizer" in readme
    assert "| under (tokens) | pages | share |" in readme
    assert "| kind | pages | tokens | token share | characters | chunks |" in readme
    assert "| budget (tokens) | pages fitting whole |" in readme
    assert "uv run --with huggingface_hub python -m glossator.eval.corpus_stats" in readme


def test_the_readme_states_the_corpus_total_against_the_model_context() -> None:
    metrics = summarize(ROWS, {"corpus_dir": "corpus/mistral-docs", "corpus_commit": "2e094f7"})
    total = sum(page.tokens for page in ROWS)
    readme = render_readme(metrics)
    assert f"The corpus totals {total:,} tokens across its {len(ROWS)} pages" in readme
    assert f"{total / 256_000:.1f} times Mistral Medium 3.5's 256k context" in readme


def test_the_readme_names_the_section_read_as_the_large_page_path() -> None:
    metrics = summarize(ROWS, {"corpus_dir": "corpus/mistral-docs", "corpus_commit": "2e094f7"})
    readme = render_readme(metrics)
    assert (
        "the surface reads those by section: a search hit on one of them names the "
        "section to pass to read_page." in readme
    )
    assert "The tokenizer file is downloaded from the Hugging Face Hub on first run" in readme
    # Each table appears once: the README is rendered from one pass over the parts.
    for header in (
        "| under (tokens) | pages | share |",
        "| # | page | kind | tokens | characters | chunks |",
    ):
        assert readme.count(header) == 1


def test_the_histogram_marks_the_budgets_and_names_the_tokenizer() -> None:
    svg = histogram_svg([120, 9_000, 17_000, 33_000])
    assert 'width="800"' in svg
    assert "mistral-medium-2604" in svg
    assert "page body tokens (log scale)" in svg
    # One reference line per marker budget, each with its label.
    for marker in MARKERS:
        assert f">{marker / 1_000:g}k</text>" in svg
    # The x-axis ticks span the log decades the bins cover.
    for tick in ("1", "10", "100", "1k", "10k", "100k"):
        assert f">{tick}</text>" in svg


def test_the_histogram_scales_the_y_axis_to_the_largest_bin() -> None:
    """The gridline labels are bin counts. The first version printed the last
    page's token count on every gridline, so the labels are pinned here."""
    counts = [50, 60, 70, 80, 90]
    svg = histogram_svg(counts)
    assert ">0</text>" in svg
    # All five values share the bin [46.4, 100), so that is also the top label.
    assert svg.count(">5</text>") == 1
    # A data value never appears as a gridline label.
    assert ">90</text>" not in svg


def test_pages_outside_the_axis_are_counted_not_dropped_silently() -> None:
    # 5 tokens falls inside the axis (it starts at 1); only the millionth does not.
    svg = histogram_svg([5, 10**6])
    assert "+1 pages outside the axis" in svg
