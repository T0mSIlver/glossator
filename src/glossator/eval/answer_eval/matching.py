"""Whether an answer's verified citations land on the dataset's gold sources."""

from __future__ import annotations

import re
from collections.abc import Sequence
from functools import cache
from pathlib import Path
from urllib.parse import urlparse

from glossator.eval.answer_eval.models import QuestionRecord
from glossator.eval.datasets import QuestionType
from glossator.ingest.pages import load_page

MODEL_CARDS_ROOT = Path(__file__).resolve().parents[4] / "corpus" / "mistral-docs" / "models"
_API_NAMES_ROW = re.compile(r"(?mi)^\|\s*API names?\s*\|(?P<value>.+?)\|\s*$")
_CODE_VALUE = re.compile(r"`([^`]+)`")


def gold_url_match(record: QuestionRecord) -> bool:
    """A verified citation names a gold page or an accepted capability model card."""
    return exact_gold_url_match(record) or gold_relaxed_match(record)


def gold_anchor_match(record: QuestionRecord) -> bool:
    """A verified citation names a gold page *and* lands on the gold section.

    A gold source with no anchor is matched by any citation to that page: the
    dataset is saying the page is the answer, and 53% of the corpus's sections
    have no anchor to be more precise about (D-003a).
    """
    return exact_gold_anchor_match(record) or gold_relaxed_match(record)


def exact_gold_url_match(record: QuestionRecord) -> bool:
    gold = set(record.gold_urls)
    return any(citation.url in gold for citation in record.citations)


def exact_gold_anchor_match(record: QuestionRecord) -> bool:
    pairs = list(zip(record.gold_urls, record.gold_anchors, strict=True))
    return any(
        citation.url == url and (anchor is None or citation.anchor == anchor)
        for citation in record.citations
        for url, anchor in pairs
    )


def accepts_model_card(
    url: str, *, question: str, question_type: str, gold_urls: Sequence[str]
) -> bool:
    """Whether one URL is a named model's card standing in for the capability matrix.

    Capability gold points to ``/models`` because the matrix answers the full
    question. A card for a model named in the question is also valid evidence for
    that model. The relaxation requires the exact model title or one of the API
    names declared by that card. It takes a bare URL rather than a record so that
    the same rule can be applied to a citation, a retrieved chunk or an assembled
    source, which is what the failure analysis needs.
    """
    if question_type != QuestionType.CAPABILITY.value:
        return False
    matrix_hosts = {
        parsed.netloc
        for parsed in (urlparse(gold) for gold in gold_urls)
        if parsed.path.rstrip("/") == "/models"
    }
    if not matrix_hosts:
        return False
    parsed = urlparse(url)
    prefix = "/models/"
    if parsed.netloc not in matrix_hosts or not parsed.path.startswith(prefix):
        return False
    slug = parsed.path.removeprefix(prefix).strip("/")
    if not slug or "/" in slug:
        return False
    return any(_names_model(question, name) for name in _model_names(slug))


def gold_relaxed_match(record: QuestionRecord) -> bool:
    """A verified citation names the card of a model the capability question names.

    Counted separately in the run, because it is a relaxation of the dataset's
    gold and not a match against it.
    """
    return any(
        accepts_model_card(
            citation.url,
            question=record.question,
            question_type=record.question_type,
            gold_urls=record.gold_urls,
        )
        for citation in record.citations
    )


@cache
def _model_names(slug: str) -> tuple[str, ...]:
    path = MODEL_CARDS_ROOT / f"{slug}.md"
    if not path.is_file():
        return ()
    page = load_page(path)
    api_names: list[str] = []
    if row := _API_NAMES_ROW.search(page.body):
        api_names.extend(_CODE_VALUE.findall(row.group("value")))
    return (page.title, *api_names)


def _names_model(question: str, name: str) -> bool:
    return bool(re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", question, re.IGNORECASE))
