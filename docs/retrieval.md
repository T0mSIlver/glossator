# Search and index variants

| Variant | Vespa schema | Chunking | Embedding model |
|---|---|---|---|
| `page128` | `docs_page_lowdim` | whole-page chunks | `mistral-embed-dim128-2510` |
| `sec128` | `docs_section_lowdim` | heading sections | `mistral-embed-dim128-2510` |
| `sec1024` | `docs_section_fulldim` | heading sections | `mistral-embed` |

```bash
make search query="Which models support function calling?" variant=sec1024 top_k=10
uv run python -m glossator.retrieval "How do I stream?" --rerank
uv run python -m glossator.retrieval "What causes feline hyperthyroidism?" --footing
```

The embedding probe checks five fixed semantic pairs and one stored-vector round
trip before ingestion and serving. Retrieval can also apply an absolute cosine
floor, a margin below the best hit, and a lexical-footing check. The floors stay
off until a run on the full corpus supports them.

Vespa blocks feeds when disk usage exceeds 80% by default. Ingestion tests a
small write before processing the corpus and aborts without replacing any page
if Vespa rejects it. A package redeploy restores Vespa's default resource limit,
including when the running deployment had a hand-patched limit.

# Retrieval evaluation

The retrieval grid compares index variants, ranking weights, and the listwise
reranker. It reports page-level and section-level metrics separately because
many documentation headings have no live anchor.

```bash
make eval-retrieval dataset=eval/dev.jsonl name=dev
make eval-retrieval dataset=eval/dev.jsonl name=quick \
  configs=sec1024-shipped limit=20
make calibrate-floors dataset=eval/dev.jsonl name=dev
```

Each run writes `config.json`, `records.jsonl`, `calls.jsonl`, `metrics.json`, a
README, and figures under `eval/runs/<date>-<name>/`. Rebuild its report with:

```bash
make eval-report run=eval/runs/2026-09-08-2329-fixture-grid
```

The definitive grid, `../eval/runs/2026-09-09-0136-dev-grid-v2/`, ran 294
development questions through 13 configurations at a depth of 20 hits, collapsed
to distinct pages or sections before scoring (`DECISIONS.md` D-034). Section-level
numbers cover the 142 questions whose gold names an anchor.

| Configuration | Page recall@1 | Page recall@5 | Page MRR | Section recall@1 | Section recall@5 | Section MRR | Median latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| `page128-shipped` (starter chunking) | 0.62 | 0.90 | 0.82 | 0 | 0 | 0 | 12 ms |
| `sec128-shipped` | 0.62 | 0.87 | 0.79 | 0.75 | 0.92 | 0.81 | 7 ms |
| `sec1024-shipped` | 0.59 | 0.86 | 0.77 | 0.70 | 0.88 | 0.78 | 11 ms |
| `sec1024-vector-heavy` | 0.60 | 0.86 | 0.77 | 0.73 | 0.94 | 0.81 | 9 ms |
| `sec1024-lexical-heavy` | 0.58 | 0.86 | 0.77 | 0.66 | 0.87 | 0.75 | 9 ms |
| `sec1024-shipped+rerank` | 0.70 | 0.90 | 0.87 | 0.82 | 0.92 | 0.86 | 4.4 s |
| **`sec1024-vector-heavy+rerank`** (shipped) | **0.71** | **0.92** | **0.88** | **0.87** | **0.98** | **0.92** | 4.4 s |

Whole-page chunks cannot deep-link, and the reranker is the largest single gain
(API-reference questions go from 0.64 to 0.90 at rank 1). The similarity-floor
calibration (`../eval/runs/2026-09-09-0115-dev-floors/`) found a corridor too
narrow to use and no separation for unanswerable questions, so floors stay off
(D-030b).

| Run | Scope | Result |
|---|---|---|
| `../eval/runs/2026-09-09-0136-dev-grid-v2/` | 294 questions, 13 configurations | Chose section chunks, vector-heavy weights, reranker on. |
| `../eval/runs/2026-09-09-0115-dev-floors/` | similarity calibration over 294 real, 15 junk, 50 unanswerable questions | Corridor 0.017 wide; floors stay off. |
| `../eval/runs/2026-09-08-2305-dev60-baseline/`, `2026-09-09-0232-dev60-anchors/`, `2026-09-09-0312-dev60-rerank/` | 60 questions, answer strategies | See `evaluation.md`. |
| `eval/runs/<held-out-run>/` | held-out questions | Pending. |

Dataset generation and judging use GLM through the z.ai API. Serving uses only
Mistral models. Every run names its models and prompt hashes.
