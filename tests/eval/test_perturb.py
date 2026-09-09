"""The perturbations: what each kind produces, what the filter drops, what repeats."""

import argparse
import asyncio
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from glossator.eval.datasets import EvalQuestion, GoldSource, QuestionSource, QuestionType
from glossator.eval.perturb import (
    CHATTY,
    KEYBOARD_NEIGHBOURS,
    KEYWORDS,
    KINDS,
    MAX_TYPOS,
    MIN_TYPOS,
    TYPOS,
    VAGUE,
    WRONG_TERM,
    NoisyQuestion,
    SameQuestion,
    WrongTermQuestion,
    assign_kinds,
    perturb_one,
    run,
    typo_variant,
)
from glossator.eval.providers import Completion, ProviderCallError, TokenUsage

QUESTION_TEXT = "How do I set the temperature parameter on a chat completion request?"


def question(index: int = 0, text: str = QUESTION_TEXT) -> EvalQuestion:
    return EvalQuestion(
        id=f"q-{index}",
        question=text,
        type=QuestionType.SINGLE_PAGE,
        gold=[GoldSource(url="https://docs.mistral.ai/api", anchor="chat")],
        reference_answer="Send temperature in the request body.",
        language="en",
        source=QuestionSource.GENERATED,
        generator={"prompt_version": "v1"},
    )


class StubProvider:
    """Answers every schema with a valid object, configurable per test."""

    def __init__(
        self,
        *,
        variant: str = "temperature chat completion request",
        same: bool = True,
        adds_facts: bool = False,
        parses: bool = True,
        fails: bool = False,
    ) -> None:
        self.variant = variant
        self.same = same
        self.adds_facts = adds_facts
        self.parses = parses
        self.fails = fails
        self.prompts: list[str] = []

    async def complete(
        self,
        messages: Sequence[Any],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        response_schema: type[BaseModel] | None,
        thinking: Any,
        cache_nonce: str | None = None,
    ) -> Completion:
        del model, temperature, max_tokens, thinking, cache_nonce
        self.prompts.append(messages[-1]["content"])
        if self.fails:
            raise ProviderCallError("stub failure")
        parsed: BaseModel | None = None
        if self.parses:
            if response_schema is SameQuestion:
                parsed = SameQuestion(
                    asks_the_same_thing=self.same, adds_facts=self.adds_facts, reason="stub"
                )
            elif response_schema is WrongTermQuestion:
                parsed = WrongTermQuestion(
                    noisy_question=self.variant,
                    original_term="temperature",
                    replacement_term="top_p",
                )
            elif response_schema is NoisyQuestion:
                parsed = NoisyQuestion(noisy_question=self.variant)
        return Completion(
            text="{}",
            parsed=parsed,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5),
            cached=False,
            model="stub",
            provider="zai",
            finish_reason="stop",
        )


# --------------------------------------------------------------------------- #
# Typos
# --------------------------------------------------------------------------- #


def test_typos_change_the_question_without_a_model() -> None:
    variant = typo_variant(QUESTION_TEXT, seed=0, question_id="q-0")

    assert variant is not None
    assert variant != QUESTION_TEXT


def test_the_same_seed_and_question_always_mistype_the_same_way() -> None:
    first = typo_variant(QUESTION_TEXT, seed=0, question_id="q-0")

    assert typo_variant(QUESTION_TEXT, seed=0, question_id="q-0") == first


def test_a_different_seed_mistypes_differently() -> None:
    variants = {typo_variant(QUESTION_TEXT, seed=seed, question_id="q-0") for seed in range(6)}

    assert len(variants) > 1


def test_a_question_is_mistyped_independently_of_its_neighbours() -> None:
    """The id seeds the typos, so the same question in a different subset repeats."""
    assert typo_variant(QUESTION_TEXT, seed=0, question_id="q-7") != typo_variant(
        QUESTION_TEXT, seed=0, question_id="q-0"
    )


@pytest.mark.parametrize("seed", range(12))
def test_the_number_of_slips_stays_within_the_range(seed: int) -> None:
    variant = typo_variant(QUESTION_TEXT, seed=seed, question_id="q-0")

    assert variant is not None
    # A slip changes, drops or doubles one character, so the length moves by at
    # most one per typo and the edited positions are at most MAX_TYPOS.
    assert abs(len(variant) - len(QUESTION_TEXT)) <= MAX_TYPOS
    assert _differences(QUESTION_TEXT, variant) >= 1


def test_a_question_with_too_few_letters_is_not_mistyped() -> None:
    assert typo_variant("A?", seed=0, question_id="q-0") is None


