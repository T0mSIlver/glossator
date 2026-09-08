"""Question generators for the development set.

Six kinds of question, one generator each, all drawing on the vendored corpus and
all recorded: every candidate the model produced, why it was kept or dropped, and
every call behind it (D-023). A generator is only allowed to be wrong loudly --
a candidate that cannot be checked is dropped and recorded, never silently
turned into a dataset row.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import random
import re
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol, TypeVar, cast

import structlog
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, field_validator

from glossator.eval.corpus import (
    CorpusDocument,
    block_text,
    estimate_tokens,
    load_documents,
)
from glossator.eval.datasets import (
    EvalQuestion,
    GoldSource,
    QuestionSource,
    QuestionType,
    validate_against_corpus,
    write_jsonl,
)
from glossator.eval.lexical import LexicalIndex
from glossator.eval.prompts import (
    API_REFERENCE_INSTRUCTIONS,
    CAPABILITY_INSTRUCTIONS,
    CLOSED_BOOK_INSTRUCTIONS,
    CORPUS_CHECK_INSTRUCTIONS,
    CROSS_PAGE_INSTRUCTIONS,
    FILTER_INSTRUCTIONS,
    PAGE_ALONE_INSTRUCTIONS,
    POST_CUTOFF_INSTRUCTIONS,
    PROMPT_HASHES,
    PROMPT_VERSION,
    SINGLE_SECTION_INSTRUCTIONS,
    UNANSWERABLE_INSTRUCTIONS,
)
from glossator.eval.providers import (
    Completion,
    Message,
    OpenAICompatibleProvider,
    ProviderCallError,
    ProviderName,
    ThinkingMode,
    call_scope,
    candidate_scope,
)
from glossator.eval.run_records import RunRecorder, create_run_directory
from glossator.ingest.links import extract_links
from glossator.ingest.pages import read_manifest
from glossator.ingest.sections import Section

logger = structlog.get_logger(__name__)

# One truncation constant, applied once per page or section text handed to a
# model. Different limits in generation and filtering let the filter reject a
# fact the generator legitimately used.
MAX_SOURCE_CHARS = 8000

MIN_SECTION_TOKENS = 80

GENERATION_TEMPERATURE = 0.7
GENERATION_MAX_TOKENS = 700
CHECK_TEMPERATURE = 0.0
CHECK_MAX_TOKENS = 500
PROBE_MAX_TOKENS = 400

# How many corpus sections an unanswerable candidate is checked against.
UNANSWERABLE_CHECK_TOP_K = 5

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


DROP_PROVIDER_ERROR = "provider_error"

Language = Literal["en", "fr"]

T = TypeVar("T")


def _language(locale: str) -> Language:
    """The dataset language for a page locale. Only the two mirrors exist (D-008)."""
    return "fr" if locale == "fr" else "en"


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
        cache_nonce: str | None,
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


class CrossPageOutput(CandidateOutput):
    page_a_contribution: str
    page_b_contribution: str


class CapabilityOutput(CandidateOutput):
    names_single_model: bool


class FilterOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    standalone: bool
    gold_condition_met: bool
    not_answerable_from_title_alone: bool
    uses_every_gold_source: bool
    about_the_documented_product: bool
    reasons: list[str]


class PageAloneOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    fully_answerable: bool
    reason: str


class PageAloneVerdict(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    title: str
    fully_answerable: bool
    reason: str


class CorpusCheckOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    answered_by_corpus: bool
    reason: str


class SampledSource(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    title: str
    anchor: str | None
    heading_path: list[str]
    content: str


class SourceContribution(BaseModel):
    """Which page supplies which half of a cross-page answer.

    Kept on the record only: the reference answer a judge scores against stays a
    natural answer, with no page labels to score formatting on.
    """

    model_config = ConfigDict(frozen=True)

    url: str
    contribution: str


class GenerationAttempt(BaseModel):
    """One row of ``records.jsonl``: every candidate, kept or not."""

    model_config = ConfigDict(frozen=True)

    candidate_id: str
    generator_type: str
    seed: list[str]
    candidate: CandidateOutput | None = None
    filter: FilterOutput | None = None
    page_alone: list[PageAloneVerdict] = []
    corpus_check: CorpusCheckOutput | None = None
    consulted_sections: list[str] = []
    closed_book_answer: str | None = None
    contributions: list[SourceContribution] = []
    foreign_vendors: list[str] = []
    duplicate: bool = False
    kept: bool
    drop_reasons: list[str]
    sampled_sources: list[SampledSource]
    question: EvalQuestion | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class AttemptPlan:
    """What one attempt will ask about, decided before any model is called."""

    question_type: QuestionType
    documents: tuple[CorpusDocument, ...]
    sources: tuple[SampledSource, ...]
    gold: tuple[GoldSource, ...]
    language: Language
    nonce: int

    @property
    def candidate_id(self) -> str:
        material = {
            "type": self.question_type.value,
            "sources": [(source.url, source.anchor) for source in self.sources],
            "nonce": self.nonce,
        }
        digest = hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()
        return f"cand-{digest[:16]}"


@dataclass(slots=True)
class AttemptOutcome:
    """What the model calls produced, before duplicate detection."""

    plan: AttemptPlan
    candidate: CandidateOutput | None = None
    filter: FilterOutput | None = None
    page_alone: list[PageAloneVerdict] = field(default_factory=list)
    corpus_check: CorpusCheckOutput | None = None
    consulted_sections: list[str] = field(default_factory=list)
    closed_book_answer: str | None = None
    contributions: list[SourceContribution] = field(default_factory=list)
    foreign_vendors: list[str] = field(default_factory=list)
    gold: tuple[GoldSource, ...] = ()
    drop_reasons: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass(slots=True)
class TypeResult:
    """Per-type outcome, including a shortfall the run does not abort on."""

    question_type: QuestionType
    requested: int
    accepted: int
    attempted: int

    @property
    def shortfall(self) -> int:
        return max(self.requested - self.accepted, 0)


@dataclass(slots=True)
class GenerationContext:
    provider: ChatProvider
    model: str
    thinking: ThinkingMode | None
    documents: list[CorpusDocument]
    index: LexicalIndex
    recorder: RunRecorder | None = None
    seen: set[str] = field(default_factory=set)


# --------------------------------------------------------------------------- #
# Sampling
# --------------------------------------------------------------------------- #


def eligible_sections(
    documents: Sequence[CorpusDocument],
    *,
    kinds: set[str] | None = None,
    post_cutoff_only: bool = False,
    exclude_post_cutoff: bool = False,
    min_tokens: int = MIN_SECTION_TOKENS,
) -> dict[str, list[tuple[CorpusDocument, Section]]]:
    """Candidate sections grouped by the site area they belong to.

    Grouping is what stops ``/studio``, which is most of the corpus, from
    supplying most of the questions.
    """
    grouped: dict[str, list[tuple[CorpusDocument, Section]]] = defaultdict(list)
    for document in documents:
        if kinds is not None and document.page.kind not in kinds:
            continue
        if post_cutoff_only and not document.is_post_cutoff:
            continue
        if exclude_post_cutoff and document.is_post_cutoff:
            continue
        for section in document.sections:
            if section.level <= 1 or estimate_tokens(section.body) < min_tokens:
                continue
            grouped[document.top_level].append((document, section))
    return dict(grouped)


def draw_balanced[T](
    grouped: dict[str, list[T]],
    n: int,
    rng: random.Random,
) -> list[T]:
    """Draw up to ``n`` items, round-robin over groups, without replacement.

    Sampling with replacement wastes a generation call and a filter call on a
    duplicate that the duplicate check then drops.
    """
    pools = {name: list(items) for name, items in sorted(grouped.items()) if items}
    for items in pools.values():
        rng.shuffle(items)
    drawn: list[T] = []
    while len(drawn) < n and pools:
        for name in sorted(pools):
            if len(drawn) >= n:
                break
            drawn.append(pools[name].pop())
            if not pools[name]:
                del pools[name]
    return drawn


def sample_sections(
    documents: Sequence[CorpusDocument],
    n: int,
    rng: random.Random,
    *,
    kinds: set[str] | None = None,
    post_cutoff_only: bool = False,
    exclude_post_cutoff: bool = False,
) -> list[tuple[CorpusDocument, Section]]:
    grouped = eligible_sections(
        documents,
        kinds=kinds,
        post_cutoff_only=post_cutoff_only,
        exclude_post_cutoff=exclude_post_cutoff,
    )
    return draw_balanced(grouped, n, rng)


def cross_page_groups(
    documents: Sequence[CorpusDocument],
) -> dict[str, list[tuple[CorpusDocument, CorpusDocument]]]:
    """Pairs of related pages, grouped by the breadcrumb parent they share.

    Pairing inside a breadcrumb group is quadratic in the size of the group, so
    without grouping the largest category on the real corpus would supply nearly
    every pair. Pages that link to each other are paired too, under the group of
    the linking page.
    """
    groups: dict[str, list[tuple[CorpusDocument, CorpusDocument]]] = defaultdict(list)
    links = {
        document.url: set(extract_links(document.page.body, base_url=document.url))
        for document in documents
    }
    for index, left in enumerate(documents):
        for right in documents[index + 1 :]:
            shared = (
                left.page.breadcrumbs
                and right.page.breadcrumbs
                and left.page.breadcrumbs[-1] == right.page.breadcrumbs[-1]
            )
            linked = right.url in links[left.url] or left.url in links[right.url]
            if shared:
                groups[left.page.breadcrumbs[-1]].append((left, right))
            elif linked:
                groups[f"links:{left.top_level}"].append((left, right))
    return dict(groups)


CapabilitySeed = tuple[CorpusDocument, Section, CorpusDocument | None]


def capability_pairs(
    documents: Sequence[CorpusDocument],
    rng: random.Random,
) -> dict[str, list[CapabilitySeed]]:
    """Feature sections of the capability matrix, each with a model card.

    D-006: "which models support function calling" is answerable from a feature
    section of the matrix; "does model Y support X" also needs Y's card. Every
    seed leads with the matrix, which is always gold -- it carries the per-feature
    model lists and the context lengths. The card is drawn from the models that
    feature section links to, so the pair is about the same feature, and seeds are
    grouped by feature so that one large feature cannot supply every question.
    """
    matrix = next(
        (
            document
            for document in documents
            if document.page.kind == "model" and document.path == "/models"
        ),
        None,
    )
    if matrix is None:
        return {}
    cards = {
        document.url: document
        for document in documents
        if document.page.kind == "model" and document.path.startswith("/models/")
    }
    grouped: dict[str, list[CapabilitySeed]] = defaultdict(list)
    for section in matrix.sections:
        if section.level <= 1 or estimate_tokens(section.body) < MIN_SECTION_TOKENS:
            continue
        linked = [
            cards[url] for url in extract_links(section.body, base_url=matrix.url) if url in cards
        ]
        rng.shuffle(linked)
        grouped[section.heading].append((matrix, section, None))
        for card in linked[:4]:
            grouped[section.heading].append((matrix, section, card))
    return dict(grouped)


def api_operations(
    documents: Sequence[CorpusDocument],
) -> dict[str, list[tuple[CorpusDocument, Section]]]:
    """Operation sections of the API pages, grouped by API area.

    On API pages the anchors are operation ids (D-003a), so a section with an
    anchor is one operation, and its subsections carry the request body and the
    response codes.
    """
    grouped: dict[str, list[tuple[CorpusDocument, Section]]] = defaultdict(list)
    for document in documents:
        if document.page.kind != "api":
            continue
        group = "/".join(document.path.strip("/").split("/")[:3]) or "api"
        for section in document.sections:
            if section.anchor is None or section.level <= 1:
                continue
            grouped[group].append((document, section))
    return dict(grouped)


# --------------------------------------------------------------------------- #
# Planning
# --------------------------------------------------------------------------- #


def _section_source(document: CorpusDocument, section: Section, text: str) -> SampledSource:
    return SampledSource(
        url=document.url,
        title=document.title,
        anchor=section.anchor,
        heading_path=list(section.heading_path),
        content=text[:MAX_SOURCE_CHARS],
    )


def _page_source(document: CorpusDocument) -> SampledSource:
    return SampledSource(
        url=document.url,
        title=document.title,
        anchor=None,
        heading_path=[document.title],
        content=document.page.body[:MAX_SOURCE_CHARS],
    )


def plan_attempts(
    documents: Sequence[CorpusDocument],
    question_type: QuestionType,
    count: int,
    rng: random.Random,
) -> list[AttemptPlan]:
    """The ``count`` attempts of one question type, sampled before any call.

    Planning up front is what lets ``--dry-run`` show exactly what a real run
    would ask about.
    """
    plans: list[AttemptPlan] = []
    if question_type == QuestionType.CROSS_PAGE:
        for nonce, (left, right) in enumerate(
            draw_balanced(cross_page_groups(documents), count, rng)
        ):
            plans.append(
                AttemptPlan(
                    question_type=question_type,
                    documents=(left, right),
                    sources=(_page_source(left), _page_source(right)),
                    gold=(GoldSource(url=left.url), GoldSource(url=right.url)),
                    language=_language(left.page.locale),
                    nonce=nonce,
                )
            )
        return plans

    if question_type == QuestionType.CAPABILITY:
        for nonce, (matrix, section, card) in enumerate(
            draw_balanced(capability_pairs(documents, rng), count, rng)
        ):
            sources = [_section_source(matrix, section, block_text(matrix, section))]
            documents_used = [matrix]
            if card is not None:
                sources.append(_page_source(card))
                documents_used.append(card)
            plans.append(
                AttemptPlan(
                    question_type=question_type,
                    documents=tuple(documents_used),
                    sources=tuple(sources),
                    # The card joins the gold only when the question names that
                    # model; decided after generation.
                    gold=(GoldSource(url=matrix.url, anchor=section.anchor),),
                    language=_language(matrix.page.locale),
                    nonce=nonce,
                )
            )
        return plans

    if question_type == QuestionType.API_REFERENCE:
        for nonce, (document, section) in enumerate(
            draw_balanced(api_operations(documents), count, rng)
        ):
            plans.append(
                AttemptPlan(
                    question_type=question_type,
                    documents=(document,),
                    sources=(_section_source(document, section, block_text(document, section)),),
                    gold=(GoldSource(url=document.url, anchor=section.anchor),),
                    language=_language(document.page.locale),
                    nonce=nonce,
                )
            )
        return plans

    sampled = sample_sections(
        documents,
        count,
        rng,
        kinds={"doc"} if question_type == QuestionType.SINGLE_PAGE else None,
        exclude_post_cutoff=question_type == QuestionType.SINGLE_PAGE,
        post_cutoff_only=question_type == QuestionType.POST_CUTOFF,
    )
    for nonce, (document, section) in enumerate(sampled):
        gold: tuple[GoldSource, ...] = ()
        if question_type != QuestionType.UNANSWERABLE:
            gold = (GoldSource(url=document.url, anchor=section.anchor),)
        plans.append(
            AttemptPlan(
                question_type=question_type,
                documents=(document,),
                sources=(_section_source(document, section, section.body),),
                gold=gold,
                language=_language(document.page.locale),
                nonce=nonce,
            )
        )
    return plans


# --------------------------------------------------------------------------- #
# Generation and checking
# --------------------------------------------------------------------------- #


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


def _capability_gold(plan: AttemptPlan, candidate: CandidateOutput) -> tuple[GoldSource, ...]:
    """Gold for a capability question: the matrix, plus the model card it names.

    The generator's ``names_single_model`` flag alone is not enough -- the card
    joins the gold only when the question actually writes that model's name.
    """
    gold = list(plan.gold)
    if not isinstance(candidate, CapabilityOutput) or not candidate.names_single_model:
        return tuple(gold)
    question = candidate.question.casefold()
    for source in plan.sources[1:]:
        names = [source.title, *_api_names(source.content)]
        if any(name.casefold() in question for name in names if name):
            gold.append(GoldSource(url=source.url))
    return tuple(gold)


_API_NAME_RE = re.compile(r"`([a-z0-9][a-z0-9.\-]{4,})`")


def _api_names(text: str) -> list[str]:
    return _API_NAME_RE.findall(text)


async def run_attempt(context: GenerationContext, plan: AttemptPlan) -> AttemptOutcome:
    """One candidate, generated and checked. Never raises on a provider failure."""
    outcome = AttemptOutcome(plan=plan, gold=plan.gold)
    with candidate_scope(plan.candidate_id):
        try:
            candidate = await generate_candidate(context, plan)
            outcome.candidate = candidate
            if isinstance(candidate, CrossPageOutput):
                outcome.contributions = [
                    SourceContribution(
                        url=plan.sources[0].url, contribution=candidate.page_a_contribution
                    ),
                    SourceContribution(
                        url=plan.sources[1].url, contribution=candidate.page_b_contribution
                    ),
                ]
            outcome.gold = (
                _capability_gold(plan, candidate)
                if plan.question_type == QuestionType.CAPABILITY
                else plan.gold
            )
            outcome.filter = await filter_candidate(context, plan, candidate, outcome.gold)
            if plan.question_type == QuestionType.CROSS_PAGE:
                outcome.page_alone = list(
                    await asyncio.gather(
                        check_page_alone(context, candidate, plan.documents[0], "Page A alone"),
                        check_page_alone(context, candidate, plan.documents[1], "Page B alone"),
                    )
                )
            if plan.question_type == QuestionType.UNANSWERABLE:
                outcome.corpus_check, outcome.consulted_sections = await check_corpus_answers(
                    context, candidate
                )
            if plan.question_type == QuestionType.POST_CUTOFF:
                outcome.closed_book_answer = await closed_book_probe(context, candidate)
        except ProviderCallError as error:
            # One unrecoverable call must cost one candidate, not the run.
            outcome.error = str(error)
            outcome.drop_reasons = [DROP_PROVIDER_ERROR]
            logger.info(
                "candidate_dropped_on_provider_error",
                question_type=plan.question_type.value,
                candidate_id=plan.candidate_id,
                error=str(error),
            )
            return outcome
    outcome.foreign_vendors = foreign_vendors_named(outcome.candidate.question)
    outcome.drop_reasons = _check_reasons(plan, outcome, outcome.candidate)
    return outcome


def _check_reasons(
    plan: AttemptPlan, outcome: AttemptOutcome, candidate: CandidateOutput
) -> list[str]:
    """Every reason this candidate fails, from the checks that were run."""
    reasons: list[str] = []
    verdict = outcome.filter
    if verdict is not None:
        if not verdict.standalone:
            reasons.append("not standalone")
        if not verdict.gold_condition_met:
            reasons.append("gold condition failed")
        if not verdict.not_answerable_from_title_alone:
            reasons.append("answerable from title alone")
        if not verdict.uses_every_gold_source:
            reasons.append("does not require every gold source")
        if not verdict.about_the_documented_product:
            reasons.append("not about the documented product")
    if outcome.foreign_vendors:
        reasons.append("names another vendor's product")
    expected_fully_answered = plan.question_type != QuestionType.UNANSWERABLE
    if candidate.fully_answered != expected_fully_answered:
        reasons.append("fully_answered conflicts with question type")
    if any(page.fully_answerable for page in outcome.page_alone):
        # One reason for every page, not one per page title: the title belongs on
        # the verdict in the record, and a reason that varies cannot be counted.
        reasons.append("answerable from one page alone")
    if outcome.corpus_check is not None and outcome.corpus_check.answered_by_corpus:
        reasons.append("the corpus answers it after all")
    return reasons


def finalize_attempt(
    context: GenerationContext, outcome: AttemptOutcome, *, still_needed: bool = True
) -> GenerationAttempt:
    """Turn an outcome into a record row, applying duplicate detection.

    Runs after the concurrent attempts of a wave have finished, so that two
    identical questions produced at the same time cannot both be accepted, and
    so that ``kept`` means what the dataset holds rather than what passed the
    checks: a wave overshoots on purpose, and the surplus is recorded as such.
    """
    plan = outcome.plan
    drop_reasons = list(outcome.drop_reasons)
    duplicate = False
    if outcome.candidate is not None:
        normalized = normalize_question(outcome.candidate.question)
        duplicate = normalized in context.seen
        if duplicate:
            drop_reasons.append("duplicate question")
        if not drop_reasons and not still_needed:
            drop_reasons.append("surplus, the type was already filled")
    kept = outcome.candidate is not None and not drop_reasons

    question: EvalQuestion | None = None
    if kept and outcome.candidate is not None:
        context.seen.add(normalize_question(outcome.candidate.question))
        question = EvalQuestion(
            id=_question_id(plan.question_type, outcome.candidate.question, outcome.gold),
            question=outcome.candidate.question.strip(),
            type=plan.question_type,
            gold=list(outcome.gold),
            reference_answer=outcome.candidate.reference_answer.strip(),
            language=plan.language,
            source=QuestionSource.GENERATED,
            generator=_generator_metadata(context, plan, outcome),
        )
    attempt = GenerationAttempt(
        candidate_id=plan.candidate_id,
        generator_type=plan.question_type.value,
        seed=[source.url for source in plan.sources],
        candidate=outcome.candidate,
        filter=outcome.filter,
        page_alone=outcome.page_alone,
        corpus_check=outcome.corpus_check,
        consulted_sections=outcome.consulted_sections,
        closed_book_answer=outcome.closed_book_answer,
        contributions=outcome.contributions,
        foreign_vendors=outcome.foreign_vendors,
        duplicate=duplicate,
        kept=kept,
        drop_reasons=drop_reasons,
        sampled_sources=list(plan.sources),
        question=question,
        error=outcome.error,
    )
    if context.recorder is not None:
        context.recorder.record_candidate(attempt)
    if not kept:
        logger.info(
            "generated_question_dropped",
            question_type=plan.question_type.value,
            reasons=drop_reasons,
        )
    return attempt


def _generator_metadata(
    context: GenerationContext, plan: AttemptPlan, outcome: AttemptOutcome
) -> dict[str, object]:
    metadata: dict[str, object] = {
        "model": context.model,
        "prompt_version": PROMPT_VERSION,
        "prompt_hashes": PROMPT_HASHES,
        "candidate_id": plan.candidate_id,
        "seed_section": [source.url for source in plan.sources],
    }
    if context.recorder is not None:
        metadata["run_dir"] = str(context.recorder.run_dir)
    if outcome.consulted_sections:
        metadata["sections_consulted"] = outcome.consulted_sections
    if outcome.closed_book_answer is not None:
        metadata["closed_book_answer"] = outcome.closed_book_answer
    if outcome.contributions:
        metadata["contributions"] = [item.model_dump(mode="json") for item in outcome.contributions]
    return metadata


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #


async def generate_questions(
    provider: ChatProvider,
    documents: Sequence[CorpusDocument],
    *,
    n: int,
    model: str,
    seed: int,
    thinking: ThinkingMode | None = "disabled",
    attempts_per_question: int = 4,
    recorder: RunRecorder | None = None,
) -> tuple[list[EvalQuestion], list[GenerationAttempt], list[TypeResult]]:
    """Generate up to ``n`` questions, evenly across the six types.

    A type that cannot be filled does not fail the run: the dataset is written
    with what was accepted and the shortfall is reported.
    """
    if n < len(QuestionType):
        raise ValueError(f"n must be at least {len(QuestionType)} so every type is represented")
    context = GenerationContext(
        provider=provider,
        model=model,
        thinking=thinking,
        documents=list(documents),
        index=LexicalIndex(documents),
        recorder=recorder,
    )
    rng = random.Random(seed)
    allocations = _allocations(n)
    accepted: list[EvalQuestion] = []
    attempts: list[GenerationAttempt] = []
    results: list[TypeResult] = []

    for question_type in QuestionType:
        target = allocations[question_type]
        budget = target * attempts_per_question
        plans = plan_attempts(documents, question_type, budget, rng)
        kept_here = 0
        used = 0
        while kept_here < target and used < len(plans):
            # Waves are sized to the remaining shortfall, doubled: at a high
            # acceptance rate the run pays for barely more than it needs, at a
            # low one it still finishes in a handful of round trips.
            wave = plans[used : used + min(len(plans) - used, max(1, (target - kept_here) * 2))]
            used += len(wave)
            outcomes = await asyncio.gather(*(run_attempt(context, plan) for plan in wave))
            for outcome in outcomes:
                attempt = finalize_attempt(context, outcome, still_needed=kept_here < target)
                attempts.append(attempt)
                if attempt.question is not None:
                    accepted.append(attempt.question)
                    kept_here += 1
        results.append(
            TypeResult(
                question_type=question_type,
                requested=target,
                accepted=kept_here,
                attempted=used,
            )
        )
        if kept_here < target:
            logger.warning(
                "question_type_short",
                question_type=question_type.value,
                accepted=kept_here,
                requested=target,
                attempted=used,
            )
    return accepted, attempts, results


def normalize_question(question: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", question.casefold()))


def _question_id(question_type: QuestionType, question: str, gold: Sequence[GoldSource]) -> str:
    material = {
        "type": question_type.value,
        "question": normalize_question(question),
        "gold": [source.model_dump() for source in gold],
    }
    digest = hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()[:16]
    return f"gen-{digest}"


def _allocations(n: int) -> dict[QuestionType, int]:
    order = list(QuestionType)
    allocations = {question_type: 1 for question_type in order}
    for index in range(n - len(order)):
        allocations[order[index % len(order)]] += 1
    return allocations


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a documentation evaluation set")
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--name")
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--provider", choices=("zai", "mistral"), default="zai")
    parser.add_argument("--model", default="glm-5.3-flash")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument(
        "--attempts-per-question",
        type=int,
        default=4,
        help="candidates generated per requested question before a type is left short",
    )
    parser.add_argument("--thinking", choices=("enabled", "disabled"), default="disabled")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print what the run would sample, call nothing and write nothing",
    )
    return parser.parse_args()


def _dry_run(documents: Sequence[CorpusDocument], args: argparse.Namespace) -> None:
    """Show the sources a real run with these arguments would ask about."""
    rng = random.Random(args.seed)
    allocations = _allocations(args.n)
    for question_type in QuestionType:
        budget = allocations[question_type] * args.attempts_per_question
        for plan in plan_attempts(documents, question_type, budget, rng):
            print(
                json.dumps(
                    {
                        "type": question_type.value,
                        "candidate_id": plan.candidate_id,
                        "sources": [
                            {
                                "url": source.url,
                                "anchor": source.anchor,
                                "heading_path": source.heading_path,
                            }
                            for source in plan.sources
                        ],
                    }
                )
            )


async def _run(args: argparse.Namespace) -> None:
    documents = load_documents(args.corpus)
    if args.dry_run:
        _dry_run(documents, args)
        return

    run_name = args.name or (args.out.stem if args.out else "generate")
    run_dir = create_run_directory(run_name)
    dataset_path = args.out or run_dir / "questions.jsonl"
    corpus_commits = sorted({document.page.source_commit for document in documents})
    # z.ai is the only provider that takes a thinking setting; sending it to
    # Mistral is an error, and D-020 and D-021 both rest on this being swappable.
    thinking = cast(ThinkingMode, args.thinking) if args.provider == "zai" else None
    config = {
        "name": run_name,
        "run_dir": str(run_dir),
        "corpus": str(args.corpus),
        "corpus_commit": corpus_commits[0] if len(corpus_commits) == 1 else corpus_commits,
        "out": str(dataset_path),
        "n": args.n,
        "provider": args.provider,
        "model": args.model,
        "thinking": thinking,
        "seed": args.seed,
        "concurrency": args.concurrency,
        "attempts_per_question": args.attempts_per_question,
        "prompt_version": PROMPT_VERSION,
        "prompt_hashes": PROMPT_HASHES,
        "cache_dir": ".cache/llm",
        "minimum_section_tokens": MIN_SECTION_TOKENS,
        "max_source_chars": MAX_SOURCE_CHARS,
        "generation_temperature": GENERATION_TEMPERATURE,
        "generation_max_tokens": GENERATION_MAX_TOKENS,
        "check_temperature": CHECK_TEMPERATURE,
        "check_max_tokens": CHECK_MAX_TOKENS,
        "unanswerable_check_top_k": UNANSWERABLE_CHECK_TOP_K,
        "http_attempts": 3,
        "structured_output_repairs": 1,
    }
    recorder = RunRecorder.start(run_dir, config)
    try:
        async with OpenAICompatibleProvider(
            cast(ProviderName, args.provider),
            asyncio.Semaphore(args.concurrency),
            caller_tag="eval.generate",
            recorder=recorder,
            seed=args.seed,
        ) as provider:
            questions, _attempts, results = await generate_questions(
                provider,
                documents,
                n=args.n,
                model=args.model,
                seed=args.seed,
                thinking=thinking,
                attempts_per_question=args.attempts_per_question,
                recorder=recorder,
            )
        manifest_path = args.corpus / "manifest.json"
        if manifest_path.exists():
            issues = validate_against_corpus(
                questions,
                read_manifest(args.corpus),
                [document.page for document in documents],
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
    recorder.finalize(
        dataset_path=dataset_path,
        error=None,
        shortfalls={
            result.question_type.value: result.shortfall for result in results if result.shortfall
        },
        requested_by_type={result.question_type.value: result.requested for result in results},
    )
    print(
        json.dumps(
            {
                "written": len(questions),
                "out": str(dataset_path),
                "run_dir": str(run_dir),
                "requested": {result.question_type.value: result.requested for result in results},
                "accepted": {result.question_type.value: result.accepted for result in results},
                "shortfall": {
                    result.question_type.value: result.shortfall
                    for result in results
                    if result.shortfall
                },
                "usage": recorder.usage_line(),
            }
        )
    )


def main() -> None:
    # Not override=True: an operator who exports a key for one run should not
    # have it replaced by whatever .env holds.
    load_dotenv()
    asyncio.run(_run(_parse_args()))


if __name__ == "__main__":
    main()
