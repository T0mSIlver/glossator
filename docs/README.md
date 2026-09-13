# Documentation

- [`alternatives.md`](alternatives.md): the decisions that shaped the product and the alternatives measured against it.
- [`evaluation.md`](evaluation.md): the evaluation story, dataset by dataset, with every run linked; [`eval-status.md`](eval-status.md) is the stage-by-stage table.
- [`failure-classes.md`](failure-classes.md): the four classes of question still answered wrong, with causes, fixes and costs.
- [`mcp.md`](mcp.md): the tool contract and the Vibe Work setup.
- [`architecture.md`](architecture.md): the pipeline in ten lines.
- [`upstream.md`](upstream.md): the defects found in Mistral's packages and documentation, ranked, with where each fix goes.
- [`search-toolkit.md`](search-toolkit.md): the Mistral Search Toolkit kept, wrapped, replaced, skipped.
- [`mistral-stack.md`](mistral-stack.md): every Mistral component with its version, defects and constraints.
- [`api.md`](api.md): the HTTP routes, environment variables, local model servers and running locally.
- [`retrieval.md`](retrieval.md): index variants, the retrieval grid, ingestion guards.
- [`corpus.md`](corpus.md): where the corpus comes from and how it is checked.
- [`../deploy/README.md`](../deploy/README.md): deployment, the tunnel, Connector registration; the refresh gate is D-045.
- [`../DECISIONS.md`](../DECISIONS.md): every choice with the facts that decided it; append an entry when a change reverses one.

## Superseded, kept for the record

- [`context-surface-audit.md`](context-surface-audit.md): describes the eight-tool surface D-044 replaced.
- [`improvement-axes.md`](improvement-axes.md): describes the eight-tool surface D-044 replaced.

## Repository layout

```text
src/glossator/    corpus adapter, ingest, index, retrieval, answer, surface (what the tools and routes do), eval
  citing.py       section keys and citation links, shared by the surface and the snapshot tools
  doc_paths.py    the docs.mistral.ai path a tool argument names, in any form a model writes it
  history.py      phrase, section and under-a-path history over the stored snapshots (the
                  snapshot diff; surface/history.py only resolves the tool's argument forms onto it)
  changelog.py    builds and reads the precomputed snapshot changelog
  clients.py      the chat and embedding Mistral clients every model call is built on
  surface/pages.py  page sizes, section keys and paths the tools read without the index;
                  ingest/pages.py is the unrelated reader of the vendored corpus files
src/entrypoints/  FastAPI and MCP servers over glossator.surface (CLIs are python -m glossator.{corpus,ingest,retrieval,answer})
corpus/           vendored corpus, manifest, license, notice
eval/             datasets, committed run directories, corpus stats, replay exports
docs/             architecture, evaluation, retrieval, corpus, stack notes
skills/           the mistral-docs workspace Skill for Work
deploy/           image, compose file, deploy script, tunnel templates
tests/            offline tests and optional backend integration tests
```

## Deployment

`deploy/` puts the server on a Linux host behind a Cloudflare tunnel in one command (`make deploy HOST=<ssh-host>`); modes, checks and manual steps are in [`deploy/README.md`](../deploy/README.md).