def test_every_substitution_comes_from_the_keyboard_layout() -> None:
    """A slip lands on a neighbouring key, never on an arbitrary letter."""
    text = "aaaa aaaa aaaa aaaa"

    variant = typo_variant(text, seed=3, question_id="q-0")

    assert variant is not None
    changed = {character for character in variant if character not in {"a", " "}}
    assert changed <= set(KEYBOARD_NEIGHBOURS["a"])


def _differences(left: str, right: str) -> int:
    return sum(1 for a, b in zip(left, right, strict=False) if a != b) + abs(len(left) - len(right))


# --------------------------------------------------------------------------- #
# Kinds, the filter and the record
# --------------------------------------------------------------------------- #


def test_kinds_are_drawn_round_robin() -> None:
    pairs = assign_kinds([question(index) for index in range(12)])

    assert [kind for _, kind in pairs[: len(KINDS)]] == list(KINDS)
    assert [kind for _, kind in pairs][5] == KINDS[0]


def test_a_typo_variant_keeps_the_gold_and_the_reference_answer() -> None:
    row = asyncio.run(perturb_one(StubProvider(), question(), TYPOS, model="stub", seed=0))

    assert row.kept
    assert row.question is not None
    assert row.question.id == "q-0-typos"
    assert row.question.gold == question().gold
    assert row.question.reference_answer == question().reference_answer
    assert row.question.generator is not None
    assert row.question.generator["noise"] == TYPOS
    assert row.question.generator["original_question"] == QUESTION_TEXT
    assert row.question.question != QUESTION_TEXT


@pytest.mark.parametrize("kind", [KEYWORDS, VAGUE, CHATTY])
def test_a_model_written_variant_is_checked_before_it_is_kept(kind: str) -> None:
    provider = StubProvider()

    row = asyncio.run(perturb_one(provider, question(), kind, model="stub", seed=0))

    assert row.kept
    assert row.variant == "temperature chat completion request"
    assert row.filter is not None
    # One call to write the variant, one to check it.
    assert len(provider.prompts) == 2
    assert QUESTION_TEXT in provider.prompts[1]


def test_the_filter_drops_a_variant_that_asks_something_else() -> None:
    row = asyncio.run(
        perturb_one(StubProvider(same=False), question(), KEYWORDS, model="stub", seed=0)
    )

    assert not row.kept
    assert row.question is None
    assert row.drop_reasons == ["the variant asks something else"]
    # The rejected variant and the verdict behind the drop are still recorded.
    assert row.variant == "temperature chat completion request"
    assert row.filter is not None and not row.filter.asks_the_same_thing


def test_the_filter_drops_a_variant_that_adds_a_fact() -> None:
    row = asyncio.run(
        perturb_one(StubProvider(adds_facts=True), question(), VAGUE, model="stub", seed=0)
    )

    assert not row.kept
    assert row.drop_reasons == ["the variant adds a fact the question did not carry"]


def test_a_variant_identical_to_the_question_is_dropped_without_a_check() -> None:
    provider = StubProvider(variant=QUESTION_TEXT)

    row = asyncio.run(perturb_one(provider, question(), KEYWORDS, model="stub", seed=0))

    assert not row.kept
    assert row.drop_reasons == ["the variant is the question it came from"]
    assert len(provider.prompts) == 1


def test_a_wrong_term_variant_records_the_substitution() -> None:
    row = asyncio.run(perturb_one(StubProvider(), question(), WRONG_TERM, model="stub", seed=0))

    assert row.kept
    assert row.substitution is not None
    assert (row.substitution.removed, row.substitution.inserted) == ("temperature", "top_p")
    assert row.question is not None and row.question.generator is not None
    assert row.question.generator["noise_substitution"] == {
        "removed": "temperature",
        "inserted": "top_p",
    }


def test_a_reply_that_does_not_parse_is_a_recorded_drop() -> None:
    row = asyncio.run(
        perturb_one(StubProvider(parses=False), question(), KEYWORDS, model="stub", seed=0)
    )

    assert not row.kept
    assert row.drop_reasons[0].startswith("provider_error")


def test_a_provider_failure_is_a_recorded_drop() -> None:
    row = asyncio.run(
        perturb_one(StubProvider(fails=True), question(), CHATTY, model="stub", seed=0)
    )

    assert not row.kept
    assert row.drop_reasons[0].startswith("provider_error")


