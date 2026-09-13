# Working in this repository

Read `DECISIONS.md` before changing behaviour: every choice is recorded there with the facts behind it, and a change that reverses one gets a new entry. If `.local/AGENTS.md` exists, read it first; it is machine-local and never committed.

`mistralai-search-toolkit` is pinned at 0.0.13 and has no public source: the installed package under `.venv` is the only reference. Never guess a class or parameter name; read `.agents/skills/search/SKILL.md` and the package. Its traps are D-012 to D-016.

Entrypoints (`src/entrypoints/`) only parse arguments and call `glossator.surface`; behaviour lives in the package.

Pydantic models are frozen; update with `model_copy(update=...)`.

Every LLM call goes through `glossator.eval.providers` (offline tools) or `glossator.answer` (serving path): cached on disk by content hash, token usage logged. Do not call a model client directly.

`make test` is the offline suite (`pytest -m "not slow"`); tests needing Vespa or an API key skip when unconfigured; `make test-all` adds the container image build. Before a commit: `uv run ruff format . && uv run ruff check --fix . && uv run mypy`. `mypy` takes its file list from `pyproject.toml`; `eval/replay/run_replay.py` is outside it on purpose (standard library only, copied to other machines).

Commit messages describe the product change, imperative, no scope prefixes, no attribution lines.
