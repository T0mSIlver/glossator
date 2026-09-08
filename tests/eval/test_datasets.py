from pathlib import Path

from glossator.eval.corpus_reader import read_corpus, read_manifest
from glossator.eval.datasets import (
    EvalQuestion,
    GoldSource,
    QuestionSource,
    QuestionType,
    read_jsonl,
    validate_against_corpus,
    write_jsonl,
)

FIXTURE_CORPUS = Path("tests/fixtures/corpus")


def question(*, url: str, anchor: str | None) -> EvalQuestion:
    return EvalQuestion(
        id="q1",
        question="How is state reused?",
        type=QuestionType.SINGLE_PAGE,
        gold=[GoldSource(url=url, anchor=anchor)],
        reference_answer="Reuse the conversation identifier.",
        language="en",
        source=QuestionSource.HANDWRITTEN,
    )


def test_jsonl_round_trip(tmp_path: Path) -> None:
    original = question(
        url="https://docs.mistral.ai/studio/conversations",
        anchor="reusing-conversation-state",
    )
    path = tmp_path / "questions.jsonl"
    write_jsonl(path, [original])

    assert read_jsonl(path) == [original]


def test_reports_missing_urls_and_anchors() -> None:
    pages = read_corpus(FIXTURE_CORPUS)
    manifest = read_manifest(FIXTURE_CORPUS / "manifest.json")
    questions = [
        question(url="https://docs.mistral.ai/missing", anchor=None),
        question(
            url="https://docs.mistral.ai/studio/conversations",
            anchor="not-there",
        ).model_copy(update={"id": "q2"}),
    ]

    issues = validate_against_corpus(questions, manifest, pages)

    assert [issue.message for issue in issues] == [
        "gold URL is missing from the manifest",
        "gold anchor is missing from the page",
    ]
