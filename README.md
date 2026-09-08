# glossator

glossator answers technical questions over [docs.mistral.ai](https://docs.mistral.ai)
with cited sources: every factual sentence carries an `[n]` marker, and every
citation carries a verbatim quote that is checked against the chunk it names
before the answer is returned. It is served two ways — an HTTP API and an MCP
server — over one retrieval engine.

## Architecture, in ten lines

1. The corpus is vendored: 411 normalized markdown pages converted from the
   docs repo's MDX (`src/glossator/corpus/mistral_docs/`), pinned to commit
   `2e094f7…`, with per-page sha256 hashes in a manifest.
2. Ingest chunks pages into sections (never across a heading, ~600-token
   target) and embeds each chunk with `mistral-embed` (`src/glossator/ingest/`).
3. Vespa stores one schema per index variant; hybrid BM25 + vector search and
   two-phase ranking happen inside it (`src/glossator/index/`,
   `src/glossator/retrieval/`).
4. Hits are citable units: url, anchor, heading path, offsets.
5. The answer layer assembles context, generates with structured output, and
   verifies each citation's quote in code (`src/glossator/answer/`).
6. `src/entrypoints/api.py` (FastAPI) and `src/entrypoints/mcp_server.py` are
   thin surfaces over the same engine and the same `ask` call.
7. Evaluation runs live under `eval/runs/`, one self-describing directory per
   run (`src/glossator/eval/`).

## Quickstart

```bash
make installdeps          # uv sync
# put MISTRAL_API_KEY=... in .env (ports optional: VESPA_QUERY_PORT, VESPA_CONFIG_PORT)
make setup-vespa          # start Vespa, apply schema migrations
make ingest corpus=corpus/mistral-docs variant=sec1024
make search query="how do I stream a chat completion"
make ask question="how do I stream a chat completion" model=ministral-8b-2512
make api                  # HTTP API on 127.0.0.1:8080 (make api host=0.0.0.0 port=9000)
make mcp                  # MCP server, HTTP transport on 127.0.0.1:8000
```

Notes:

- `make ask` defaults to Mistral Medium 3.5. On a free-tier key that model is
  rate-limited to zero (DECISIONS.md D-017a); pass `model=ministral-8b-2512`
  until the account is provisioned.
- The MCP server serves the variant named by `GLOSSATOR_VARIANT` (default
  `sec1024`) and can pin its generation model with `GLOSSATOR_MODEL`.
- Vespa blocks feeding above 80% host disk usage (D-025).

## HTTP API

`make api` (or `uv run uvicorn entrypoints.api:app --host 127.0.0.1 --port 8080`).
Interactive docs at `/docs`; the OpenAPI schema at `/openapi.json`.

| Route | Body / params | Returns |
|---|---|---|
| `POST /ask` | `question`, optional `strategy` (`single_pass` \| `search_loop` \| `outline`), `variant`, `model` | the `Answer`: markdown with `[n]` markers, citations (url, anchor, quote, verified), trace + trace summary, token usage, cost, latency |
| `POST /search` | `query`, `top_k` (1–100), `kinds` (`doc`\|`api`\|`model`), `locales`, `exclude_ids`, `variant` | hits with url, anchor, citation url, heading path, preview, score, chunk id, offsets |
| `GET /pages/{path}` | e.g. `/pages/api/endpoint/chat` | the page's sections in reading order, from the index |
| `GET /health` | — | Vespa reachability, per-variant document counts, corpus commit |
| `GET /version` | — | version, index variants, generation models |

Errors are typed JSON — `{"error": {"code", "message", "next"}}` — with codes
like `E_BAD_PARAM` (400/422), `E_UNKNOWN_PAGE` (404), `E_UPSTREAM` (503/500).
Send `X-Request-Id` to have it echoed on the response and in the logs.

## MCP server

`make mcp` serves HTTP on `127.0.0.1:8000/mcp`; stdio is the default transport
for `.mcp.json` (Claude Code) and `.vibe/config.toml` (Vibe). The server
instructions, the `glossator://guide` resource, and every `next:` line teach
the same flow. Read-only by design: the index is built by `make ingest`, never
from a tool call (D-026).

| Tool | Purpose |
|---|---|
| `search(query, top_k=5, kinds, locales, exclude_ids)` | Hybrid BM25 + vector search; every hit prints its `url#anchor`, chunk id, offsets |
| `open(chunk_id, window=2)` | A chunk and its neighbours, in reading order |
| `navigate(source_id, start_offset, end_offset, direction, top_k=1)` | Step forward/backward through a page |
| `read(source_id, start_offset, end_offset, top_k=20)` | Fetch a known offset range (or the whole page) verbatim |
| `grep(source_id, pattern, mode="phrase", top_k=5)` | Exact phrase or terms within one page |
| `ask(question, strategy="single_pass")` | Answer with verified citations: `[n]` markers, numbered source list, `citations verified: x/y` |

Responses are text tuned for agents: a `next:` hint on every response,
announced clamps (`note: clamped server-side: top_k=500 → 50`), typed errors
(`E_BAD_PARAM`, `E_UNKNOWN_PAGE`, `E_UNKNOWN_CHUNK`, `E_EMPTY_QUERY`, `E_BUSY`,
`E_UPSTREAM`), and empty results that say which kind of empty they are.
Three resources exist and no others: `glossator://guide` (rules and flow),
`glossator://index` (page list), `glossator://context` (limits, id formats,
corpus commit, counts, model ids).

```bash
make mcp
npx @modelcontextprotocol/inspector http://127.0.0.1:8000/mcp   # explore the surface
```

## Index variants

One Vespa schema per (chunking, embedding) pair, so the eval grid can compare
them on the same corpus. The table lives in `src/glossator/index/variants.py`.

| variant | schema | chunking | embedding model |
|---|---|---|---|
| `page128` | `docs_page_lowdim` | whole-page markdown chunks (the starter's splitter) | `mistral-embed-dim128-2510` |
| `sec128` | `docs_section_lowdim` | one or more chunks per heading section | `mistral-embed-dim128-2510` |
| `sec1024` | `docs_section_fulldim` | one or more chunks per heading section | `mistral-embed` |

## Evaluation

Datasets live in `eval/` (`eval/dev-smoke.jsonl` so far); every run writes a
self-describing directory under `eval/runs/<date>-<name>/` — `README.md`
(what was measured and concluded), `config.json`, `records.jsonl` (per
question: hits, context, prompts, raw model output, verified citations, usage,
latency), `calls.jsonl` (every LLM call verbatim), `metrics.json`, `figures/`.

```bash
make dev-set      # generate the development question set (GLM, D-020)
make eval-report run=eval/runs/2026-09-08-2218-dev-smoke   # regenerate a run's README + figures
```

Published runs so far (the placeholder the retrieval/answer grids will fill):

| run | what it measured | headline result |
|---|---|---|
| `eval/runs/2026-09-08-2218-dev-smoke/` | retrieval smoke on the dev-smoke set | first scores for the section variants |
| `eval/runs/2026-09-09-answer-smoke/` | five questions × three strategies, Ministral 8B | `outline` alone refused the unanswerable question (D-027a) |
| `eval/runs/…-retrieval-grid/` | ranking-weight grid | _to be run_ |
| `eval/runs/…-answer-grid/` | top_k / context budget / strategy grid | _to be run_ |

Which model produced which table is stated in each run's README (D-017a);
dataset generation and judging use GLM through the z.ai API, disclosed per run.

## Corpus provenance

- Source: `mistralai/platform-docs-public`, pinned at commit
  `2e094f7bbe1395de4a738a3483def3573143d973` (2026-09-07), converted from MDX
  to normalized markdown by `src/glossator/corpus/mistral_docs/` (D-001).
- License: Apache-2.0, notice kept at `corpus/mistral-docs/LICENSE` and
  `NOTICE` (D-009).
- 411 pages: 296 docs, 49 API reference, 66 model cards; French is measured,
  not yet indexed (D-008).

```bash
make corpus-refresh            # rebuild from the docs repo (REF=<commit|tag|branch> to move the pin)
make corpus-check              # offline tests + every URL and anchor against the live site
```

`corpus-check` also runs weekly in CI (`.github/workflows/ci.yml`) so a site
change that breaks anchors is caught without a local run.

## Layout

```
src/glossator/
├── corpus/mistral_docs/  docs repo MDX → normalized markdown (corpus-specific)
├── ingest/               pages → sections → chunks → embed → index (make ingest)
├── index/                Vespa app, variants, migrations
├── retrieval/            engine, retriever, ranking config (make search)
├── answer/               context assembly, generation, citation verification (make ask)
└── eval/                 datasets, providers, run records, reports
src/entrypoints/          api.py (FastAPI), mcp_server.py
corpus/                   vendored corpus + manifest + upstream LICENSE
eval/                     datasets and run directories
tests/                    make test; backend tests skip without Vespa/key
.mcp.json / .vibe/        MCP server configs for Claude Code / Vibe
```

`DECISIONS.md` records every choice with the facts behind it; read it before
changing behaviour.

## Development

```bash
uv run ruff format . && uv run ruff check --fix . && uv run mypy src
uv run pytest -q          # or: make test
```
