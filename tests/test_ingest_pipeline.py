"""The guards that stand between a corpus on disk and the index.

Neither needs Vespa or an API key: the manifest check runs before anything is
embedded, and the partial-run guard is about what `ingest_corpus` does with a
failure it has already collected.
"""

import asyncio
import shutil
from collections.abc import Iterable
from pathlib import Path

import pytest

from glossator.ingest.pages import CorpusError, verify_manifest
from glossator.ingest.pipeline import IngestReport, PartialIngestError, ingest_corpus


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


def test_a_partial_run_raises_rather_than_returning(
    corpus_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A caller that never inspects `failures` would otherwise measure a corpus with holes."""
    import glossator.ingest.pipeline as pipeline_module

    async def _all_fail(
        paths: Iterable[Path], ingest_one: object, sequential: bool = False
    ) -> list[Path]:
        return list(paths)

    monkeypatch.setattr(pipeline_module, "_run_batch", _all_fail)
    monkeypatch.setattr(pipeline_module, "build_pipeline", lambda *a, **k: None)

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
        paths: Iterable[Path], ingest_one: object, sequential: bool = False
    ) -> list[Path]:
        return list(paths)

    monkeypatch.setattr(pipeline_module, "_run_batch", _all_fail)
    monkeypatch.setattr(pipeline_module, "build_pipeline", lambda *a, **k: None)

    report = asyncio.run(ingest_corpus(corpus_dir, "sec128", allow_partial=True))

    assert len(report.failures) == 9
