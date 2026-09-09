"""The guards that stand between a corpus on disk and the index.

Neither needs Vespa or an API key: the manifest check runs before anything is
embedded, and the partial-run guard is about what `ingest_corpus` does with a
failure it has already collected.
"""

import asyncio
import shutil
from collections.abc import Iterable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from mistralai.search.toolkit.context import IngestContext
from mistralai.search.toolkit.document import Document
from mistralai.search.toolkit.search.errors import IndexingError

from glossator.index.variants import get_variant
from glossator.ingest.pages import CorpusError, verify_manifest
from glossator.ingest.pipeline import (
    IndexWritePreflightError,
    IngestReport,
    PartialIngestError,
    _verify_index_writable,
    ingest_corpus,
)


class FakeIndex:
    def __init__(self, *, reject: bool = False) -> None:
        self.reject = reject
        self.indexed: list[Document] = []
        self.deleted: list[str] = []

    async def index_document(
        self, document: Document, context: IngestContext = IngestContext()
    ) -> None:
        if self.reject:
            raise IndexingError("Failed to index document")
        self.indexed.append(document)

    async def delete_document(self, doc_id: str, context: IngestContext = IngestContext()) -> None:
        self.deleted.append(doc_id)


class RejectingPipeline:
    def __init__(self, index: FakeIndex) -> None:
        self.stores = [index]
        self.paths: list[str] = []

    async def run_file(self, file: Any) -> None:
        self.paths.append(file.path)
        raise IndexingError("Failed to index document")


@pytest.fixture
def corpus_copy(corpus_dir: Path, tmp_path: Path) -> Path:
    target = tmp_path / "corpus"
    shutil.copytree(corpus_dir, target)
    return target


def test_the_fixture_corpus_matches_its_manifest(corpus_dir: Path) -> None:
    assert verify_manifest(corpus_dir) == 9


def test_an_edited_page_is_refused(corpus_copy: Path) -> None:
    """A page changed after the manifest was written is content no commit produced."""
    page = corpus_copy / "models-mistral-medium.md"
    page.write_text(page.read_text() + "\nAn edit nobody recorded.\n")

    with pytest.raises(CorpusError, match="content changed"):
        verify_manifest(corpus_copy)


def test_a_missing_page_is_refused(corpus_copy: Path) -> None:
    (corpus_copy / "models-mistral-medium.md").unlink()

    with pytest.raises(CorpusError, match="missing"):
        verify_manifest(corpus_copy)


def test_a_corpus_without_a_manifest_is_allowed(tmp_path: Path, corpus_dir: Path) -> None:
    """Checked as far as it can be: not at all, and said so in the log."""
    target = tmp_path / "unmanifested"
    target.mkdir()
    shutil.copy(corpus_dir / "models-mistral-medium.md", target)

    assert verify_manifest(target) == 0


def test_ingest_refuses_a_corpus_that_does_not_match_its_manifest(
    corpus_copy: Path,
) -> None:
    """The check runs before any page is embedded, so nothing is spent on it."""
    page = corpus_copy / "models-mistral-medium.md"
    page.write_text(page.read_text() + "\nAn edit nobody recorded.\n")

    with pytest.raises(CorpusError, match="manifest"):
        asyncio.run(ingest_corpus(corpus_copy, "sec128"))


def test_the_write_probe_is_fed_and_deleted_before_ingestion() -> None:
    index = FakeIndex()

    asyncio.run(_verify_index_writable(index, get_variant("sec128")))

    assert len(index.indexed) == 1
    assert len(index.indexed[0].chunks[0].embedding or []) == 128
    assert index.deleted == [index.indexed[0].id]


def test_a_rejected_write_probe_names_the_schema_and_likely_disk_cause() -> None:
    index = FakeIndex(reject=True)

    with pytest.raises(IndexWritePreflightError, match="docs_section_lowdim") as raised:
        asyncio.run(_verify_index_writable(index, get_variant("sec128")))

    assert "disk usage" in str(raised.value)
    assert index.deleted == []


def test_ingestion_stops_after_the_first_page_feed_failure(
    corpus_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import glossator.ingest.pipeline as pipeline_module

    pipeline = RejectingPipeline(FakeIndex())
    monkeypatch.setattr(pipeline_module, "build_pipeline", lambda *a, **k: pipeline)

    with pytest.raises(PartialIngestError):
        asyncio.run(ingest_corpus(corpus_dir, "sec128", concurrency=1))

    assert len(pipeline.paths) == 1


def test_allow_partial_continues_after_page_feed_failures(
    corpus_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import glossator.ingest.pipeline as pipeline_module

    pipeline = RejectingPipeline(FakeIndex())
    monkeypatch.setattr(pipeline_module, "build_pipeline", lambda *a, **k: pipeline)

    report = asyncio.run(ingest_corpus(corpus_dir, "sec128", concurrency=1, allow_partial=True))

    assert len(set(pipeline.paths)) == 9
    assert len(report.failures) == 9


def test_a_partial_run_raises_rather_than_returning(
    corpus_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A caller that never inspects `failures` would otherwise measure a corpus with holes."""
    import glossator.ingest.pipeline as pipeline_module

    async def _all_fail(
        paths: Iterable[Path], ingest_one: object, sequential: bool = False, **kwargs: object
    ) -> list[Path]:
        return list(paths)

    monkeypatch.setattr(pipeline_module, "_run_batch", _all_fail)
    monkeypatch.setattr(
        pipeline_module, "build_pipeline", lambda *a, **k: SimpleNamespace(stores=[FakeIndex()])
    )

    with pytest.raises(PartialIngestError) as raised:
        asyncio.run(ingest_corpus(corpus_dir, "sec128"))

    report = raised.value.report
    assert isinstance(report, IngestReport)
    assert len(report.failures) == 9
    assert report.pages == 0


def test_allow_partial_returns_the_report_instead(
    corpus_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import glossator.ingest.pipeline as pipeline_module

    async def _all_fail(
        paths: Iterable[Path], ingest_one: object, sequential: bool = False, **kwargs: object
    ) -> list[Path]:
        return list(paths)

    monkeypatch.setattr(pipeline_module, "_run_batch", _all_fail)
    monkeypatch.setattr(
        pipeline_module, "build_pipeline", lambda *a, **k: SimpleNamespace(stores=[FakeIndex()])
    )

    report = asyncio.run(ingest_corpus(corpus_dir, "sec128", allow_partial=True))

    assert len(report.failures) == 9
