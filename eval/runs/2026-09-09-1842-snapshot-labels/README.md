# Snapshot availability labels

A cell is `present` when a verified supporting quote occurs in that snapshot. A
match on another page is marked as moved. If no quote matches, GLM 5.3 and GLM
5.3 Flash compare the reference answer with the five highest-scoring lexical
pages. The primary judge assigns `present_rephrased`, `changed`, or `absent`.
Cells still waiting for that judged step are `unknown` (shown grey): a later run
without `--deterministic-only` judges exactly those cells and never re-decides
the rest.

Correctness can only be scored on present cells because an answer cannot be
correct when its fact is missing or has a different dated value. Absent cells
instead measure whether the answer refuses to invent a current-looking answer.

## Datasets

- `eval/dev-fresh60.jsonl`: `c663126d79ebf3c0c8cc6000a73be2fd9281c0ae672ae4d42532f1fae8fa7fc0`
- `eval/mined.jsonl`: `a276e09f853024f2647dad9d7f7c4c8c34e1754dafdf6a6dc4fbb994dfd5b2a2`

## Counts

| snapshot | present | rephrased | changed | absent | deterministic share |
|---|---:|---:|---:|---:|---:|
| 2026-06-01 | 108 | 0 | 0 | 0 | 0.745 |
| 2026-06-15 | 112 | 0 | 0 | 0 | 0.772 |
| 2026-07-01 | 119 | 0 | 0 | 0 | 0.821 |
| 2026-07-15 | 121 | 0 | 0 | 0 | 0.834 |
| 2026-08-01 | 121 | 0 | 0 | 0 | 0.834 |
| 2026-08-15 | 126 | 0 | 0 | 0 | 0.869 |
| 2026-09-01 | 130 | 0 | 0 | 0 | 0.897 |
| 2026-09-07 | 135 | 0 | 0 | 0 | 0.931 |

The two judges agreed exactly on no judged cells;
quadratic-weighted kappa was not defined.
The figure at `figures/availability.svg` combines exact and rephrased cells as present.
