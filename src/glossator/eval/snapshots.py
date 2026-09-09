"""Label and evaluate questions across dated documentation snapshots."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import random
import statistics
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

from glossator.answer.citations import contains_span
from glossator.answer.config import LOCAL_MINISTRAL_3_14B, AnswerConfig
from glossator.answer.llm import MistralLLM
from glossator.clients import chat_client, chat_reasoning_effort
from glossator.corpus.snapshots import DEFAULT_MANIFEST, SnapshotRecord, read_snapshot_manifest
from glossator.eval.agreement import agreement_report
from glossator.eval.answer_eval import (
    AnswerCallRecorder,
    JudgeModel,
    RunDirectory,
    answer_one,
    judge_with_models,
    make_judge_providers,
    resolve_run_directory,
)
from glossator.eval.corpus import CorpusDocument, block_text, load_documents
from glossator.eval.datasets import EvalQuestion, dataset_hash, read_jsonl
from glossator.eval.lexical import LexicalIndex
from glossator.eval.providers import OpenAICompatibleProvider
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import SearchEngine

RUNS_ROOT = Path("eval/runs")
CURRENT_CORPUS = Path("corpus/mistral-docs")
PRIMARY_JUDGE = "glm-5.3"
SECONDARY_JUDGE = "glm-5.3-flash"
LABEL_SEED = 0
PAGE_PROMPT_CHARS = 6000


@dataclass(frozen=True, slots=True)
class Span:
    """A supporting span and the page it was cited from at the pinned commit."""

    page: str
    text: str


class FactVerdict(BaseModel):
    model_config = ConfigDict(frozen=True)

    classification: Literal["stated", "different_value", "not_stated"]
    reason: str
    page: str | None = None
    evidence: str = ""


JUDGE_SYSTEM = (
    "You compare one reference answer with documentation from an older date. "
    "Decide only whether the same fact is stated in the supplied pages, whether "
    "the pages state the fact with a different value, or whether the fact is not "
    "stated. Different wording with the same meaning is stated. Do not use outside "
    "knowledge. Return a short reason and quote the decisive evidence when there is any."
)


class LabelCallRecorder:
    def __init__(self, path: Path) -> None:
        self.path = path

    def record_call(self, **row: Any) -> None:
        encoded: dict[str, Any] = {}
        for key, value in row.items():
            if isinstance(value, BaseModel):
                encoded[key] = value.model_dump(mode="json")
            elif key == "messages":
                encoded[key] = [dict(message) for message in value]
            else:
                encoded[key] = value
        with self.path.open("a") as handle:
            handle.write(json.dumps(encoded, sort_keys=True) + "\n")


def _built_snapshots(path: Path) -> list[SnapshotRecord]:
    return [row for row in read_snapshot_manifest(path) if row.status == "built"]


def _load_questions(paths: Sequence[Path]) -> list[tuple[str, EvalQuestion]]:
    rows: list[tuple[str, EvalQuestion]] = []
    seen: set[str] = set()
    for path in paths:
        for question in read_jsonl(path):
            if question.id in seen:
                raise ValueError(f"duplicate question id {question.id!r} across datasets")
            seen.add(question.id)
            rows.append((path.stem, question))
    return rows


def _verified_quotes(runs_root: Path = RUNS_ROOT) -> dict[str, list[Span]]:
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


def _fallback_spans(
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


def _exact_cell(
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


def _top_pages(index: LexicalIndex, reference_answer: str, top_k: int = 5) -> list[dict[str, str]]:
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


def _judge_prompt(question: EvalQuestion, pages: Sequence[Mapping[str, str]]) -> str:
    rendered = "\n\n".join(
        f"PAGE {index}: {page['url']}\n{page['text']}" for index, page in enumerate(pages, 1)
    )
    return (
        f"QUESTION\n{question.question}\n\nREFERENCE ANSWER\n{question.reference_answer}"
        f"\n\nOLDER DOCUMENTATION\n{rendered or '(no lexical match)'}"
    )


async def _judge_cell(
    question: EvalQuestion,
    pages: list[dict[str, str]],
    providers: Mapping[str, OpenAICompatibleProvider],
) -> tuple[str, dict[str, Any]]:
    prompt = _judge_prompt(question, pages)

    async def call(model: str) -> tuple[str, dict[str, Any]]:
        completion = await providers[model].complete(
            [{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": prompt}],
            model=model,
            temperature=0.0,
            max_tokens=800,
            response_schema=FactVerdict,
            thinking="disabled",
        )
        verdict = completion.parsed
        if not isinstance(verdict, FactVerdict):
            raise ValueError(f"{model} returned no valid fact verdict")
        return model, {
            "classification": verdict.classification,
            "reason": verdict.reason,
            "page": verdict.page,
            "evidence": verdict.evidence,
            "raw": completion.text,
            "usage": completion.usage.model_dump(mode="json"),
            "cached": completion.cached,
        }

    judged = dict(await asyncio.gather(call(PRIMARY_JUDGE), call(SECONDARY_JUDGE)))
    primary = judged[PRIMARY_JUDGE]["classification"]
    label = {
        "stated": "present_rephrased",
        "different_value": "changed",
        "not_stated": "absent",
    }[primary]
    return label, judged


def _run_path(name: str, root: Path = RUNS_ROOT) -> Path:
    return resolve_run_directory(name, root=root)


def _append(path: Path, row: Mapping[str, Any]) -> None:
    with path.open("a") as handle:
        handle.write(json.dumps(dict(row), sort_keys=True) + "\n")


def _metrics(
    rows: Sequence[Mapping[str, Any]], snapshots: Sequence[SnapshotRecord]
) -> dict[str, Any]:
    per_snapshot: dict[str, Any] = {}
    for snapshot in snapshots:
        cells = [row for row in rows if row["snapshot"] == snapshot.date]
        counts = Counter(str(row["label"]) for row in cells)
        deterministic = sum(row["decided_by"] == "exact_span" for row in cells)
        per_snapshot[snapshot.date] = {
            "counts": dict(sorted(counts.items())),
            "cells": len(cells),
            "deterministic": deterministic,
            "deterministic_share": deterministic / len(cells) if cells else None,
        }
    judge_maps: dict[str, dict[tuple[str, str], Any]] = {PRIMARY_JUDGE: {}, SECONDARY_JUDGE: {}}
    mapped = {"stated": "correct", "different_value": "partial", "not_stated": "wrong"}
    for row in rows:
        for model, verdict in row.get("judges", {}).items():
            judge_maps[model][(str(row["question_id"]), str(row["snapshot"]))] = mapped[
                verdict["classification"]
            ]
    return {
        "cells": len(rows),
        "per_snapshot": per_snapshot,
        "deterministic_share": (
            sum(row["decided_by"] == "exact_span" for row in rows) / len(rows) if rows else None
        ),
        "agreement": agreement_report(judge_maps),
    }


def _svg(metrics: Mapping[str, Any]) -> str:
    snapshots = list(metrics["per_snapshot"])
    width, height = 900, 420
    chart_height = 300
    bar_width = 70
    gap = 35
    maximum = max((cell["cells"] for cell in metrics["per_snapshot"].values()), default=1)
    colors = {"present": "#2f855a", "changed": "#d69e2e", "absent": "#c53030"}
    pending_color = "#a0aec0"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="20" y="28" font-family="sans-serif" font-size="18">'
        "Question availability by snapshot</text>",
    ]
    for index, date in enumerate(snapshots):
        x = 45 + index * (bar_width + gap)
        y = 345
        counts = metrics["per_snapshot"][date]["counts"]
        groups = {
            "present": counts.get("present", 0) + counts.get("present_rephrased", 0),
            "changed": counts.get("changed", 0),
            "absent": counts.get("absent", 0),
        }
        for label in ("present", "changed", "absent"):
            segment = chart_height * groups[label] / maximum
            y -= segment
            parts.append(
                f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" '
                f'height="{segment:.1f}" fill="{colors[label]}"/>'
            )
        pending = counts.get("unknown", 0)
        if pending:
            segment = chart_height * pending / maximum
            y -= segment
            parts.append(
                f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" '
                f'height="{segment:.1f}" fill="{pending_color}"/>'
            )
        parts.append(
            f'<text x="{x + bar_width / 2}" y="370" text-anchor="middle" '
            f'font-family="sans-serif" font-size="11">{date[5:]}</text>'
        )
    parts.extend(
        [
            '<rect x="620" y="20" width="12" height="12" fill="#2f855a"/>'
            '<text x="638" y="31" font-family="sans-serif" font-size="12">present</text>',
            '<rect x="700" y="20" width="12" height="12" fill="#d69e2e"/>'
            '<text x="718" y="31" font-family="sans-serif" font-size="12">changed</text>',
            '<rect x="790" y="20" width="12" height="12" fill="#c53030"/>'
            '<text x="808" y="31" font-family="sans-serif" font-size="12">absent</text>',
            "</svg>\n",
        ]
    )
    return "".join(parts)


def _readme(metrics: Mapping[str, Any], datasets: Sequence[Path]) -> str:
    rows = []
    for date, cell in metrics["per_snapshot"].items():
        counts = cell["counts"]
        rows.append(
            f"| {date} | {counts.get('present', 0)} | {counts.get('present_rephrased', 0)} | "
            f"{counts.get('changed', 0)} | {counts.get('absent', 0)} | "
            f"{cell['deterministic_share']:.3f} |"
        )
    pair = (metrics.get("agreement", {}).get("pairwise") or [{}])[0]
    agreement = pair.get("percentage_agreement")
    kappa = pair.get("quadratic_weighted_kappa")
    dataset_lines = "\n".join(f"- `{path}`: `{dataset_hash(path)}`" for path in datasets)
    return f"""# Snapshot availability labels

