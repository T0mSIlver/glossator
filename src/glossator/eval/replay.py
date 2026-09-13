"""Replay recorded generation prompts on another model, off the pipeline.

Every answer evaluation writes the request it sent to the generator, verbatim,
into `calls.jsonl` (D-023). Those requests are the whole generation step: the
assembled context is in the user message and nothing else reached the model. So
the generator can be swapped without Vespa, embeddings or a reranker in the loop:
export the prompts, run them anywhere an OpenAI-compatible endpoint answers, and
bring the completions back. Retrieval and context are then byte-identical
between the two generators, and any difference is the generator's alone, which
is the column the failure analysis says to move (D-042).

`export` writes one line per question: the messages, sampling and schema as
they were sent, plus the ids that let `import` pair each completion with the
record it replays. Only the first attempt of each question is exported; later
attempts in the ledger are transport retries with the same messages.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import structlog
from mistralai.search.toolkit.common.text import sanitize_text
from mistralai.search.toolkit.document import compute_char_locator, compute_id

from glossator.answer.citations import (
    Citation,
    Trace,
    TraceEvent,
    fabricated,
    resolve,
    strip_markers,
    unmatched,
)
from glossator.answer.config import ModelPrice, price_of
from glossator.answer.context import AssembledContext, Source, SourcePiece, _merged
from glossator.answer.generation import GeneratedAnswer
from glossator.answer.llm import TokenUsage as AnswerTokenUsage
from glossator.answer.llm import _parse
from glossator.eval.answer_eval.judge import source_texts
from glossator.eval.answer_eval.models import QuestionRecord, parse_judge_models
from glossator.eval.answer_eval.rejudge import rejudge
from glossator.eval.answer_eval.run_dir import RunDirectory, read_records
from glossator.eval.run_records import create_run_directory
from glossator.index.variants import VARIANTS, ChunkStrategy
from glossator.ingest.chunker import PageFacts, build_chunker
from glossator.ingest.pages import iter_page_paths, load_page
from glossator.retrieval.engine import Hit

logger = structlog.get_logger(__name__)

PURPOSE = "single_pass:grounded_answer"


def _calls(run_dir: Path) -> Iterator[dict[str, Any]]:
    with (run_dir / "calls.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def _records(run_dir: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    with (run_dir / "records.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("strategy") == "single_pass":
                out[row["question_id"]] = row
    return out


def export_prompts(
    run_dirs: list[Path],
    output: Path,
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """Write the first grounded-answer request of every single-pass question.

    `temperature` and `max_tokens` override the recorded sampling on every row,
    for runs that were generated under a local model's own settings (D-038b):
    the shipped sampling is what a comparison with the API runs needs, and the
    row keeps the recorded values under `source_temperature` and
    `source_max_tokens`.
    """
    schema = GeneratedAnswer.model_json_schema()
    rows: list[dict[str, Any]] = []
    per_run: dict[str, int] = {}
    for run_dir in run_dirs:
        records = _records(run_dir)
        seen: set[str] = set()
        for call in _calls(run_dir):
            if call.get("purpose") != PURPOSE or call["question_id"] in seen:
                continue
            seen.add(call["question_id"])
            record = records.get(call["question_id"], {})
            rows.append(
                {
                    "id": f"{run_dir.name}/{call['question_id']}",
                    "run": run_dir.name,
                    "question_id": call["question_id"],
                    "question_type": record.get("question_type"),
                    "source_call_id": call["call_id"],
                    "source_model": call["model"],
                    "messages": call["messages"],
                    "temperature": call["temperature"] if temperature is None else temperature,
                    "max_tokens": call["max_tokens"] if max_tokens is None else max_tokens,
                    "source_temperature": call["temperature"],
                    "source_max_tokens": call["max_tokens"],
                    "response_schema": "GeneratedAnswer",
                    "json_schema": schema,
                }
            )
        per_run[run_dir.name] = len(seen)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return {"prompts": len(rows), "per_run": per_run, "sha256": digest, "path": str(output)}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    exp = sub.add_parser("export", help="write the recorded generation prompts of one or more runs")
    exp.add_argument("run_dirs", nargs="+", type=Path)
    exp.add_argument("--output", type=Path, required=True)
    exp.add_argument(
        "--temperature", type=float, default=None, help="override the recorded sampling"
    )
    exp.add_argument(
        "--max-tokens", type=int, default=None, help="override the recorded completion cap"
    )
    imp = sub.add_parser("import", help="score replayed completions as new run directories")
    imp.add_argument("results", type=Path)
    imp.add_argument("--prompts", type=Path, required=True)
    imp.add_argument("--name", required=True, help="run name prefix, e.g. medium35-replay")
    imp.add_argument("--model", required=True, help="the model id the completions came from")
    imp.add_argument("--corpus", type=Path, default=Path("corpus/mistral-docs"))
    imp.add_argument("--runs-root", type=Path, default=Path("eval/runs"))
    imp.add_argument(
        "--judge-models", default=None, help="provider:model list; omit to import unjudged"
    )
    imp.add_argument("--note", action="append", default=[], dest="notes")
    chk = sub.add_parser("check", help="prove the rebuilt sources reproduce a run's own verdicts")
    chk.add_argument("run_dirs", nargs="+", type=Path)
    chk.add_argument("--corpus", type=Path, default=Path("corpus/mistral-docs"))
    args = parser.parse_args(argv)
    if args.command == "export":
        summary = export_prompts(
            args.run_dirs, args.output, temperature=args.temperature, max_tokens=args.max_tokens
        )
        print(json.dumps(summary, indent=2))
    elif args.command == "check":
        for run_dir in args.run_dirs:
            print(json.dumps(check_rebuild(run_dir, corpus_dir=args.corpus), indent=2))
    elif args.command == "import":
        written = import_results(
            args.results,
            args.prompts,
            name=args.name,
            model=args.model,
            corpus_dir=args.corpus,
            runs_root=args.runs_root,
            notes=args.notes,
        )
        for run_path in written:
            print(run_path)
        if args.judge_models:
            judges = parse_judge_models(args.judge_models)
            for run_path in written:
                asyncio.run(rejudge(run_path, judge_models=judges))
                print(f"judged {run_path}")


# --------------------------------------------------------------------------- #
# Rebuilding the sources a record's model saw
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class _ChunkText:
    url: str
    anchor: str | None
    page_title: str
    heading_path: tuple[str, ...]
    content: str
    start: int
    end: int


@cache
def _chunk_texts(corpus_dir: Path, chunking: ChunkStrategy) -> Mapping[str, _ChunkText]:
    """Every chunk one chunking of the corpus produces, with its stored content.

    Same walk as `glossator.eval.failures.corpus.chunk_index`, keeping the text: the
    verifier needs each merged source's chunk boundaries to name the chunk a
    quote came from, and the run's trace stores chunk ids, not offsets.
    """
    chunker = build_chunker(chunking)
    texts: dict[str, _ChunkText] = {}
    for path in iter_page_paths(corpus_dir):
        page = load_page(path)
        body = sanitize_text(page.body)
        page_facts = PageFacts(url=page.url, title=page.title, kind=page.kind, locale=page.locale)
        for spec in chunker.plan(body, page_facts):
            chunk_id = compute_id(page.url, compute_char_locator(spec.start, spec.end))
            texts[chunk_id] = _ChunkText(
                url=page.url,
                anchor=spec.metadata.anchor,
                page_title=page.title,
                heading_path=tuple(spec.metadata.heading_path),
                content=spec.content,
                start=spec.start,
                end=spec.end,
            )
    return texts


def _split_url(citation_url: str) -> tuple[str, str | None]:
    url, _, anchor = citation_url.partition("#")
    return url, anchor or None


def rebuild_context(
    trace: Trace, *, corpus_dir: Path, chunking: ChunkStrategy
) -> tuple[AssembledContext, list[str]]:
    """The `AssembledContext` behind a recorded trace, and the notes of what
    could not be rebuilt exactly.

    The passage text comes from the recorded context, verbatim. The chunk
    boundaries inside a merged passage come from re-chunking the vendored
    corpus and stitching the source's chunks the way assembly did; when the
    stitched text is not the recorded passage, the source keeps one piece for
    its first chunk and the note says so.
    """
    passages = source_texts(trace)
    texts = _chunk_texts(corpus_dir, chunking)
    notes: list[str] = []
    sources: list[Source] = []
    for traced in trace.sources:
        passage = passages.get(traced.n)
        if passage is None:
            notes.append(f"source {traced.n}: passage not found in the recorded context")
            continue
        _heading, _, content = passage.partition("\n")
        url, anchor = _split_url(traced.citation_url)
        hits = [_hit(chunk_id, texts) for chunk_id in traced.chunk_ids]
        pieces: tuple[SourcePiece, ...] | None = None
        page_title = ""
        if all(hit is not None for hit in hits):
            stitched, stitched_pieces = _merged([hit for hit in hits if hit is not None])
            page_title = next(hit.page_title for hit in hits if hit is not None)
            # `source_texts` right-strips each passage; the stitched text keeps
            # the trailing newlines assembly wrote, so it is the exact content.
            if stitched.rstrip() == content.rstrip():
                content = stitched
                pieces = stitched_pieces
            else:
                notes.append(f"source {traced.n}: stitched chunks differ from the recorded passage")
        else:
            notes.append(f"source {traced.n}: a chunk id is not in the corpus chunking")
        if pieces is None:
            pieces = (
                SourcePiece(
                    chunk_id=traced.chunk_ids[0] if traced.chunk_ids else "",
                    score=traced.score,
                    start_offset=None,
                    end_offset=None,
                    text_start=0,
                    text_end=len(content),
                ),
            )
        sources.append(
            Source(
                n=traced.n,
                url=url,
                anchor=anchor,
                page_title=page_title,
                heading_path=tuple(traced.heading_path),
                source_id=url,
                content=content,
                pieces=pieces,
                score=traced.score,
                tokens=traced.tokens,
            )
        )
    return (
        AssembledContext(
            text=trace.context_text,
            sources=tuple(sources),
            tokens=trace.context_tokens,
            dropped_chunk_ids=tuple(trace.dropped_chunk_ids),
        ),
        notes,
    )


def _hit(chunk_id: str, texts: Mapping[str, _ChunkText]) -> Hit | None:
    chunk = texts.get(chunk_id)
    if chunk is None:
        return None
    return Hit(
        chunk_id=chunk_id,
        score=0.0,
        url=chunk.url,
        anchor=chunk.anchor,
        heading_path=chunk.heading_path,
        page_title=chunk.page_title,
        kind="",
        locale="",
        section_index=None,
        content=chunk.content,
        source_id=chunk.url,
        start_offset=chunk.start,
        end_offset=chunk.end,
    )


# --------------------------------------------------------------------------- #
# Turning a replayed completion into a record
# --------------------------------------------------------------------------- #


def _single_pass_records(run_dir: Path) -> dict[str, QuestionRecord]:
    return {
        record.question_id: record
        for record in read_records(run_dir / "records.jsonl")
        if record.strategy == "single_pass"
    }


def replay_record(
    source: QuestionRecord,
    result: Mapping[str, Any],
    *,
    model: str,
    corpus_dir: Path,
    chunking: ChunkStrategy,
    min_quote_chars: int,
    prices: Mapping[str, ModelPrice] | None = None,
) -> tuple[QuestionRecord, list[str]]:
    """The source record with its answer replaced by the replayed completion.

    Mirrors `AnswerRun.finish` and `_answer`: parse, verify, strip the markers
    nothing verified, and keep the rejected citations in the trace. The
    retrieval trace, sources and context are the source record's, untouched.
    """
    if source.trace is None:
        raise ValueError(f"{source.question_id}: the source record has no trace")
    context, notes = rebuild_context(source.trace, corpus_dir=corpus_dir, chunking=chunking)
    usage_row = result.get("usage") or {}
    usage = AnswerTokenUsage(
        prompt_tokens=int(usage_row.get("prompt_tokens") or 0),
        completion_tokens=int(usage_row.get("completion_tokens") or 0),
    )
    cost = price_of(model, usage.prompt_tokens, usage.completion_tokens, prices) or 0.0
    events = list(source.trace.events)
    step = max((event.step for event in events), default=0) + 1
    if result.get("error"):
        events.append(
            TraceEvent(
                step=step, kind="generation", name="replay_error", note=result["error"][:500]
            )
        )
        record = source.model_copy(
            update={
                "model": model,
                "answer_markdown": "",
                "citations": [],
                "unverified_citations": [],
                "insufficient_evidence": True,
                "trace": source.trace.model_copy(
                    update={"events": events, "unverified_citations": [], "unmatched_markers": []}
                ),
                "usage": usage,
                "latency_ms": float(result.get("latency_ms") or 0.0),
                "cost_usd": cost,
                "cost_usd_v1": None,
                "error": str(result["error"]),
                "judge": None,
                "judges": {},
                "judges_v1": {},
            }
        )
        return record, notes

    parsed, parse_error = _parse(str(result.get("text") or ""), GeneratedAnswer)
    if parsed is None:
        events.append(TraceEvent(step=step, kind="generation", name="unparsed", note=parse_error))
        markdown = str(result.get("text") or "")
        verified: list[Citation] = []
        rejected: list[Citation] = []
        insufficient = True
    else:
        generated = GeneratedAnswer.model_validate(parsed)
        events.append(TraceEvent(step=step, kind="generation", name="replayed", note=model))
        verified, rejected = resolve(
            [(citation.n, citation.quote) for citation in generated.citations],
            context,
            min_quote_chars=min_quote_chars,
        )
        markdown = generated.answer_markdown
        insufficient = generated.insufficient_evidence or not verified

    unmatched_markers = unmatched(markdown, verified + rejected)
    verified_numbers = {citation.n for citation in verified}
    rejected_fabricated = {
        citation.n for citation in fabricated(rejected) if citation.n not in verified_numbers
    }
    rendered = strip_markers(markdown, set(unmatched_markers) | rejected_fabricated)
    trace = source.trace.model_copy(
        update={
            "events": events,
            "unverified_citations": rejected,
            "unmatched_markers": unmatched_markers,
        }
    )
    record = source.model_copy(
        update={
            "model": model,
            "answer_markdown": rendered,
            "citations": verified,
            "unverified_citations": rejected,
            "insufficient_evidence": insufficient,
            "trace": trace,
            "usage": usage,
            "latency_ms": float(result.get("latency_ms") or 0.0),
            "cost_usd": cost,
            "cost_usd_v1": None,
            "error": None,
            "judge": None,
            "judges": {},
            "judges_v1": {},
        }
    )
    return record, notes


def _call_row(
    result: Mapping[str, Any], prompt: Mapping[str, Any], record: QuestionRecord
) -> dict[str, Any]:
    """One `calls.jsonl` line in the answer layer's shape (D-023)."""
    parsed, _ = _parse(str(result.get("text") or ""), GeneratedAnswer)
    return {
        "call_id": f"replay:{result['id']}",
        "purpose": PURPOSE,
        "question_id": record.question_id,
        "strategy": record.strategy,
        "started_at": result.get("started_at"),
        "model": result.get("model"),
        "temperature": result.get("temperature"),
        "max_tokens": result.get("max_tokens"),
        "attempt": result.get("attempt"),
        "messages": prompt["messages"],
        "response_schema": "GeneratedAnswer",
        "response_format": result.get("response_format"),
        "response": result.get("response"),
        "text": result.get("text") or "",
        "parsed": parsed,
        "finish_reason": result.get("finish_reason"),
        "usage": {
            "prompt_tokens": record.usage.prompt_tokens,
            "completion_tokens": record.usage.completion_tokens,
        },
        "latency_ms": record.latency_ms,
        "cost_usd": record.cost_usd,
        "error": result.get("error"),
        "source_call_id": result.get("source_call_id"),
    }


