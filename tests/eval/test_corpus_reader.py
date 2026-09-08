from pathlib import Path

from glossator.eval.corpus_reader import read_corpus, read_manifest

FIXTURE_CORPUS = Path("tests/fixtures/corpus")


def test_reads_pages_and_manifest() -> None:
    pages = read_corpus(FIXTURE_CORPUS)
    manifest = read_manifest(FIXTURE_CORPUS / "manifest.json")

    assert len(pages) == 5
    assert len(manifest) == 5
    assert {page.kind for page in pages} == {"doc", "api", "model"}


def test_builds_nested_heading_paths_and_section_boundaries() -> None:
    page = next(
        page
        for page in read_corpus(FIXTURE_CORPUS)
        if page.title == "Conversations API"
    )
    by_anchor = {section.anchor: section for section in page.sections}

    assert by_anchor["supplying-new-inputs"].heading_path == [
        "Conversations API",
        "Reusing conversation state",
        "Supplying new inputs",
    ]
    assert "New inputs may contain" in by_anchor["reusing-conversation-state"].body
    assert by_anchor["reusing-conversation-state"].token_estimate >= 80
    assert by_anchor["supplying-new-inputs"].token_estimate >= 80
