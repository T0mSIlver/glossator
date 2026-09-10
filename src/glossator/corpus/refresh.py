"""Build a candidate snapshot from the docs repository's current head (D-045).

`glossator.corpus.snapshots build` resolves the fixed biweekly dates and the
pinned commit; it never looks past the pin. A refresh needs one more snapshot:
whatever `main` of `mistralai/platform-docs-public` is today. This module
builds it into the snapshot root, appends it to the manifest, writes a gate
manifest holding exactly two snapshots, the served one and the candidate, so
labelling and evaluation run on both dates in one pass with the same code and
models, and prints the dates and commits for the workflow to carry to
ingestion and the gate. Whether a snapshot is served is not a manifest
status: the served pointer under `eval/refresh/served.json` names the accepted
snapshot, its commit and the run whose gate accepted it, and the deploy reads
that pointer.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from glossator.corpus.mistral_docs.build import build_corpus
from glossator.corpus.mistral_docs.source import DEFAULT_CACHE_DIR, fetch_docs_repo
from glossator.corpus.snapshots import (
    DEFAULT_MANIFEST,
    DEFAULT_SNAPSHOT_ROOT,
    SnapshotRecord,
    corpus_digest,
    read_snapshot_manifest,
    write_snapshot_manifest,
)

logger = structlog.get_logger(__name__)

SERVED_POINTER = Path("eval/refresh/served.json")
DEFAULT_GATE_MANIFEST = DEFAULT_SNAPSHOT_ROOT / "gate-manifest.json"
DOCS_HEAD = "main"


def read_served(path: Path = SERVED_POINTER) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_served(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _portable(path: Path) -> str:
    home = Path.home()
    try:
        return "~/" + str(path.relative_to(home))
    except ValueError:
        return str(path)


def _openapi_path(checkout_path: Path) -> Path | None:
    for relative in ("openapi-public-doc.yaml", "openapi.yaml"):
        candidate = checkout_path / relative
        if candidate.is_file():
            return candidate
    return None


def build_candidate(
    *,
    ref: str = DOCS_HEAD,
    manifest_path: Path = DEFAULT_MANIFEST,
    snapshot_root: Path = DEFAULT_SNAPSHOT_ROOT,
    repo: Path = DEFAULT_CACHE_DIR,
    served_path: Path = SERVED_POINTER,
    gate_manifest: Path = DEFAULT_GATE_MANIFEST,
) -> dict[str, Any]:
    """Build the head of the docs repository as a candidate snapshot.

    Returns what the workflow needs: the candidate's date and commit, the
    served snapshot and commit, the gate manifest, and whether there is
    anything new to evaluate.
    """
    checkout = fetch_docs_repo(ref, cache_dir=repo)
    served = read_served(served_path) if served_path.is_file() else {}
    if checkout.commit == served.get("commit"):
        logger.info("Docs head is the served commit", commit=checkout.commit)
        return {
            "changed": False,
            "commit": checkout.commit,
            "served_commit": served.get("commit"),
            "served_snapshot": served.get("snapshot"),
        }
    date = datetime.now(UTC).strftime("%Y-%m-%d")
    corpus_dir = snapshot_root.expanduser() / date
    openapi = _openapi_path(checkout.path)
    summary = build_corpus(
        checkout,
        out_dir=corpus_dir,
        cache_dir=repo.expanduser().parent / "openapi",
        search_docs=None,
        openapi_offline=openapi,
    )
    record = SnapshotRecord(
        date=date,
        commit=checkout.commit,
        pages=summary.total_pages,
        content_digest=corpus_digest(corpus_dir),
        corpus_dir=_portable(corpus_dir),
        status="built",
        error=None,
        openapi_source=(str(openapi.relative_to(checkout.path)) if openapi is not None else None),
        openapi_snapshot_exact=openapi is not None,
        models_snapshot_exact=True,
    )
    records = [r for r in read_snapshot_manifest(manifest_path) if r.date != date]
    records.append(record)
    write_snapshot_manifest(manifest_path, records)
    served_records = [r for r in records if r.date == served.get("snapshot")]
    if served.get("snapshot") and not served_records:
        raise ValueError(f"served snapshot {served['snapshot']} is not in {manifest_path}")
    write_snapshot_manifest(gate_manifest.expanduser(), [*served_records, record])
    logger.info(
        "Built candidate snapshot", date=date, commit=checkout.commit, pages=summary.total_pages
    )
    return {
        "changed": True,
        "date": date,
        "commit": checkout.commit,
        "pages": summary.total_pages,
        "corpus_dir": str(corpus_dir),
        "gate_manifest": str(gate_manifest.expanduser()),
        "served_commit": served.get("commit"),
        "served_snapshot": served.get("snapshot"),
        "record": asdict(record),
    }


def accept(
    *,
    date: str,
    commit: str,
    run: str,
    labels: str,
    gate: str,
    manifest_path: Path = DEFAULT_MANIFEST,
    served_path: Path = SERVED_POINTER,
) -> dict[str, Any]:
    """Point the served pointer at a candidate the gate passed."""
    if not any(
        r.date == date and r.commit == commit for r in read_snapshot_manifest(manifest_path)
    ):
        raise ValueError(f"no snapshot {date} {commit} in {manifest_path}")
    payload = {
        "snapshot": date,
        "commit": commit,
        "run": run,
        "labels": labels,
        "gate": gate,
        "accepted_at": datetime.now(UTC).isoformat(),
    }
    write_served(served_path, payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="build the docs head as a candidate snapshot")
    build.add_argument("--ref", default=DOCS_HEAD)
    build.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    build.add_argument("--out", type=Path, default=DEFAULT_SNAPSHOT_ROOT)
    build.add_argument("--repo", type=Path, default=DEFAULT_CACHE_DIR)
    build.add_argument("--served", type=Path, default=SERVED_POINTER)
    build.add_argument("--gate-manifest", type=Path, default=DEFAULT_GATE_MANIFEST)
    acc = sub.add_parser("accept", help="move the served pointer to a candidate the gate passed")
    acc.add_argument("--date", required=True)
    acc.add_argument("--commit", required=True)
    acc.add_argument("--run", required=True, help="the run directory whose gate accepted it")
    acc.add_argument("--labels", required=True)
    acc.add_argument("--gate", required=True, help="directory holding gate.json")
    acc.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    acc.add_argument("--served", type=Path, default=SERVED_POINTER)
    args = parser.parse_args(argv)
    if args.command == "build":
        result = build_candidate(
            ref=args.ref,
            manifest_path=args.manifest,
            snapshot_root=args.out,
            repo=args.repo,
            served_path=args.served,
            gate_manifest=args.gate_manifest,
        )
    else:
        result = accept(
            date=args.date,
            commit=args.commit,
            run=args.run,
            labels=args.labels,
            gate=args.gate,
            manifest_path=args.manifest,
            served_path=args.served,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
