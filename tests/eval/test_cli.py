"""The generate CLI: the dry run, and what it refuses to leave behind."""

import json
import random
from argparse import Namespace
from pathlib import Path

import pytest

from glossator.eval.corpus import load_documents
from glossator.eval.datasets import QuestionType
from glossator.eval.generate.cli import _dry_run, _run
from glossator.eval.generate.planning import plan_attempts

FIXTURE_CORPUS = Path("tests/fixtures/corpus")


def arguments(**overrides: object) -> Namespace:
    defaults: dict[str, object] = {
        "corpus": FIXTURE_CORPUS,
        "out": None,
        "name": "dry",
        "n": 6,
        "provider": "zai",
        "model": "stub",
        "seed": 0,
        "concurrency": 2,
        "attempts_per_question": 2,
        "thinking": "disabled",
        "dry_run": True,
    }
    defaults.update(overrides)
    return Namespace(**defaults)


@pytest.mark.asyncio
async def test_a_dry_run_calls_nothing_and_leaves_no_run_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    corpus = FIXTURE_CORPUS.resolve()
    monkeypatch.chdir(tmp_path)

    await _run(arguments(corpus=corpus))

    assert not (tmp_path / "eval").exists()
    assert capsys.readouterr().out


def test_the_dry_run_samples_exactly_what_the_real_run_would(
    capsys: pytest.CaptureFixture[str],
) -> None:
    documents = load_documents(FIXTURE_CORPUS)
    args = arguments()

    _dry_run(documents, args)
    printed = [json.loads(line) for line in capsys.readouterr().out.splitlines()]

    single = [row for row in printed if row["type"] == QuestionType.SINGLE_PAGE.value]
    expected = plan_attempts(
        documents,
        QuestionType.SINGLE_PAGE,
        args.attempts_per_question,
        random.Random(args.seed),
    )
    assert single
    assert [row["candidate_id"] for row in single] == [plan.candidate_id for plan in expected]
