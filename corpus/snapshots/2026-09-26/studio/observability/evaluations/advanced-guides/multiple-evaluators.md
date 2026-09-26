---
url: https://docs.mistral.ai/studio/observability/evaluations/advanced-guides/multiple-evaluators
title: Multiple evaluators
breadcrumbs: [Studio, Observability, Offline evaluations, Advanced guides]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/evaluations/advanced-guides/multiple-evaluators/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
---

# Multiple evaluators

A run can hold any number of evaluators — pass them as a list to `evaluators`. The SDK runs each one and computes its statistics independently, so every metric shows up separately in Studio.

## Multiple scorers in one run {#multiple-scorers-in-one-run}

```python
import asyncio
import os

from mistralai.evaluations import Evaluation, Evaluator, Mistral, ScorerContext, TaskContext

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

def contains_expected(ctx: ScorerContext) -> int:
    return 1 if ctx.input_record["expected"] in str(ctx.output).lower() else 0

def is_short(ctx: ScorerContext) -> int:
    return 1 if len(str(ctx.output)) < 80 else 0

def starts_capitalized(ctx: ScorerContext) -> int:
    text = str(ctx.output).strip()
    return 1 if text and text[0].isupper() else 0

async def task(ctx: TaskContext) -> str:
    response = await client.chat.complete_async(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": ctx.input_record["prompt"]}],
    )
    return str(response.choices[0].message.content)

async def main():
    run = await client.evaluation.run(
        evaluation=Evaluation(name="Multi-metric eval"),
        dataset=dataset,
        task=task,
        evaluators=[
            Evaluator(name="contains_expected", description="1 if expected substring is in the output.", scorer=contains_expected),
            Evaluator(name="is_short", description="1 if the output is under 80 characters.", scorer=is_short),
            Evaluator(name="starts_capitalized", description="1 if the output starts with an uppercase letter.", scorer=starts_capitalized),
        ],
    )
    run.show(level="run")

asyncio.run(main())
```

## Mix rule-based and LLM judges {#mixing-rule-based-and-llm-judges}

Scorers are functions, so rule-based checks and [LLM judges](https://docs.mistral.ai/studio/observability/evaluations/evaluators#llm-as-judge) live side by side in the same run:

```python
evaluators=[
    Evaluator(name="exact_match", description="1 if output matches expected exactly.", scorer=exact_match_scorer),
    Evaluator(name="llm_quality", description="LLM judge quality score (0 to 5).", scorer=llm_judge, num_scores=3),
    Evaluator(name="response_length", description="Character count of the output.", scorer=length_scorer),
]
```

## Per-evaluator goals and statistics {#per-evaluator-goals-and-statistics}

Each evaluator carries its own configuration — nothing is shared or merged across them:

- **Goals**: set an independent pass/fail gate per evaluator (for example `goal=Goal.gte(0.8)` on one, `goal=Goal.lte(500)` on another). See [Set goals](https://docs.mistral.ai/studio/observability/evaluations/goals).
- **Statistics**: each evaluator exposes its own run-level statistics, and you can declare exactly which ones. Non-numeric scores get frequency distributions and a mode instead of numeric reductions. See [Configure statistics](https://docs.mistral.ai/studio/observability/evaluations/statistics).
