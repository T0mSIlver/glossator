"""Invariants the committed corpus must hold, checked without network access."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from glossator.corpus.mistral_docs.fences import (
    iter_lines,
    strip_fenced_lines,
    strip_inline_code,
)
from glossator.corpus.mistral_docs.frontmatter import split as split_frontmatter
from glossator.corpus.mistral_docs.writer import KIND_API, KIND_DOC, KIND_MODEL

CORPUS_DIR = Path(__file__).resolve().parents[2] / "corpus" / "mistral-docs"
JSX_RESIDUE = re.compile(r"<[A-Z][A-Za-z]*[ >/]")
ANCHOR = re.compile(r"\{#([^}]+)\}")
REQUIRED_KEYS = ("url", "title", "breadcrumbs", "kind", "locale", "source_path", "source_commit")

pytestmark = pytest.mark.skipif(
    not (CORPUS_DIR / "manifest.json").is_file(),
    reason="corpus not built; run `make corpus-refresh`",
)


@pytest.fixture(scope="module")
def manifest() -> list[dict[str, str]]:
    entries = json.loads((CORPUS_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert isinstance(entries, list)
    return [dict(entry) for entry in entries]


def test_manifest_matches_the_files_on_disk(manifest: list[dict[str, str]]) -> None:
    on_disk = {str(path.relative_to(CORPUS_DIR)) for path in CORPUS_DIR.rglob("*.md")}
    assert {entry["path"] for entry in manifest} == on_disk


def test_manifest_hashes_are_current(manifest: list[dict[str, str]]) -> None:
    for entry in manifest:
        content = (CORPUS_DIR / entry["path"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == entry["sha256"], entry["path"]


def test_every_page_has_valid_frontmatter(manifest: list[dict[str, str]]) -> None:
    for entry in manifest:
        text = (CORPUS_DIR / entry["path"]).read_text(encoding="utf-8")
        metadata, body = split_frontmatter(text)
        assert metadata, entry["path"]
        for key in REQUIRED_KEYS:
            assert key in metadata, f"{entry['path']} is missing {key}"
        assert metadata["url"] == entry["url"]
        assert metadata["url"].startswith("https://docs.mistral.ai/")
        assert metadata["kind"] in {KIND_DOC, KIND_API, KIND_MODEL}
        assert metadata["locale"] == "en"
        assert isinstance(metadata["breadcrumbs"], list)
        assert body.lstrip().startswith("# "), entry["path"]


def test_no_jsx_residue_outside_fences(manifest: list[dict[str, str]]) -> None:
    offenders = []
    for entry in manifest:
        _, body = split_frontmatter((CORPUS_DIR / entry["path"]).read_text(encoding="utf-8"))
        # Inline code carries placeholder tokens such as `<PROVIDER>_API_KEY`, which are
        # content, not markup, so they are excluded the same way fenced blocks are.
        prose = strip_inline_code(strip_fenced_lines(body))
        if JSX_RESIDUE.search(prose):
            offenders.append(entry["path"])
    assert offenders == []


LINK_TARGET = re.compile(r"\]\((?P<target>[^)\s]*)")
ABSOLUTE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def test_every_link_target_is_absolute(manifest: list[dict[str, str]]) -> None:
    # A corpus file is not a URL, so a relative target resolves against the wrong base.
    offenders = []
    for entry in manifest:
        _, body = split_frontmatter((CORPUS_DIR / entry["path"]).read_text(encoding="utf-8"))
        for line, in_fence in iter_lines(body):
            if in_fence:
                continue
            for match in LINK_TARGET.finditer(line):
                target = match.group("target")
                if target and not ABSOLUTE.match(target):
                    offenders.append((entry["path"], target))
    assert offenders == []


# Pages where the upstream MDX reuses one `sectionId` on several headings, so the
# live deep link resolves to the first of them. Reproduced faithfully rather than
# renamed, because renaming would invent an anchor the site does not have.
UPSTREAM_DUPLICATE_ANCHORS = {"resources/deprecated/finetuning.md"}


def test_anchors_are_unique_except_where_upstream_reuses_them(
    manifest: list[dict[str, str]],
) -> None:
    offenders = set()
    for entry in manifest:
        _, body = split_frontmatter((CORPUS_DIR / entry["path"]).read_text(encoding="utf-8"))
        anchors = [
            match.group(1)
            for line, in_fence in iter_lines(body)
            if not in_fence and line.startswith("#")
            for match in ANCHOR.finditer(line)
        ]
        if len(anchors) != len(set(anchors)):
            offenders.add(entry["path"])
    assert offenders == UPSTREAM_DUPLICATE_ANCHORS


def test_licence_and_notice_are_present() -> None:
    assert (CORPUS_DIR / "LICENSE").is_file()
    notice = (CORPUS_DIR / "NOTICE").read_text(encoding="utf-8")
    assert "platform-docs-public" in notice
    assert "Source commit:" in notice


def test_the_capability_matrix_answers_the_function_calling_question() -> None:
    matrix = (CORPUS_DIR / "models.md").read_text(encoding="utf-8")
    assert "**[Function Calling]" in matrix
    assert "mistral-medium-latest" in matrix
