# eval/dev.jsonl

Generated development set for tuning retrieval and answer configurations. Never used for the reported held-out numbers.

- Questions: 294 (api_reference 50, capability 44, cross_page 50, post_cutoff 50, single_page 50, unanswerable 50); languages: {'en': 294}
- sha256: `89dfbd3f54b1e6c8d5b4fe0d5088fd50e1049cf9c12c1a6e281b1180f0ea65d0` since 2026-09-26, when the gold link of `dev-027` followed its page to `advanced-guides/` (D-045b); `acf3c2e1…` before, the hash every earlier run records
- Sources: eval/dev-smoke.jsonl (12), eval/dev-batch-1.jsonl (96), eval/dev-batch-2.jsonl (96), eval/dev-batch-3.jsonl (96); duplicates dropped: {'duplicate question': 6}
- Generator runs (records, calls, README each): 2026-09-08-2218-dev-smoke, 2026-09-08-2226-dev-batch-1, 2026-09-08-2233-dev-batch-2, 2026-09-08-2241-dev-batch-3
- Generator: glm-5.3-flash through the z.ai coding plan, thinking disabled, seeds 0 to 3, prompts v1 (see the run directories' config.json)
- Corpus: `corpus/mistral-docs` at the commit recorded in each run's config.json

Regenerate with `make dev-set` (one batch) or the batch commands recorded in the run READMEs, then re-run this merge.
