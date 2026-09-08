"""Shared fixtures: the sample corpus every ingestion test reads."""

from pathlib import Path

import pytest

from glossator.ingest.pages import CorpusPage, load_page

FIXTURE_CORPUS = Path(__file__).parent / "fixtures" / "corpus"


@pytest.fixture(scope="session")
def corpus_dir() -> Path:
    return FIXTURE_CORPUS


@pytest.fixture(scope="session")
def corpus_pages() -> list[CorpusPage]:
    return [load_page(path) for path in sorted(FIXTURE_CORPUS.glob("*.md"))]


@pytest.fixture(scope="session")
def function_calling_page() -> CorpusPage:
    """The long page: several headings, code fences, and a section over the budget."""
    return load_page(FIXTURE_CORPUS / "capabilities-function-calling.md")


@pytest.fixture(scope="session")
def table_page() -> CorpusPage:
    """The page whose sections are mostly one large table each."""
    return load_page(FIXTURE_CORPUS / "models-capability-matrix.md")
