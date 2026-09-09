"""Build reproducible dated corpora from the documentation repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from glossator.corpus.mistral_docs import PINNED_REF
from glossator.corpus.mistral_docs.build import BuildError, build_corpus
from glossator.corpus.mistral_docs.source import (
    DEFAULT_CACHE_DIR,
    DocsCheckout,
    SourceError,
    fetch_docs_repo,
)
from glossator.ingest.pages import read_manifest

logger = structlog.get_logger(__name__)

SNAPSHOT_DATES = (
    "2026-06-01",
    "2026-06-15",
    "2026-07-01",
    "2026-07-15",
    "2026-08-01",
    "2026-08-15",
    "2026-09-01",
)
DEFAULT_MANIFEST = Path("eval/snapshots/manifest.json")
MANIFEST_VAR = "GLOSSATOR_SNAPSHOT_MANIFEST"
DEFAULT_SNAPSHOT_ROOT = Path.home() / ".cache" / "glossator" / "snapshots"
OPENAPI_CANDIDATES = (
    "openapi-public-doc.yaml",
    "openapi.yaml",
    "public/openapi.yaml",
)


@dataclass(frozen=True, slots=True)
class SnapshotRecord:
    date: str
    commit: str
    pages: int | None
    content_digest: str | None
    corpus_dir: str
    status: str
    error: str | None
    openapi_source: str | None
    openapi_snapshot_exact: bool
    models_snapshot_exact: bool


def configured_manifest() -> Path:
    """Where a serving entrypoint reads the snapshot manifest from.

    Read at call time, and in one place: the API and the MCP server both expose
    the `history` forms and must agree about which manifest they answer from.
    """
    return Path(os.environ.get(MANIFEST_VAR, "").strip() or DEFAULT_MANIFEST)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise SourceError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def resolve_snapshots(repo: Path = DEFAULT_CACHE_DIR) -> list[tuple[str, str]]:
    """Resolve the seven dated commits and the project's pinned commit."""
    if not (repo / ".git").is_dir():
        fetch_docs_repo(PINNED_REF, cache_dir=repo)
    resolved = [
        (date, _git(repo, "rev-list", "-1", f"--before={date}", "HEAD")) for date in SNAPSHOT_DATES
    ]
    pinned = _git(repo, "rev-parse", f"{PINNED_REF}^{{commit}}")
    pinned_date = _git(repo, "show", "-s", "--format=%cs", pinned)
    resolved.append((pinned_date, pinned))
    return resolved


def _openapi_path(checkout: DocsCheckout) -> Path | None:
    for relative in OPENAPI_CANDIDATES:
        candidate = checkout.path / relative
        if candidate.is_file():
            return candidate
    return None


def corpus_digest(corpus_dir: Path) -> str:
    """Digest the ordered page paths and hashes from a corpus manifest."""
    entries = read_manifest(corpus_dir)
    material = [
        {"path": str(row.get("path", "")), "sha256": str(row.get("sha256", ""))} for row in entries
    ]
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def build_snapshots(
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    snapshot_root: Path = DEFAULT_SNAPSHOT_ROOT,
    repo: Path = DEFAULT_CACHE_DIR,
) -> list[SnapshotRecord]:
    """Build all snapshots, recording failures without stopping later dates."""
    records: list[SnapshotRecord] = []
    for date, commit in resolve_snapshots(repo):
        corpus_dir = snapshot_root / date
        openapi_source: str | None = None
        openapi_exact = False
        try:
            checkout = fetch_docs_repo(commit, cache_dir=repo)
            openapi = _openapi_path(checkout)
            openapi_source = (
                str(openapi.relative_to(checkout.path)) if openapi is not None else None
            )
            openapi_exact = openapi is not None
            summary = build_corpus(
                checkout,
                out_dir=corpus_dir,
                cache_dir=repo.parent / "openapi",
                search_docs=None,
                openapi_offline=openapi,
            )
            records.append(
                SnapshotRecord(
                    date=date,
                    commit=commit,
                    pages=summary.total_pages,
                    content_digest=corpus_digest(corpus_dir),
                    corpus_dir=_portable_path(corpus_dir),
                    status="built",
                    error=None,
                    openapi_source=openapi_source,
                    openapi_snapshot_exact=openapi_exact,
                    models_snapshot_exact=True,
                )
            )
        except (BuildError, SourceError, OSError, ValueError) as exc:
            logger.error("Snapshot build failed", date=date, commit=commit, error=str(exc))
            records.append(
                SnapshotRecord(
                    date=date,
                    commit=commit,
                    pages=None,
                    content_digest=None,
                    corpus_dir=_portable_path(corpus_dir),
                    status="failed",
                    error=str(exc),
                    openapi_source=openapi_source,
                    openapi_snapshot_exact=openapi_exact,
                    models_snapshot_exact=True,
                )
            )
    write_snapshot_manifest(manifest_path, records)
    return records


def _portable_path(path: Path) -> str:
    resolved = path.expanduser()
    try:
        return f"~/{resolved.relative_to(Path.home())}"
    except ValueError:
        return str(path)


def write_snapshot_manifest(path: Path, records: list[SnapshotRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "source_repo": "https://github.com/mistralai/platform-docs-public.git",
        "resolved_with": "git rev-list -1 --before=<date> HEAD",
        "generated_at": datetime.now(UTC).isoformat(),
        "snapshots": [asdict(record) for record in records],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def read_snapshot_manifest(path: Path = DEFAULT_MANIFEST) -> list[SnapshotRecord]:
    payload = json.loads(path.read_text())
    rows = payload.get("snapshots") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise ValueError(f"{path}: expected a snapshots list")
    return [SnapshotRecord(**row) for row in rows]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glossator.corpus.snapshots")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    build.add_argument("--out", type=Path, default=DEFAULT_SNAPSHOT_ROOT)
    build.add_argument("--repo", type=Path, default=DEFAULT_CACHE_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    records = build_snapshots(
        manifest_path=args.manifest,
        snapshot_root=args.out,
        repo=args.repo,
    )
    for record in records:
        detail = f"{record.pages} pages" if record.pages is not None else record.error
        print(f"{record.date} {record.commit[:12]} {record.status}: {detail}")
    return 1 if any(record.status == "failed" for record in records) else 0


if __name__ == "__main__":
    raise SystemExit(main())