def import_results(
    results_path: Path,
    prompts_path: Path,
    *,
    name: str,
    model: str,
    corpus_dir: Path,
    runs_root: Path,
    notes: Sequence[str] = (),
) -> list[Path]:
    """One run directory per source run, holding the replayed answers unjudged."""
    prompts = {row["id"]: row for row in _jsonl(prompts_path)}
    results = _jsonl(results_path)
    by_run: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        by_run.setdefault(result["run"], []).append(result)
    results_sha = hashlib.sha256(results_path.read_bytes()).hexdigest()
    written: list[Path] = []
    for source_name, rows in by_run.items():
        source_dir = runs_root / source_name
        source_config = json.loads((source_dir / "config.json").read_text())
        variant = str(source_config.get("variant", "sec1024"))
        chunking = VARIANTS[variant].chunking
        min_quote_chars = int(source_config.get("answer_config", {}).get("min_quote_chars", 8))
        records = _single_pass_records(source_dir)
        config = {
            **{k: v for k, v in source_config.items() if k not in ("resumed_records", "notes")},
            "kind": "answer_eval",
            "name": f"{name}-{_short_name(source_name)}",
            "model": model,
            "replay": {
                "source_run": source_name,
                "source_model": source_config.get("model"),
                "results": str(results_path),
                "results_sha256": results_sha,
                "prompts": str(prompts_path),
                "response_format": sorted({str(r.get("response_format")) for r in rows}),
                "endpoint_model": sorted({str(r.get("model")) for r in rows}),
            },
            "strategies": ["single_pass"],
            "judge_models": [],
            "judge_model": None,
            "notes": [
                f"Generation replayed on {model} from the recorded prompts of "
                f"`{source_name}`; retrieval, reranking and context are that run's, unchanged.",
                *notes,
            ],
        }
        config["answer_config"] = {**source_config.get("answer_config", {}), "model": model}
        run_path = create_run_directory(config["name"], root=runs_root)
        run_dir = RunDirectory.open(run_path, config)
        rebuild_notes: list[str] = []
        skipped: list[str] = []
        for result in sorted(rows, key=lambda r: r["question_id"]):
            source = records.get(result["question_id"])
            if source is None or source.trace is None:
                # The prompt was exported from the call ledger, but the source
                # run's record for it ended in an error and holds no trace, so
                # there is nothing to verify the replayed quotes against.
                logger.warning(
                    "No source record with a trace", run=source_name, question=result["question_id"]
                )
                skipped.append(result["question_id"])
                continue
            record, notes_for = replay_record(
                source,
                result,
                model=model,
                corpus_dir=corpus_dir,
                chunking=chunking,
                min_quote_chars=min_quote_chars,
                prices=_price_table(source_config),
            )
            rebuild_notes.extend(f"{result['question_id']}: {note}" for note in notes_for)
            run_dir.append_call("replay", _call_row(result, prompts[result["id"]], record))
            run_dir.record(record)
        if skipped:
            run_dir.config["notes"].append(
                f"{len(skipped)} replayed answer(s) not scored because the source record "
                f"ended in an error and has no trace: {', '.join(skipped)}."
            )
            run_dir.config["replay"]["skipped_no_trace"] = skipped
            (run_path / "config.json").write_text(
                json.dumps(run_dir.config, indent=2, sort_keys=True) + "\n"
            )
        (run_path / "rebuild-notes.txt").write_text(
            "\n".join(rebuild_notes) + ("\n" if rebuild_notes else "")
        )
        run_dir.finalize(status="unjudged", error=None)
        logger.info(
            "Imported replay",
            run=str(run_path),
            answers=len(run_dir.records),
            rebuild_notes=len(rebuild_notes),
        )
        written.append(run_path)
    return written


