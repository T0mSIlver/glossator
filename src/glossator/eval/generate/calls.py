"""The model calls behind one candidate: generation, the filter, and the answerability checks."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import cast

from pydantic import BaseModel

from glossator.eval.corpus import CorpusDocument
from glossator.eval.datasets import GoldSource, QuestionType
from glossator.eval.generate.models import (
    CHECK_MAX_TOKENS,
    CHECK_TEMPERATURE,
    GENERATION_MAX_TOKENS,
    GENERATION_TEMPERATURE,
    MAX_SOURCE_CHARS,
    PROBE_MAX_TOKENS,
    UNANSWERABLE_CHECK_TOP_K,
    AttemptPlan,
    CandidateOutput,
    CapabilityOutput,
    CorpusCheckOutput,
    CrossPageOutput,
    FilterOutput,
    GenerationContext,
    PageAloneOutput,
    PageAloneVerdict,
    SampledSource,
)
from glossator.eval.generate.prompts import (
    API_REFERENCE_INSTRUCTIONS,
    CAPABILITY_INSTRUCTIONS,
    CLOSED_BOOK_INSTRUCTIONS,
    CORPUS_CHECK_INSTRUCTIONS,
    CROSS_PAGE_INSTRUCTIONS,
    FILTER_INSTRUCTIONS,
    PAGE_ALONE_INSTRUCTIONS,
    POST_CUTOFF_INSTRUCTIONS,
    SINGLE_SECTION_INSTRUCTIONS,
    UNANSWERABLE_INSTRUCTIONS,
)
from glossator.eval.providers import Completion, call_scope

# A generated question naming one of these is about somebody else's product; the
# filter model has been observed to pass such a question (review finding H5), so
# the check is deterministic rather than asked.
FOREIGN_VENDORS = (
    "OpenAI",
    "GPT",
    "Gemini",
    "Anthropic",
    "Claude",
    "Cohere",
    "Llama",
    "Bedrock",
    "Vertex",
    "Azure OpenAI",
)
_FOREIGN_VENDOR_RE = re.compile(
    r"\b(" + "|".join(re.escape(name) for name in FOREIGN_VENDORS) + r")\b",
    re.IGNORECASE,
)


def _render_source(source: SampledSource, label: str) -> str:
    return (
        f"{label}: {source.title}\n"
        f"Heading path: {' > '.join(source.heading_path)}\n"
        f"{source.content}"
    )


async def _ask(
    context: GenerationContext,
    prompt: str,
    *,
    kind: str,
    schema: type[BaseModel] | None,
    temperature: float,
    max_tokens: int,
    cache_nonce: str | None = None,
) -> Completion:
    with call_scope(kind):
        return await context.provider.complete(
            [{"role": "user", "content": prompt}],
            model=context.model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_schema=schema,
            thinking=context.thinking,
            cache_nonce=cache_nonce,
        )


async def generate_candidate(context: GenerationContext, plan: AttemptPlan) -> CandidateOutput:
    """The candidate question for one plan, from the generator its type names."""
    question_type = plan.question_type
    if question_type == QuestionType.CROSS_PAGE:
        prompt = (
            f"{CROSS_PAGE_INSTRUCTIONS}\n\n"
            f"{_render_source(plan.sources[0], 'Page A')}\n\n"
            f"{_render_source(plan.sources[1], 'Page B')}\n"
        )
        schema: type[CandidateOutput] = CrossPageOutput
    elif question_type == QuestionType.CAPABILITY:
        rendered = "\n\n".join(
            _render_source(source, f"Source {index + 1}")
            for index, source in enumerate(plan.sources)
        )
        prompt = f"{CAPABILITY_INSTRUCTIONS}\n\n{rendered}\n"
        schema = CapabilityOutput
    else:
        instructions = {
            QuestionType.SINGLE_PAGE: SINGLE_SECTION_INSTRUCTIONS,
            QuestionType.API_REFERENCE: API_REFERENCE_INSTRUCTIONS,
            QuestionType.POST_CUTOFF: POST_CUTOFF_INSTRUCTIONS,
            QuestionType.UNANSWERABLE: UNANSWERABLE_INSTRUCTIONS,
        }[question_type]
        prompt = f"{instructions}\n\n{_render_source(plan.sources[0], 'Source')}\n"
        schema = CandidateOutput
    completion = await _ask(
        context,
        prompt,
        kind="generation",
        schema=schema,
        temperature=GENERATION_TEMPERATURE,
        max_tokens=GENERATION_MAX_TOKENS,
        cache_nonce=plan.candidate_id,
    )
    return cast(CandidateOutput, completion.parsed)


def gold_sources(plan: AttemptPlan, gold: Sequence[GoldSource]) -> list[SampledSource]:
    """The sampled text behind each gold source, in gold order.

    The filter must judge what the dataset row claims as evidence. A generator
    may show the model more than it makes gold -- a capability question sees a
    model card it need not cite -- and asking whether every *shown* source was
    necessary drops good questions for using their context.
    """
    by_url = {source.url: source for source in plan.sources}
    return [by_url[item.url] for item in gold if item.url in by_url]


async def filter_candidate(
    context: GenerationContext,
    plan: AttemptPlan,
    candidate: CandidateOutput,
    gold: Sequence[GoldSource],
) -> FilterOutput:
    expected = (
        "The sources must not answer the question. gold_condition_met is true only if the "
        "claimed missing information is absent."
        if plan.question_type == QuestionType.UNANSWERABLE
        else "The sources must fully answer the question. gold_condition_met is true only if "
        "they do."
    )
    every_source = (
        "uses_every_gold_source is true only if the answer uses one fact exclusive to Source 1 "
        "and another fact exclusive to Source 2. Set it to false when one source states both "
        "facts, even if the two facts are described separately."
        if plan.question_type == QuestionType.CROSS_PAGE
        else "uses_every_gold_source is true when every assigned source is evidence for part "
        "of the answer."
    )
    sources = gold_sources(plan, gold) or list(plan.sources)
    rendered = "\n\n".join(
        _render_source(source, f"SOURCE {index + 1}") for index, source in enumerate(sources)
    )
    prompt = (
        f"{FILTER_INSTRUCTIONS}\n\n"
        f"Question: {candidate.question}\n"
        f"Reference answer: {candidate.reference_answer}\n"
        f"Question type: {plan.question_type.value}\n\n"
        f"Gold condition: {expected}\n"
        f"Every-source condition: {every_source}\n\n"
        f"{rendered}\n"
    )
    completion = await _ask(
        context,
        prompt,
        kind="filter",
        schema=FilterOutput,
        temperature=CHECK_TEMPERATURE,
        max_tokens=CHECK_MAX_TOKENS,
    )
    return cast(FilterOutput, completion.parsed)


async def check_page_alone(
    context: GenerationContext,
    candidate: CandidateOutput,
    document: CorpusDocument,
    label: str,
) -> PageAloneVerdict:
    prompt = (
        f"{PAGE_ALONE_INSTRUCTIONS}\n\n"
        f"Question: {candidate.question}\n"
        f"Reference answer: {candidate.reference_answer}\n\n"
        f"{label}: {document.title}\n"
        f"{document.page.body[:MAX_SOURCE_CHARS]}\n"
    )
    completion = await _ask(
        context,
        prompt,
        kind="page_alone",
        schema=PageAloneOutput,
        temperature=CHECK_TEMPERATURE,
        max_tokens=CHECK_MAX_TOKENS,
    )
    verdict = cast(PageAloneOutput, completion.parsed)
    return PageAloneVerdict(
        url=document.url,
        title=document.title,
        fully_answerable=verdict.fully_answerable,
        reason=verdict.reason,
    )


async def check_corpus_answers(
    context: GenerationContext, candidate: CandidateOutput
) -> tuple[CorpusCheckOutput, list[str]]:
    """Whether anything in the corpus answers a supposedly unanswerable question.

    One section cannot establish that the documentation is silent (review M1), so
    the top lexical hits over every section are shown to the model. The sections
    consulted are returned for the record.
    """
    hits = context.index.search(candidate.question, top_k=UNANSWERABLE_CHECK_TOP_K)
    consulted = [hit.label for hit in hits]
    if not hits:
        return CorpusCheckOutput(
            answered_by_corpus=False,
            reason="No section of the documentation shares a term with the question.",
        ), consulted
    rendered = "\n\n".join(
        f"SECTION {index + 1}: {hit.label}\n{hit.section.body[:MAX_SOURCE_CHARS]}"
        for index, hit in enumerate(hits)
    )
    prompt = (
        f"{CORPUS_CHECK_INSTRUCTIONS}\n\n"
        f"Question: {candidate.question}\n"
        f"Claimed gap: {candidate.reference_answer}\n\n"
        f"{rendered}\n"
    )
    completion = await _ask(
        context,
        prompt,
        kind="corpus_check",
        schema=CorpusCheckOutput,
        temperature=CHECK_TEMPERATURE,
        max_tokens=CHECK_MAX_TOKENS,
    )
    return cast(CorpusCheckOutput, completion.parsed), consulted


async def closed_book_probe(context: GenerationContext, candidate: CandidateOutput) -> str:
    """What the model answers with no documentation in front of it.

    Recorded on post-cutoff records, not used to filter: it becomes the signal
    that separates a question the model already knew from one it could not.
    """
    completion = await _ask(
        context,
        f"{CLOSED_BOOK_INSTRUCTIONS}\n\nQuestion: {candidate.question}\n",
        kind="closed_book",
        schema=None,
        temperature=CHECK_TEMPERATURE,
        max_tokens=PROBE_MAX_TOKENS,
    )
    return completion.text.strip()


def foreign_vendors_named(question: str) -> list[str]:
    """Competitor product names the question mentions, in the order they appear."""
    found: list[str] = []
    for match in _FOREIGN_VENDOR_RE.finditer(question):
        name = match.group(1)
        if name not in found:
            found.append(name)
    return found
