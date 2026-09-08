# glossator

A [Mistral Search Toolkit](https://pypi.org/project/mistralai-search-toolkit/) project with a Vespa backend.

SDK namespace: `mistralai.search.toolkit` — see the [toolkit docs](https://github.com/mistralai/mistral-pro/tree/main/dashboards/main/search/toolkit) for architecture and extension guides.

## Setup

```bash
make installdeps
```

`.env` carries secrets and ports only: `MISTRAL_API_KEY`, and optionally
`VESPA_QUERY_PORT` / `VESPA_CONFIG_PORT`. Schema names are owned by the index
package, not by the environment.

## Commands

### Start Vespa and apply schema migrations

```bash
make setup-vespa
```

Expected output (success): Vespa container `Healthy`, migration `"activated": true`, then `Application is up!` / `Application ready`. Warnings about `no_query_match` and `summary_fields` are normal. First startup may take up to a minute.

Ports default to **18080** (query) and **19072** (config server). If either is already in use, set `VESPA_QUERY_PORT` / `VESPA_CONFIG_PORT` in `.env` and rerun `make setup-vespa`.

To wipe local Vespa data and redeploy from scratch:

```bash
make reset-vespa
make setup-vespa
```

### Index variants

The migration creates one Vespa schema per index variant, so the same corpus can be
indexed several ways and compared. The table lives in
`src/glossator/index/variants.py`:

| variant | schema | chunking | embedding model |
|---|---|---|---|
| `page128` | `docs_page_lowdim` | whole-page markdown chunks (the starter's splitter) | `mistral-embed-dim128-2510` |
| `sec128` | `docs_section_lowdim` | one or more chunks per heading section | `mistral-embed-dim128-2510` |
| `sec1024` | `docs_section_fulldim` | one or more chunks per heading section | `mistral-embed` |

### Ingest the corpus

Reads a directory of normalized markdown pages with YAML frontmatter, checks it
against its `manifest.json` (sha256 per page; a mismatch aborts before anything is
embedded), chunks each page, embeds, and writes to the variant's schema. Re-running
replaces rather than duplicates.

```bash
make ingest corpus=corpus/mistral-docs variant=sec1024
make ingest corpus=tests/fixtures/corpus variant=sec128   # the sample corpus
```

The run prints chunks indexed, embedding tokens spent and the estimated cost, and
exits non-zero if any page failed.

### Search

Hybrid BM25 + vector, both inside Vespa: the YQL is `userInput OR nearestNeighbor`
and a two-phase rank profile combines the lexical and vector features. Ranking
weights are baked into the schema by `set_default_ranking_weights` in
`src/glossator/index/migrations/001_vespa_create_index_schema.py`; a query may
override any of them. No named query profile is used, because that would disable
`exclude_ids` and per-query filters.

```bash
make search query="how do I stream a chat completion"
make search query="which models support function calling" variant=sec1024 top_k=10
```

Each hit prints its citation URL (the page, deep-linked to the section when the
heading has an anchor), the score, the heading path and a preview.

Before the first query of a process, the embedding model is checked against five
fixed question/passage pairs and two unrelated passages, and one stored chunk is
re-embedded and compared with its indexed vector. A model whose weights no longer
mean anything passes every shape check and fails this one; the command aborts and
names the variant and the model. `--skip-probe` skips it.

Three optional flags change what comes back:

```bash
make search query="which models support function calling" variant=sec1024 top_k=10
uv run python -m glossator.retrieval "how do I stream a chat completion" --rerank
uv run python -m glossator.retrieval "what causes feline hyperthyroidism" --footing
```

`--rerank` spends one model call on reordering the top 20 candidates: the query
and each candidate's citation, heading path and first ~300 tokens go to the model,
which returns the candidates in relevance order with a short reason for the best
few. The reordered hits carry both scores, `rerank_score` and `retrieval_score`. A
malformed ranking keeps the retrieval order and says so; it never raises. The
model and temperature are `RetrievalConfig.rerank_model` and
`rerank_temperature`; the serving default is Mistral Small 4.

`--footing` reports whether any content word of the query occurs anywhere in the
corpus. It is what makes "the documentation does not cover this" reachable: with
vector search alone, every query matches something.

`RetrievalConfig` also carries an absolute cosine floor and a relative margin
below the query's best hit. Both default to off until they are calibrated against
the live index:

```bash
make calibrate-floors dataset=eval/dev.jsonl name=dev
```

That run searches the real questions and 15 junk questions from unrelated domains,
records the similarity at ranks 1, 5, 20 and 50 for each, and proposes a floor and
a margin only when the two distributions leave a corridor between them.

### Ask a question

Retrieval, grounded generation and citation verification in one call. Three
strategies differ only in how evidence is gathered:

| strategy | how it gathers evidence |
|---|---|
| `single_pass` | one hybrid search, one generation |
| `search_loop` | the model drives `search` / `open` / `grep` / `read` as tools, up to four rounds |
| `outline` | the model picks up to four pages from the site outline and reads them whole |

```bash
make ask question="how do I create a conversational workflow"
make ask question="what models support function calling" strategy=search_loop
uv run python -m glossator.answer "comment marche le mode JSON ?" --strategy outline --record calls.jsonl
```

Every factual sentence carries an `[n]` marker, and every citation carries a
verbatim quote that is checked against the chunk it names: a citation whose quote
is not in its source is dropped and reported in the trace. An answer with no
verified citation comes back flagged as insufficient evidence. The command prints
the answer, each citation with its status, the trace, token usage, latency and the
USD the run cost. `--record` writes every model request and response verbatim as
JSON lines.

### Compare retrieval configurations

Every question of a dataset through every configuration of a grid, with the ranked
hits of each run kept so any number in the report can be traced to the hits it
came from.

```bash
make eval-retrieval dataset=eval/dev.jsonl name=dev
make eval-retrieval dataset=eval/dev.jsonl name=quick configs=sec1024-shipped limit=20
```

The grid is `eval/configs/retrieval-grid.yaml`: a cross product of index variants
and ranking weight sets, plus the reranked rows named at the bottom of the file.
Results are reported at two matchings — the hit's URL against the gold URL, and
the hit's URL *and* anchor against a gold URL and anchor — because most markdown
headings in this corpus carry no anchor, so a question whose gold has none is
scored at page level only. Unanswerable questions are excluded from recall and
reported on their own.

The run writes `eval/runs/<date>-<name>/` with `config.json`, `records.jsonl`,
`calls.jsonl`, `metrics.json`, `figures/` and a README. Both are regenerated from
the recorded rows by:

```bash
make eval-report run=eval/runs/2026-09-08-2307-fixture-grid
```

### Run the tests

```bash
make test
```

Chunker, section parsing, corpus manifest and retrieval-config tests run offline. A
round-trip test indexes and searches a document through the same `get_index` the
engine uses, and an end-to-end test ingests the sample corpus and searches it. Both
skip with a reason when Vespa or `MISTRAL_API_KEY` is missing, so `make test` is
safe before `make setup-vespa`.

### MCP server

An MCP server exposes search and agentic navigation over the indexed
documentation, so agents (Vibe, Claude Code, etc.) can query it directly. It is
read-only: the index is built from the vendored, hash-checked corpus by
`make ingest`, and there is no tool that writes to it.

It serves the variant named by `GLOSSATOR_VARIANT` (default `sec1024`) and fails
fast at startup if `MISTRAL_API_KEY` is missing, the variant is unknown, or the
schema does not support navigation. Vespa must be running (`make start-vespa`).

**Available tools:**

| Tool | Description |
|------|-------------|
| `search(query, top_k=5, exclude_ids=None)` | Hybrid BM25 + vector search; returns ranked chunks with **id**, score, **citation_url**, url, anchor, page_title, **heading_path**, kind, content, source_id, **start_offset**, **end_offset**. `exclude_ids` skips chunks already seen in the loop |
| `open(chunk_id, window=2)` | Expand context around a chunk from search — pass the chunk `id`, the server resolves its position and returns the anchor chunk plus `window` neighbours on each side, in reading order |
| `navigate(source_id, start_offset, end_offset, direction, top_k=1)` | Step through a page from a known position; `direction` is `"next"` or `"previous"` |
| `read(source_id, start_offset=None, end_offset=None, top_k=20)` | Fetch a known offset range directly, no context expansion; omit either bound to read from the start or to the end |
| `grep(source_id, pattern, mode="phrase", top_k=5)` | Lexical search within a single page; `mode` is `"phrase"` (ordered) or `"term"` (any order) |

### Vibe CLI

Run `vibe` from this project directory. It automatically reads `.vibe/config.toml` and connects to the server via stdio — no manual setup needed. You can immediately ask Vibe to search the documentation.

> On first run, Vibe will ask you to trust this directory before loading the project config. Accept the prompt, or pass `--trust` to skip it for that session.

### Claude Code

Open this project directory in Claude Code. It automatically reads `.mcp.json` and connects to the server via stdio — no manual setup needed. You can immediately ask Claude to search the documentation.

### MCP Inspector

```bash
make mcp
npx @modelcontextprotocol/inspector http://127.0.0.1:8000/mcp
```

### Bruno API files (optional)

```bash
make bruno
```

Opens collection under `vespa/bruno/vespa/` (uses `WORKSPACE_ROOT=.` from `.env`).

### Vespa lock snapshot (optional)

```bash
make generate-vespa-lock
```

## Project layout

```
src/glossator/
├── index/            # Vespa application: variant table + schema migrations
├── ingest/           # pages → sections → chunks → embed → index (make ingest)
├── retrieval/        # config, retriever, engine, reranker, embedding probe (make search)
├── answer/           # context assembly, grounded generation, citations (make ask)
└── eval/             # datasets, retrieval grid, floor calibration, reports
src/entrypoints/
└── mcp_server.py     # read-only MCP server over glossator.retrieval
eval/configs/         # the retrieval grid definition
eval/runs/            # one committed directory per evaluation run
tests/                # make test; tests/fixtures/corpus/ is the sample corpus
.mcp.json             # MCP server config (auto-loaded by Claude Code)
.vibe/config.toml     # MCP server config (auto-loaded by Vibe CLI)
vespa/bruno/vespa/    # Generated by `make bruno` (optional)
```

`glossator.ingest` and `glossator.retrieval` are runnable directly, which is what
the Make targets do:

```bash
uv run python -m glossator.ingest --corpus <dir> --variant sec1024
uv run python -m glossator.retrieval "query" --variant sec1024 --top-k 10
```

## Development

```bash
uv run ruff format .
uv run ruff check --fix .
uv run mypy src
uv run pytest -q
```
