"""What ``GET /health`` measures: each variant's document count and the vendored corpus."""

import asyncio
import json
from pathlib import Path
from typing import Any

import structlog

from glossator.surface.engines import EngineRegistry

logger = structlog.get_logger(__name__)


async def variant_documents(registry: EngineRegistry, name: str) -> int | None:
    """One variant's document count, or None when asking for it failed."""
    try:
        return await asyncio.wait_for(registry.get(name).document_count(), timeout=5.0)
    except Exception as exc:
        logger.warning("Health probe failed", variant=name, error=str(exc))
        return None


def corpus_summary(corpus_dir: Path) -> dict[str, Any] | None:
    """Page count, source commit and page kinds from the vendored manifest."""
    manifest_path = corpus_dir / "manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        pages = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    commits = {page.get("source_commit") for page in pages if page.get("source_commit")}
    kinds: dict[str, int] = {}
    for page in pages:
        kind = str(page.get("kind", "?"))
        kinds[kind] = kinds.get(kind, 0) + 1
    return {
        "pages": len(pages),
        "source_commit": sorted(commits)[0] if len(commits) == 1 else sorted(commits),
        "source_repo": "mistralai/platform-docs-public",
        "license": "Apache-2.0",
        "kinds": kinds,
    }


__all__ = ["corpus_summary", "variant_documents"]
