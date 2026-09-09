"""The dataset schema: what a question must be, and what it is checked against."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from glossator.eval.datasets import (
    EvalQuestion,
    GoldSource,
    QuestionSource,
    QuestionType,
    read_jsonl,
    validate_against_corpus,
    write_jsonl,
)
from glossator.ingest.pages import CorpusPage, iter_page_paths, load_page, read_manifest

FIXTURE_CORPUS = Path("tests/fixtures/corpus")


def question(
    *,
    url: str = "https://docs.mistral.ai/agents/conversations",
    anchor: str | None = None,
    **overrides: object,
) -> EvalQuestion:
    fields: dict[str, object] = {
        "id": "q1",
        "question": "How is conversation state reused?",
        "type": QuestionType.SINGLE_PAGE,
        "gold": [GoldSource(url=url, anchor=anchor)],
        "reference_answer": "Reuse the conversation identifier.",
        "language": "en",
        "source": QuestionSource.HANDWRITTEN,
    }
    fields.update(overrides)
    return EvalQuestion.model_validate(fields)


def test_jsonl_round_trip_keeps_the_generator_metadata(tmp_path: Path) -> None:
    original = question(
        generator={
            "model": "glm-5.3-flash",
            "prompt_version": "v1",
            "prompt_hashes": {"single_section": "abc123"},
            "seed_section": ["https://docs.mistral.ai/agents/conversations"],
        },
    )
    path = tmp_path / "questions.jsonl"
    write_jsonl(path, [original])

    assert read_jsonl(path) == [original]


def test_blank_lines_and_non_ascii_survive_a_round_trip(tmp_path: Path) -> None:
    original = question(question="Combien de textes une requête d'embeddings accepte-t-elle ?")
    path = tmp_path / "questions.jsonl"
    write_jsonl(path, [original])
    path.write_text("\n" + path.read_text() + "\n\n")

    assert read_jsonl(path) == [original]


def test_a_malformed_line_names_its_line_number(tmp_path: Path) -> None:
    path = tmp_path / "questions.jsonl"
    write_jsonl(path, [question(), question()])
    path.write_text(path.read_text() + "not json\n")

    with pytest.raises(ValueError, match=r"questions\.jsonl:3"):
        read_jsonl(path)


def test_a_three_line_reference_answer_is_rejected() -> None:
    with pytest.raises(ValidationError, match="at most two lines"):
        question(reference_answer="one\ntwo\nthree")


def test_an_unanswerable_question_may_not_carry_gold() -> None:
    with pytest.raises(ValidationError, match="no gold sources"):
        question(type=QuestionType.UNANSWERABLE)


def test_an_answerable_question_needs_gold() -> None:
    with pytest.raises(ValidationError, match="at least one gold source"):
        question(gold=[])


def test_an_unanswerable_question_without_gold_is_valid() -> None:
    accepted = question(type=QuestionType.UNANSWERABLE, gold=[])

    assert accepted.gold == []


def test_reports_missing_urls_and_anchors(corpus_pages: list[CorpusPage]) -> None:
    manifest = read_manifest(FIXTURE_CORPUS)
    questions = [
        question(url="https://docs.mistral.ai/missing"),
        question(
            url="https://docs.mistral.ai/capabilities/embeddings", anchor="not-there"
        ).model_copy(update={"id": "q2"}),
    ]

    issues = validate_against_corpus(questions, manifest, corpus_pages)

    assert [issue.message for issue in issues] == [
        "gold URL is missing from the manifest",
        "gold anchor is missing from the page",
    ]


def test_an_anchor_the_page_declares_validates(corpus_pages: list[CorpusPage]) -> None:
    manifest = read_manifest(FIXTURE_CORPUS)
    questions = [
        question(url="https://docs.mistral.ai/capabilities/embeddings", anchor="the-models")
    ]

    assert validate_against_corpus(questions, manifest, corpus_pages) == []


def test_an_anchorless_gold_source_on_a_page_with_no_anchors_validates(
    corpus_pages: list[CorpusPage],
) -> None:
    manifest = read_manifest(FIXTURE_CORPUS)
    questions = [question(url="https://docs.mistral.ai/agents/conversations", anchor=None)]

    assert validate_against_corpus(questions, manifest, corpus_pages) == []


VENDORED_CORPUS = Path("corpus/mistral-docs")


@pytest.mark.parametrize(
    "dataset", sorted(Path("eval").glob("*.jsonl")), ids=lambda path: path.name
)
def test_every_shipped_dataset_still_resolves_against_the_vendored_corpus(dataset: Path) -> None:
    """A dataset whose gold no longer exists scores every configuration wrongly.

    The corpus is vendored and the datasets are committed beside it, so the two can
    only drift through a change in this repository, which is what this catches.
    """
    pages = [load_page(path) for path in iter_page_paths(VENDORED_CORPUS)]

    issues = validate_against_corpus(read_jsonl(dataset), read_manifest(VENDORED_CORPUS), pages)

    assert issues == []
