"""Self-check: the rebuilt sources must reproduce the source run's own verdicts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from glossator.answer.citations import resolve
from glossator.eval.replay.context import rebuild_context
from glossator.eval.replay.export import PURPOSE, read_calls
from glossator.eval.replay.records import single_pass_records
from glossator.index.variants import VARIANTS


def check_rebuild(run_dir: Path, *, corpus_dir: Path) -> dict[str, Any]:
    """Re-verify the source run's own citations against the rebuilt sources.

    For each single-pass answer the model's raw `(n, quote)` pairs are read from
    the call ledger and pushed through `resolve` on the rebuilt context; the
    verdicts and chunk ids must equal the record's. A mismatch means the rebuild
    is not what the run saw, and a replay scored on it would not be comparable.
    """
    config = json.loads((run_dir / "config.json").read_text())
    chunking = VARIANTS[str(config.get("variant", "sec1024"))].chunking
    min_quote_chars = int(config.get("answer_config", {}).get("min_quote_chars", 8))
    records = single_pass_records(run_dir)
    raw: dict[str, list[tuple[int, str]]] = {}
    for call in read_calls(run_dir):
        if call.get("purpose") == PURPOSE and call.get("parsed") and call["question_id"] not in raw:
            raw[call["question_id"]] = [
                (int(citation["n"]), str(citation["quote"]))
                for citation in call["parsed"].get("citations", [])
            ]
    compared = matched = 0
    mismatches: list[dict[str, Any]] = []
    notes = 0
    for question_id, record in records.items():
        if record.trace is None or question_id not in raw:
            continue
        context, rebuild_notes = rebuild_context(
            record.trace, corpus_dir=corpus_dir, chunking=chunking
        )
        notes += len(rebuild_notes)
        verified, rejected = resolve(raw[question_id], context, min_quote_chars=min_quote_chars)
        got = sorted((c.n, c.verified, c.chunk_id, c.url, c.anchor) for c in verified + rejected)
        want = sorted(
            (c.n, c.verified, c.chunk_id, c.url, c.anchor)
            for c in record.citations + record.unverified_citations
        )
        compared += 1
        if got == want:
            matched += 1
        else:
            mismatches.append({"question_id": question_id, "got": got, "want": want})
    return {
        "run": run_dir.name,
        "compared": compared,
        "matched": matched,
        "rebuild_notes": notes,
        "mismatches": mismatches[:10],
    }
