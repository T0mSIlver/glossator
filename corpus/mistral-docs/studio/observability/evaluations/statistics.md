---
url: https://docs.mistral.ai/studio/observability/evaluations/statistics
title: Configure statistics
breadcrumbs: [Studio, Observability, Offline evaluations]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/evaluations/statistics/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
---

# Configure statistics

Statistics are the run-level values an evaluator exposes from its per-record numeric scores: an average, a total, a percentile. They are what you see in the run table header, chart over time, and target with a goal.

By default an evaluator computes the historical set (`avg`, `min`, `max`, `std`, `count`). Declare `statistics` when you want a different set: a total number of failures, latency percentiles, or nothing at all.

Each declared statistic is a serializable declaration understood by the SDK, the backend, and Studio alike, so it can be recomputed after filtering or rescoring, charted, compared, and gated by a goal.

## Quick example {#quick-example}

```python
from mistralai.evaluations import Evaluator, Goal, Statistic

Evaluator(
    name="latency_ms",
    description="End-to-end response time in milliseconds.",
    scorer=latency_scorer,
    statistics=[
        Statistic.percentile(95, goal=Goal.lte(500)),
        Statistic.percentile(50),
        Statistic.percentile(75),
    ],
)
```

## The factories {#the-factories}

The `Statistic` factory declares each built-in reduction:

| Method | Meaning | Id |
|--------|---------|----|
| `Statistic.avg()` | Arithmetic mean of the numeric scores | `avg` |
| `Statistic.sum()` | Sum of the numeric scores (for example, a total number of failures) | `sum` |
| `Statistic.min()` | Smallest numeric score | `min` |
| `Statistic.max()` | Largest numeric score | `max` |
| `Statistic.std()` | Population standard deviation | `std` |
| `Statistic.count()` | Number of successful, non-null numeric scores | `count` |
| `Statistic.percentile(p)` | The `p`-th percentile, `0 <= p <= 100` | `p50`, `p95`, `p99.9`, … |

Each id is **canonical and stable**: `avg`, `sum`, `min`, `max`, `std`, `count`, and `p{p}` for percentiles (`p50`, `p95`). Ids are how a statistic is referenced across the SDK, the run payload, and the UI, so they never change once declared. A median is `Statistic.percentile(50)` — there is no separate factory for it.

There is deliberately no `rate` reduction: a rate is `avg` over 0/1 scores.

## Omission vs. an explicit list {#omission-vs-explicit}

The `statistics` field has two modes:

- **Omitted** (the default) — historical behavior is preserved. Studio detects the score type and, for numeric scores, exposes the default set `avg`, `min`, `max`, `std`, `count`.
- **An explicit list** — authoritative. Exactly these statistics are computed and exposed, in the order given, with no implicit defaults added. An empty list `statistics=[]` means the evaluator exposes **no** run-level statistics.

The **first** entry of the effective list is the evaluator's *headline* statistic: the single value shown in the run table header for compact display. It is a presentation convention, not a persisted flag.

## Examples {#examples}

### Default set (omission) {#default-set}

Omitting `statistics` keeps the default set:

```python
Evaluator(name="quality", scorer=quality_scorer)
# exposes avg, min, max, std, count — avg is the headline
```

### Total failures {#total-failures}

An evaluator whose scorer returns `0`/`1` per record, exposing only the total number of failures, gated at zero:

```python
from mistralai.evaluations import Evaluator, Goal, Statistic

Evaluator(
    name="failures",
    description="1 when the record failed, 0 otherwise.",
    scorer=failure_scorer,  # returns numeric 0 or 1
    statistics=[Statistic.sum(goal=Goal.lte(0))],
)
```

`sum` totals the 0/1 scores, and its goal fails the run if any record failed.

### Latency percentiles {#latency-percentiles}

```python
from mistralai.evaluations import Evaluator, Goal, Statistic

Evaluator(
    name="latency_ms",
    description="End-to-end response time in milliseconds.",
    scorer=latency_scorer,
    statistics=[
        Statistic.percentile(95, goal=Goal.lte(500)),
        Statistic.percentile(50),
        Statistic.percentile(75),
    ],
)
```

This exposes exactly `p50`, `p75`, and `p95` — no `avg`, `min`, `max`, `std`, or `count`. Because it is first, `p95` is the headline statistic shown in the run table header, and its `Goal.lte(500)` fails the run when the 95th percentile latency exceeds 500 ms.

## Statistic-level goals {#statistic-level-goals}

A goal attached to a statistic targets that statistic — at both the record and the run aggregation scope. This is the recommended way to gate a run and the replacement for `aggregate_goal`:

```python
# Recommended
Evaluator(
    name="accuracy",
    scorer=accuracy_scorer,
    statistics=[Statistic.avg(goal=Goal.gte(0.9))],
)

# Deprecated — prefer a statistic-level goal
Evaluator(
    name="accuracy",
    scorer=accuracy_scorer,
    aggregate_goal=Goal.gte(0.9),
)
```

A statistic-level goal never carries its own `metric`: the target is the statistic it is attached to. (Only the deprecated `aggregate_goal` path uses `metric` to name a statistic.)

## Scores must be numeric 0/1, not booleans {#scores-must-be-numeric}

Statistics are numeric reductions. An evaluator that gates on pass/fail must emit numeric `0` or `1`, **not** `True`/`False`. Booleans are classified as *categorical* values, so a boolean-returning scorer produces categorical statistics (frequencies and mode) and none of the numeric reductions above apply.

```python
def failure_scorer(ctx) -> int:
    return 1 if failed(ctx) else 0   # numeric — correct

def failure_scorer(ctx) -> bool:
    return failed(ctx)               # boolean — categorical, no sum/percentile
```

## The percentile algorithm {#percentile-algorithm}

`Statistic.percentile(p)` uses the Hyndman-Fan **type-7** algorithm (NumPy's default). For sorted scores `x` of length `n` and rank `h = (n - 1) * p / 100`, the result linearly interpolates between `x[floor(h)]` and `x[ceil(h)]`; a single score returns that score. The identical algorithm runs in the Python SDK, the TypeScript SDK, and the backend, so the same scores always produce the same value.

## Empty samples {#empty-samples}

When no successful numeric scores fed the computation, a declared `count` is `0` and every other declared statistic is `null` (unevaluable). An empty dataset therefore never accidentally satisfies a goal like `Statistic.sum(goal=Goal.lte(0))`.
