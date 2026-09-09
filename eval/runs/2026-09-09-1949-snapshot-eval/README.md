# Answer evaluation across snapshots

Each question ran once against each dated `snap1024` partition with the shipped
reranker. Generation used the recorded local server, never the Mistral API.
Correctness includes only cells labeled present or present with different
wording. Refusal includes only cells labeled absent. The `unscored` column counts
the cells whose availability label is missing or still pending the judged step;
they score in neither column.

- Dataset: `eval/dev-fresh60.jsonl`, sha256 `c663126d79ebf3c0c8cc6000a73be2fd9281c0ae672ae4d42532f1fae8fa7fc0`
- Availability labels: `eval/runs/2026-09-09-1929-snapshot-labels/labels.jsonl`

| snapshot | present cells | correctness | absent cells | refusal rate | unscored |
|---|---:|---:|---:|---:|---:|
| 2026-06-01 | 48 | 0.760 | 12 | 0.583 | 0 |
| 2026-06-15 | 49 | 0.796 | 10 | 0.600 | 1 |
| 2026-07-01 | 52 | 0.760 | 7 | 0.714 | 1 |
| 2026-07-15 | 54 | 0.778 | 5 | 0.800 | 1 |
| 2026-08-01 | 54 | 0.806 | 5 | 0.600 | 1 |
| 2026-08-15 | 55 | 0.800 | 5 | 0.600 | 0 |
| 2026-09-01 | 56 | 0.821 | 4 | 0.500 | 0 |
| 2026-09-07 | 57 | 0.807 | 3 | 0.333 | 0 |

`changelog.jsonl` lists questions whose answer text changed between consecutive
snapshots. `figures/correctness.svg` is generated from `metrics.json`.
