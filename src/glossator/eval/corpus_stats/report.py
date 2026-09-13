"""The corpus-stats README."""

from __future__ import annotations

from typing import Any

from glossator.eval.corpus_stats.tokens import (
    MEDIUM_CONTEXT_TOKENS,
    MEDIUM_MODEL_ID,
    MEDIUM_TOKENIZER_REPO,
)


def _fmt(value: int) -> str:
    return f"{value:,}"


def render_readme(metrics: dict[str, Any]) -> str:
    config = metrics["config"]
    dist = metrics["distribution"]
    parts = [
        "# Corpus page sizes in Mistral Medium 3.5 tokens\n",
        "## What this measures\n",
        f"Every page of the vendored corpus (`{config['corpus_dir']}`, commit "
        f"`{config['corpus_commit'][:12]}`) is counted with the tokenizer Mistral "
        f"Medium 3.5 tokenizes requests with: model id `{MEDIUM_MODEL_ID}`, the "
        f"`tekken.json` of `{MEDIUM_TOKENIZER_REPO}` loaded through "
        "`MistralTokenizer.from_hf_hub`. What is counted is the page body -- the "
        "markdown after the frontmatter, which is what `read_page` merges its "
        "chunks back into. Chunk counts are the shipped `sec1024` section "
        "chunking's, whose own budgets are counted with tokenizer v1 (D-010a), so "
        "chunk counts and token counts in the same row come from two tokenizers "
        "on purpose: the chunk count describes the index, the token count the "
        "model.\n",
        "The answer layer's `count_mistral_tokens` (`glossator/answer/context.py`) "
        "loads `MistralTokenizer.v1()`, an older model's sentencepiece tokenizer "
        "pinned there so context budgets stay comparable with the chunker's. It "
        "is **not** the Medium 3.5 tokenizer; this run does not reuse it.\n",
        "## Distribution of page tokens\n",
        _distribution_table(dist),
        _corpus_total(metrics),
        "## Share of pages under a threshold\n",
        _shares_table(metrics),
        "## The ten largest pages\n",
        _largest_table(metrics),
        "## Totals per kind\n",
        _kind_table(metrics),
        "## Pages per single read-page call\n",
        _budget_table(metrics),
        "## Conclusion\n",
        _conclusion(metrics),
        "## Figure\n",
        "- `figures/page-tokens.svg`: histogram of page token counts, log x-axis, "
        "reference lines at the marker budgets\n",
        "## Reproduce\n",
        "The tokenizer file is downloaded from the Hugging Face Hub on first run "
        "and cached there, which is why the command needs `huggingface_hub`.\n",
        "```\n"
        "uv run --with huggingface_hub python -m glossator.eval.corpus_stats "
        f"--corpus {config['corpus_dir']} --out eval/corpus-stats\n"
        "```\n",
    ]
    return "\n".join(part.rstrip() + "\n" for part in parts)


def _distribution_table(dist: dict[str, Any]) -> str:
    keys = ("min", "p50", "p75", "p90", "p95", "p99", "max", "mean")
    cells = " | ".join(_fmt(dist[key]) for key in keys)
    header = " | ".join(keys)
    return f"| pages | {header} |\n|---|{'---|' * len(keys)}\n| {dist['n']} | {cells} |"


def _corpus_total(metrics: dict[str, Any]) -> str:
    total = metrics["totals"]["tokens"]
    return (
        f"The corpus totals {_fmt(total)} tokens across its {metrics['totals']['pages']} pages, "
        f"{total / MEDIUM_CONTEXT_TOKENS:.1f} times Mistral Medium 3.5's 256k context.\n"
    )


def _shares_table(metrics: dict[str, Any]) -> str:
    lines = ["| under (tokens) | pages | share |", "|---|---|---|"]
    for row in metrics["shares_under"].values():
        lines.append(f"| {_fmt(row['threshold'])} | {row['pages']} | {row['share']:.2%} |")
    return "\n".join(lines)


def _largest_table(metrics: dict[str, Any]) -> str:
    lines = ["| # | page | kind | tokens | characters | chunks |", "|---|---|---|---|---|---|"]
    for position, row in enumerate(metrics["largest_pages"], start=1):
        lines.append(
            f"| {position} | `{row['url']}` | {row['kind']} | {_fmt(row['tokens'])} "
            f"| {_fmt(row['characters'])} | {row['chunks']} |"
        )
    return "\n".join(lines)


def _kind_table(metrics: dict[str, Any]) -> str:
    lines = [
        "| kind | pages | tokens | token share | characters | chunks |",
        "|---|---|---|---|---|---|",
    ]
    for kind, row in sorted(metrics["by_kind"].items()):
        lines.append(
            f"| {kind} | {row['pages']} | {_fmt(row['tokens'])} | {row['token_share']:.2%} "
            f"| {_fmt(row['characters'])} | {_fmt(row['chunks'])} |"
        )
    return "\n".join(lines)


def _budget_table(metrics: dict[str, Any]) -> str:
    lines = [
        "| budget (tokens) | pages fitting whole | share of corpus | median-sized pages per call |",
        "|---|---|---|---|",
    ]
    for row in metrics["read_page_budgets"].values():
        lines.append(
            f"| {_fmt(row['budget'])} | {row['pages_fitting_whole']} "
            f"| {row['share_fitting_whole']:.2%} | {row['median_sized_pages_per_call']} |"
        )
    return "\n".join(lines)


def _conclusion(metrics: dict[str, Any]) -> str:
    """The paragraph the surface redesign reads; every figure it leans on sits
    in the tables above, so the prose carries no numbers of its own."""
    return (
        "At an 8,000-token budget a single `read_page` call holds the typical page "
        "with room to spare -- nearly the whole corpus fits whole in one call, and "
        "the budget covers several pages of median size -- so per-page calls almost "
        "never need to paginate, and the calls that do are the long tail in the "
        "table above. At a 16,000-token budget the corpus but a handful of pages "
        "fits in one call, so a multi-page read is a matter of choosing which "
        "pages, not of splitting them. The pages that overflow either budget are "
        "the batch, OCR and transcription pages at the top of the table, and the "
        "surface reads those by section: a search hit on one of them names the "
        "section to pass to read_page."
    )
