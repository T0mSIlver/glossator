# Answer evaluation across snapshots

Each question ran once against each dated `snap1024` partition with the shipped
reranker. Generation used the recorded local server, never the Mistral API.
Correctness includes only cells labeled present or present with different
wording. Refusal includes only cells labeled absent. The `unscored` column counts
the cells whose availability label is missing or still pending the judged step;
they score in neither column.

- Dataset: `eval/dev-fresh60.jsonl`, sha256 `c663126d79ebf3c0c8cc6000a73be2fd9281c0ae672ae4d42532f1fae8fa7fc0`
- Availability labels: `eval/runs/2026-09-26-1036-refresh-labels-2026-09-26/labels.jsonl`

| snapshot | present cells | correctness | absent cells | refusal rate | unscored |
|---|---:|---:|---:|---:|---:|
| 2026-09-07 | 59 | 0.847 | 1 | 1.000 | 0 |
| 2026-09-26 | 58 | 0.862 | 2 | 1.000 | 0 |

`changelog.jsonl` lists questions whose answer text changed between consecutive
snapshots. `figures/correctness.svg` is generated from `metrics.json`.
