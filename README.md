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

### Ask a question

Retrieval, grounded generation and citation verification in one call. Three
strategies differ only in how evidence is gathered:

| strategy | how it gathers evidence |
|---|---|
| `single_pass` | one hybrid search, one generation |
| `search_loop` | the model drives `search` / `open` / `grep` / `read` as tools, over a capped number of rounds |
| `outline` | the model picks pages from the site outline and reads them whole |

Round cap, page cap, `top_k`, the context budget and the model all live in
`AnswerConfig` (`src/glossator/answer/config.py`).

```bash
make ask question="how do I create a conversational workflow"
make ask question="what models support function calling" strategy=search_loop
make ask question="how do I stream" model=ministral-8b-2512
uv run python -m glossator.answer "comment marche le mode JSON ?" --strategy outline --record calls.jsonl
```

Every factual sentence carries an `[n]` marker, and every citation carries a
verbatim quote that is checked against the chunk it names: a citation whose quote
is not in its source is dropped and reported in the trace. An answer with no
verified citation comes back flagged as insufficient evidence. The command prints
the answer, each citation with its status, the trace, token usage, latency and the
USD the run cost. `--record` writes every model request and response verbatim as
JSON lines.

### Evaluate the answers

Runs every question of a dataset through each strategy against one index variant
and scores each answer twice: deterministic checks that need no model (did a
verified citation land on a gold page, did the quotes survive the verifier, was
the refusal correct, what did it cost), and an LLM judge for correctness,
groundedness and citation relevance. The judge never sees which strategy wrote
the answer.

```bash
make eval-answers dataset=eval/dev.jsonl name=answers-dev
make eval-answers dataset=tests/fixtures/answer-questions.jsonl name=answers-fixture \
  strategies=single_pass variant=sec128 limit=4
```

Each run writes `eval/runs/<date>-<name>/` with `config.json`, `calls.jsonl`,
`records.jsonl`, `metrics.json`, a README of tables and `figures/`. The records
are also the checkpoint: re-running the same `name` skips the questions already
recorded and pays only for the rest. `limit=N` takes a stratified sample that
keeps every question type represented. Regenerate a run's README and figures from
its records with `make eval-report run=<dir>`.

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
├── retrieval/        # config, retriever, engine (make search)
└── answer/           # context assembly, grounded generation, citations (make ask)
src/entrypoints/
└── mcp_server.py     # read-only MCP server over glossator.retrieval
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
