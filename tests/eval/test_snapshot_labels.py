import asyncio
import json
from pathlib import Path

from glossator.corpus.snapshots import SnapshotRecord
from glossator.eval.snapshots import label, score_snapshot_records


def _page(path: Path, url: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"url: {url}\n"
        "title: Test page\n"
        "kind: doc\n"
        "locale: en\n"
        "source_path: page.mdx\n"
        "source_commit: abc\n"
        "breadcrumbs: []\n"
        "---\n"
        f"{body}"
    )


def _fixtures(tmp_path: Path) -> tuple[Path, Path, Path]:
    corpus = tmp_path / "2026-06-01"
    _page(corpus / "page.md", "https://docs.mistral.ai/page", "# Page\n\nThe limit is 10.\n")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "snapshots": [
                    {
                        "date": "2026-06-01",
                        "commit": "20260601",
                        "pages": 1,
                        "content_digest": "digest",
                        "corpus_dir": str(corpus),
                        "status": "built",
                        "error": None,
                        "openapi_source": "openapi.yaml",
                        "openapi_snapshot_exact": True,
                        "models_snapshot_exact": True,
                    }
                ]
            }
        )
    )
    dataset = tmp_path / "questions.jsonl"
    dataset.write_text(
        "".join(
            json.dumps(row) + "\n"
            for row in [
                {
                    "id": "q-present",
                    "question": "What is the limit?",
                    "type": "single_page",
                    "gold": [{"url": "https://docs.mistral.ai/page", "anchor": None}],
                    "reference_answer": "The limit is 10.",
                    "language": "en",
                    "source": "handwritten",
                },
                {
                    "id": "q-pending",
                    "question": "What is the quota?",
                    "type": "single_page",
                    "gold": [{"url": "https://docs.mistral.ai/page", "anchor": None}],
                    "reference_answer": "The quota is seven per region.",
                    "language": "en",
                    "source": "handwritten",
                },
            ]
        )
    )
    runs_root = tmp_path / "runs"
    shipped = runs_root / "x-fresh60-shipped"
    shipped.mkdir(parents=True)
    (shipped / "records.jsonl").write_text(
        "".join(
            json.dumps(row) + "\n"
            for row in [
                {
                    "question_id": "q-present",
                    "strategy": "single_pass",
                    "citations": [{"quote": "The limit is 10.", "verified": True}],
                },
                {
                    "question_id": "q-pending",
                    "strategy": "single_pass",
                    "citations": [{"quote": "a quota nobody ever wrote", "verified": True}],
                },
            ]
        )
    )
    return dataset, manifest, runs_root


def test_deterministic_only_labels_exact_cells_and_defers_the_rest(tmp_path: Path) -> None:
    dataset, manifest, runs_root = _fixtures(tmp_path)

    run_path, metrics = asyncio.run(
        label(
            [dataset],
            name="fixture-labels",
            manifest_path=manifest,
            runs_root=runs_root,
            deterministic_only=True,
        )
    )

    rows = [
        json.loads(line) for line in (run_path / "labels.jsonl").read_text().splitlines() if line
    ]
    assert len(rows) == 2
    by_id = {row["question_id"]: row for row in rows}
    assert by_id["q-present"]["label"] == "present"
    assert by_id["q-present"]["decided_by"] == "exact_span"
    pending = by_id["q-pending"]
    assert pending["label"] == "unknown"
    assert pending["decided_by"] == "pending_judges"
    assert pending["top_pages"], "the later judged pass needs the lexical pages"
    # No judge was called: the step is deterministic and makes no model calls.
    assert (run_path / "calls.jsonl").read_text() == ""
    assert metrics["per_snapshot"]["2026-06-01"]["counts"] == {"present": 1, "unknown": 1}


def test_deterministic_only_resume_does_not_duplicate_pending_cells(tmp_path: Path) -> None:
    dataset, manifest, runs_root = _fixtures(tmp_path)
    first, _ = asyncio.run(
        label(
            [dataset],
            name="fixture-resume",
            manifest_path=manifest,
            runs_root=runs_root,
            deterministic_only=True,
        )
    )
    before = (first / "labels.jsonl").read_text()

    second, _ = asyncio.run(
        label(
            [dataset],
            name="fixture-resume",
            manifest_path=manifest,
            runs_root=runs_root,
            deterministic_only=True,
        )
    )

    assert second == first
    assert (second / "labels.jsonl").read_text() == before
    assert len(before.splitlines()) == 2


def test_snapshot_scoring_ignores_rows_without_a_judge_verdict() -> None:
    snapshots = [
        SnapshotRecord(
            date="2026-06-01",
            commit="20260601",
            pages=1,
            content_digest="digest",
            corpus_dir="/tmp/never-read",
            status="built",
            error=None,
            openapi_source="openapi.yaml",
            openapi_snapshot_exact=True,
            models_snapshot_exact=True,
        )
    ]
    records = [
        {
            "snapshot": "2026-06-01",
            "availability_label": "present",
            "judge": None,
            "insufficient_evidence": False,
        },
        {
            "snapshot": "2026-06-01",
            "availability_label": "absent",
            "judge": None,
            "insufficient_evidence": True,
        },
    ]

    scored = score_snapshot_records(records, snapshots)

    assert scored["2026-06-01"]["present_cells"] == 1
    assert scored["2026-06-01"]["absent_cells"] == 1
    assert scored["2026-06-01"]["correctness_present"] is None
    assert scored["2026-06-01"]["refusal_rate_absent"] == 1.0
