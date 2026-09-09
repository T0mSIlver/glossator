import asyncio
import hashlib
import json
from pathlib import Path

from mistralai.search.toolkit.context import RetrievalContext
from mistralai.search.toolkit.embedding import Embedder, EmbeddingResult

from glossator.history import phrase_history, question_history, section_history
from glossator.ingest.pipeline import CachedEmbedder
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import Hit


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
    result = section_history("/page#limits", _manifest(tmp_path))

    assert [row["state"] for row in result["states"]] == ["same", "changed"]
    assert "-The limit is 10." in result["states"][1]["diff"]
    assert "+The limit is 20." in result["states"][1]["diff"]


def test_question_history_filters_every_retrieval_to_its_date(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    configs: list[RetrievalConfig] = []

    class FakeEngine:
        def __init__(self, config: RetrievalConfig) -> None:
            configs.append(config)
            self.config = config

        async def search(self, question: str, top_k: int) -> list[Hit]:
            del question, top_k
            date = self.config.snapshot or ""
            content = f"answer on {date}"
            return [
                Hit(
                    chunk_id=date,
                    score=1.0,
                    url="https://docs.mistral.ai/page",
                    anchor="limits",
                    heading_path=("Page", "Limits"),
                    page_title="Page",
                    kind="doc",
                    locale="en",
                    section_index=1,
                    content=content,
                    source_id=f"page:{date}",
                    start_offset=0,
                    end_offset=len(content),
                    snapshot=date,
                    content_sha256=hashlib.sha256(content.encode()).hexdigest(),
                )
            ]

    result = asyncio.run(
        question_history("what is the limit?", manifest, engine_factory=FakeEngine)
    )

    assert [config.snapshot for config in configs] == ["2026-06-01", "2026-06-15"]
    assert all(config.rerank for config in configs)
    assert len(result["states"]) == 2


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
