# glossator

glossator gives agents Mistral's documentation: an MCP server with three
read-only tools over the 411 pages of [docs.mistral.ai](https://docs.mistral.ai)
at a pinned commit, a search that returns sections addressed by their
`url#anchor`, whole-page reads, and a history of what changed across dated
snapshots. The agent does the research and writes the answer. A FastAPI
service keeps the generated-answer path, with `[n]` markers and quotes checked
against the retrieved chunks, as the evaluated baseline.

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
`GLOSSATOR_VARIANT`, `GLOSSATOR_MODEL`, `GLOSSATOR_CORPUS_DIR`,
`GLOSSATOR_MCP_TOKEN`, and `GLOSSATOR_MCP_TOOLS`. Both read
`GLOSSATOR_SNAPSHOT_MANIFEST` for the `history` forms. Do not put
schema names in `.env`.

Chat completions -- the answer model, the listwise reranker, and the translation
and rewrite calls -- go to a local OpenAI-compatible server when
`GLOSSATOR_CHAT_SERVER_URL` is set, with `GLOSSATOR_CHAT_API_KEY` if it wants a
key and `GLOSSATOR_CHAT_REASONING_EFFORT` to set or disable its thinking.
Embeddings always go to the Mistral API. Every run records which server and
which effort it used.

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
| `POST /ask` | `question`; optional `strategy`, `variant`, `model` | answer Markdown, verified citations, the rendered `sources_markdown` block, trace, usage, cost, latency |
| `POST /search` | `query`; optional `top_k`, `kinds`, `locales`, `exclude_ids`, `variant` | ranked hits with citation URL, heading path, preview, score, ID, and offsets |
| `POST /cite` | `draft`, `quotes` (`n`, `quote`, plus `chunk_id` or page `url`); optional `variant` | per-quote verdicts, uncovered markers, deduplicated sources, the rendered `sources_markdown` block |
| `GET /pages/{path}` | documentation path; optional `variant`, `start_offset`, `top_k` | up to 100 page sections in reading order; `truncated` says whether more exist |
| `GET /history` | exactly one of `text`, `section`, `question` | a phrase's first and last stored snapshot, a section's state and diff per date, or the top retrieved section per date |
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

The server is named `mistral-docs` and exposes three read-only tools. The agent
calling them does the research and writes the answer; nothing generates text
inside the server (`DECISIONS.md` D-044).

| Tool | Purpose |
|---|---|
| `mistral_docs_search(q, max_hits=5, kind)` | The sections that state something: one hit per section with its `url#anchor`, heading path and snippet. |
| `mistral_docs_read_page(page_url, section)` | A whole page in reading order, or one section of a large page with its neighbours. |
| `mistral_docs_history(text \| section \| question)` | When a phrase appeared, how a section changed across the dated snapshots, or what a question retrieved on each date. |

Every hit and every section is addressed by its `url#anchor` on
docs.mistral.ai, which is also the citation; there is no other identifier for a
model to carry. 97% of pages fit one `read_page` call whole
(`eval/corpus-stats/`); a hit on one of the dozen larger pages names the
section to pass. Every tool is annotated read-only, idempotent and
closed-world, so a host can call one without asking (D-037b, D-037c). Unknown
parameters are rejected with `E_BAD_PARAM` naming the likely one, and
host-supplied arguments whose name starts with an underscore are dropped.

The MCP server cannot ingest or delete content. Corpus changes go through the
adapter, manifest checks, and ingestion command. `GLOSSATOR_MCP_TOOLS` names a
subset of the three tools to register, which the consumer evaluation uses to
serve one arm per deployment.

The generated answer with verified quotes, the listwise reranker and the search
loop remain in the package and the HTTP API (`POST /ask`, `POST /cite`) as the
measured context-injection baseline the agent path is compared against
(D-040b, D-017b); they are not on the MCP surface.

## Mistral Work

Serve the MCP server over HTTP behind a tunnel, then register it as a custom
MCP Connector. From the documentation page on MCP Connectors, in its exact
words:

1. Open the `Connectors` page.
2. Click `+ Add Connector` and switch to the `Custom MCP Connector` tab.
3. Fill in the required fields:
   - **Connector name**: a unique identifier (no spaces or special characters).
   - **Server URL**: the full URL of your MCP-compatible server.
   - **Description** (optional): a short explanation of what this Connector does.
4. Click `Connect`. The platform detects the server's authentication method automatically.

Authentication, again in the page's exact words:

> Our platform auto-detects the authentication method when you provide the server URL:
>
> - **No authentication**: for publicly accessible or trusted internal servers.
> - **HTTP Bearer Token / Basic Auth**: for servers that require credentials in the `Authorization` header.
> - **OAuth 2.1** (with dynamic client registration): for servers using standard OAuth 2.1 delegated access. You'll be guided through the consent flow.

Set `GLOSSATOR_MCP_TOKEN` on the server. Every MCP HTTP request must then
carry `Authorization: Bearer <token>`; requests without it get a 401 naming
the missing header. Work detects "bearer" automatically when registering the
Connector. Pre-authorize the three read functions per Connector so they run
without approval prompts; the server exposes no write functions. `GET /health`
needs no header and reports the served variant, the page and chunk counts,
whether the embedding probe passed, and the registered tool names, so the
Connectors Debugger and the tunnel can check the server. `GET /` is a landing
page and `/favicon.svg` the icon, both open.

`skills/mistral-docs/SKILL.md` is a workspace Skill for documentation
questions: search first with the mistral-docs connector, read the page behind
the best hit, link the section behind each claim, use the history tool for
"when did this change" questions, and say when the documentation does not
answer. Its `README.md` explains how to add it as a workspace Skill, and
`custom-instructions.md` holds two sentences a workspace admin can paste into
`Context` > `Instructions`. Custom MCP Connectors do not read MCP resources or
prompts, so the rules reach Work through the tool descriptions and the Skill.

## Deployment

`deploy/` puts the MCP server on a Linux host over SSH in one command, behind a
Cloudflare tunnel that gives it the HTTPS hostname a Connector needs. The host
needs docker with the compose plugin and nothing else.

```bash
cp deploy/.env.deploy.example deploy/.env.deploy   # fill in the key and the token
make deploy HOST=lxc-glossator                     # MCP server against an existing index
make deploy HOST=lxc-glossator MODE=full           # Vespa, migrations and ingestion too
make deploy-check HOST=lxc-glossator               # health and bearer-token checks only
```

`remote-index` mode points the server at a Vespa that already serves the shipped
schemas, so it embeds and ingests nothing. `full` mode syncs
`~/.cache/glossator/embeddings` to the host and mounts it into the ingestion job,
so a redeploy pays only for chunks whose text changed; it refuses to run when the
host's docker filesystem is 80% full or more, because Vespa blocks feeds above
that mark and re-indexing deletes a page's chunks before writing the
replacements.

A deploy ends by printing the health JSON, the result of one MCP call without
the token and one with it, and the `curl` and `claude mcp add` commands for the
tunnel hostname. `deploy/README.md` has the Cloudflare steps to do by hand and
the Connector registration in the documentation's own words.

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

Mistral Medium 3.5 was measured on the same single-pass answers by replaying
the recorded prompts through an OpenAI-compatible endpoint (`eval/replay/`,
`DECISIONS.md` D-017b), so retrieval and context are byte-identical and only
the generator changes. Judged correctness is unchanged within the interval
(0.93 → 0.91 on the tuned sixty, 0.84 → 0.84 on the fresh sixty, 0.76 → 0.80
on the 85 mined questions, GLM 5.3 blind), fabricated quotes per answer halve,
and answers are a third shorter; the runs are
`eval/runs/2026-09-10-1615-medium35-replay-*/`.

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

Recorded spend is a lower bound for runs made before 2026-09-09: their answer
evaluations built the search engine without a call recorder, so the listwise
reranker's calls are absent from their `calls.jsonl` and from their totals, and
embeddings are not priced per run at all. The console figure is the number of
record for spend. Runs from that date on share one recorder between the engine
and the answer model, so reranker calls land beside generation calls.

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
deploy/                   compose file, deploy script, and Cloudflare tunnel templates
eval/                     datasets, grids, and committed run directories
tests/                    offline tests and optional backend integration tests
Dockerfile                the application image: MCP server, API, and ingestion CLI
```

`DECISIONS.md` records the facts behind product behavior. Append a new entry when
a change reverses an existing decision.

`docs/search-toolkit.md` assesses the Mistral Search Toolkit as used here: which
parts were kept, which were worked around, and which were replaced, with a
reproduction for each.

## Development

```bash
uv run ruff format .
uv run ruff check --fix .
uv run mypy
uv run pytest -q
```

Tests that need Vespa or an API key skip when those services are unavailable.
