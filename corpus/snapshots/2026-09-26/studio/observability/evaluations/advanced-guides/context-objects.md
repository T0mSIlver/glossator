---
url: https://docs.mistral.ai/studio/observability/evaluations/advanced-guides/context-objects
title: Use context objects
breadcrumbs: [Studio, Observability, Offline evaluations, Advanced guides]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/evaluations/advanced-guides/context-objects/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
---

# Use context objects

Tasks, scorers, and metadata callbacks receive their inputs through **context objects**: typed Pydantic models that bundle all available data into a single parameter. This page is a reference for each context type.

## TaskContext {#taskcontext}

A task function receives a `TaskContext` with the input record, system configuration, and run metadata:

```python
from mistralai.evaluations import TaskContext

async def task(ctx: TaskContext) -> str:
    response = await client.chat.complete_async(
        model=str(ctx.system.params["model"]),
        messages=[{"role": "user", "content": ctx.input_record["prompt"]}],
    )
    return str(response.choices[0].message.content)
```

| Field | Type | Description |
|-------|------|-------------|
| `input_record` | `dict[str, Any]` | The current dataset record |
| `system` | `System \| None` | System config from `evaluation.run(system=...)` |
| `metadata` | `dict[str, Any] \| None` | Run metadata from `evaluation.run(metadata=...)` |

## ScorerContext {#scorercontext}

A scorer function receives a `ScorerContext` with the input record and the task output:

```python
from mistralai.evaluations import ScorerContext

def accuracy_scorer(ctx: ScorerContext) -> int:
    return 1 if ctx.input_record["expected"].lower() in str(ctx.output).lower() else 0
```

| Field | Type | Description |
|-------|------|-------------|
| `input_record` | `dict[str, Any]` | The current dataset record |
| `output` | `Any` | The task output for this generation |
| `system` | `System \| None` | System config from `evaluation.run(system=...)` |
| `metadata` | `dict[str, Any] \| None` | Run metadata from `evaluation.run(metadata=...)` |

## RunEvaluatorContext {#runevaluatorcontext}

[Run evaluators](https://docs.mistral.ai/studio/observability/evaluations/advanced-guides/run-evaluators) receive all records and aggregated statistics after the run completes:

```python
from mistralai.evaluations import RunEvaluatorContext

def accuracy_gate(ctx: RunEvaluatorContext):
    return ctx.statistics["accuracy"].avg >= 0.8
```

| Field | Type | Description |
|-------|------|-------------|
| `records` | `list[RunEvaluatorRecord]` | All processed records with their scores |
| `statistics` | `dict[str, EvaluatorStatistics]` | Per-evaluator aggregate statistics |
| `metadata` | `dict[str, JsonValue]` | Run metadata |
| `system` | `System \| None` | System config from `evaluation.run(system=...)` |

Use `get_score(record, "evaluator_name")` to access a specific evaluator's score for a given record.

## RecordMetadataContext {#recordmetadatacontext}

A `record_metadata` callback receives a `RecordMetadataContext` once a record's task and scorers have finished. Its returned dict is stored on the record's metadata in Studio:

```python
from mistralai.evaluations import RecordMetadataContext

def record_metadata(ctx: RecordMetadataContext) -> dict:
    return {"output_len": len(str(ctx.record.generations[0].output))}
```

| Field | Type | Description |
|-------|------|-------------|
| `input_record` | `dict[str, Any]` | The current dataset record |
| `record` | `EvaluationRunRecord` | The processed record, including its generations and scores |
| `system` | `System \| None` | System config from `evaluation.run(system=...)` |
| `metadata` | `dict[str, JsonValue]` | Run metadata |

## RunMetadataContext {#runmetadatacontext}

A `metadata` callback (when passed a function instead of a dict) receives a `RunMetadataContext` after all records are scored. Its returned dict is merged into the run metadata:

```python
from mistralai.evaluations import RunMetadataContext

def run_metadata(ctx: RunMetadataContext) -> dict:
    return {"num_records": len(ctx.records)}
```

| Field | Type | Description |
|-------|------|-------------|
| `records` | `list[RunEvaluatorRecord]` | All processed records with their scores |
| `statistics` | `dict[str, EvaluatorStatistics]` | Per-evaluator aggregate statistics |
| `run_scores` | `dict[str, Score]` | Run-level evaluator scores |
| `metadata` | `dict[str, JsonValue]` | Run metadata |
| `system` | `System \| None` | System config from `evaluation.run(system=...)` |
