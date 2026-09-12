import asyncio
import json
from pathlib import Path

import pytest
from mistralai.search.toolkit.context import RetrievalContext
from mistralai.search.toolkit.embedding import Embedder, EmbeddingResult

from glossator.history import UnknownPageError, phrase_history, section_history
from glossator.ingest.pipeline import CachedEmbedder


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


def _manifest(tmp_path: Path) -> Path:
    snapshots = []
    for date, body in (
        ("2026-06-01", "# Page\n\n## Limits {#limits}\n\nThe limit is 10.\n"),
        ("2026-06-15", "# Page\n\n## Limits {#limits}\n\nThe limit is 20.\n"),
    ):
        corpus = tmp_path / date
        _page(corpus / "page.md", "https://docs.mistral.ai/page", body)
        snapshots.append(
            {
                "date": date,
                "commit": date.replace("-", ""),
                "pages": 1,
                "content_digest": "digest",
                "corpus_dir": str(corpus),
                "status": "built",
                "error": None,
                "openapi_source": "openapi.yaml",
                "openapi_snapshot_exact": True,
                "models_snapshot_exact": True,
            }
        )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"snapshots": snapshots}))
    return manifest


def test_phrase_history_reports_first_and_last_snapshot(tmp_path: Path) -> None:
    result = phrase_history("The limit is", _manifest(tmp_path))

    assert result["first"]["snapshot"] == "2026-06-01"
    assert result["last"]["snapshot"] == "2026-06-15"
    assert ":~:text=" in result["first"]["fragment_url"]


def test_section_history_reports_a_changed_section_and_diff(tmp_path: Path) -> None:
    result = section_history("/page", "limits", _manifest(tmp_path))

    assert [row["state"] for row in result["states"]] == ["same", "changed"]
    assert "-The limit is 10." in result["states"][1]["diff"]
    assert "+The limit is 20." in result["states"][1]["diff"]


def test_section_history_rejects_unknown_page(tmp_path: Path) -> None:
    with pytest.raises(UnknownPageError):
        section_history("/missing", None, _manifest(tmp_path))


def test_section_history_rejects_unknown_key(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match='no section "missing"'):
        section_history("/page", "missing", _manifest(tmp_path))


def test_section_history_addresses_generated_key(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    for date in ("2026-06-01", "2026-06-15"):
        _page(
            tmp_path / date / "page.md",
            "https://docs.mistral.ai/page",
            "# Page\n\n## Limits\n\nThe limit is 10.\n",
        )

    result = section_history("/page", "limits", manifest)

    assert result["section"] == "limits"
    assert all(row["anchor"] == "limits" for row in result["states"])


def test_section_history_prefers_renamed_page_for_leading_history(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    payload = json.loads(manifest.read_text())
    old_root = Path(payload["snapshots"][0]["corpus_dir"])
    new_root = Path(payload["snapshots"][1]["corpus_dir"])
    (old_root / "page.md").unlink()
    _page(
        old_root / "old.md",
        "https://docs.mistral.ai/studio-api/conversations/page",
        "# Page\n\n## Before {#before}\n\nShared introduction.\n",
    )
    _page(
        old_root / "unrelated.md",
        "https://docs.mistral.ai/admin/page",
        "# Admin\n\n## Before {#before}\n\nShared introduction.\n",
    )
    _page(
        new_root / "page.md",
        "https://docs.mistral.ai/studio/conversations/page",
        "# Page\n\n## Before {#before}\n\nShared introduction.\n",
    )

    states = section_history(
        "https://docs.mistral.ai/studio/conversations/page", "before", manifest
    )["states"]

    assert states[0]["page"] == "https://docs.mistral.ai/studio-api/conversations/page"
    assert states[1]["state"] == "moved"


class FakeEmbedder(Embedder):
    def __init__(self) -> None:
        super().__init__("fake-model")
        self.calls = 0

    async def embed(
        self, texts: list[str], context: RetrievalContext = RetrievalContext()
    ) -> EmbeddingResult:
        del context
        self.calls += 1
        return EmbeddingResult(
            embeddings=[[float(len(text)), 1.0] for text in texts], total_tokens=len(texts)
        )


def test_embedding_cache_reuses_unchanged_chunk_content(tmp_path: Path) -> None:
    inner = FakeEmbedder()
    first = CachedEmbedder(inner, 2, tmp_path)
    second = CachedEmbedder(inner, 2, tmp_path)

    one = asyncio.run(first.embed(["unchanged"]))
    two = asyncio.run(second.embed(["unchanged"]))

    assert one.embeddings == two.embeddings
    assert inner.calls == 1
    assert first.embedded_chunks == 1
    assert second.cached_chunks == 1


def test_first_and_last_follow_the_dates_not_the_manifest_order(tmp_path: Path) -> None:
    """Every form reads its answer out of the snapshot order, so a manifest
    written out of order would invert "first appeared" and "last seen"."""
    manifest = _manifest(tmp_path)
    payload = json.loads(manifest.read_text())
    payload["snapshots"].reverse()
    manifest.write_text(json.dumps(payload))

    result = phrase_history("The limit is", manifest)

    assert result["first"]["snapshot"] == "2026-06-01"
    assert result["last"]["snapshot"] == "2026-06-15"
    states = section_history("https://docs.mistral.ai/page#limits", None, manifest)["states"]
    assert [state["snapshot"] for state in states] == ["2026-06-01", "2026-06-15"]
    assert states[1]["state"] == "changed"


def test_phrase_history_scoped_to_a_page_and_a_path(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)

    on_page = phrase_history("The limit is", manifest, page_url="/page")
    assert on_page["page_url"] == "https://docs.mistral.ai/page"
    assert on_page["snapshots_found"] == 2

    under = phrase_history("The limit is", manifest, under="/")
    assert under["under"] == "https://docs.mistral.ai"
    assert under["snapshots_found"] == 2

    with pytest.raises(UnknownPageError):
        phrase_history("The limit is", manifest, page_url="/missing")
    with pytest.raises(ValueError, match="page_url or under, not both"):
        phrase_history("The limit is", manifest, page_url="/page", under="/")
