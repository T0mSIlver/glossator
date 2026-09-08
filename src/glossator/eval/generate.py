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

logger = structlog.get_logger(__name__)
PROMPT_VERSION = "s2-v2"
LINK_RE = re.compile(r"\[[^]]+\]\((?P<href>[^)#]+)(?:#[^)]+)?\)")


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


class GenerationAttempt(BaseModel):
    model_config = ConfigDict(frozen=True)

    generator_type: str
    seed: list[str]
    candidate: CandidateOutput
    filter: FilterOutput
    duplicate: bool


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
    prompt = f"""Write one realistic question that a developer would ask and that the supplied documentation section fully answers.

The question must stand alone. It must not say "this page", "this section", "the example above", or assume that the reader sees the source. The page title alone must not answer it. Use details from the body, not merely the heading. Preserve API fields, model names, and other identifiers exactly as written. Keep the reference answer to no more than two lines.

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
    prompt = f"""Write one developer question whose complete answer requires facts from both documentation pages below. Reject any idea that one page can answer by itself.

Choose one fact that appears only in Page A and one fact that appears only in Page B. Do not build the question around facts repeated by both pages. Before returning the candidate, verify that removing either page leaves one part unanswered.

Make the question standalone and specific. Do not mention pages, supplied text, examples above, or documentation structure. Ask for a comparison, integration, or multi-step decision that combines the two source-exclusive facts. The reference answer must have exactly two short lines. Start line one with "{left.title}:" and line two with "{right.title}:". Each line must state its source-exclusive contribution. Set fully_answered to true only if both supplied pages together support the whole answer.

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
    prompt = f"""Write one plausible developer question related to the supplied section that the documentation does not answer. Ask about a nonexistent feature, an unstated limit, or an unsupported behavior. Do not ask something that ordinary reasoning can infer from the text.

The question must stand alone and must not refer to a page, section, or example. The reference answer must state exactly what information the documentation does not provide, in no more than two lines. Set fully_answered to false.

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
    prompt = f"""Audit this generated evaluation question. Be strict.

Question: {candidate.question}
Reference answer: {candidate.reference_answer}
Question type: {question_type.value}

Set standalone to false if the question refers to unseen context. {expected}
Set not_answerable_from_title_alone to false if a source title reveals the answer without reading its body. {all_sources}
Reject misspelled, truncated, or invented API fields and model identifiers.
List short, concrete failure reasons. Use an empty list only when every check passes.

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


async def generate_questions(
    provider: ChatProvider,
    pages: Sequence[CorpusPage],
    *,
    n: int,
    model: str,
    seed: int,
    thinking: ThinkingMode | None = "disabled",
    cross_page_review_count: int = 0,
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
            f"accepted {len(cross_accepted)} of {cross_target} required cross-page candidates"
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
) -> tuple[EvalQuestion | None, GenerationAttempt]:
    result = await filter_candidate(
        provider,
        candidate,
        sources=sources,
        question_type=question_type,
        model=model,
        thinking=thinking,
    )
    normalized = normalize_question(candidate.question)
    duplicate = normalized in seen
    expected_fully_answered = question_type != QuestionType.UNANSWERABLE
    accepted = (
        result.accepted
        and not duplicate
        and candidate.fully_answered == expected_fully_answered
    )
    reasons = list(result.reasons)
    if duplicate:
        reasons.append("duplicates an earlier normalized question")
    if candidate.fully_answered != expected_fully_answered:
        reasons.append("fully_answered conflicts with the question type")
    final_filter = result.model_copy(update={"reasons": reasons})
    attempt = GenerationAttempt(
        generator_type=question_type.value,
        seed=seed_values,
        candidate=candidate,
        filter=final_filter,
        duplicate=duplicate,
    )
    if not accepted:
        logger.info(
            "generated_question_dropped",
            question_type=question_type.value,
            reasons=reasons,
        )
        return None, attempt
    seen.add(normalized)
    metadata: dict[str, object] = {
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "seed_section": seed_values,
        "filter": {"accepted": True, "reasons": reasons},
    }
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
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--provider", choices=("zai", "mistral"), default="zai")
    parser.add_argument("--model", default="glm-5.3-flash")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cross-page-review-out", type=Path)
    return parser.parse_args()


async def _run(args: argparse.Namespace) -> None:
    pages = read_corpus(args.corpus)
    if args.dry_run:
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
        return

    review_count = 10 if args.cross_page_review_out else 0
    provider_name = cast(ProviderName, args.provider)
    async with OpenAICompatibleProvider(
        provider_name,
        asyncio.Semaphore(args.concurrency),
        caller_tag="eval.generate",
    ) as provider:
        questions, attempts = await generate_questions(
            provider,
            pages,
            n=args.n,
            model=args.model,
            seed=args.seed,
            cross_page_review_count=review_count,
        )
    manifest_path = args.corpus / "manifest.json"
    if manifest_path.exists():
        issues = validate_against_corpus(questions, read_manifest(manifest_path), pages)
        if issues:
            raise RuntimeError(
                "generated questions contain invalid gold sources: "
                + "; ".join(issue.message for issue in issues)
            )
    write_jsonl(args.out, questions)
    if args.cross_page_review_out:
        cross_attempts = [
            attempt
            for attempt in attempts
            if attempt.generator_type == QuestionType.CROSS_PAGE.value
        ]
        args.cross_page_review_out.parent.mkdir(parents=True, exist_ok=True)
        args.cross_page_review_out.write_text(
            "".join(attempt.model_dump_json() + "\n" for attempt in cross_attempts)
        )
    counts = {question_type.value: 0 for question_type in _allocations(args.n)}
    for question in questions:
        counts[question.type.value] += 1
    print(
        json.dumps({"written": len(questions), "out": str(args.out), "counts": counts})
    )


def main() -> None:
    load_dotenv(override=True)
    asyncio.run(_run(_parse_args()))


if __name__ == "__main__":
    main()
