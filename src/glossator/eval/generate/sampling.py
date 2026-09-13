"""Which corpus sections and pages a question type can be asked about, drawn evenly."""

from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Sequence
from typing import TypeVar

from glossator.eval.corpus import CorpusDocument, estimate_tokens
from glossator.eval.generate.models import MIN_SECTION_TOKENS
from glossator.ingest.links import extract_links
from glossator.ingest.sections import Section

T = TypeVar("T")


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
