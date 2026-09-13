"""What a question's reference answer rests on, looked up in one snapshot."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from glossator.answer.citations import contains_span
from glossator.eval.corpus import CorpusDocument, block_text, load_documents
from glossator.eval.datasets import EvalQuestion, read_jsonl
from glossator.eval.lexical import LexicalIndex
from glossator.eval.snapshots.models import CURRENT_CORPUS, PAGE_PROMPT_CHARS, Span
from glossator.eval.snapshots.run_files import RUNS_ROOT


def load_questions(paths: Sequence[Path]) -> list[tuple[str, EvalQuestion]]:
    rows: list[tuple[str, EvalQuestion]] = []
    seen: set[str] = set()
    for path in paths:
        for question in read_jsonl(path):
            if question.id in seen:
                raise ValueError(f"duplicate question id {question.id!r} across datasets")
            seen.add(question.id)
            rows.append((path.stem, question))
    return rows


def verified_quotes(runs_root: Path = RUNS_ROOT) -> dict[str, list[Span]]:
    """The spans an answer relied on, each with the page it was cited from at the
    pinned commit. A span found on that same page at an older snapshot is
    ``present``; found on another page it is ``present`` and ``moved``."""
    quotes: dict[str, list[Span]] = {}
    patterns = ("*fresh60-shipped", "*mined-shipped")
    for pattern in patterns:
        for run_dir in sorted(runs_root.glob(pattern)):
            records = run_dir / "records.jsonl"
            if not records.is_file():
                continue
            for line in records.read_text().splitlines():
                row = json.loads(line)
                if row.get("strategy") != "single_pass":
                    continue
                found = [
                    Span(page=str(citation.get("url") or ""), text=str(citation["quote"]))
                    for citation in row.get("citations", [])
                    if citation.get("verified", True) and citation.get("quote")
                ]
                if found:
                    quotes[str(row["question_id"])] = found
    return quotes


def fallback_spans(
    questions: Sequence[tuple[str, EvalQuestion]], corpus_dir: Path = CURRENT_CORPUS
) -> dict[str, list[Span]]:
    documents = {document.url: document for document in load_documents(corpus_dir)}
    spans: dict[str, list[Span]] = {}
    for _dataset, question in questions:
        selected: list[Span] = []
        for gold in question.gold:
            document = documents.get(gold.url)
            if document is None:
                continue
            if gold.anchor is None:
                selected.append(Span(page=gold.url, text=document.page.body))
                continue
            section = next(
                (item for item in document.sections if item.own_anchor == gold.anchor), None
            )
            if section is not None:
                selected.append(Span(page=gold.url, text=block_text(document, section)))
        if selected:
            spans[question.id] = selected
    return spans


def exact_cell(
    question: EvalQuestion,
    spans: Sequence[Span],
    documents: Sequence[CorpusDocument],
) -> dict[str, Any] | None:
    """Deterministic step: a span found on the page it was cited from at the
    pinned commit is ``present``; found only on another page it is ``present``
    and ``moved``; found nowhere, the cell goes to the judged step."""
    by_url = {document.url: document for document in documents}
    for span in spans:
        home = by_url.get(span.page)
        if home is not None and contains_span(home.page.body, span.text):
            return {
                "label": "present",
                "moved": False,
                "decided_by": "exact_span",
                "page": home.url,
                "judges": {},
            }
    for span in spans:
        for document in documents:
            if document.url != span.page and contains_span(document.page.body, span.text):
                return {
                    "label": "present",
                    "moved": True,
                    "decided_by": "exact_span",
                    "page": document.url,
                    "judges": {},
                }
    return None


def best_matching_pages(
    index: LexicalIndex, reference_answer: str, top_k: int = 5
) -> list[dict[str, str]]:
    pages: list[dict[str, str]] = []
    seen: set[str] = set()
    for hit in index.search(reference_answer, top_k=25):
        if hit.document.url in seen:
            continue
        seen.add(hit.document.url)
        pages.append(
            {
                "url": hit.document.url,
                "title": hit.document.title,
                "text": hit.document.page.body[:PAGE_PROMPT_CHARS],
            }
        )
        if len(pages) == top_k:
            break
    return pages