A cell is `present` when a verified supporting quote occurs in that snapshot. A
match on another page is marked as moved. If no quote matches, GLM 5.3 and GLM
5.3 Flash compare the reference answer with the five highest-scoring lexical
pages. The primary judge assigns `present_rephrased`, `changed`, or `absent`.
Cells still waiting for that judged step are `unknown` (shown grey): a later run
without `--deterministic-only` judges exactly those cells and never re-decides
the rest.

Correctness can only be scored on present cells because an answer cannot be
correct when its fact is missing or has a different dated value. Absent cells
instead measure whether the answer refuses to invent a current-looking answer.

## Datasets

{dataset_lines}

## Counts

| snapshot | present | rephrased | changed | absent | deterministic share |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

The two judges agreed exactly on {agreement if agreement is not None else "no judged cells"};
quadratic-weighted kappa was {kappa if kappa is not None else "not defined"}.
The figure at `figures/availability.svg` combines exact and rephrased cells as present.
"""


async def label(
    datasets: Sequence[Path],
    *,
    name: str,
    manifest_path: Path = DEFAULT_MANIFEST,
    runs_root: Path = RUNS_ROOT,
    seed: int = LABEL_SEED,
    deterministic_only: bool = False,
) -> tuple[Path, dict[str, Any]]:
    """Decide one availability cell per question and snapshot.

    With ``deterministic_only`` the exact-span step runs and every other cell is
    recorded as ``pending_judges`` (label ``unknown``) with its lexical top pages,
    so the judged step can fill it in later without re-deciding anything. A later
    run without the flag drops the pending rows and judges them; finished cells
    are never re-decided.
    """
    questions = _load_questions(datasets)
    snapshots = _built_snapshots(manifest_path)
    run_path = _run_path(name, runs_root)
    (run_path / "figures").mkdir(parents=True, exist_ok=True)
    labels_path = run_path / "labels.jsonl"
    calls_path = run_path / "calls.jsonl"
    records_path = run_path / "records.jsonl"
    calls_path.touch()
    labels_path.touch()
    records_path.touch()
    stored = [json.loads(line) for line in labels_path.read_text().splitlines() if line]
    existing = [row for row in stored if row.get("decided_by") != "pending_judges"]
    if len(existing) != len(stored):
        # Pending rows are placeholders for a later judged pass: drop them here so
        # the resume below re-examines exactly those cells instead of duplicating
        # them, and keep both files in sync with what the metrics are computed from.
        labels_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in existing))
        records_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in existing))
    done = {(row["question_id"], row["snapshot"]) for row in existing}
    quotes = _verified_quotes(runs_root)
    fallbacks = _fallback_spans(questions)
    recorder = LabelCallRecorder(calls_path)
    providers: Mapping[str, OpenAICompatibleProvider] = {}
    if not deterministic_only:
        providers = {
            model: OpenAICompatibleProvider(
                "zai",
                asyncio.Semaphore(1),
                caller_tag="eval.snapshots",
                recorder=recorder,
                seed=seed,
            )
            for model in (PRIMARY_JUDGE, SECONDARY_JUDGE)
        }
    try:
        for snapshot in snapshots:
            documents = load_documents(Path(snapshot.corpus_dir).expanduser())
            lexical = LexicalIndex(documents)
            for dataset, question in questions:
                key = (question.id, snapshot.date)
                if key in done:
                    continue
                spans = quotes.get(question.id) or fallbacks.get(question.id, [])
                cell = _exact_cell(question, spans, documents)
                top_pages: list[dict[str, str]] = []
                if cell is None and deterministic_only:
                    top_pages = _top_pages(lexical, question.reference_answer)
                    cell = {
                        "label": "unknown",
                        "moved": False,
                        "decided_by": "pending_judges",
                        "page": None,
                        "judges": {},
                    }
                if cell is None:
                    top_pages = _top_pages(lexical, question.reference_answer)
                    cell_label, judges = await _judge_cell(question, top_pages, providers)
                    cell = {
                        "label": cell_label,
                        "moved": False,
                        "decided_by": "judges",
                        "page": judges[PRIMARY_JUDGE].get("page"),
                        "judges": judges,
                    }
                row = {
                    "question_id": question.id,
                    "dataset": dataset,
                    "snapshot": snapshot.date,
                    **cell,
                    "question": question.question,
                    "reference_answer": question.reference_answer,
                    "gold": [source.model_dump(mode="json") for source in question.gold],
                    "supporting_spans": [{"page": span.page, "text": span.text} for span in spans],
                    "top_pages": top_pages,
                }
                _append(labels_path, row)
                _append(records_path, row)
                existing.append(row)
    finally:
        await asyncio.gather(*(provider.aclose() for provider in providers.values()))

    metrics = _metrics(existing, snapshots)
    config = {
        "kind": "snapshot_labels",
        "name": name,
        "datasets": [{"path": str(path), "sha256": dataset_hash(path)} for path in datasets],
        "snapshot_manifest": str(manifest_path),
        "snapshot_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "judges": [PRIMARY_JUDGE, SECONDARY_JUDGE],
        "seed": seed,
        "deterministic_only": deterministic_only,
        "prompt_sha256": hashlib.sha256(JUDGE_SYSTEM.encode()).hexdigest(),
    }
    (run_path / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    (run_path / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_path / "README.md").write_text(_readme(metrics, datasets))
    (run_path / "figures" / "availability.svg").write_text(_svg(metrics))
    judged = [row for row in existing if row["decided_by"] == "judges"]
    sample = random.Random(seed).sample(judged, min(20, len(judged)))
    (run_path / "human-sample.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in sample)
    )
    return run_path, metrics


def _labels_by_key(path: Path) -> dict[tuple[str, str], str]:
    return {
        (row["question_id"], row["snapshot"]): row["label"]
        for row in (json.loads(line) for line in path.read_text().splitlines() if line)
    }


def score_snapshot_records(
    records: Sequence[Mapping[str, Any]], snapshots: Sequence[SnapshotRecord]
) -> dict[str, Any]:
    """Correctness on present cells and refusal on absent cells, per snapshot.

    Rows without a judge verdict (a run with ``--skip-judge``) contribute their
    cell counts but no score: correctness and refusal stay ``None`` until judges
    fill them in.
    """
    per_snapshot: dict[str, Any] = {}
    for snapshot in snapshots:
        cells = [row for row in records if row["snapshot"] == snapshot.date]
        present = [
            row for row in cells if row["availability_label"] in {"present", "present_rephrased"}
        ]
        absent = [row for row in cells if row["availability_label"] == "absent"]
        correctness = []
        for row in present:
            verdict = (row.get("judge") or {}).get("verdict") or {}
            score = {"wrong": 0.0, "partial": 0.5, "correct": 1.0}.get(
                verdict.get("correctness", "")
            )
            if score is not None:
                correctness.append(score)
        refusal = [bool(row["insufficient_evidence"]) for row in absent]
        per_snapshot[snapshot.date] = {
            "present_cells": len(present),
            "absent_cells": len(absent),
            "correctness_present": statistics.fmean(correctness) if correctness else None,
            "refusal_rate_absent": statistics.fmean(refusal) if refusal else None,
        }
    return per_snapshot


def _eval_svg(metrics: Mapping[str, Any]) -> str:
    cells = list(metrics["per_snapshot"].items())
    points = []
    for index, (_date, cell) in enumerate(cells):
        value = cell["correctness_present"]
        if value is None:
            continue
        x = 65 + index * 105
        y = 340 - float(value) * 280
        points.append((x, y))
    polyline = " ".join(f"{x},{y:.1f}" for x, y in points)
    labels = "".join(
        f'<text x="{65 + index * 105}" y="370" text-anchor="middle" '
        f'font-family="sans-serif" font-size="11">{date[5:]}</text>'
        for index, (date, _cell) in enumerate(cells)
    )
    dots = "".join(f'<circle cx="{x}" cy="{y:.1f}" r="4" fill="#2b6cb0"/>' for x, y in points)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="400" '
        'viewBox="0 0 900 400"><rect width="100%" height="100%" fill="white"/>'
        '<text x="20" y="28" font-family="sans-serif" font-size="18">'
        "Correctness on present cells</text>"
        '<line x1="50" y1="340" x2="850" y2="340" stroke="#777"/>'
        '<line x1="50" y1="60" x2="50" y2="340" stroke="#777"/>'
        f'<polyline points="{polyline}" fill="none" stroke="#2b6cb0" stroke-width="2"/>'
        f"{dots}{labels}</svg>\n"
    )


def _eval_readme(metrics: Mapping[str, Any], dataset: Path, labels_path: Path) -> str:
    rows = []
    for date, cell in metrics["per_snapshot"].items():
        correctness = cell["correctness_present"]
        refusal = cell["refusal_rate_absent"]
        correctness_text = f"{correctness:.3f}" if correctness is not None else "--"
        refusal_text = f"{refusal:.3f}" if refusal is not None else "--"
        rows.append(
            f"| {date} | {cell['present_cells']} | {correctness_text} | "
            f"{cell['absent_cells']} | {refusal_text} |"
        )
    skipped = (
        "\nJudges were skipped for this run (`--skip-judge`): correctness and refusal "
        "are empty until a judged pass fills them in.\n"
        if metrics.get("judge_skipped")
        else ""
    )
    return f"""# Answer evaluation across snapshots

