---
url: https://docs.mistral.ai/studio/observability/evaluations/local-mode
title: Iterate locally
breadcrumbs: [Studio, Observability, Offline evaluations]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/evaluations/local-mode/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
hidden: true
---

# Iterate locally

Set `local=True` to run evaluations without uploading results to Studio. This is useful for fast iteration during development.

## Usage {#usage}

```python
run = await client.evaluation.run(
    dataset=dataset,
    task=task,
    evaluators=[Evaluator(name="accuracy", scorer=scorer)],
    local=True,
)
run.show(level="records")
```

In local mode:
- No data is sent to Studio.
- You don't need to specify a `project` or `evaluation`.
- Results are only available in your terminal or as JSON.

## Recommended workflow {#recommended-workflow}

1. **Iterate locally**: set `local=True` and adjust your task and scorers until results look right.
2. **Push to Studio**: remove `local=True` and add `project` and `evaluation` to track results over time.

```python
# Step 1: iterate locally
run = await client.evaluation.run(
    dataset=dataset,
    task=task,
    evaluators=[Evaluator(name="accuracy", scorer=scorer)],
    local=True,
)

# Step 2: happy with results, push to Studio
run = await client.evaluation.run(
    project=Project(name="My Project"),
    evaluation=Evaluation(name="My Eval"),
    dataset=dataset,
    task=task,
    evaluators=[Evaluator(name="accuracy", scorer=scorer)],
)
```

## JSON export {#json-export}

Export results as JSON for further processing:

```python
run.show(mode="json", level="records")
```
