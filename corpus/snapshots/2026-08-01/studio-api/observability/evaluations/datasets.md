---
url: https://docs.mistral.ai/studio-api/observability/evaluations/datasets
title: Datasets
breadcrumbs: [Studio, Observability, Offline evaluations]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/observability/evaluations/datasets/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
hidden: true
---

# Datasets

A dataset is the set of test cases that drives an offline evaluation. In the [Evaluation SDK](https://docs.mistral.ai/studio-api/observability/evaluations#installation), a dataset is a **list of Python dicts** where each dict is an input record, and you define the keys to match what your task function expects.

## Record structure {#record-structure}

Each record is a plain dict. The keys are up to you:

```python
dataset = [
    {"sentence": "Hello, how are you?", "groundtruth": "English"},
    {"sentence": "Bonjour, comment ça va?", "groundtruth": "French"},
    {"sentence": "Hola, ¿cómo estás?", "groundtruth": "Spanish"},
]
```

In your task and scorer, access the record via `ctx.input_record`:

```python
from mistralai.observability import TaskContext, ScorerContext

async def task(ctx: TaskContext) -> str:
    return ctx.input_record["sentence"]  # access any key you defined

def scorer(ctx: ScorerContext) -> int:
    return 1 if ctx.input_record["groundtruth"].lower() == str(ctx.output).lower() else 0
```

## Type safety with TypedDict {#type-safety}

Use `TypedDict` to make record schemas explicit and get IDE autocompletion:

```python
from typing import TypedDict

class LanguageRecord(TypedDict):
    sentence: str
    groundtruth: str

dataset: list[LanguageRecord] = [
    {"sentence": "Hello, how are you?", "groundtruth": "English"},
    {"sentence": "Bonjour, comment ça va?", "groundtruth": "French"},
]
```

## What to include in records {#what-to-include}

Records can contain anything your task or scorer needs:

| Field type | Purpose | Example |
|------------|---------|---------|
| Task inputs | What the task processes | `prompt`, `context`, `text`, `question` |
| Ground truth | Reference output for scoring | `expected`, `groundtruth`, `reference_answer` |
| Metadata | Extra context for scorers or LLM judges | `category`, `difficulty`, `grading_guidance` |

Include ground truth in records when you want to compare the task output against a known-good answer:

```python
dataset = [
    {
        "prompt": "What is the capital of France?",
        "expected": "Paris",
        "difficulty": "easy",
    },
    {
        "prompt": "Explain the difference between precision and recall.",
        "expected": "Precision measures true positives over predicted positives; recall measures true positives over actual positives.",
        "difficulty": "medium",
    },
]

def accuracy_scorer(ctx: ScorerContext) -> int:
    return 1 if ctx.input_record["expected"].lower() in str(ctx.output).lower() else 0
```

## Best practices {#best-practices}

### Keep datasets focused

A dataset built around a single task or capability produces clearer signals than a broad, mixed-topic collection. Maintain separate datasets for distinct evaluation goals (for example, `language_detection`, `qa_factual`, `code_generation`).

### Curate for representativeness

- Include edge cases and failure modes, not easy examples alone.
- Balance your dataset: if 90% of records are easy cases, the evaluation won't reveal real problems.
- Remove records where even a human couldn't reliably score the response (ambiguous inputs add noise).

### Version your datasets

Freeze your dataset between runs if you want to track performance over time. Even small changes to records can make runs incomparable. Use meaningful names like `qa_baseline_2025_06` rather than `test_data`.

### Ground truth quality matters

Inaccurate or ambiguous ground truth produces noisy scores. If you use an LLM judge (see [Judges](https://docs.mistral.ai/studio-api/observability/evaluations/judges)), include a `grading_guidance` field to give the judge explicit scoring instructions per record.

## Organizing in Studio {#organizing-in-studio}

The Evaluation SDK organizes results using **Projects**, **Evaluations**, and **Runs** in Studio, not by the dataset itself. Pass your dataset directly to `evaluation.run()`:

```python
from mistralai.observability import Evaluation, Project

run = await client.evaluation.run(
    project=Project(name="Language Detection"),
    evaluation=Evaluation(name="Accuracy Eval"),
    dataset=dataset,  # your list of dicts
    task=task,
    evaluators=[...],
)
```

Tags and metadata on the run help you trace back which dataset version was used:

```python
run = await client.evaluation.run(
    ...
    tags=["dataset:qa_baseline_2025_06", "model:mistral-small"],
    metadata={"dataset_version": "2025-06", "record_count": len(dataset)},
)
```

## FAQ {#faq}

### How large can my dataset be? {#how-large-can-my-dataset-be}

There is no hard limit enforced by the SDK. In practice, keep datasets small enough to run during iteration. Use `local=True` to test on a subset before a full run.

### Can I load records from a file? {#can-i-load-records-from-a-file}

Yes. Load any file format (JSONL, CSV, and other formats) into a list of dicts before passing to `evaluation.run()`. The SDK only requires a Python list.

### My scores are noisy. Is it the dataset or the scorer? {#my-scores-are-noisy-is-it-the-dataset-or-the-scorer}

Start with the dataset. Inspect low-scoring records: are the inputs ambiguous? Is the ground truth accurate? Fix the dataset first, then tune the scorer or judge instructions.
