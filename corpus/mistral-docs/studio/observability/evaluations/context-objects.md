---
url: https://docs.mistral.ai/studio/observability/evaluations/context-objects
title: Use context objects
breadcrumbs: [Studio, Observability, Offline evaluations]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/evaluations/context-objects/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
hidden: true
---

# Use context objects

Tasks and scorers receive their inputs through **context objects**: typed Pydantic models that bundle all available data into a single parameter. This page is a reference for the three context types.

## TaskContext {#taskcontext}

A task function receives a `TaskContext` with the input record, system configuration, and run metadata:

```python
from mistralai.observability import TaskContext

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
from mistralai.observability import ScorerContext

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

[Run evaluators](https://docs.mistral.ai/studio/observability/evaluations/run-evaluators) receive all records and aggregated statistics after the run completes:

```python
from mistralai.observability import RunEvaluatorContext

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
