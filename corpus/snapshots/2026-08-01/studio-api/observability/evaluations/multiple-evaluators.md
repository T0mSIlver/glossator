---
url: https://docs.mistral.ai/studio-api/observability/evaluations/multiple-evaluators
title: Combine evaluators
breadcrumbs: [Studio, Observability, Offline evaluations]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/observability/evaluations/multiple-evaluators/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
hidden: true
---

# Combine evaluators

You can stack as many evaluators as you need in a single run. The SDK computes statistics (avg, min, max, std) per evaluator automatically.

## Example: multiple rule-based scorers {#example-multiple-rule-based-scorers}

```python
import asyncio
import os

from mistralai.observability import Evaluation, Evaluator, Mistral, ScorerContext, System, TaskContext

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

## Mixing rule-based and LLM judges {#mixing-rule-based-and-llm-judges}

You can freely combine rule-based and LLM-based scorers in the same run:

```python
evaluators=[
    Evaluator(name="exact_match", description="1 if output matches expected exactly.", scorer=exact_match_scorer),
    Evaluator(name="llm_quality", description="LLM judge quality score (0 to 5).", scorer=llm_judge, num_scores=3),
    Evaluator(name="response_length", description="Character count of the output.", scorer=length_scorer),
]
```

Each evaluator produces independent statistics. In Studio, you can filter and compare across all metrics.

## Independent goals per evaluator {#independent-goals-per-evaluator}

Set different pass/fail criteria on each evaluator:

```python
from mistralai.observability import Goal

evaluators=[
    Evaluator(name="exact_match", description="1 if output matches expected exactly.", scorer=exact_match_scorer, goal=Goal.gte(0.8)),
    Evaluator(name="llm_quality", description="LLM judge quality score (0 to 5).", scorer=llm_judge, goal=Goal.gte(3.5)),
    Evaluator(name="response_length", description="Character count of the output.", scorer=length_scorer, goal=Goal.lte(500)),
]
```

See [Goals](https://docs.mistral.ai/studio-api/observability/evaluations/goals) for the full guide.

## Statistics computed per evaluator {#statistics-computed-per-evaluator}

| Statistic | Description |
|-----------|-------------|
| `avg` | Mean score across all records |
| `min` | Minimum score |
| `max` | Maximum score |
| `std` | Standard deviation |
| `count` | Number of scored records |

For non-numeric scores (categorical values), the SDK computes frequency distributions and mode instead.
