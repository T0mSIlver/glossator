"""Noisy rewordings of an evaluation subset, one kind of noise per question.

Every generated development question was written by a model from the section that
answers it, so it uses the documentation's own words and is well formed by
construction (D-020a). That is the distribution on which the shipped single pass
matched the search loop (D-035), and it is not the distribution a user types in.
This tool builds the other one: the same questions, the same gold sources and the
same reference answers, reworded into what a hurried, vague or mistaken user
would have asked, so the strategy decision can be re-tested out of distribution.

The rewording may not change the answer. A variant that asks something else, or
that carries a fact the original did not, is a different question with the wrong
gold attached, so every variant is checked by a second call and dropped and
recorded when it fails (D-023).

Usage:
    uv run python -m glossator.eval.perturb --dataset eval/dev.jsonl \\
        --out eval/dev-noisy.jsonl --n 120 --seed 0 --provider zai --model glm-5.3 \\
        --name dev-noisy
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

from glossator.eval.charts import bar_chart
from glossator.eval.datasets import EvalQuestion, read_jsonl, stratified_subset, write_jsonl
from glossator.eval.providers import (
    ChatProvider,
    OpenAICompatibleProvider,
    ProviderCallError,
    ProviderName,
    ThinkingMode,
    call_scope,
    candidate_scope,
)
from glossator.eval.run_records import RunRecorder, create_run_directory

PROMPT_VERSION = "perturb-v1"

TYPOS = "typos"
KEYWORDS = "keywords"
VAGUE = "vague"
WRONG_TERM = "wrong_term"
CHATTY = "chatty"

KINDS: tuple[str, ...] = (TYPOS, KEYWORDS, VAGUE, WRONG_TERM, CHATTY)
"""Drawn round-robin over the subset, so every kind covers the same spread of
question types and no kind lands on the easy half of the dataset."""

MODEL_KINDS = frozenset(KINDS) - {TYPOS}
"""Typos are generated in code. A model asked for a typo writes a plausible
misspelling, which is a different failure from a finger on the wrong key, and it
writes a different one every time the run is repeated."""

SYSTEM = (
    "You degrade the wording of questions about Mistral AI's platform documentation, to "
    "test a documentation search system on badly worded input. You never change what is "
    "being asked and you never add information. The degraded question must have exactly "
    "the same correct answer as the original: same feature, same parameter, same model, "
    "same scope. Do not answer the question. Do not explain yourself. Return JSON only."
)

KIND_INSTRUCTIONS: dict[str, str] = {
    KEYWORDS: (
        "Reduce the question to three to six search keywords, the way someone types into a "
        "search box. Keep the words that carry the subject, including identifiers and model "
        "names. Drop question words, articles and grammar. Add no word the question does not "
        "imply."
    ),
    VAGUE: (
        "Rewrite the question as a user who does not know the product's vocabulary would ask "
        "it. Replace the documentation's terms with everyday descriptions of the same thing, "
        "in one sentence. Keep numbers and quoted values. Do not name the feature, the "
        "parameter or the endpoint the original names, and do not describe a different one."
    ),
    WRONG_TERM: (
        "Replace exactly one product term in the question with a plausible wrong one, the way "
        "a user who half-remembers the documentation would: `temperature` for `top_p`, agent "
        "for workflow, embeddings for tokenization. Change nothing else: the rest of the "
        "question must stay word for word, and what is being asked about must still be "
        "recognizable from the rest. Report the term you removed and the one you put in its "
        "place."
    ),
    CHATTY: (
        "Bury the question in two sentences of context about what the user is building, in "
        "the first person. The request must still be there and must still be the only thing "
        "asked. Invent nothing about the product: the context is about the user's own project "
        "and may not state or assume any fact about Mistral's platform."
    ),
}

FILTER_INSTRUCTIONS = (
    "Two versions of a question about Mistral AI's platform documentation are below: the "
    "original, and a deliberately degraded rewording of it. Decide whether the degraded "
    "version still asks for the same thing, so that a correct answer to the original is a "
    "correct answer to it.\n\n"
    "Judge intent, not quality. Bad grammar, misspellings, missing question words, bare "
    "keywords, vagueness, a wrong product term and irrelevant surrounding chatter are all "
    "expected here and none of them is a reason to fail it. Set asks_the_same_thing to "
    "false only when the degraded version asks about a different feature, parameter, model "
    "or scope, when it has become so unspecific that several different documentation "
    "sections would answer it equally well, or when the request has disappeared. Set "
    "adds_facts to true if the degraded version states or assumes anything about Mistral's "
    "platform that the original did not. Give one concrete reason."
)

GENERATION_TEMPERATURE = 0.7
GENERATION_MAX_TOKENS = 400
CHECK_TEMPERATURE = 0.0
CHECK_MAX_TOKENS = 300

MIN_TYPOS = 2
MAX_TYPOS = 4

# Physically adjacent keys on a QWERTY keyboard. A typo is a finger landing next
# door, so the substitutions come from the layout rather than from a letter
# confusion table, which is a different kind of mistake.
KEYBOARD_NEIGHBOURS: dict[str, str] = {
    "a": "qwsz",
    "b": "vghn",
    "c": "xdfv",
    "d": "serfcx",
    "e": "wsdr",
    "f": "drtgvc",
    "g": "ftyhbv",
    "h": "gyujnb",
    "i": "ujko",
    "j": "huikmn",
    "k": "jiolm",
    "l": "kop",
    "m": "njk",
    "n": "bhjm",
    "o": "iklp",
    "p": "ol",
    "q": "wa",
    "r": "edft",
    "s": "awedxz",
    "t": "rfgy",
    "u": "yhji",
    "v": "cfgb",
    "w": "qase",
    "x": "zsdc",
    "y": "tghu",
    "z": "asx",
}

TYPO_OPERATIONS = ("substitute", "transpose", "drop", "double")

DROP_PROVIDER_ERROR = "provider_error"
DROP_UNPARSED = "the model's reply did not parse"
DROP_EMPTY = "the variant came back empty"
DROP_UNCHANGED = "the variant is the question it came from"
DROP_TOO_SHORT = "the question has too few letters to mistype"
DROP_DIFFERENT_QUESTION = "the variant asks something else"
DROP_ADDS_FACTS = "the variant adds a fact the question did not carry"
DROP_NO_SUBSTITUTION = "no term substitution was reported"

FIGURES = ("kept-by-kind.svg", "drop-reasons.svg")


class NoisyQuestion(BaseModel):
    model_config = ConfigDict(frozen=True)

    noisy_question: str


class WrongTermQuestion(NoisyQuestion):
    original_term: str
    replacement_term: str


class SameQuestion(BaseModel):
    model_config = ConfigDict(frozen=True)

    asks_the_same_thing: bool
    adds_facts: bool
    reason: str


class Substitution(BaseModel):
    """The term a `wrong_term` variant removed, and what took its place."""

    model_config = ConfigDict(frozen=True)

    removed: str
    inserted: str


class PerturbationRow(BaseModel):
    """One row of ``records.jsonl``: every variant, kept or not."""

    model_config = ConfigDict(frozen=True)

    candidate_id: str
    source_id: str
    noise: str
    generator_type: str
    """The noise kind again, under the name the shared summarizer groups rows by,
    so ``metrics.json`` counts kept and dropped per kind without a second pass."""

    original_question: str
    variant: str | None = None
    substitution: Substitution | None = None
    filter: SameQuestion | None = None
    kept: bool
    drop_reasons: list[str]
    question: EvalQuestion | None = None


def assign_kinds(subset: Sequence[EvalQuestion]) -> list[tuple[EvalQuestion, str]]:
    """One noise kind per question, round-robin in subset order."""
    return [(question, KINDS[index % len(KINDS)]) for index, question in enumerate(subset)]


def typo_variant(question: str, *, seed: int, question_id: str) -> str | None:
    """The question with two to four keyboard slips in it, or None if it is too short.

    Seeded by the run's seed and the question's id rather than by position, so the
    same question mistyped in two runs of the same seed comes out the same however
    the subset around it changed.
    """
    rng = random.Random(f"{seed}:{question_id}")
    positions = [
        index
        for index, character in enumerate(question)
        # The first letter of the question is left alone: a typo there reads as a
        # different word rather than as a slip, and search treats it as one.
        if index > 0 and character.lower() in KEYBOARD_NEIGHBOURS
    ]
    if len(positions) < MIN_TYPOS * 2:
        return None

    wanted = rng.randint(MIN_TYPOS, MAX_TYPOS)
    chosen: list[int] = []
    for index in rng.sample(positions, k=len(positions)):
        # Two slips in the same short word leave a token nothing can match, which
        # is a harder question than "the user mistyped"; spread them out.
        if all(abs(index - taken) > 2 for taken in chosen):
            chosen.append(index)
        if len(chosen) == wanted:
            break

    characters = list(question)
    for index in sorted(chosen, reverse=True):
        _apply_typo(characters, index, rng)
    variant = "".join(characters)
    return variant if variant != question else None


def _apply_typo(characters: list[str], index: int, rng: random.Random) -> None:
    character = characters[index]
    operation = rng.choice(TYPO_OPERATIONS)
    if operation == "transpose" and index + 1 < len(characters):
        characters[index], characters[index + 1] = characters[index + 1], character
        return
    if operation == "drop":
        del characters[index]
        return
    if operation == "double":
        characters.insert(index, character)
        return
    neighbours = KEYBOARD_NEIGHBOURS[character.lower()]
    replacement = rng.choice(neighbours)
    characters[index] = replacement.upper() if character.isupper() else replacement


async def noisy_variant(
    provider: ChatProvider,
    question: EvalQuestion,
    kind: str,
    *,
    model: str,
    thinking: ThinkingMode | None = None,
) -> NoisyQuestion:
    """One model-written variant of ``kind``."""
    schema: type[NoisyQuestion] = WrongTermQuestion if kind == WRONG_TERM else NoisyQuestion
    user = (
        f"{KIND_INSTRUCTIONS[kind]}\n\n"
        f"Question: {question.question}\n"
        f"Return JSON with noisy_question"
        + (" , original_term and replacement_term.\n" if kind == WRONG_TERM else ".\n")
    )
    with candidate_scope(question.id), call_scope(f"perturb:{kind}"):
        completion = await provider.complete(
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
            model=model,
            temperature=GENERATION_TEMPERATURE,
            max_tokens=GENERATION_MAX_TOKENS,
            response_schema=schema,
            thinking=thinking,
            cache_nonce=None,
        )
    parsed = completion.parsed
    if not isinstance(parsed, NoisyQuestion):
        raise ValueError(DROP_UNPARSED)
    return parsed


async def check_variant(
    provider: ChatProvider,
    question: EvalQuestion,
    kind: str,
    variant: str,
    *,
    model: str,
    thinking: ThinkingMode | None = None,
) -> SameQuestion:
    """Whether the variant still asks what the question asked."""
    user = (
        f"{FILTER_INSTRUCTIONS}\n\n"
        f"Degradation applied: {kind}\n"
        f"Original: {question.question}\n"
        f"Degraded: {variant}\n"
    )
    with candidate_scope(question.id), call_scope("filter"):
        completion = await provider.complete(
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
            model=model,
            temperature=CHECK_TEMPERATURE,
            max_tokens=CHECK_MAX_TOKENS,
            response_schema=SameQuestion,
            thinking=thinking,
            cache_nonce=None,
        )
    parsed = completion.parsed
    if not isinstance(parsed, SameQuestion):
        raise ValueError(DROP_UNPARSED)
    return parsed


async def perturb_one(
    provider: ChatProvider,
    question: EvalQuestion,
    kind: str,
    *,
    model: str,
    seed: int,
    thinking: ThinkingMode | None = None,
) -> PerturbationRow:
    """One question, one kind of noise, checked. Never raises: a failure is a row."""
    row = PerturbationRow(
        candidate_id=f"{question.id}-{kind}",
        source_id=question.id,
        noise=kind,
        generator_type=kind,
        original_question=question.question,
        kept=False,
        drop_reasons=[],
    )
    substitution: Substitution | None = None
    try:
        if kind == TYPOS:
            variant = typo_variant(question.question, seed=seed, question_id=question.id)
            if variant is None:
                return row.model_copy(update={"drop_reasons": [DROP_TOO_SHORT]})
        else:
            generated = await noisy_variant(
                provider, question, kind, model=model, thinking=thinking
            )
            variant = generated.noisy_question.strip()
            if isinstance(generated, WrongTermQuestion):
                substitution = Substitution(
                    removed=generated.original_term.strip(),
                    inserted=generated.replacement_term.strip(),
                )
    except (ProviderCallError, ValueError) as error:
        return row.model_copy(
            update={"drop_reasons": [f"{DROP_PROVIDER_ERROR}: {type(error).__name__}: {error}"]}
        )

    row = row.model_copy(update={"variant": variant, "substitution": substitution})
    reasons = _mechanical_reasons(question, kind, variant, substitution)
    if reasons:
        return row.model_copy(update={"drop_reasons": reasons})

    try:
        verdict = await check_variant(
            provider, question, kind, variant, model=model, thinking=thinking
        )
    except (ProviderCallError, ValueError) as error:
        return row.model_copy(
            update={"drop_reasons": [f"{DROP_PROVIDER_ERROR}: {type(error).__name__}: {error}"]}
        )

    row = row.model_copy(update={"filter": verdict})
    if not verdict.asks_the_same_thing:
        return row.model_copy(update={"drop_reasons": [DROP_DIFFERENT_QUESTION]})
    if verdict.adds_facts:
        return row.model_copy(update={"drop_reasons": [DROP_ADDS_FACTS]})
    return row.model_copy(
        update={"kept": True, "question": noisy_question(question, kind, variant, substitution)}
    )


def _mechanical_reasons(
    question: EvalQuestion, kind: str, variant: str, substitution: Substitution | None
) -> list[str]:
    """What can be decided about a variant without asking a model."""
    reasons: list[str] = []
    if not variant:
        reasons.append(DROP_EMPTY)
    elif variant == question.question:
        reasons.append(DROP_UNCHANGED)
    if kind == WRONG_TERM and (
        substitution is None
        or not substitution.removed
        or not substitution.inserted
        or substitution.removed == substitution.inserted
    ):
        reasons.append(DROP_NO_SUBSTITUTION)
    return reasons


def noisy_question(
    question: EvalQuestion, kind: str, variant: str, substitution: Substitution | None
) -> EvalQuestion:
    """The dataset row: the noisy wording, the original gold and reference answer."""
    generator = dict(question.generator or {})
    generator.update(
        {
            "noise": kind,
            "perturbed_from": question.id,
            "perturbation_prompt": PROMPT_VERSION,
            "original_question": question.question,
        }
    )
    if substitution is not None:
        generator["noise_substitution"] = substitution.model_dump(mode="json")
    return question.model_copy(
        update={"id": f"{question.id}-{kind}", "question": variant, "generator": generator}
    )


def render_figures(metrics: dict[str, Any], figures_dir: Path) -> None:
    """The two charts the README names, from the run's own metrics."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    candidates = metrics["candidates_by_type"]
    kept = metrics["kept_by_type"]
    (figures_dir / "kept-by-kind.svg").write_text(
        bar_chart(
            "Variants kept and dropped, per noise kind",
            [
                (kind, [float(kept.get(kind, 0)), float(count - kept.get(kind, 0))])
                for kind, count in sorted(candidates.items())
            ],
            ["kept", "dropped"],
        )
    )
    (figures_dir / "drop-reasons.svg").write_text(
        bar_chart(
            "Why variants were dropped",
            [
                (reason[:60], [float(count)])
                for reason, count in sorted(metrics["dropped_by_reason"].items())
            ],
            ["variants"],
        )
    )