def test_a_dropped_variant_never_reaches_the_dataset(tmp_path: Path) -> None:
    dataset = tmp_path / "dev.jsonl"
    dataset.write_text(
        "".join(question(index).model_dump_json() + "\n" for index in range(4)),
    )
    out = tmp_path / "noisy.jsonl"
    args = argparse.Namespace(
        dataset=str(dataset),
        out=str(out),
        name="perturb-test",
        n=4,
        provider="zai",
        model="stub",
        seed=0,
        concurrency=2,
    )

    summary = _run_offline(args, StubProvider(same=False), tmp_path)

    assert summary["written"] == 0
    assert out.read_text() == ""
    run_dir = Path(summary["run_dir"])
    rows = [json.loads(line) for line in (run_dir / "records.jsonl").read_text().splitlines()]
    assert len(rows) == 4
    assert all(not row["kept"] for row in rows)
    assert {reason for row in rows for reason in row["drop_reasons"]} == {
        "the variant asks something else"
    }


def test_the_run_writes_the_records_the_figures_and_the_readme(tmp_path: Path) -> None:
    dataset = tmp_path / "dev.jsonl"
    dataset.write_text(
        "".join(question(index).model_dump_json() + "\n" for index in range(10)),
    )
    out = tmp_path / "noisy.jsonl"
    args = argparse.Namespace(
        dataset=str(dataset),
        out=str(out),
        name="perturb-test",
        n=10,
        provider="zai",
        model="stub",
        seed=0,
        concurrency=4,
    )

    summary = _run_offline(args, StubProvider(), tmp_path)

    assert summary["written"] == 10
    run_dir = Path(summary["run_dir"])
    metrics = json.loads((run_dir / "metrics.json").read_text())
    assert metrics["kept_by_type"] == dict.fromkeys(sorted(KINDS), 2)
    assert (run_dir / "figures" / "kept-by-kind.svg").is_file()
    readme = (run_dir / "README.md").read_text()
    assert "figures/kept-by-kind.svg" in readme
    assert "wrong_term: 2 candidates, 2 kept" in readme
    # Every kept row carries the kind it was degraded with.
    kinds = [
        json.loads(line)["generator"]["noise"] for line in out.read_text().splitlines() if line
    ]
    assert sorted(set(kinds)) == sorted(KINDS)


def test_the_subset_and_its_kinds_repeat_for_the_same_seed(tmp_path: Path) -> None:
    dataset = tmp_path / "dev.jsonl"
    dataset.write_text(
        "".join(question(index).model_dump_json() + "\n" for index in range(20)),
    )

    first = _perturbed_ids(tmp_path / "a", dataset, seed=0)
    again = _perturbed_ids(tmp_path / "b", dataset, seed=0)
    other = _perturbed_ids(tmp_path / "c", dataset, seed=3)

    assert first == again
    assert first != other


def _perturbed_ids(root: Path, dataset: Path, *, seed: int) -> list[str]:
    root.mkdir()
    out = root / "noisy.jsonl"
    args = argparse.Namespace(
        dataset=str(dataset),
        out=str(out),
        name="perturb-test",
        n=10,
        provider="zai",
        model="stub",
        seed=seed,
        concurrency=4,
    )
    _run_offline(args, StubProvider(), root)
    return [json.loads(line)["id"] for line in out.read_text().splitlines() if line]


def _run_offline(args: argparse.Namespace, provider: StubProvider, root: Path) -> dict[str, Any]:
    """`run` with the provider injected and the run directory under `root`."""
    return asyncio.run(run(args, provider=provider, run_dir=root / f"run-{args.name}"))


def test_a_perturbation_run_rebuilds_its_own_report(tmp_path: Path) -> None:
    """`make eval-report` has to know this run kind, or the charts cannot be redrawn."""
    from glossator.eval.report import rebuild

    dataset = tmp_path / "dev.jsonl"
    dataset.write_text("".join(question(index).model_dump_json() + "\n" for index in range(5)))
    args = argparse.Namespace(
        dataset=str(dataset),
        out=str(tmp_path / "noisy.jsonl"),
        name="perturb-test",
        n=5,
        provider="zai",
        model="stub",
        seed=0,
        concurrency=5,
    )
    run_dir = Path(_run_offline(args, StubProvider(), tmp_path)["run_dir"])
    for figure in run_dir.glob("figures/*.svg"):
        figure.unlink()

    metrics = rebuild(run_dir)

    assert metrics["kept"] == 5
    assert (run_dir / "figures" / "kept-by-kind.svg").is_file()


def test_the_range_of_typos_is_the_documented_one() -> None:
    assert (MIN_TYPOS, MAX_TYPOS) == (2, 4)