Each question ran once against each dated `snap1024` partition with the shipped
reranker. Generation used the recorded local server, never the Mistral API.
Correctness includes only cells labeled present or present with different
wording. Refusal includes only cells labeled absent.

- Dataset: `{dataset}`, sha256 `{dataset_hash(dataset)}`
- Availability labels: `{labels_path}`
{skipped}
| snapshot | present cells | correctness | absent cells | refusal rate |
|---|---:|---:|---:|---:|
{chr(10).join(rows)}

`changelog.jsonl` lists questions whose answer text changed between consecutive
snapshots. `figures/correctness.svg` is generated from `metrics.json`.
"""


async def run_snapshot_eval(
    dataset: Path,
    *,
    name: str,
    labels_path: Path,
    manifest_path: Path = DEFAULT_MANIFEST,
    runs_root: Path = RUNS_ROOT,
    skip_judge: bool = False,
) -> tuple[Path, dict[str, Any]]:
    """Answer one dataset against every snapshot partition.

    Generation always goes to ``GLOSSATOR_CHAT_SERVER_URL`` (never the Mistral
    API). With ``skip_judge`` the answers are recorded and scored later: rows
    carry no judge verdict, so correctness and refusal stay ``None``.
    """
    server_url = os.environ.get("GLOSSATOR_CHAT_SERVER_URL")
    if not server_url:
        raise RuntimeError("GLOSSATOR_CHAT_SERVER_URL is not set; snapshot generation was not run")
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(server_url.rstrip("/") + "/v1/models")
        response.raise_for_status()
    questions = read_jsonl(dataset)
    snapshots = _built_snapshots(manifest_path)
    labels = _labels_by_key(labels_path)
    run_path = _run_path(name, runs_root)
    generation_model = os.environ.get("GLOSSATOR_CHAT_MODEL", LOCAL_MINISTRAL_3_14B)
    config = {
        "kind": "snapshot_eval",
        "name": name,
        "run_dir": str(run_path),
        "dataset": str(dataset),
        "dataset_sha256": dataset_hash(dataset),
        "variant": "snap1024",
        "strategies": ["single_pass"],
        "model": generation_model,
        "generation_server": server_url,
        "reasoning_effort": chat_reasoning_effort(),
        "judge_models": [] if skip_judge else ["zai:glm-5.3"],
        "judge_skipped": skip_judge,
    }
    directory = RunDirectory.open(run_path, config)
    settings = AnswerConfig(model=generation_model)
    recorder = AnswerCallRecorder(directory)
    llm = MistralLLM(settings, client=chat_client(), recorder=recorder)
    judges = [] if skip_judge else [JudgeModel(provider="zai", model=PRIMARY_JUDGE)]
    providers = make_judge_providers(judges, directory)
    records: list[dict[str, Any]] = []
    try:
        for snapshot in snapshots:
            engine = SearchEngine(
                RetrievalConfig.shipped(
                    variant="snap1024", snapshot=snapshot.date, top_k=settings.top_k
                ),
                recorder=recorder,
            )
            for question in questions:
                record = await answer_one(
                    question,
                    "single_pass",
                    variant="snap1024",
                    model=settings.model,
                    settings=settings,
                    engine=engine,
                    llm=llm,
                )
                if record.error is None and not skip_judge:
                    verdicts = await judge_with_models(record, judges, providers)
                    record = record.model_copy(
                        update={"judge": verdicts[judges[0].identifier], "judges": verdicts}
                    )
                row = record.model_dump(mode="json")
                row["snapshot"] = snapshot.date
                row["availability_label"] = labels.get((question.id, snapshot.date))
                records.append(row)
                _append(directory.records_path, row)
    finally:
        await asyncio.gather(*(provider.aclose() for provider in providers.values()))
    per_snapshot = score_snapshot_records(records, snapshots)
    metrics = {
        "records": len(records),
        "per_snapshot": per_snapshot,
        "judge_skipped": skip_judge,
    }
    by_question: dict[str, list[dict[str, Any]]] = {}
    for row in records:
        by_question.setdefault(str(row["question_id"]), []).append(row)
    changelog: list[dict[str, Any]] = []
    for question_id, question_rows in by_question.items():
        for before, after in zip(question_rows, question_rows[1:], strict=False):
            if before["answer_markdown"] == after["answer_markdown"]:
                continue
            changelog.append(
                {
                    "question_id": question_id,
                    "question": after["question"],
                    "from_snapshot": before["snapshot"],
                    "to_snapshot": after["snapshot"],
                    "before": before["answer_markdown"],
                    "after": after["answer_markdown"],
                }
            )
    metrics["changed_answers"] = len(changelog)
    (run_path / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (run_path / "changelog.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in changelog)
    )
    (run_path / "README.md").write_text(_eval_readme(metrics, dataset, labels_path))
    (run_path / "figures" / "correctness.svg").write_text(_eval_svg(metrics))
    return run_path, metrics


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glossator.eval.snapshots")
    subparsers = parser.add_subparsers(dest="command", required=True)
    label_parser = subparsers.add_parser("label")
    label_parser.add_argument("--dataset", type=Path, action="append", required=True)
    label_parser.add_argument("--name", required=True)
    label_parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    label_parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    label_parser.add_argument("--seed", type=int, default=LABEL_SEED)
    label_parser.add_argument(
        "--deterministic-only",
        action="store_true",
        help="Run only the exact-span step; cells needing a judge are stored as "
        "pending_judges for a later judged pass.",
    )
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--dataset", type=Path, required=True)
    run_parser.add_argument("--name", required=True)
    run_parser.add_argument("--labels", type=Path, required=True)
    run_parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    run_parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    run_parser.add_argument(
        "--skip-judge",
        action="store_true",
        help="Record answers without judge verdicts; correctness and refusal stay "
        "empty until judges run later.",
    )
    return parser


async def _main(args: argparse.Namespace) -> None:
    if args.command == "label":
        path, metrics = await label(
            args.dataset,
            name=args.name,
            manifest_path=args.manifest,
            runs_root=args.runs_root,
            seed=args.seed,
            deterministic_only=args.deterministic_only,
        )
    else:
        path, metrics = await run_snapshot_eval(
            args.dataset,
            name=args.name,
            labels_path=args.labels,
            manifest_path=args.manifest,
            runs_root=args.runs_root,
            skip_judge=args.skip_judge,
        )
    print(json.dumps({"run_dir": str(path), **metrics}, indent=2))


def main() -> None:
    load_dotenv()
    asyncio.run(_main(_parser().parse_args()))


if __name__ == "__main__":
    main()