async def perturb_all(
    provider: ChatProvider,
    pairs: Sequence[tuple[EvalQuestion, str]],
    *,
    recorder: RunRecorder,
    model: str,
    seed: int,
    thinking: ThinkingMode | None,
    concurrency: int,
) -> list[EvalQuestion]:
    """Every pair, in batches, recorded as each batch lands."""
    kept: list[EvalQuestion] = []
    for start in range(0, len(pairs), concurrency):
        batch = pairs[start : start + concurrency]
        rows = await asyncio.gather(
            *(
                perturb_one(provider, question, kind, model=model, seed=seed, thinking=thinking)
                for question, kind in batch
            )
        )
        # Recorded in subset order rather than completion order, so the same seed
        # writes the same file whatever the network did.
        for row in rows:
            recorder.record_candidate(row)
            if row.question is not None:
                kept.append(row.question)
    return kept


async def run(
    args: argparse.Namespace,
    *,
    provider: ChatProvider | None = None,
    run_dir: Path | None = None,
) -> dict[str, Any]:
    """The whole run. ``provider`` and ``run_dir`` are injectable so a test can
    exercise the batching, the records and the README without a network."""
    questions = read_jsonl(Path(args.dataset))
    subset = stratified_subset(questions, args.n, args.seed)
    pairs = assign_kinds(subset)
    run_dir = run_dir or create_run_directory(args.name)
    config = {
        "kind": "perturb",
        "dataset": args.dataset,
        "n": args.n,
        "seed": args.seed,
        "provider": args.provider,
        "model": args.model,
        "prompt_version": PROMPT_VERSION,
        "noise_kinds": list(KINDS),
        "source_questions": [question.id for question in subset],
        "figures": list(FIGURES),
    }
    provider_name: ProviderName = args.provider
    # Reasoning has to be set and checked per call on z.ai, and recorded (D-020).
    thinking: ThinkingMode | None = "disabled" if provider_name == "zai" else None
    config["thinking"] = thinking
    recorder = RunRecorder.start(run_dir, config)

    async def perturb_with(client: ChatProvider) -> list[EvalQuestion]:
        return await perturb_all(
            client,
            pairs,
            recorder=recorder,
            model=args.model,
            seed=args.seed,
            thinking=thinking,
            concurrency=args.concurrency,
        )

    if provider is not None:
        kept = await perturb_with(provider)
    else:
        async with OpenAICompatibleProvider(
            provider_name,
            asyncio.Semaphore(args.concurrency),
            caller_tag="eval.perturb",
            recorder=recorder,
            seed=args.seed,
        ) as client:
            kept = await perturb_with(client)

    out = Path(args.out)
    write_jsonl(out, kept)
    recorder.finalize(dataset_path=out, error=None)
    render_figures(
        cast(dict[str, Any], json.loads(recorder.metrics_path.read_text())), run_dir / "figures"
    )
    return {
        "written": len(kept),
        "dropped": len(pairs) - len(kept),
        "out": str(out),
        "run_dir": str(run_dir),
        **recorder.usage_line(),
    }


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Rewrite an evaluation subset into badly worded variants"
    )
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--n", type=int, default=120)
    parser.add_argument("--provider", choices=["zai", "mistral"], default="zai")
    parser.add_argument("--model", default="glm-5.3")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=4)
    print(json.dumps(asyncio.run(run(parser.parse_args())), ensure_ascii=False))


if __name__ == "__main__":
    main()


__all__ = [
    "KINDS",
    "KIND_INSTRUCTIONS",
    "MODEL_KINDS",
    "PROMPT_VERSION",
    "NoisyQuestion",
    "PerturbationRow",
    "SameQuestion",
    "Substitution",
    "WrongTermQuestion",
    "assign_kinds",
    "perturb_all",
    "check_variant",
    "noisy_question",
    "noisy_variant",
    "perturb_one",
    "render_figures",
    "run",
    "typo_variant",
]
