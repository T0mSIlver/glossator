"""Write normalized pages, the manifest, and the upstream licence and notice."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

from . import DOCS_REPO_URL, LOCALE, SITE_ORIGIN
from .frontmatter import render as render_frontmatter

log = structlog.get_logger(__name__)

MANIFEST_NAME = "manifest.json"
LICENSE_NAME = "LICENSE"
NOTICE_NAME = "NOTICE"

KIND_DOC = "doc"
KIND_API = "api"
KIND_MODEL = "model"


@dataclass
class CorpusPage:
    """One page ready to be written."""

    url_path: str
    title: str
    kind: str
    markdown: str
    source_path: str
    breadcrumbs: list[str] = field(default_factory=list)
    hidden: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def url(self) -> str:
        return f"{SITE_ORIGIN}{self.url_path}"

    @property
    def relative_path(self) -> str:
        return f"{self.url_path.strip('/') or 'index'}.md"


def write_corpus(
    pages: list[CorpusPage],
    out_dir: Path,
    source_commit: str,
    license_text: str | None,
) -> list[dict[str, Any]]:
    """Write every page plus the manifest; remove files no longer in the corpus."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: set[Path] = set()
    manifest: list[dict[str, Any]] = []

    for page in sorted(pages, key=lambda page: page.url_path):
        target = out_dir / page.relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        document = _render_page(page, source_commit)
        target.write_text(document, encoding="utf-8")
        written.add(target.resolve())
        manifest.append(
            {
                "url": page.url,
                "path": page.relative_path,
                "title": page.title,
                "kind": page.kind,
                "source_path": page.source_path,
                "source_commit": source_commit,
                "sha256": hashlib.sha256(document.encode("utf-8")).hexdigest(),
            }
        )

    manifest_path = out_dir / MANIFEST_NAME
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", "utf-8")
    written.add(manifest_path.resolve())

    if license_text is not None:
        license_path = out_dir / LICENSE_NAME
        license_path.write_text(license_text, encoding="utf-8")
        written.add(license_path.resolve())

    notice_path = out_dir / NOTICE_NAME
    notice_path.write_text(_notice(source_commit, len(manifest)), encoding="utf-8")
    written.add(notice_path.resolve())

    removed = _remove_stale(out_dir, written)
    if removed:
        log.info("removed stale corpus files", count=removed)
    return manifest


def _render_page(page: CorpusPage, source_commit: str) -> str:
    metadata: dict[str, Any] = {
        "url": page.url,
        "title": page.title,
        "breadcrumbs": page.breadcrumbs,
        "kind": page.kind,
        "locale": LOCALE,
        "source_path": page.source_path,
        "source_commit": source_commit,
    }
    if page.hidden:
        metadata["hidden"] = True
    metadata.update(page.extra)
    return render_frontmatter(metadata) + "\n" + page.markdown.strip() + "\n"


def _remove_stale(out_dir: Path, keep: set[Path]) -> int:
    removed = 0
    for path in sorted(out_dir.rglob("*"), reverse=True):
        if path.is_dir():
            if not any(path.iterdir()):
                path.rmdir()
            continue
        if path.resolve() not in keep:
            path.unlink()
            removed += 1
    return removed


def _notice(source_commit: str, page_count: int) -> str:
    return (
        "This directory contains documentation from Mistral AI's public documentation\n"
        f"repository, {DOCS_REPO_URL}, converted to normalized markdown.\n"
        "\n"
        f"Source commit: {source_commit}\n"
        f"Site: {SITE_ORIGIN}\n"
        f"Pages: {page_count}\n"
        "\n"
        "The upstream repository is licensed under the Apache License 2.0; a copy is\n"
        "in this directory as LICENSE. Content here is derived from that repository,\n"
        "from the OpenAPI specification published at\n"
        f"{SITE_ORIGIN}/openapi.yaml, and from the model catalog in the same\n"
        "repository. Each page records its own upstream source path in frontmatter.\n"
    )
