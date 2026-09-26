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
| 2026-09-07 | 127 | 15 | 1 | 2 | 0.876 |
| 2026-09-26 | 125 | 16 | 1 | 3 | 0.862 |

The two judges agreed exactly on 0.9210526315789473;
quadratic-weighted kappa was 0.7723035952063915.
The figure at `figures/availability.svg` combines exact and rephrased cells as present.
