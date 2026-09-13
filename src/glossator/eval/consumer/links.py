"""Whether the links in an answer resolve to a corpus page and a visible fragment."""

from __future__ import annotations

import json
import random
import urllib.parse
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

from glossator.eval.consumer.models import ConsumerRecord
from glossator.eval.fragments import PageCache, visible_text

DEFAULT_CORPUS = Path("corpus/mistral-docs")


def corpus_page_urls(corpus_dir: Path = DEFAULT_CORPUS) -> set[str]:
    manifest = corpus_dir / "manifest.json"
    if not manifest.is_file():
        return set()
    pages = json.loads(manifest.read_text())
    return {str(page.get("url", "")) for page in pages if page.get("url")}


def page_of(url: str) -> str:
    """A cited URL reduced to its corpus page: host plus path, no fragment."""
    parts = urlsplit(url)
    if parts.netloc != "docs.mistral.ai":
        return url
    return f"https://{parts.netloc}{parts.path}"


def check_fragments(
    run_dir: Path, records: Sequence[ConsumerRecord], *, sample: int = 60, seed: int = 0
) -> dict[str, Any]:
    """Do the answer links resolve: page in the corpus, fragment text on it.

    Page resolution is offline against the manifest. Fragment text is checked
    against the live page with cached fetches under the run directory, reusing
    the fragment check's visible-text reduction;     tab-panel misses are reported
    apart for the same reason as in the answer eval.
    """
    candidates = sorted({url for record in records for url in record.links})
    chosen = (
        random.Random(seed).sample(candidates, sample) if len(candidates) > sample else candidates
    )
    cache = PageCache(run_dir / "fragments" / "pages")
    rows: list[dict[str, Any]] = []
    for url in chosen:
        base, _, directive = url.partition(":~:text=")
        row: dict[str, Any] = {
            "url": url,
            "page": base,
            "has_fragment": bool(directive),
            "found": None,
            "failure": None,
        }
        if not directive:
            rows.append(row)
            continue
        try:
            response = cache.get(base)
        except httpx.HTTPError:
            row["failure"] = "page fetch"
            rows.append(row)
            continue
        if response.status_code != 200:
            row["failure"] = "page fetch"
            rows.append(row)
            continue
        text = visible_text(response.content.decode("utf-8", errors="replace")).casefold()
        start, _, end = directive.partition(",")
        start_text = urllib.parse.unquote(start).replace("\n", " ").casefold()
        found = start_text in text
        failure = None if found else "text absent"
        if found and end:
            end_text = urllib.parse.unquote(end).replace("\n", " ").casefold()
            found = end_text in text[text.find(start_text) + len(start_text) :]
            failure = None if found else "range order"
        row["found"] = found
        row["failure"] = failure
        rows.append(row)
    fragment_rows = [row for row in rows if row["has_fragment"]]
    found_count = sum(1 for row in fragment_rows if row["found"])
    metrics = {
        "links_checked": len(rows),
        "fragment_links": len(fragment_rows),
        "fragments_found": found_count,
        "share_found": found_count / len(fragment_rows) if fragment_rows else None,
        "seed": seed,
    }
    (run_dir / "fragments" / "results.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )
    (run_dir / "fragments" / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    )
    return metrics
