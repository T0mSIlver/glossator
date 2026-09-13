"""Command line: measure every page and write the output directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import structlog

from glossator.eval.corpus_stats.figure import histogram_svg
from glossator.eval.corpus_stats.measure import RUN_KIND, measure_page, summarize
from glossator.eval.corpus_stats.report import render_readme
from glossator.eval.corpus_stats.tokens import (
    MEDIUM_MODEL_ID,
    MEDIUM_TOKENIZER_REPO,
    load_medium_tokenizer,
    medium_counter,
)
from glossator.index.variants import ChunkStrategy
from glossator.ingest.chunker import build_chunker
from glossator.ingest.pages import iter_page_paths, load_page, read_manifest

logger = structlog.get_logger(__name__)


def run(corpus_dir: Path, out_dir: Path) -> dict[str, Any]:
    """Measure every page and write the output directory."""
    manifest = read_manifest(corpus_dir)
    commits = {str(entry.get("source_commit", "")) for entry in manifest}
    config = {
        "kind": RUN_KIND,
        "corpus_dir": str(corpus_dir),
        "corpus_commit": (commits.pop() if len(commits) == 1 else ",".join(sorted(commits))),
        "tokenizer": {
            "model_id": MEDIUM_MODEL_ID,
            "repo": MEDIUM_TOKENIZER_REPO,
            "file": "tekken.json",
        },
        "counts": "page body (markdown after the frontmatter)",
        "chunks": "sec1024 (section chunker: target 600 / cap 1024 / overlap 60 tokens)",
    }

    paths = list(iter_page_paths(corpus_dir))
    counter = medium_counter(load_medium_tokenizer())
    chunker = build_chunker(ChunkStrategy.SECTION)
    rows = [measure_page(load_page(path), count_tokens=counter, chunker=chunker) for path in paths]
    logger.info("Measured corpus pages", pages=len(rows), corpus_dir=str(corpus_dir))

    metrics = summarize(rows, config)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pages.jsonl").write_text(
        "".join(row.model_dump_json() + "\n" for row in rows), encoding="utf-8"
    )
    (out_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    figures = out_dir / "figures"
    figures.mkdir(exist_ok=True)
    (figures / "page-tokens.svg").write_text(
        histogram_svg([row.tokens for row in rows]), encoding="utf-8"
    )
    (out_dir / "README.md").write_text(render_readme(metrics), encoding="utf-8")
    return metrics


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure corpus page sizes with the Mistral Medium 3.5 tokenizer."
    )
    parser.add_argument("--corpus", type=Path, default=Path("corpus/mistral-docs"))
    parser.add_argument("--out", type=Path, default=Path("eval/corpus-stats"))
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    metrics = run(args.corpus, args.out)
    dist = metrics["distribution"]
    print(
        json.dumps(
            {
                "out": str(args.out),
                "pages": dist["n"],
                "p50": dist["p50"],
                "p90": dist["p90"],
                "p99": dist["p99"],
                "max": dist["max"],
                "under_8000": metrics["shares_under"]["8000"]["share"],
                "under_16000": metrics["shares_under"]["16000"]["share"],
            },
            indent=2,
        )
    )
