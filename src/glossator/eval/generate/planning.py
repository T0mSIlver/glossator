"""Every attempt of a question type, sampled before any model is called."""

from __future__ import annotations

import random
from collections.abc import Sequence

from glossator.eval.corpus import CorpusDocument, block_text
from glossator.eval.datasets import GoldSource, QuestionType
from glossator.eval.generate.models import MAX_SOURCE_CHARS, AttemptPlan, Language, SampledSource
from glossator.eval.generate.sampling import (
    api_operations,
    capability_pairs,
    cross_page_groups,
    draw_balanced,
    sample_sections,
)
from glossator.ingest.sections import Section


def _language(locale: str) -> Language:
    """The dataset language for a page locale. Only the two mirrors exist (D-008)."""
    return "fr" if locale == "fr" else "en"


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