def _price_table(config: Mapping[str, Any]) -> dict[str, ModelPrice] | None:
    prices = config.get("answer_config", {}).get("prices")
    if not prices:
        return None
    return {model: ModelPrice.model_validate(price) for model, price in prices.items()}


def _short_name(run_name: str) -> str:
    # `2026-09-09-0312-dev60-rerank` -> `dev60-rerank`
    return re.sub(r"^\d{4}-\d{2}-\d{2}-\d{4}-", "", run_name)


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


# --------------------------------------------------------------------------- #
# Self-check: the rebuilt sources must reproduce the original verdicts
# --------------------------------------------------------------------------- #


def check_rebuild(run_dir: Path, *, corpus_dir: Path) -> dict[str, Any]:
    """Re-verify the source run's own citations against the rebuilt sources.

    For each single-pass answer the model's raw `(n, quote)` pairs are read from
    the call ledger and pushed through `resolve` on the rebuilt context; the
    verdicts and chunk ids must equal the record's. A mismatch means the rebuild
    is not what the run saw, and a replay scored on it would not be comparable.
    """
    config = json.loads((run_dir / "config.json").read_text())
    chunking = VARIANTS[str(config.get("variant", "sec1024"))].chunking
    min_quote_chars = int(config.get("answer_config", {}).get("min_quote_chars", 8))
    records = _single_pass_records(run_dir)
    raw: dict[str, list[tuple[int, str]]] = {}
    for call in _calls(run_dir):
        if call.get("purpose") == PURPOSE and call.get("parsed") and call["question_id"] not in raw:
            raw[call["question_id"]] = [
                (int(citation["n"]), str(citation["quote"]))
                for citation in call["parsed"].get("citations", [])
            ]
    compared = matched = 0
    mismatches: list[dict[str, Any]] = []
    notes = 0
    for question_id, record in records.items():
        if record.trace is None or question_id not in raw:
            continue
        context, rebuild_notes = rebuild_context(
            record.trace, corpus_dir=corpus_dir, chunking=chunking
        )
        notes += len(rebuild_notes)
        verified, rejected = resolve(raw[question_id], context, min_quote_chars=min_quote_chars)
        got = sorted((c.n, c.verified, c.chunk_id, c.url, c.anchor) for c in verified + rejected)
        want = sorted(
            (c.n, c.verified, c.chunk_id, c.url, c.anchor)
            for c in record.citations + record.unverified_citations
        )
        compared += 1
        if got == want:
            matched += 1
        else:
            mismatches.append({"question_id": question_id, "got": got, "want": want})
    return {
        "run": run_dir.name,
        "compared": compared,
        "matched": matched,
        "rebuild_notes": notes,
        "mismatches": mismatches[:10],
    }


if __name__ == "__main__":
    main()
