import json
from pathlib import Path

import pytest

from glossator.changelog import (
    StaleChangelogError,
    build_changelog,
    history_under,
    read_changelog,
)


def _page(root: Path, name: str, url: str, body: str, *, title: str | None = None) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"url: {url}\n"
        f"title: {title or name}\n"
        "kind: doc\nlocale: en\nsource_path: page.mdx\nsource_commit: abc\n"
        "breadcrumbs: []\n---\n"
        f"{body}"
    )


def _manifest(tmp_path: Path) -> Path:
    one, two, three = (tmp_path / date for date in ("one", "two", "three"))
    _page(one, "keep.md", "https://docs.mistral.ai/keep", "# Keep\n\n## A {#a}\n\nOld.\n")
    _page(one, "gone.md", "https://docs.mistral.ai/gone", "# Gone\n\nGone body.\n")
    _page(
        one,
        "move.md",
        "https://docs.mistral.ai/old",
        "# Move\n\nSee https://docs.mistral.ai/legacy/reference#part.\n",
    )
    _page(
        one,
        "rewrite.md",
        "https://docs.mistral.ai/legacy/guide",
        "# Guide\n\nOld prose.\n",
        title="Guide",
    )
    _page(two, "keep.md", "https://docs.mistral.ai/keep", "# Keep\n\n## A {#a}\n\nNew.\n")
    _page(
        two,
        "move.md",
        "https://docs.mistral.ai/new",
        "# Move\n\nSee https://docs.mistral.ai/current/reference#part.\n",
    )
    _page(
        two,
        "rewrite.md",
        "https://docs.mistral.ai/current/guide",
        "# Guide\n\nRewritten prose.\n",
        title="Guide",
    )
    _page(two, "added.md", "https://docs.mistral.ai/added", "# Added\n\nAdded body.\n")
    _page(three, "keep.md", "https://docs.mistral.ai/keep", "# Keep\n\n## A {#renamed}\n\nNew.\n")
    _page(
        three,
        "move.md",
        "https://docs.mistral.ai/new",
        "# Move\n\nSee https://docs.mistral.ai/current/reference#part.\n",
    )
    _page(
        three,
        "rewrite.md",
        "https://docs.mistral.ai/current/guide",
        "# Guide\n\nRewritten prose.\n",
        title="Guide",
    )
    _page(three, "added.md", "https://docs.mistral.ai/added", "# Added\n\nAdded body.\n")
    rows = []
    for date, root in (("2026-06-01", one), ("2026-06-15", two), ("2026-07-01", three)):
        rows.append(
            {
                "date": date,
                "commit": date,
                "pages": len(list(root.glob("*.md"))),
                "content_digest": f"digest-{date}",
                "corpus_dir": str(root),
                "status": "built",
                "error": None,
                "openapi_source": None,
                "openapi_snapshot_exact": True,
                "models_snapshot_exact": True,
            }
        )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"snapshots": rows}))
    return manifest


def test_builder_finds_added_changed_moved_removed_and_key_rename(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    out = tmp_path / "changelog"

    index = build_changelog(manifest, out)
    first = json.loads((out / "2026-06-01..2026-06-15.json").read_text())
    second = json.loads((out / "2026-06-15..2026-07-01.json").read_text())

    assert index["pairs"][0]["counts"] == {
        "added": 1,
        "changed": 2,
        "moved": 1,
        "removed": 1,
    }
    assert next(row for row in first if row["state"] == "added")["sections"] == 1
    assert next(row for row in first if row["state"] == "removed")["sections"] == 1
    move = next(row for row in first if row["state"] == "moved")
    assert (move["old_page"], move["page"]) == (
        "https://docs.mistral.ai/old",
        "https://docs.mistral.ai/new",
    )
    rewritten = next(row for row in first if row["page"] == "https://docs.mistral.ai/current/guide")
    assert rewritten["state"] == "changed"
    assert rewritten["old_page"] == "https://docs.mistral.ai/legacy/guide"
    rename = next(row for row in second if row["state"] == "moved")
    assert (rename["old_key"], rename["key"]) == ("a", "renamed")


def test_reader_refuses_manifest_digest_change(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    out = tmp_path / "changelog"
    build_changelog(manifest, out)
    payload = json.loads(manifest.read_text())
    payload["snapshots"][0]["content_digest"] = "changed"
    manifest.write_text(json.dumps(payload))

    with pytest.raises(StaleChangelogError):
        read_changelog(manifest, out)


def test_under_filters_rows_and_snaps_since_forward(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    out = tmp_path / "changelog"
    build_changelog(manifest, out)

    result = history_under("/keep", "2026-06-02", manifest, out)

    assert result["since"] == "2026-06-15"
    assert len(result["intervals"]) == 1
    assert [row["state"] for row in result["intervals"][0]["rows"]] == ["moved"]


def test_under_unknown_path_names_nearest_ancestor(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    out = tmp_path / "changelog"
    build_changelog(manifest, out)

    with pytest.raises(ValueError, match='nearest path with pages: "https://docs.mistral.ai/keep"'):
        history_under("/keep/missing", None, manifest, out)
