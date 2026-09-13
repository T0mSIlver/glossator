"""The record side: what one answer retrieved, was shown, cited and was judged."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from glossator.answer.citations import Trace
from glossator.eval.answer_eval.matching import accepts_model_card
from glossator.eval.answer_eval.models import QuestionRecord
from glossator.eval.datasets import QuestionType


def page_url(url: str) -> str:
    """A citation or gold URL without its fragment: the page a reader lands on."""
    return urlparse(url)._replace(fragment="").geturl()


def retrieved_chunk_ids(trace: Trace | None) -> list[str]:
    """Every chunk id any round of this answer saw, in the order it first appeared.

    Every event that returns chunks carries them: the seed retrieval, each tool
    search, open, grep and read of the loop, and the assembly. A chunk the loop
    found in round three is as retrieved as one the seed search found.
    """
    if trace is None:
        return []
    seen: dict[str, None] = {}
    for event in trace.events:
        for chunk_id in event.result_ids:
            seen.setdefault(chunk_id, None)
    return list(seen)


def context_chunk_ids(trace: Trace | None) -> list[str]:
    """The chunk ids of the sources the model was actually shown."""
    if trace is None:
        return []
    seen: dict[str, None] = {}
    for source in trace.sources:
        for chunk_id in source.chunk_ids:
            seen.setdefault(chunk_id, None)
    return list(seen)


def accepts_page(record: QuestionRecord, url: str) -> bool:
    """Whether this URL is one the dataset's gold accepts for this question.

    The gold URLs, plus the capability relaxation the answer evaluation already
    applies to citations (D-033): the card of a model the question names stands
    in for the ``/models`` matrix.
    """
    if page_url(url) in {page_url(gold) for gold in record.gold_urls}:
        return True
    return accepts_model_card(
        url,
        question=record.question,
        question_type=record.question_type,
        gold_urls=record.gold_urls,
    )


def accepts_section(record: QuestionRecord, url: str, anchor: str | None) -> bool:
    """Whether this (URL, anchor) pair is the section the dataset points at.

    A gold source with no anchor is matched by any section of that page: the
    dataset is saying the page is the answer, and most of the corpus's headings
    have no anchor to be more precise about (D-003a). Same convention as
    `answer_eval.gold_anchor_match`, so the two numbers stay comparable.
    """
    for gold_url, gold_anchor in zip(record.gold_urls, record.gold_anchors, strict=True):
        if page_url(url) == page_url(gold_url) and (gold_anchor is None or anchor == gold_anchor):
            return True
    return accepts_model_card(
        url,
        question=record.question,
        question_type=record.question_type,
        gold_urls=record.gold_urls,
    )


def is_answerable(record: QuestionRecord) -> bool:
    return record.question_type != QuestionType.UNANSWERABLE.value


def verdict_of(record: QuestionRecord) -> str | None:
    """The primary judge's correctness label, or None when nothing judged it."""
    if record.judge is None or record.judge.verdict is None:
        return None
    return record.judge.verdict.correctness


def refusal_correct(record: QuestionRecord) -> bool:
    return record.insufficient_evidence == (not is_answerable(record))


def is_failure(record: QuestionRecord) -> bool:
    """Whether this answer failed at all: a bad verdict, or a refusal in the wrong direction."""
    return verdict_of(record) in ("partial", "wrong") or not refusal_correct(record)


_CANDIDATE_LINE = re.compile(r"^\[(?P<number>\d+)\] (?P<url>\S+) \| ", re.MULTILINE)


def rerank_candidates(run_dir: Path) -> dict[tuple[str, str], set[str]]:
    """The pages the reranker was offered, per (question, strategy), from `calls.jsonl`.

    The reranker prompt lists its candidates as ``[n] <citation url> | <heading>``
    (`glossator.retrieval.reranker.render_candidates`), so a recorded rerank call
    is the only surviving record of what ranked *before* the reranker cut the list
    to `top_k`. Runs made before reranker calls reached the ledger (D-023b) have
    none, and the caller reports that as an unknown rather than as a search miss.
    """
    calls = run_dir / "calls.jsonl"
    if not calls.exists():
        return {}
    offered: dict[tuple[str, str], set[str]] = {}
    with calls.open() as handle:
        for line in handle:
            # Parsing every row of a 14 MB ledger to find a call kind that most
            # runs do not have costs more than the whole analysis.
            if '"rerank"' not in line:
                continue
            row = json.loads(line)
            if row.get("purpose") != "rerank":
                continue
            key = (str(row.get("question_id")), str(row.get("strategy")))
            for message in row.get("messages") or []:
                if message.get("role") != "user":
                    continue
                for match in _CANDIDATE_LINE.finditer(str(message.get("content") or "")):
                    offered.setdefault(key, set()).add(page_url(match.group("url")))
    return offered
