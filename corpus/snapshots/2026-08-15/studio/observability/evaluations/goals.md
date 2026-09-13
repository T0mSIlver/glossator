---
url: https://docs.mistral.ai/studio/observability/evaluations/goals
title: Set goals
breadcrumbs: [Studio, Observability, Offline evaluations]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/evaluations/goals/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
hidden: true
---

# Set goals

Goals let you define pass/fail criteria on evaluator scores. When a goal is set, the SDK displays `PASS` or `FAIL` verdicts in the terminal output alongside each score.

## Goal types {#goal-types}

| Method | Meaning |
|--------|---------|
| `Goal.gte(0.8)` | Score must be `>= 0.8` |
| `Goal.lte(0.1)` | Score must be `<= 0.1` |
| `Goal.between(0.2, 0.8)` | Score must be in `[0.2, 0.8]` |
| `Goal.higher_is_better()` | Direction hint only, no threshold |
| `Goal.lower_is_better()` | Direction hint only, no threshold |

Direction-only goals (`higher_is_better`, `lower_is_better`) don't produce `PASS`/`FAIL` verdicts. They're metadata for comparison views in Studio.

All goal methods accept an optional `metric` parameter (`"avg"`, `"min"`, `"max"`, `"std"`) to target a specific statistic instead of the default average.

## Basic usage {#basic-usage}

```python
from mistralai.observability import Evaluator, Goal

Evaluator(
    name="accuracy",
    description="1 if the expected answer appears in the output.",
    scorer=accuracy_scorer,
    goal=Goal.gte(0.8),
)
```

## Per-generation and aggregate goals {#per-generation-and-aggregate-goals}

Evaluators support two goal levels:

- `goal`: evaluated against each individual generation score.
- `aggregate_goal`: evaluated against the aggregated result across all generations.

```python
Evaluator(
    name="accuracy",
    description="1 if the expected answer appears in the output.",
    scorer=accuracy_scorer,
    goal=Goal.gte(0.7),           # each generation must score >= 0.7
    aggregate_goal=Goal.gte(0.9), # overall average must be >= 0.9
)
```

When you call `run.show()`:
- **Run level**: shows whether the aggregate passes the `aggregate_goal` (falls back to `goal` on the average if no aggregate is set).
- **Record level** (with `num_generations > 1`): shows how many generations passed the `goal` (for example, "2/3 PASS"), with aggregate verdict when applicable.
- **Generation level**: shows `PASS`/`FAIL` for each individual score against `goal`.

## Goals on run evaluators {#goals-on-run-evaluators}

[Run evaluators](https://docs.mistral.ai/studio/observability/evaluations/run-evaluators) also support goals:

```python
from mistralai.observability import RunEvaluator, Goal

RunEvaluator(
    name="f1",
    description="Harmonic mean of precision and recall across all records.",
    scorer=f1_scorer,
    goal=Goal.gte(0.85),
)
```

## Full example {#full-example}

```python
import asyncio
import os

from mistralai.observability import (
    Evaluation, Evaluator, Goal, Mistral, Project,
    RunEvaluator, RunEvaluatorContext, ScorerContext, System, TaskContext,
)

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

dataset = [
    {"prompt": "What is 2+2?", "expected": "4"},
    {"prompt": "Capital of France?", "expected": "Paris"},
    {"prompt": "Largest planet?", "expected": "Jupiter"},
]

async def task(ctx: TaskContext) -> str:
    r = await client.chat.complete_async(
        model=str(ctx.system.params["model"]),
        messages=[{"role": "user", "content": ctx.input_record["prompt"]}],
    )
    return str(r.choices[0].message.content)

def accuracy_scorer(ctx: ScorerContext) -> int:
    return 1 if ctx.input_record["expected"].lower() in str(ctx.output).lower() else 0

def accuracy_gate(ctx: RunEvaluatorContext):
    return ctx.statistics["accuracy"].avg

async def main():
    run = await client.evaluation.run(
        project=Project(name="QA Pipeline"),
        evaluation=Evaluation(name="Accuracy with Goals"),
        system=System(name="mistral-small", params={"model": "mistral-small-latest"}),
        dataset=dataset,
        task=task,
        evaluators=[
            Evaluator(
                name="accuracy",
                description="1 if the expected answer appears in the output.",
                scorer=accuracy_scorer,
                goal=Goal.gte(0.8),
                aggregate_goal=Goal.gte(0.9),
            ),
        ],
        run_evaluators=[
            RunEvaluator(
                name="accuracy_avg",
                description="Average accuracy across all records.",
                scorer=accuracy_gate,
                goal=Goal.gte(0.85),
            ),
        ],
        num_generations=3,
    )
    run.show(level="generations")

asyncio.run(main())
```

### What happens if I set both goal and aggregate_goal? {#what-happens-if-i-set-both-goal-and-aggregategoal}

Both are evaluated independently. `goal` checks each generation's score. `aggregate_goal` checks the aggregated statistic (default: average) across all generations and records. Either can fail independently.

### Can I target a metric other than the average? {#can-i-target-a-metric-other-than-the-average}

Yes. Pass a `metric` parameter: `Goal.gte(0.8, metric="min")` requires the minimum score to be at least 0.8.
