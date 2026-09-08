"""The in-process BM25 an unanswerable candidate is checked against."""

from pathlib import Path

from glossator.eval.corpus import load_documents
from glossator.eval.lexical import LexicalIndex, tokenize

FIXTURE_CORPUS = Path("tests/fixtures/corpus")


def test_tokenize_keeps_identifiers_and_drops_punctuation() -> None:
    assert tokenize("`mistral-embed` returns 1024 dimensions.") == [
        "mistral",
        "embed",
        "returns",
        "1024",
        "dimensions",
    ]


def test_the_index_finds_the_section_that_states_the_fact() -> None:
    index = LexicalIndex(load_documents(FIXTURE_CORPUS))

    hits = index.search("how many dimensions does mistral-embed return", top_k=3)

    assert hits
    assert any("capabilities/embeddings" in hit.document.url for hit in hits)
    assert hits[0].score > 0
    assert hits[0].label.startswith(hits[0].document.title)


def test_a_question_sharing_no_term_with_the_corpus_finds_nothing() -> None:
    index = LexicalIndex(load_documents(FIXTURE_CORPUS))

    assert index.search("zzzqqq unrelated wingding") == []


def test_hits_are_ordered_by_score_and_bounded_by_top_k() -> None:
    index = LexicalIndex(load_documents(FIXTURE_CORPUS))

    hits = index.search("function calling tool choice", top_k=4)

    assert len(hits) <= 4
    assert [hit.score for hit in hits] == sorted((hit.score for hit in hits), reverse=True)


def test_an_empty_corpus_returns_no_hits() -> None:
    assert LexicalIndex([]).search("anything") == []
