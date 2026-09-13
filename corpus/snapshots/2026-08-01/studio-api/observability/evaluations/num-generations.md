---
url: https://docs.mistral.ai/studio-api/observability/evaluations/num-generations
title: Reduce variance with multiple generations
breadcrumbs: [Studio, Observability, Offline evaluations]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/observability/evaluations/num-generations/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
hidden: true
---

# Reduce variance with multiple generations

When your task is non-deterministic (for example, `temperature > 0`), a single generation per input may not give you a reliable picture. Set `num_generations=N` to run the task N times per record. The SDK aggregates per-record mean and standard deviation automatically.

## Usage {#usage}

```python
import asyncio
import os

from mistralai.observability import (
    Evaluation, Evaluator, Goal, Mistral, ScorerContext, System, TaskContext,
)

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

dataset = [
    {"prompt": "What is the capital of France?", "expected": "Paris"},
    {"prompt": "What is 2+2?", "expected": "4"},
]

async def task(ctx: TaskContext) -> str:
    response = await client.chat.complete_async(
        model=str(ctx.system.params["model"]),
        temperature=float(ctx.system.params["temperature"]),
        messages=[{"role": "user", "content": ctx.input_record["prompt"]}],
    )
    return str(response.choices[0].message.content)

def scorer(ctx: ScorerContext) -> int:
    return 1 if ctx.input_record["expected"].lower() in str(ctx.output).lower() else 0

async def main():
    run = await client.evaluation.run(
        evaluation=Evaluation(name="Variance check"),
        dataset=dataset,
        task=task,
        system=System(
            name="small-t09",
            params={"model": "mistral-small-latest", "temperature": 0.9},
        ),
        evaluators=[
            Evaluator(
                name="accuracy",
                description="1 if expected answer is in the output.",
                scorer=scorer,
                goal=Goal.gte(0.5),
            )
        ],
        num_generations=3,
    )
    run.show(level="generations")

asyncio.run(main())
```

## How it works {#how-it-works}

With `num_generations=3`, the SDK:

1. Runs the task 3 times per input record.
2. Scores each generation independently.
3. Computes per-record statistics (mean, std) across the 3 generations.
4. Computes overall run statistics across all records.

Use `run.show(level="generations")` to see the per-generation breakdown.

## When to use it {#when-to-use-it}

- **Comparing temperatures**: run the same prompt at different temperatures to measure stability.
- **Noisy tasks**: tasks that produce meaningfully different outputs on each call.
- **Confidence intervals**: get a sense of how reliable your scores are before drawing conclusions.

## Example: comparing temperatures {#example-comparing-temperatures}

```python
import asyncio
import os

from mistralai.observability import Evaluation, Evaluator, Goal, Mistral, System, ScorerContext, TaskContext

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

async def task(ctx: TaskContext) -> str:
    response = await client.chat.complete_async(
        model=str(ctx.system.params["model"]),
        temperature=float(ctx.system.params["temperature"]),
        messages=[{"role": "user", "content": ctx.input_record["prompt"]}],
    )
    return str(response.choices[0].message.content)

def scorer(ctx: ScorerContext) -> int:
    return 1 if ctx.input_record["expected"].lower() in str(ctx.output).lower() else 0

async def main():
    for temp in [0.0, 0.3, 0.7, 1.0]:
        run = await client.evaluation.run(
            evaluation=Evaluation(name="Temperature Impact"),
            dataset=dataset,
            task=task,
            system=System(
                name=f"small-t{temp}",
                params={"model": "mistral-small-latest", "temperature": temp},
            ),
            evaluators=[Evaluator(name="accuracy", description="1 if expected answer is in the output.", scorer=scorer, goal=Goal.gte(0.5))],
            num_generations=5,
            tags=[f"temperature:{temp}"],
        )

asyncio.run(main())
```

In Studio, each run has its `System` recorded. You can compare score distributions across temperatures at a glance. See [System params](https://docs.mistral.ai/studio-api/observability/evaluations/system-params) for details.
