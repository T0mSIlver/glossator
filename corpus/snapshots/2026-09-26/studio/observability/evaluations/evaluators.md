---
url: https://docs.mistral.ai/studio/observability/evaluations/evaluators
title: Evaluators
breadcrumbs: [Studio, Observability, Offline evaluations]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/evaluations/evaluators/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
---

# Evaluators

An evaluator scores each record of a run. It pairs a name with a **scorer** — a function that receives a [`ScorerContext`](https://docs.mistral.ai/studio/observability/evaluations/advanced-guides/context-objects) and returns a score — plus an optional description and [goal](https://docs.mistral.ai/studio/observability/evaluations/goals).

```python
from mistralai.evaluations import Evaluator, Goal

Evaluator(
    name="accuracy",
    description="1 if the expected answer appears in the output.",
    scorer=accuracy_scorer,
    goal=Goal.gte(0.8),
)
```

A scorer can be one of two kinds:

- **Rule-based** — a plain function that computes a score from the output. Deterministic, fast, and free.
- **LLM-as-judge** — a function that calls a model to grade the output. Use it for criteria that are hard to express in code, such as helpfulness, factual accuracy, or tone.

Both are just functions, so a single run can hold any mix of them. See [Multiple evaluators](https://docs.mistral.ai/studio/observability/evaluations/advanced-guides/multiple-evaluators) to run several at once.

## Rule-based scorers {#rule-based-scorers}

A rule-based scorer returns a number (or a `str`/`bool` for categorical scores) computed directly from the record and output:

```python
from mistralai.evaluations import ScorerContext

def contains_expected(ctx: ScorerContext) -> int:
    return 1 if ctx.input_record["expected"].lower() in str(ctx.output).lower() else 0
```

Numeric scores produce numeric statistics (avg, min, max, std, count); `str`/`bool` scores produce frequency distributions and a mode. See [Configure statistics](https://docs.mistral.ai/studio/observability/evaluations/statistics).

## LLM-as-judge scorers {#llm-as-judge}

To use a model as a judge, call the Mistral API inside your scorer and return a numeric score:

```python
from mistralai.evaluations import ScorerContext

JUDGE_PROMPT = """You are a strict grader. Given a user prompt and a model answer,
respond with a single integer between 0 and 5 (higher is better) measuring how helpful and on-topic
the answer is. Respond with only the integer, no other text.

User prompt: {prompt}
Model answer: {answer}
"""

def llm_judge(ctx: ScorerContext) -> int:
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "user",
                "content": JUDGE_PROMPT.format(
                    prompt=ctx.input_record["prompt"], answer=ctx.output
                ),
            }
        ],
        temperature=0,
    )
    raw = str(response.choices[0].message.content).strip()
    try:
        return int(raw[0])
    except (ValueError, IndexError):
        return 0
```

Use it in an evaluator like any other scorer:

```python
from mistralai.evaluations import Evaluator, Goal

Evaluator(
    name="helpfulness",
    description="LLM judge: helpfulness score from 0 to 5.",
    scorer=llm_judge,
    goal=Goal.gte(3.5),
)
```

## Structured output with Score {#structured-output}

For richer feedback, return a `Score` object with a value and a rationale. The rationale is stored alongside the score in Studio:

```python
from pydantic import BaseModel
from mistralai.evaluations import ScorerContext, Score

class RecallJudgment(BaseModel):
    score: float
    comment: str

async def recall_scorer(ctx: ScorerContext) -> Score:
    completion = await client.chat.parse_async(
        model="mistral-large-latest",
        messages=[
            {
                "role": "user",
                "content": (
                    f"Evaluate recall between 0.0 and 1.0.\n\n"
                    f"Expected: {ctx.input_record['expected']}\n"
                    f"Got: {ctx.output}\n\n"
                    f"Provide a score and a short comment."
                ),
            }
        ],
        response_format=RecallJudgment,
    )
    judgment = completion.choices[0].message.parsed
    return Score(value=judgment.score, rationale=judgment.comment)
```

## Reduce judge variance {#reducing-variance}

LLM judges can be noisy. Set `num_scores` on the evaluator to score each generation multiple times and average the results:

```python
Evaluator(
    name="recall",
    description="LLM judge: recall score (0.0 to 1.0).",
    scorer=recall_scorer,
    num_scores=3,  # scored 3 times per generation, results are averaged
)
```

## Write good judge instructions {#writing-judge-instructions}

Craft your judge prompts with care:

- **Be specific.** Avoid vague criteria: describe exactly what a good response looks like for your use case.
- **Don't assume** the judge knows your context. Spell out what "good" means explicitly.
- **Use boundary examples**: *"A score of 3 means the response partially answers the question but omits a key detail."*
- **Keep temperature low** (for example, `temperature=0`) for more deterministic judgments.
- **Test on a small sample** before using a judge in a large evaluation run. Spot inconsistencies early.

## FAQ {#faq}

### How do I choose between a rule-based scorer and an LLM judge? {#how-do-i-choose-between-a-rule-based-scorer-and-an-llm-judge}

Use rule-based scoring whenever possible: it's deterministic, fast, and cheap. Use an LLM judge when the quality criterion can't be captured with code, such as tone, coherence, or nuanced factual accuracy.

### My judge gives inconsistent scores on similar inputs {#my-judge-gives-inconsistent-scores-on-similar-inputs}

The prompt is probably too vague. Add explicit criteria and concrete boundary examples. Try a stronger model. Run the same input multiple times and set `num_scores` to average out noise.

### The judge returns parsing errors or out-of-range values {#the-judge-returns-parsing-errors-or-out-of-range-values}

Use structured output (`response_format`) with a Pydantic model to force valid output. Add a try/except around the parsing logic to return a fallback score rather than crashing.

### Can I reuse the same evaluator across runs? {#can-i-reuse-the-same-evaluator-across-runs}

Yes. An evaluator is a function paired with a name. Reuse it across any number of runs. If you change a judge prompt between runs, scores won't be directly comparable.
