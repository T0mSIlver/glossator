---
url: https://docs.mistral.ai/studio/observability/evaluations/advanced-guides/retry-failed-records
title: Retry failed records
breadcrumbs: [Studio, Observability, Offline evaluations, Advanced guides]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/evaluations/advanced-guides/retry-failed-records/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
---

# Retry failed records

Evaluations can fail partially: a transient API error, a rate limit, or a bug in your scorer. Instead of rerunning the entire evaluation from scratch, the SDK lets you retry only the failed records and patch the results in place.

## Why it matters {#why-it-matters}

A typical evaluation run can involve hundreds or thousands of LLM calls. If 5 out of 500 records fail, rerunning everything wastes time and money. `retry_failed_records()` identifies which records failed (at the generation or scoring level), reruns only those, and patches the original run so your results stay in one place in Studio.

## Basic workflow {#basic-workflow}

```python
import asyncio
import os

from mistralai.evaluations import (
    Evaluation, Evaluator, Mistral, ScorerContext, System, TaskContext,
)

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

dataset = [
    {"prompt": "Say hello", "expected": "hello"},
    {"prompt": "Say goodbye", "expected": "goodbye"},
]

async def task(ctx: TaskContext):
    response = await client.chat.complete_async(
        model=str(ctx.system.params["model"]),
        messages=[{"role": "user", "content": ctx.input_record["prompt"]}],
    )
    return str(response.choices[0].message.content)

def scorer(ctx: ScorerContext):
    return 1 if ctx.input_record["expected"] in str(ctx.output).lower() else 0

async def main():
    system = System(name="mistral-small", params={"model": "mistral-small-latest"})

    # Step 1: run the evaluation
    run = await client.evaluation.run(
        evaluation=Evaluation(name="My Eval"),
        system=system,
        dataset=dataset,
        task=task,
        evaluators=[Evaluator(name="accuracy", scorer=scorer)],
    )

    # Step 2: if some records failed, retry them
    result = await client.evaluation.retry_failed_records(
        run_id=run.run_id,
        dataset=dataset,
        task=task,
        evaluators=[Evaluator(name="accuracy", scorer=scorer)],
        system=system,
    )
    print(f"Retried: {result.retried_count}, Patched: {result.patched_count}")

asyncio.run(main())
```

## Fixing the task before retrying {#fixing-the-task-before-retrying}

You don't have to retry with the same task. If failures were caused by a bug in your code, fix it and pass the corrected version:

```python
# Fix the task, retry only the failed records
async def fixed_task(ctx: TaskContext):
    response = await client.chat.complete_async(
        model=str(ctx.system.params["model"]),
        messages=[{"role": "user", "content": ctx.input_record["prompt"]}],
    )
    return str(response.choices[0].message.content)

result = await client.evaluation.retry_failed_records(
    run_id=run.run_id,
    dataset=dataset,
    task=fixed_task,
    evaluators=[Evaluator(name="accuracy", scorer=scorer)],
    system=system,
)
```

## What happens {#what-happens}

1. The SDK fetches the existing run and identifies records with status `"error"` (failed generation or scoring).
2. Only those records are re-processed with the provided task and evaluators.
3. Successful results are patched into the original run.
4. If the original run had `run_evaluators`, their scores are recomputed with the updated data.

The original run in Studio is updated in place. No duplicate runs, no manual cleanup.

## API reference {#api-reference}

`client.evaluation.retry_failed_records(...)` takes the following parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `run_id` | `str` | **Required.** ID of the run containing failed records. |
| `dataset` | `Sequence[Mapping[str, Any]]` | **Required.** Same dataset used in the original run. |
| `task` | `TaskFunction` | **Required.** Task function (can be a corrected version). |
| `evaluators` | `list[Evaluator]` | **Required.** Evaluators to re-score with. |
| `run_evaluators` | `list[RunEvaluator]` | Run-level evaluators to recompute after patching. |
| `num_generations` | `int` | Number of generations per record (default: `1`). |
| `system` | `System` | System params to inject into the task. |
| `max_concurrency` | `int` | Maximum concurrent tasks (default: `10`). |
| `upload_batch_size` | `int` | Batch size for uploading patched results (default: `10`). |

It returns a `RetryFailedRecordsResult`:

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | `str` | ID of the run that was retried. |
| `retried_count` | `int` | Number of records that were retried. |
| `patched_count` | `int` | Number of records successfully patched. |
| `run_scores_recomputed` | `bool` | Whether run-level scores were recomputed. |
