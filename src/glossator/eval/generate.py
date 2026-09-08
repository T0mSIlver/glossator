from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import random
import re
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, cast
from urllib.parse import urljoin, urlparse

import structlog
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, field_validator

from glossator.eval.corpus_reader import (
    CorpusPage,
    CorpusSection,
    read_corpus,
    read_manifest,
)
from glossator.eval.datasets import (
    EvalQuestion,
    GoldSource,
    QuestionSource,
    QuestionType,
    validate_against_corpus,
    write_jsonl,
)
from glossator.eval.providers import (
    Completion,
    Message,
    OpenAICompatibleProvider,
    ProviderName,
    ThinkingMode,
)
from glossator.eval.run_records import RunRecorder, create_run_directory

logger = structlog.get_logger(__name__)
PROMPT_VERSION = "s2-v3"
LINK_RE = re.compile(r"\[[^]]+\]\((?P<href>[^)#]+)(?:#[^)]+)?\)")
SINGLE_SECTION_INSTRUCTIONS = """Write one realistic question that a developer would ask and that the supplied documentation section fully answers.

The question must stand alone. It must not say "this page", "this section", "the example above", or assume that the reader sees the source. The page title alone must not answer it. Use details from the body, not merely the heading. Preserve API fields, model names, and other identifiers exactly as written. Keep the reference answer to no more than two lines."""
CROSS_PAGE_INSTRUCTIONS = """Write one developer question whose complete answer requires facts from both documentation pages below. Reject any idea that one page can answer by itself.

Choose one fact that appears only in Page A and one fact that appears only in Page B. Do not build the question around facts repeated by both pages. Before returning the candidate, verify that removing either page leaves one part unanswered.

Make the question standalone and specific. Do not mention pages, supplied text, examples above, or documentation structure. Ask for a comparison, integration, or multi-step decision that combines the two source-exclusive facts. The reference answer must have exactly two short lines. Each line must state its source-exclusive contribution. Set fully_answered to true only if both supplied pages together support the whole answer."""
UNANSWERABLE_INSTRUCTIONS = """Write one plausible developer question related to the supplied section that the documentation does not answer. Ask about a nonexistent feature, an unstated limit, or an unsupported behavior. Do not ask something that ordinary reasoning can infer from the text.

The question must stand alone and must not refer to a page, section, or example. The reference answer must state exactly what information the documentation does not provide, in no more than two lines. Set fully_answered to false."""
FILTER_INSTRUCTIONS = """Audit this generated evaluation question. Be strict.

Set standalone to false if the question refers to unseen context. Check the required gold condition. Set not_answerable_from_title_alone to false if a source title reveals the answer without reading its body. Check whether every assigned source is necessary. Reject misspelled, truncated, or invented API fields and model identifiers. List short, concrete failure reasons. Use an empty list only when every check passes."""
PAGE_ALONE_INSTRUCTIONS = """Decide whether the single supplied page can fully answer the generated question. Judge the whole question, not one clause. Set fully_answerable to true only when no fact from another source is needed. Give one concrete reason."""
PROMPT_HASHES = {
    name: hashlib.sha256(prompt.encode()).hexdigest()
    for name, prompt in {
        "single_section": SINGLE_SECTION_INSTRUCTIONS,
        "cross_page": CROSS_PAGE_INSTRUCTIONS,
        "unanswerable": UNANSWERABLE_INSTRUCTIONS,
        "filter": FILTER_INSTRUCTIONS,
        "page_alone": PAGE_ALONE_INSTRUCTIONS,
    }.items()
}


class ChatProvider(Protocol):
    async def complete(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        response_schema: type[BaseModel] | None,
        thinking: ThinkingMode | None,
    ) -> Completion: ...


class CandidateOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: str
    reference_answer: str
    fully_answered: bool

    @field_validator("reference_answer")
    @classmethod
    def answer_is_at_most_two_lines(cls, value: str) -> str:
        if len(value.splitlines()) > 2:
            raise ValueError("reference_answer must contain at most two lines")
        return value


class FilterOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    standalone: bool
    gold_condition_met: bool
    not_answerable_from_title_alone: bool
    uses_every_gold_source: bool
    reasons: list[str]

    @property
    def accepted(self) -> bool:
        return (
            self.standalone
            and self.gold_condition_met
            and self.not_answerable_from_title_alone
            and self.uses_every_gold_source
        )


class PageAloneOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    fully_answerable: bool
    reason: str


class SampledSource(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    title: str
    anchor: str | None
    heading_path: list[str]
    content: str


class GenerationAttempt(BaseModel):
    model_config = ConfigDict(frozen=True)

    generator_type: str
    seed: list[str]
    candidate: CandidateOutput
    filter: FilterOutput
    page_a_alone: PageAloneOutput | None
    page_b_alone: PageAloneOutput | None
    duplicate: bool
    kept: bool
    drop_reasons: list[str]
    sampled_sources: list[SampledSource]
    question: EvalQuestion | None


def sample_sections(
    pages: Sequence[CorpusPage],
    n: int,
    rng: random.Random,
    *,
    post_cutoff_only: bool = False,
    kinds: set[str] | None = None,
    exclude_post_cutoff: bool = False,
) -> list[CorpusSection]:
    grouped: dict[str, list[CorpusSection]] = defaultdict(list)
    for page in pages:
        path = urlparse(page.url).path
        if kinds is not None and page.kind not in kinds:
            continue
        if post_cutoff_only and not path.startswith(("/studio/search/", "/vibe/")):
            continue
        if exclude_post_cutoff and path.startswith(("/studio/search/", "/vibe/")):
            continue
        for section in page.sections:
            if section.level == 1 or section.token_estimate < 80:
                continue
            top_level = path.strip("/").split("/", maxsplit=1)[0] or "root"
            grouped[top_level].append(section)
    if not grouped:
        scope = "post-cutoff " if post_cutoff_only else ""
        raise ValueError(
            f"corpus has no eligible {scope}sections of at least 80 tokens"
        )
    groups = sorted(grouped)
    return [rng.choice(grouped[rng.choice(groups)]) for _ in range(n)]


def cross_page_pairs(
    pages: Sequence[CorpusPage],
) -> list[tuple[CorpusPage, CorpusPage]]:
    links = {page.url: _linked_urls(page) for page in pages}
    pairs: list[tuple[CorpusPage, CorpusPage]] = []
    for index, left in enumerate(pages):
        for right in pages[index + 1 :]:
            shared_parent = bool(
                left.breadcrumbs
                and right.breadcrumbs
                and left.breadcrumbs[-1] == right.breadcrumbs[-1]
            )
            linked = right.url in links[left.url] or left.url in links[right.url]
            if shared_parent or linked:
                pairs.append((left, right))
    return pairs


async def single_section(
    provider: ChatProvider,
    section: CorpusSection,
    *,
    page: CorpusPage,
    model: str,
    thinking: ThinkingMode | None = "disabled",
    variation: int = 0,
) -> CandidateOutput:
    prompt = f"""{SINGLE_SECTION_INSTRUCTIONS}

Page title: {page.title}
Heading path: {" > ".join(section.heading_path)}
Variation: {variation}

Section body:
{section.body}
"""
    return await _candidate_call(provider, prompt, model=model, thinking=thinking)


async def cross_page(
    provider: ChatProvider,
    left: CorpusPage,
    right: CorpusPage,
    *,
    model: str,
    thinking: ThinkingMode | None = "disabled",
    variation: int = 0,
) -> CandidateOutput:
    prompt = f"""{CROSS_PAGE_INSTRUCTIONS}

Start line one of the reference answer with "{left.title}:" and line two with "{right.title}:".

Variation: {variation}

Page A title: {left.title}
Page A breadcrumbs: {" > ".join(left.breadcrumbs)}
Page A content:
{left.markdown[:8000]}

Page B title: {right.title}
Page B breadcrumbs: {" > ".join(right.breadcrumbs)}
Page B content:
{right.markdown[:8000]}
"""
    return await _candidate_call(provider, prompt, model=model, thinking=thinking)


async def unanswerable(
    provider: ChatProvider,
    section: CorpusSection,
    *,
    page: CorpusPage,
    model: str,
    thinking: ThinkingMode | None = "disabled",
    variation: int = 0,
) -> CandidateOutput:
    prompt = f"""{UNANSWERABLE_INSTRUCTIONS}

Page title: {page.title}
Heading path: {" > ".join(section.heading_path)}
Variation: {variation}

Section body:
{section.body}
"""
    return await _candidate_call(provider, prompt, model=model, thinking=thinking)


async def post_cutoff(
    provider: ChatProvider,
    section: CorpusSection,
    *,
    page: CorpusPage,
    model: str,
    thinking: ThinkingMode | None = "disabled",
    variation: int = 0,
) -> CandidateOutput:
    return await single_section(
        provider,
        section,
        page=page,
        model=model,
        thinking=thinking,
        variation=variation,
    )


async def filter_candidate(
    provider: ChatProvider,
    candidate: CandidateOutput,
    *,
    sources: Sequence[tuple[str, str]],
    question_type: QuestionType,
    model: str,
    thinking: ThinkingMode | None = "disabled",
) -> FilterOutput:
    rendered_sources = "\n\n".join(
        f"SOURCE {index + 1}: {title}\n{content[:6000]}"
        for index, (title, content) in enumerate(sources)
    )
    expected = (
        "The sources must not answer the question. gold_condition_met is true only if the "
        "claimed missing information is absent."
        if question_type == QuestionType.UNANSWERABLE
        else "The sources must fully answer the question. gold_condition_met is true only if they do."
    )
    all_sources = (
        "uses_every_gold_source is true only if the answer uses one fact exclusive to Source 1 "
        "and another fact exclusive to Source 2. Set it to false when one source states both "
        "facts, even if the reference answer assigns them to separate sources."
        if question_type == QuestionType.CROSS_PAGE
        else "uses_every_gold_source is true when the assigned source is the right evidence."
    )
    prompt = f"""{FILTER_INSTRUCTIONS}

Question: {candidate.question}
Reference answer: {candidate.reference_answer}
Question type: {question_type.value}

Gold condition: {expected}
Every-source condition: {all_sources}

{rendered_sources}
"""
    completion = await provider.complete(
        [{"role": "user", "content": prompt}],
        model=model,
        temperature=0.0,
        max_tokens=500,
        response_schema=FilterOutput,
        thinking=thinking,
    )
    return cast(FilterOutput, completion.parsed)


async def check_page_alone(
    provider: ChatProvider,
    candidate: CandidateOutput,
    *,
    page: CorpusPage,
    label: str,
    model: str,
    thinking: ThinkingMode | None = "disabled",
) -> PageAloneOutput:
    prompt = f"""{PAGE_ALONE_INSTRUCTIONS}

Question: {candidate.question}
Reference answer: {candidate.reference_answer}

{label}: {page.title}
{page.markdown[:8000]}
"""
    completion = await provider.complete(
        [{"role": "user", "content": prompt}],
        model=model,
        temperature=0.0,
        max_tokens=400,
        response_schema=PageAloneOutput,
        thinking=thinking,
    )
    return cast(PageAloneOutput, completion.parsed)


async def generate_questions(
    provider: ChatProvider,
    pages: Sequence[CorpusPage],
    *,
    n: int,
    model: str,
    seed: int,
    thinking: ThinkingMode | None = "disabled",
    cross_page_review_count: int = 0,
    recorder: RunRecorder | None = None,
    run_dir: str | None = None,
) -> tuple[list[EvalQuestion], list[GenerationAttempt]]:
    if n < 6:
        raise ValueError("n must be at least 6 so every question type is represented")
    rng = random.Random(seed)
    page_by_url = {page.url: page for page in pages}
    allocations = _allocations(n)
    accepted: list[EvalQuestion] = []
    seen: set[str] = set()
    attempts: list[GenerationAttempt] = []

    ordinary = sample_sections(
        pages,
        max(allocations[QuestionType.SINGLE_PAGE] * 6, 1),
        rng,
        kinds={"doc"},
        exclude_post_cutoff=True,
    )
    await _fill_section_questions(
        provider,
        ordinary,
        page_by_url,
        accepted,
        attempts,
        seen,
        target=allocations[QuestionType.SINGLE_PAGE],
        question_type=QuestionType.SINGLE_PAGE,
        model=model,
        thinking=thinking,
        recorder=recorder,
        run_dir=run_dir,
    )

    pairs = cross_page_pairs(pages)
    if not pairs:
        raise ValueError("corpus has no pages that share a breadcrumb parent or link")
    cross_target = max(allocations[QuestionType.CROSS_PAGE], cross_page_review_count)
    cross_accepted: list[EvalQuestion] = []
    cross_attempts: list[GenerationAttempt] = []
    for variation in range(max(cross_target * 6, 1)):
        left, right = rng.choice(pairs)
        candidate = await cross_page(
            provider,
            left,
            right,
            model=model,
            thinking=thinking,
            variation=variation,
        )
        question, attempt = await _assess(
            provider,
            candidate,
            sources=[(left.title, left.markdown), (right.title, right.markdown)],
            gold=[GoldSource(url=left.url), GoldSource(url=right.url)],
            question_type=QuestionType.CROSS_PAGE,
            model=model,
            thinking=thinking,
            seen=seen,
            seed_values=[left.url, right.url],
            sampled_sources=[
                SampledSource(
                    url=left.url,
                    title=left.title,
                    anchor=None,
                    heading_path=[],
                    content=left.markdown,
                ),
                SampledSource(
                    url=right.url,
                    title=right.title,
                    anchor=None,
                    heading_path=[],
                    content=right.markdown,
                ),
            ],
            page_pair=(left, right),
            recorder=recorder,
            run_dir=run_dir,
        )
        cross_attempts.append(attempt)
        if question is not None:
            cross_accepted.append(question)
        if len(cross_accepted) >= cross_target:
            break
    attempts.extend(cross_attempts)
    accepted.extend(cross_accepted[: allocations[QuestionType.CROSS_PAGE]])
    if len(cross_accepted) < cross_target:
        raise RuntimeError(
            f"accepted {len(cross_accepted)} of {cross_target} required cross-page "
            f"candidates after {len(cross_attempts)} attempts"
        )

    api_sections = sample_sections(
        pages,
        max(allocations[QuestionType.API_REFERENCE] * 6, 1),
        rng,
        kinds={"api"},
    )
    await _fill_section_questions(
        provider,
        api_sections,
        page_by_url,
        accepted,
        attempts,
        seen,
        target=allocations[QuestionType.API_REFERENCE],
        question_type=QuestionType.API_REFERENCE,
        model=model,
        thinking=thinking,
        recorder=recorder,
        run_dir=run_dir,
    )

    capability_sections = sample_sections(
        pages,
        max(allocations[QuestionType.CAPABILITY] * 6, 1),
        rng,
        kinds={"model"},
    )
    await _fill_section_questions(
        provider,
        capability_sections,
        page_by_url,
        accepted,
        attempts,
        seen,
        target=allocations[QuestionType.CAPABILITY],
        question_type=QuestionType.CAPABILITY,
        model=model,
        thinking=thinking,
        recorder=recorder,
        run_dir=run_dir,
    )

    unanswerable_sections = sample_sections(
        pages, max(allocations[QuestionType.UNANSWERABLE] * 6, 1), rng
    )
    await _fill_section_questions(
        provider,
        unanswerable_sections,
        page_by_url,
        accepted,
        attempts,
        seen,
        target=allocations[QuestionType.UNANSWERABLE],
        question_type=QuestionType.UNANSWERABLE,
        model=model,
        thinking=thinking,
        recorder=recorder,
        run_dir=run_dir,
    )

    cutoff_sections = sample_sections(
        pages,
        max(allocations[QuestionType.POST_CUTOFF] * 6, 1),
        rng,
        post_cutoff_only=True,
    )
    await _fill_section_questions(
        provider,
        cutoff_sections,
        page_by_url,
        accepted,
        attempts,
        seen,
        target=allocations[QuestionType.POST_CUTOFF],
        question_type=QuestionType.POST_CUTOFF,
        model=model,
        thinking=thinking,
        recorder=recorder,
        run_dir=run_dir,
    )
    return accepted, attempts


async def _fill_section_questions(
    provider: ChatProvider,
    sections: Sequence[CorpusSection],
    page_by_url: dict[str, CorpusPage],
    accepted: list[EvalQuestion],
    attempts: list[GenerationAttempt],
    seen: set[str],
    *,
    target: int,
    question_type: QuestionType,
    model: str,
    thinking: ThinkingMode | None,
    recorder: RunRecorder | None,
    run_dir: str | None,
) -> None:
    start_count = sum(question.type == question_type for question in accepted)
    for variation, section in enumerate(sections):
        page = page_by_url[section.url]
        if question_type == QuestionType.UNANSWERABLE:
            candidate = await unanswerable(
                provider,
                section,
                page=page,
                model=model,
                thinking=thinking,
                variation=variation,
            )
            gold: list[GoldSource] = []
        elif question_type == QuestionType.POST_CUTOFF:
            candidate = await post_cutoff(
                provider,
                section,
                page=page,
                model=model,
                thinking=thinking,
                variation=variation,
            )
            gold = [GoldSource(url=section.url, anchor=section.anchor)]
        else:
            candidate = await single_section(
                provider,
                section,
                page=page,
                model=model,
                thinking=thinking,
                variation=variation,
            )
            gold = [GoldSource(url=section.url, anchor=section.anchor)]
        question, attempt = await _assess(
            provider,
            candidate,
            sources=[(page.title, section.body)],
            gold=gold,
            question_type=question_type,
            model=model,
            thinking=thinking,
            seen=seen,
            seed_values=[section.url, section.anchor],
            sampled_sources=[
                SampledSource(
                    url=section.url,
                    title=page.title,
                    anchor=section.anchor,
                    heading_path=section.heading_path,
                    content=section.body,
                )
            ],
            page_pair=None,
            recorder=recorder,
            run_dir=run_dir,
        )
        attempts.append(attempt)
        if question is not None:
            accepted.append(question)
        current_count = sum(question.type == question_type for question in accepted)
        if current_count - start_count >= target:
            return
    current_count = sum(question.type == question_type for question in accepted)
    raise RuntimeError(
        f"accepted {current_count - start_count} of {target} required {question_type.value} candidates"
    )


async def _assess(
    provider: ChatProvider,
    candidate: CandidateOutput,
    *,
    sources: Sequence[tuple[str, str]],
    gold: list[GoldSource],
    question_type: QuestionType,
    model: str,
    thinking: ThinkingMode | None,
    seen: set[str],
    seed_values: list[str],
    sampled_sources: list[SampledSource],
    page_pair: tuple[CorpusPage, CorpusPage] | None,
    recorder: RunRecorder | None,
    run_dir: str | None,
) -> tuple[EvalQuestion | None, GenerationAttempt]:
    page_a_alone: PageAloneOutput | None = None
    page_b_alone: PageAloneOutput | None = None
    try:
        result = await filter_candidate(
            provider,
            candidate,
            sources=sources,
            question_type=question_type,
            model=model,
            thinking=thinking,
        )
        if page_pair is not None:
            page_a_alone, page_b_alone = await asyncio.gather(
                check_page_alone(
                    provider,
                    candidate,
                    page=page_pair[0],
                    label="Page A alone",
                    model=model,
                    thinking=thinking,
                ),
                check_page_alone(
                    provider,
                    candidate,
                    page=page_pair[1],
                    label="Page B alone",
                    model=model,
                    thinking=thinking,
                ),
            )
    except Exception as error:
        if recorder is not None:
            recorder.record_candidate(
                {
                    "generator_type": question_type.value,
                    "seed": seed_values,
                    "candidate": candidate.model_dump(mode="json"),
                    "filter": None,
                    "page_a_alone": None,
                    "page_b_alone": None,
                    "duplicate": False,
                    "kept": False,
                    "drop_reasons": ["filter error"],
                    "sampled_sources": [
                        source.model_dump(mode="json") for source in sampled_sources
                    ],
                    "question": None,
                    "error": str(error),
                }
            )
        raise
    normalized = normalize_question(candidate.question)
    duplicate = normalized in seen
    expected_fully_answered = question_type != QuestionType.UNANSWERABLE
    page_a_passes = page_a_alone is None or not page_a_alone.fully_answerable
    page_b_passes = page_b_alone is None or not page_b_alone.fully_answerable
    kept = (
        result.accepted
        and not duplicate
        and candidate.fully_answered == expected_fully_answered
        and page_a_passes
        and page_b_passes
    )
    drop_reasons: list[str] = []
    if not result.standalone:
        drop_reasons.append("not standalone")
    if not result.gold_condition_met:
        drop_reasons.append("gold condition failed")
    if not result.not_answerable_from_title_alone:
        drop_reasons.append("answerable from title alone")
    if not result.uses_every_gold_source:
        drop_reasons.append("does not require every gold source")
    if duplicate:
        drop_reasons.append("duplicate question")
    if candidate.fully_answered != expected_fully_answered:
        drop_reasons.append("fully_answered conflicts with question type")
    if not page_a_passes:
        drop_reasons.append("answerable from page A alone")
    if not page_b_passes:
        drop_reasons.append("answerable from page B alone")

    question: EvalQuestion | None = None
    if kept:
        seen.add(normalized)
        metadata: dict[str, object] = {
            "model": model,
            "prompt_version": PROMPT_VERSION,
            "prompt_hashes": PROMPT_HASHES,
            "seed_section": seed_values,
            "filter": {
                "accepted": True,
                "reasons": result.reasons,
                "page_a_alone": (
                    page_a_alone.model_dump(mode="json") if page_a_alone else None
                ),
                "page_b_alone": (
                    page_b_alone.model_dump(mode="json") if page_b_alone else None
                ),
            },
        }
        if run_dir is not None:
            metadata["run_dir"] = run_dir
        question = EvalQuestion(
            id=_question_id(question_type, candidate.question, gold),
            question=candidate.question.strip(),
            type=question_type,
            gold=gold,
            reference_answer=candidate.reference_answer.strip(),
            language="en",
            source=QuestionSource.GENERATED,
            generator=metadata,
        )
    attempt = GenerationAttempt(
        generator_type=question_type.value,
        seed=seed_values,
        candidate=candidate,
        filter=result,
        page_a_alone=page_a_alone,
        page_b_alone=page_b_alone,
        duplicate=duplicate,
        kept=kept,
        drop_reasons=drop_reasons,
        sampled_sources=sampled_sources,
        question=question,
    )
    if recorder is not None:
        recorder.record_candidate(attempt)
    if not kept:
        logger.info(
            "generated_question_dropped",
            question_type=question_type.value,
            reasons=drop_reasons,
        )
        return None, attempt
    return question, attempt


async def _candidate_call(
    provider: ChatProvider,
    prompt: str,
    *,
    model: str,
    thinking: ThinkingMode | None,
) -> CandidateOutput:
    completion = await provider.complete(
        [{"role": "user", "content": prompt}],
        model=model,
        temperature=0.7,
        max_tokens=700,
        response_schema=CandidateOutput,
        thinking=thinking,
    )
    return cast(CandidateOutput, completion.parsed)


def normalize_question(question: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", question.casefold()))


def _linked_urls(page: CorpusPage) -> set[str]:
    return {
        urljoin(page.url, match.group("href"))
        for match in LINK_RE.finditer(page.markdown)
    }


def _question_id(
    question_type: QuestionType, question: str, gold: Sequence[GoldSource]
) -> str:
    material = {
        "type": question_type.value,
        "question": normalize_question(question),
        "gold": [source.model_dump() for source in gold],
    }
    digest = hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()[
        :16
    ]
    return f"gen-{digest}"


def _allocations(n: int) -> dict[QuestionType, int]:
    order = [
        QuestionType.SINGLE_PAGE,
        QuestionType.CROSS_PAGE,
        QuestionType.API_REFERENCE,
        QuestionType.CAPABILITY,
        QuestionType.UNANSWERABLE,
        QuestionType.POST_CUTOFF,
    ]
    allocations = {question_type: 1 for question_type in order}
    for index in range(n - len(order)):
        allocations[order[index % len(order)]] += 1
    return allocations


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a documentation evaluation set"
    )
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--name")
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--provider", choices=("zai", "mistral"), default="zai")
    parser.add_argument("--model", default="glm-5.3-flash")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument(
        "--thinking", choices=("enabled", "disabled"), default="disabled"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cross-page-review-count", type=int, default=0)
    return parser.parse_args()


async def _run(args: argparse.Namespace) -> None:
    pages = read_corpus(args.corpus)
    run_name = args.name or (args.out.stem if args.out else "generate")
    run_dir = create_run_directory(run_name)
    dataset_path = args.out or run_dir / "questions.jsonl"
    corpus_commits = sorted({page.source_commit for page in pages})
    corpus_commit: str | list[str] = (
        corpus_commits[0] if len(corpus_commits) == 1 else corpus_commits
    )
    config = {
        "name": run_name,
        "run_dir": str(run_dir),
        "corpus": str(args.corpus),
        "corpus_commit": corpus_commit,
        "out": str(dataset_path),
        "n": args.n,
        "provider": args.provider,
        "model": args.model,
        "thinking": args.thinking,
        "seed": args.seed,
        "concurrency": args.concurrency,
        "dry_run": args.dry_run,
        "cross_page_review_count": args.cross_page_review_count,
        "prompt_version": PROMPT_VERSION,
        "prompt_hashes": PROMPT_HASHES,
        "cache_dir": ".cache/llm",
        "minimum_section_tokens": 80,
        "generation_temperature": 0.7,
        "generation_max_tokens": 700,
        "filter_temperature": 0.0,
        "filter_max_tokens": 500,
        "page_alone_max_tokens": 400,
        "http_attempts": 3,
        "structured_output_attempts": 2,
    }
    recorder = RunRecorder(run_dir, config)
    if args.dry_run:
        try:
            rng = random.Random(args.seed)
            for section in sample_sections(pages, args.n, rng):
                print(
                    json.dumps(
                        {
                            "url": section.url,
                            "anchor": section.anchor,
                            "heading_path": section.heading_path,
                            "token_estimate": section.token_estimate,
                        }
                    )
                )
        except Exception as error:
            recorder.finalize(dataset_path=None, error=str(error))
            raise
        recorder.finalize(dataset_path=None, error=None)
        print(json.dumps({"run_dir": str(run_dir), "dry_run": True}))
        return

    provider_name = cast(ProviderName, args.provider)
    thinking = cast(ThinkingMode, args.thinking)
    try:
        async with OpenAICompatibleProvider(
            provider_name,
            asyncio.Semaphore(args.concurrency),
            caller_tag="eval.generate",
            recorder=recorder,
        ) as provider:
            questions, _ = await generate_questions(
                provider,
                pages,
                n=args.n,
                model=args.model,
                seed=args.seed,
                thinking=thinking,
                cross_page_review_count=args.cross_page_review_count,
                recorder=recorder,
                run_dir=str(run_dir),
            )
        manifest_path = args.corpus / "manifest.json"
        if manifest_path.exists():
            issues = validate_against_corpus(
                questions, read_manifest(manifest_path), pages
            )
            if issues:
                raise RuntimeError(
                    "generated questions contain invalid gold sources: "
                    + "; ".join(issue.message for issue in issues)
                )
        write_jsonl(dataset_path, questions)
    except Exception as error:
        recorder.finalize(dataset_path=None, error=str(error))
        raise
    recorder.finalize(dataset_path=dataset_path, error=None)
    counts = {question_type.value: 0 for question_type in _allocations(args.n)}
    for question in questions:
        counts[question.type.value] += 1
    print(
        json.dumps(
            {
                "written": len(questions),
                "out": str(dataset_path),
                "run_dir": str(run_dir),
                "counts": counts,
            }
        )
    )


def main() -> None:
    load_dotenv(override=True)
    asyncio.run(_run(_parse_args()))


if __name__ == "__main__":
    main()
