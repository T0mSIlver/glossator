# Answer evaluation across snapshots

Each question ran once against each dated `snap1024` partition with the shipped
reranker. Generation used the recorded local server, never the Mistral API.
Correctness includes only cells labeled present or present with different
wording. Refusal includes only cells labeled absent. The `unscored` column counts
the cells whose availability label is missing or still pending the judged step;
they score in neither column.

- Dataset: `eval/dev-fresh60.jsonl`, sha256 `c663126d79ebf3c0c8cc6000a73be2fd9281c0ae672ae4d42532f1fae8fa7fc0`
- Availability labels: `.`

| snapshot | present cells | correctness | absent cells | refusal rate | unscored |
|---|---:|---:|---:|---:|---:|
| 2026-06-01 | 41 | 0.756 | 0 | -- | 19 |
| 2026-06-15 | 43 | 0.779 | 0 | -- | 17 |
| 2026-07-01 | 48 | 0.750 | 0 | -- | 12 |
| 2026-07-15 | 49 | 0.755 | 0 | -- | 11 |
| 2026-08-01 | 49 | 0.796 | 0 | -- | 11 |
| 2026-08-15 | 53 | 0.792 | 0 | -- | 7 |
| 2026-09-01 | 54 | 0.815 | 0 | -- | 6 |
| 2026-09-07 | 55 | 0.800 | 0 | -- | 5 |

`changelog.jsonl` lists questions whose answer text changed between consecutive
snapshots. `figures/correctness.svg` is generated from `metrics.json`.
