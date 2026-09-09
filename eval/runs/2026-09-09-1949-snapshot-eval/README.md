# Answer evaluation across snapshots

Each question ran once against each dated `snap1024` partition with the shipped
reranker. Generation used the recorded local server, never the Mistral API.
Correctness includes only cells labeled present or present with different
wording. Refusal includes only cells labeled absent.

- Dataset: `eval/dev-fresh60.jsonl`, sha256 `c663126d79ebf3c0c8cc6000a73be2fd9281c0ae672ae4d42532f1fae8fa7fc0`
- Availability labels: `eval/runs/2026-09-09-1929-snapshot-labels/labels.jsonl`

Judges were skipped for this run (`--skip-judge`): correctness and refusal are empty until a judged pass fills them in.

| snapshot | present cells | correctness | absent cells | refusal rate |
|---|---:|---:|---:|---:|
| 2026-06-01 | 41 | -- | 0 | -- |
| 2026-06-15 | 43 | -- | 0 | -- |
| 2026-07-01 | 48 | -- | 0 | -- |
| 2026-07-15 | 49 | -- | 0 | -- |
| 2026-08-01 | 49 | -- | 0 | -- |
| 2026-08-15 | 53 | -- | 0 | -- |
| 2026-09-01 | 54 | -- | 0 | -- |
| 2026-09-07 | 55 | -- | 0 | -- |

`changelog.jsonl` lists questions whose answer text changed between consecutive
snapshots. `figures/correctness.svg` is generated from `metrics.json`.
