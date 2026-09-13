# Working in this repository

glossator gives agents Mistral's documentation through three read-only MCP tools (search, read a page, history) over the vendored corpus at a pinned commit; the agent does the research and writes the answer (D-044). A FastAPI service keeps the generated-answer path, with verified citations, as the evaluated baseline behind `POST /ask` and `POST /cite`. Read `DECISIONS.md` before changing behaviour: every choice is recorded there with the facts behind it, and a change that reverses one gets a new entry. If `.local/AGENTS.md` exists, read it first: it holds machine-local context and is never committed.

## Layout

```
src/glossator/
  corpus/mistral_docs/   corpus adapter: docs repo MDX → normalized markdown pages (corpus-specific)
  ingest/                pages → sections → chunks with url/anchor/heading_path metadata → index
  index/                 Vespa app and migrations
  retrieval/             retriever over Vespa, reranker, query rewriting
  answer/                context assembly, grounded generation, citation verification, search loop
  surface/               what the three MCP tools and the HTTP routes do and print: search, page reads,
                         history forms and rendering, typed errors, the parameter guard
  eval/                  datasets, retrieval metrics, answer judge, experiment grid, reports
  citing.py              section keys and citation links, shared by the surface and the snapshot tools
  history.py             phrase and section history over the stored snapshots
  changelog.py           the precomputed snapshot changelog and changes under a path
src/entrypoints/         api (FastAPI) and mcp_server (FastMCP): configuration, routes and tool
                         registration over glossator.surface; CLIs are python -m glossator.{corpus,ingest,retrieval,answer}
corpus/                  vendored normalized corpus + manifest + upstream LICENSE
eval/                    datasets, committed run directories, corpus-stats, replay exports
docs/                    architecture, evaluation, retrieval, corpus, stack notes
skills/                  the mistral-docs workspace Skill for Mistral Work
deploy/                  image, compose, deploy script, Cloudflare tunnel templates
tests/                   offline tests; tests that need Vespa or an API key skip when unconfigured
```

## Toolkit

`mistralai-search-toolkit` is pinned at 0.0.13 and its only readable source is the installed package under `.venv`. Never guess a class or parameter: read `.agents/skills/search/SKILL.md` and the source. Known traps are listed in `DECISIONS.md` (D-012 to D-016).

## Conventions

- Python 3.12+, `uv` for everything (`uv run`, `uv add`). Async I/O for toolkit calls.
- Pydantic models are frozen; update with `model_copy(update=...)`.
- `structlog` for logging in library code; no `print` outside CLI output.
- Every module has one job; entrypoints only parse arguments and call `glossator.surface`, which calls the engine.
- Tests run with `make test`; tests that need Vespa or an API key skip when they are not configured.
- `uv run ruff format . && uv run ruff check --fix . && uv run mypy` before a commit. Bare `mypy` uses the file list in `pyproject.toml` (src and tests), matching CI.
- Comments explain why, not what. No commented-out code, no TODOs without an owner.
- All LLM calls go through `glossator.eval.providers` (offline tools) or `glossator.answer` (serving path), are cached on disk by content hash, and log token usage.

## Commit messages

Describe the product change. Imperative mood, no scope prefixes, no attribution lines.
