# Working in this repository

glossator answers technical questions over Mistral's documentation with cited sources. Read `DECISIONS.md` before changing behaviour: every choice is recorded there with the facts behind it, and a change that reverses one gets a new entry. If `.local/AGENTS.md` exists, read it first: it holds machine-local context and is never committed.

## Layout

```
src/glossator/
  corpus/mistral_docs/   corpus adapter: docs repo MDX → normalized markdown pages (corpus-specific)
  ingest/                pages → sections → chunks with url/anchor/heading_path metadata → index
  index/                 Vespa app and migrations
  retrieval/             retriever over Vespa, reranker, query rewriting
  answer/                context assembly, grounded generation, citation verification, search loop
  eval/                  datasets, retrieval metrics, answer judge, experiment grid, reports
src/entrypoints/         api (FastAPI), mcp_server, cli
corpus/                  vendored normalized corpus + manifest + upstream LICENSE
eval/                    datasets and results
tests/
```

## Toolkit

`mistralai-search-toolkit` is pinned at 0.0.13 and its only readable source is the installed package under `.venv`. Never guess a class or parameter: read `.agents/skills/search/SKILL.md` and the source. Known traps are listed in `DECISIONS.md` (D-012 to D-016).

## Conventions

- Python 3.12+, `uv` for everything (`uv run`, `uv add`). Async I/O for toolkit calls.
- Pydantic models are frozen; update with `model_copy(update=...)`.
- `structlog` for logging in library code; no `print` outside CLI output.
- Every module has one job; entrypoints only parse arguments and call the engine.
- Tests run with `make test`; tests that need Vespa or an API key skip when they are not configured.
- `uv run ruff format . && uv run ruff check --fix . && uv run mypy src` before a commit.
- Comments explain why, not what. No commented-out code, no TODOs without an owner.
- All LLM calls go through `glossator.eval.providers` (offline tools) or `glossator.answer` (serving path), are cached on disk by content hash, and log token usage.

## Commit messages

Describe the product change. Imperative mood, no scope prefixes, no attribution lines.
