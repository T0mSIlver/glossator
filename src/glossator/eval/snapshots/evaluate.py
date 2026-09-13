"""Answering, re-scoring and re-judging a dataset against every snapshot partition."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx

from glossator.answer.config import LOCAL_MINISTRAL_3_14B, AnswerConfig
from glossator.answer.llm import MistralLLM
from glossator.clients import chat_client, chat_reasoning_effort, chat_server_url
from glossator.corpus.snapshots import DEFAULT_MANIFEST
from glossator.eval.answer_eval.judge import judge_with_models, make_judge_providers
from glossator.eval.answer_eval.models import JudgeModel, QuestionRecord
from glossator.eval.answer_eval.run import answer_one
from glossator.eval.answer_eval.run_dir import AnswerCallRecorder, RunDirectory
from glossator.eval.datasets import dataset_hash, read_jsonl
from glossator.eval.snapshots.eval_report import write_snapshot_outputs
from glossator.eval.snapshots.models import PRIMARY_JUDGE
from glossator.eval.snapshots.run_files import RUNS_ROOT, append_row, built_snapshots, run_path_for
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import SearchEngine


def _labels_by_key(path: Path) -> dict[tuple[str, str], str]:
    return {
        (row["question_id"], row["snapshot"]): row["label"]
        for row in (json.loads(line) for line in path.read_text().splitlines() if line)
    }


def generation_target() -> tuple[str, str | None]:
    """The model and server snapshot generation runs on.

    ``GLOSSATOR_CHAT_MODEL`` wins when set. Otherwise a configured local server
    generates on the Ministral it serves, and the Mistral API generates on the
    shipped model, so the run works on a runner without the server too.
    """
    server = chat_server_url()
    model = os.environ.get("GLOSSATOR_CHAT_MODEL", "").strip()
    if model:
        return model, server
    if server is not None:
        return LOCAL_MINISTRAL_3_14B, server
    return AnswerConfig().model, None


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

    Generation goes to the local server when ``GLOSSATOR_CHAT_SERVER_URL`` is
    set (probed first) and to the Mistral API otherwise, on the model
    :func:`generation_target` picks. With ``skip_judge`` the answers are
    recorded and scored later: rows carry no judge verdict, so correctness and
    refusal stay ``None``.
    """
    generation_model, server_url = generation_target()
    if server_url is not None:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(server_url.rstrip("/") + "/v1/models")
            response.raise_for_status()
    questions = read_jsonl(dataset)
    snapshots = built_snapshots(manifest_path)
    labels = _labels_by_key(labels_path)
    run_path = run_path_for(name, runs_root)
    config = {
        "kind": "snapshot_eval",
        "name": name,
        "run_dir": str(run_path),
        "dataset": str(dataset),
        "dataset_sha256": dataset_hash(dataset),
        "labels": str(labels_path),
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
                append_row(directory.records_path, row)
    finally:
        await asyncio.gather(*(provider.aclose() for provider in providers.values()))
    metrics = write_snapshot_outputs(
        run_path, records, snapshots, dataset, labels_path, judge_skipped=skip_judge
    )
    return run_path, metrics


def rescore_snapshot_eval(
    run_path: Path, *, manifest_path: Path = DEFAULT_MANIFEST, labels_path: Path | None = None
) -> dict[str, Any]:
    """Re-stamp every row's availability label from the labels file named in the
    run's config and rewrite the outputs. Needed after the judged label step has
    decided cells that were still pending when the answers were recorded."""
    config = json.loads((run_path / "config.json").read_text())
    if labels_path is not None:
        config["labels"] = str(labels_path)
        (run_path / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    labels = _labels_by_key(Path(config["labels"]))
    rows = [
        json.loads(line) for line in (run_path / "records.jsonl").read_text().splitlines() if line
    ]
    for row in rows:
        row["availability_label"] = labels.get((str(row["question_id"]), row["snapshot"]))
    (run_path / "records.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )
    return write_snapshot_outputs(
        run_path,
        rows,
        built_snapshots(manifest_path),
        Path(config["dataset"]),
        Path(config["labels"]),
        judge_skipped=bool(config.get("judge_skipped")),
    )


async def rejudge_snapshot_eval(
    run_path: Path,
    judge_models: Sequence[JudgeModel],
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
) -> dict[str, Any]:
    """Judge every recorded answer that has no verdict yet, keeping the snapshot
    and availability fields of each row, and rewrite the run's outputs.

    Rows already carrying a verdict from the primary judge are left as they
    are, so an interrupted pass resumes where it stopped.
    """
    config = json.loads((run_path / "config.json").read_text())
    rows = [
        json.loads(line) for line in (run_path / "records.jsonl").read_text().splitlines() if line
    ]
    snapshots = built_snapshots(manifest_path)
    directory = RunDirectory.open(run_path, config)
    providers = make_judge_providers(judge_models, directory)
    primary = judge_models[0].identifier
    records_path = run_path / "records.jsonl"
    try:
        for start in range(0, len(rows), 4):
            batch = rows[start : start + 4]

            async def judge_row(row: dict[str, Any]) -> dict[str, Any]:
                if row.get("error") is not None or (row.get("judges") or {}).get(primary):
                    return row
                record = QuestionRecord.model_validate(row)
                verdicts = await judge_with_models(record, judge_models, providers)
                judged = record.model_copy(
                    update={"judge": verdicts[judge_models[0].identifier], "judges": verdicts}
                ).model_dump(mode="json")
                judged["snapshot"] = row["snapshot"]
                judged["availability_label"] = row.get("availability_label")
                return judged

            rows[start : start + 4] = await asyncio.gather(*(judge_row(row) for row in batch))
            records_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
            print(f"re-judged {start + len(batch)} of {len(rows)} rows", flush=True)
    finally:
        await asyncio.gather(*(provider.aclose() for provider in providers.values()))
    config["judge_models"] = [judge.identifier for judge in judge_models]
    config["judge_skipped"] = False
    (run_path / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    return write_snapshot_outputs(
        run_path,
        rows,
        snapshots,
        Path(config["dataset"]),
        Path(config.get("labels", "")),
        judge_skipped=False,
    )
