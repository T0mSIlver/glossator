# glossator

glossator answers technical questions over [docs.mistral.ai](https://docs.mistral.ai)
with cited sources. It returns Markdown with `[n]` markers and checks each cited
quote against the retrieved chunk before returning it. FastAPI and MCP use the
same retrieval and answer code.

## Architecture in ten lines

1. The repository vendors 411 normalized documentation pages at a pinned source commit.
2. The corpus adapter converts the documentation MDX, OpenAPI file, and model data to Markdown.
3. Ingestion splits pages at headings with a 600-token target and a 1,024-token cap.
4. Mistral embeddings map each chunk to either 128 or 1,024 dimensions.
5. Vespa stores one schema for each index variant.
6. Vespa combines BM25 and vector features in a two-phase ranking profile.
7. Search hits carry a URL, anchor, heading path, page offsets, and an opaque chunk ID.
8. The answer layer gathers context, generates structured output, and verifies quoted citations.
9. FastAPI and MCP share lazily constructed `SearchEngine` instances.
10. Evaluation records every query, model call, hit, score, citation, cost, and latency.

## Five-minute start

```bash
make installdeps
# Add MISTRAL_API_KEY=... to .env.
make setup-vespa
make ingest corpus=corpus/mistral-docs variant=sec1024
make ask question="How do I stream a chat completion?" model=ministral-14b-2512
make api
make mcp
```

The API listens on `127.0.0.1:8080`. The MCP HTTP transport listens on
`127.0.0.1:8000/mcp`. Override either address with `host=` and `port=`. The MCP
stdio transport is configured in `.mcp.json` and `.vibe/config.toml`.

`.env` holds secrets, ports, and service endpoints only. Recognized settings are
`MISTRAL_API_KEY`, `VESPA_QUERY_PORT`, `VESPA_CONFIG_PORT`, `VESPA_ENDPOINT`,
`VESPA_CONFIG_URL`, and `WORKSPACE_ROOT` (used by the Bruno API export). The
API server also reads `GLOSSATOR_CORPUS_DIR`, and the MCP server reads
`GLOSSATOR_VARIANT`, `GLOSSATOR_MODEL`, and `GLOSSATOR_CORPUS_DIR`. Do not put
schema names in `.env`.

Vespa blocks feeds when disk usage exceeds 80% by default. Ingestion tests a small
write before processing the corpus and aborts without replacing any page if Vespa
rejects it. A package redeploy restores Vespa's default resource limit, including
when the running deployment had a hand-patched limit.

Mistral Medium 3.5 is the shipped generation default. The current free-tier key
has a zero request quota for that model, so recorded checks and evaluations use
`ministral-14b-2512`.

## HTTP API

Run `make api`, then open `/docs` for Swagger UI or `/openapi.json` for the
schema.

| Route | Input | Output |
|---|---|---|
| `POST /ask` | `question`; optional `strategy`, `variant`, `model` | answer Markdown, verified citations, trace, usage, cost, latency |
| `POST /search` | `query`; optional `top_k`, `kinds`, `locales`, `exclude_ids`, `variant` | ranked hits with citation URL, heading path, preview, score, ID, and offsets |
| `GET /pages/{path}` | documentation path; optional `variant`, `start_offset`, `top_k` | up to 100 page sections in reading order; `truncated` says whether more exist |
| `GET /health` | none | Vespa counts, corpus commit, and embedding-probe status |
| `GET /version` | none | package version, variants, and allowed generation models |

Every error uses `{"error":{"code","message","next"}}`. Unknown field names are
rejected with a suggestion for the right one. Clients can send `X-Request-Id`;
the API echoes it in the response header, the `/ask` body, and error bodies.
When the header is absent, the API creates an ID. When `GET /pages` answers
`truncated: true`, continue from the last returned section's `end_offset`:

```bash
curl -s "http://127.0.0.1:8080/pages/api/endpoint/chat?start_offset=2480&top_k=100"
```

```bash
curl -s http://127.0.0.1:8080/search \
  -H 'content-type: application/json' \
  -d '{"query":"streaming chat completions","top_k":3}'

curl -s http://127.0.0.1:8080/ask \
  -H 'content-type: application/json' \
  -d '{"question":"How do I stream a chat completion?","model":"ministral-14b-2512"}'
```

## MCP server

`make mcp` starts the streamable HTTP transport. Run the module without
`--http` for stdio:

```bash
uv run python -m entrypoints.mcp_server
```

| Tool | Purpose |
|---|---|
| `search(query, top_k=5, kinds, locales, exclude_ids)` | Find citable sections by meaning or keywords. |
| `open(chunk_id, window=2)` | Read a hit with nearby chunks in page order. |
| `navigate(source_id, start_offset, end_offset, direction, top_k=1)` | Step forward or backward through a page. |
| `read(source_id, start_offset, end_offset, top_k=20)` | Read a known page range without ranking it again. |
| `grep(source_id, pattern, mode="phrase", top_k=5)` | Match a phrase or terms inside one page. |
| `ask(question, strategy="single_pass")` | Generate an answer and print only verified citations as links. |

Every tool response ends with `next:`. The server announces clamps, rejects
unknown parameters with `E_BAD_PARAM`, and prints a citation URL on each hit.
The MCP tools clamp out-of-range values to their published ranges (a `note:`
line names the move, and `glossator://context` publishes the ranges), while the
HTTP API validates and rejects out-of-range values with `E_BAD_PARAM` and
documents them in `/openapi.json`. It exposes exactly three resources:

- `glossator://guide` contains the tool flow and shared rules.
- `glossator://index` lists every page as URL, title, and kind.
- `glossator://context` reports limits, ID formats, corpus commit, counts, and model IDs.

The MCP server cannot ingest or delete content. Corpus changes go through the
adapter, manifest checks, and ingestion command.

## Search and index variants

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

## Answer evaluation

The answer evaluator runs each question through the selected strategies. Code
checks source matches, quote verification, refusal behavior, usage, latency, and
cost. A blinded model judge scores correctness, groundedness, and citation
relevance.

```bash
make eval-answers dataset=eval/dev.jsonl name=answers-dev
make eval-answers dataset=tests/fixtures/answer-questions.jsonl \
  name=answers-fixture strategies=single_pass variant=sec128 limit=4
```

Three runs over the same 60 stratified development questions decided the
shipped strategy (`DECISIONS.md` D-033, D-033a, D-035). Answers were generated by
`ministral-14b-2512` and judged blind by `glm-5.3`; Mistral Medium 3.5 is the
shipped generator, and the same run directories re-run on it in one command once
the account's quota for it opens.

| Run | Retrieval | Strategy | Correctness | Groundedness | Correct refusal | Gold URL cited | Gold anchor cited | Median latency | Prompt tokens | USD per question at Medium 3.5 prices |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `dev60-baseline` | migration weights, no reranker | `single_pass` | 0.81 | 0.75 | 0.82 | 0.70 | 0.50 | 3.0 s | 1.9k | 0.005 |
| `dev60-baseline` | migration weights, no reranker | `search_loop` | 0.93 | 0.81 | 0.88 | 0.78 | 0.40 | 7.4 s | 16.0k | 0.028 |
| `dev60-baseline` | migration weights, no reranker | `outline` | 0.65 | 0.65 | 0.72 | 0.42 | 0.18 | 3.7 s | 8.9k | 0.016 |
| `dev60-anchors` | same, after the anchor fallback | `single_pass` | 0.83 | 0.79 | 0.87 | 0.76 | 0.58 | 3.0 s | 2.0k | 0.005 |
| `dev60-rerank` | **shipped**: vector-heavy weights, reranker on | **`single_pass`** | **0.93** | 0.82 | **0.92** | 0.82 | **0.62** | 7.2 s | 2.0k | 0.005 |
| `dev60-rerank` | shipped | `search_loop` | 0.95 | 0.85 | 0.90 | 0.82 | 0.54 | 20.7 s | 14.8k | 0.026 |

Reranked single-pass retrieval closed most of the gap to the search loop, which
remains available as the thorough mode of `ask`.

Questions in another language are rendered in English for retrieval and answered
in their own language (`DECISIONS.md` D-008b). On 36 French questions
(`eval/dev-fr.jsonl`) over the English corpus this took cited-URL match from 0.47
to 0.80 and correctness from 0.75 to 0.94, against 0.82 and 0.93 for the same
questions in English; the runs are `eval/runs/*-devfr-shipped/` and
`eval/runs/*-devfr-translated/`.

Generated questions are well worded by construction, so they say little about
badly worded ones. `eval/dev-noisy.jsonl` is the same 120 development questions
degraded into typos, bare keywords, vague wording, a wrong product term, or a
request buried in a user's context, with the gold sources and reference answers
unchanged. Noise costs the shipped single pass 19 points of correctness (0.87 to
0.68 on the same questions) and the search loop 16 (0.90 to 0.74), so the loop's
lead widens from 3 points to 6 at three times the latency and seven times the
prompt tokens. Rewording the question into the documentation's vocabulary before
retrieval (`AnswerConfig.rewrite_for_retrieval`, off by default, `--rewrite` on
the CLI and the answer eval) recovers 4 of the 19 points for a quarter of a
second and 275 prompt tokens, and costs 5 points on clean questions. The runs are
`eval/runs/*-noisy-*/` and `eval/runs/*-clean-*/`.

## Retrieval evaluation

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

The definitive grid, `eval/runs/2026-09-09-0136-dev-grid-v2/`, ran 294
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
calibration (`eval/runs/2026-09-09-0115-dev-floors/`) found a corridor too narrow
to use and no separation for unanswerable questions, so floors stay off (D-030b).

| Run | Scope | Result |
|---|---|---|
| `eval/runs/2026-09-09-0136-dev-grid-v2/` | 294 questions, 13 configurations | Chose section chunks, vector-heavy weights, reranker on. |
| `eval/runs/2026-09-09-0115-dev-floors/` | similarity calibration over 294 real, 15 junk, 50 unanswerable questions | Corridor 0.017 wide; floors stay off. |
| `eval/runs/2026-09-08-2305-dev60-baseline/`, `*-dev60-anchors/`, `*-dev60-rerank/` | 60 questions, answer strategies | See the answer evaluation above. |
| `eval/runs/<held-out-run>/` | held-out questions | Pending. |

Dataset generation and judging use GLM through the z.ai API. Serving uses only
Mistral models. Every run names its models and prompt hashes.

## Corpus provenance

- Source repository: `mistralai/platform-docs-public`.
- Source commit: `2e094f7bbe1395de4a738a3483def3573143d973`, dated 2026-09-07.
- License: Apache-2.0, preserved in `corpus/mistral-docs/LICENSE` and `NOTICE`.
- Contents: 296 documentation pages, 49 API reference pages, and 66 model cards.

```bash
make corpus-refresh
make corpus-refresh REF=<commit-or-tag>
make corpus-check
```

`make corpus-check` runs offline corpus tests and validates every URL and anchor
against the live site. CI runs the live check weekly.

## Repository layout

```text
src/glossator/
  corpus/mistral_docs/   MDX, OpenAPI, and model data to normalized Markdown
  ingest/                pages to sections, chunks, embeddings, and Vespa
  index/                 Vespa application, variants, and migrations
  retrieval/             hybrid search, reranking, floors, and probe
  answer/                context, generation, and citation verification
  eval/                  datasets, metrics, run records, and reports
src/entrypoints/          FastAPI and MCP servers (CLIs are python -m glossator.{corpus,ingest,retrieval,answer})
corpus/                   vendored corpus, manifest, license, and notice
eval/                     datasets, grids, and committed run directories
tests/                    offline tests and optional backend integration tests
```

`DECISIONS.md` records the facts behind product behavior. Append a new entry when
a change reverses an existing decision.

## Development

```bash
uv run ruff format .
uv run ruff check --fix .
uv run mypy
uv run pytest -q
```

Tests that need Vespa or an API key skip when those services are unavailable.
