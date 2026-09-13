# glossator

glossator is a Model Context Protocol (MCP) server that gives agents Mistral's documentation: 411 pages from a pinned [docs.mistral.ai](https://docs.mistral.ai) commit.
It is for agents with no filesystem or `grep`, such as those in Mistral Work, Le Chat and chat bots. The agent searches sections, reads pages and compares dated snapshots through three read-only tools, then writes the answer and cites the links the tools print.

## Try it

The deployed server is `https://glossator.tomvaucourt.com/mcp` (Streamable HTTP; the bearer token is supplied on request).

```bash
claude mcp add --transport http mistral-docs https://glossator.tomvaucourt.com/mcp --header "Authorization: Bearer <token>"
```

In Mistral Work, add that URL as a `Custom MCP Connector` under `Connectors` and pre-authorise the three read functions; [`docs/mcp.md`](docs/mcp.md) has the full setup, the workspace Skill, the health endpoint and other clients.

| Tool | Purpose |
|---|---|
| `mistral_docs_search(q, max_hits=5, under)` | The sections that state something: one hit per section with its key, heading path, snippet and the link to cite. `under` keeps the hits to the pages under a URL, or lists those pages when `q` is empty. |
| `mistral_docs_read_page(page_url, section, lang="python")` | A whole page in reading order, or one section of a large page with its neighbours. |
| `mistral_docs_history(text [+ page_url \| under] \| page_url + section \| under + since)` | When a phrase appeared, how a page or section changed across the dated snapshots, or what changed under a path between stored dates. Every change is a bound between two snapshot dates, never a day. |

## Why this shape

- The corpus is the docs repo at a commit, because all 75 `llms.txt` links return 404 and rendered HTML is 1.7% text (D-001).
- Search returns section chunks with tested anchors and prints a `cite:` line beside every hit, because 1,823 of 4,016 headings have no anchor on the live site (D-034, D-047).
- The agent writes the answer. Server-side generation stays as the measured baseline, scoring 0.78 against 0.77 at three times the latency (D-040b, D-044).
- The three tools take no ids and carry read-only annotations, without which Work asks for approval on every call (D-044, D-037b, D-037c).
- Eight biweekly snapshots and a history tool answer when a fact changed (D-041, D-048).

Every choice is in `DECISIONS.md` with the run that decided it; the alternatives considered are in [`docs/alternatives.md`](docs/alternatives.md).

## Evaluation in five lines

The runs and the judge study are in [`docs/evaluation.md`](docs/evaluation.md); the stage-by-stage table is in [`docs/eval-status.md`](docs/eval-status.md).

- The generated-answer baseline scores 0.93, 0.84 and 0.76 on the tuned, fresh and mined sets. Ministral 3 14B generated; GLM 5.3 judged without seeing the configuration. Medium 3.5 replayed on Mistral's API cut fabricated quotes per answer from 0.40–0.59 to 0.17–0.19 on all four sets, at 0.0045 to 0.0061 USD per question; its judged correctness is pending (D-017c).
- Sonnet scored 0.77 with the retrieval tools and 0.78 with server-side generation, which took three times as long. The run predates the three-tool cut.
- Across 575 answers, generation caused 77 of 164 failures. Retrieval misses were 1% to 3% on well-written questions; no context misses occurred.
- The demo itself, measured where it runs: Medium 3.5 at high reasoning through the Work Connector and the Skill scored 0.60 on thirty questions, 0.80 on the five that need the history tool and 0.20 on the five the documentation cannot answer, where it fills the gap; GLM 5.3 judged (D-049a).
- Tool results are most of a session's tokens, so a read prints one language tab, no repeated sample and no pasted output beyond its head: 36% fewer characters per read on the same thirty questions, correctness 0.62 against 0.60, inside the noise of two runs (D-050, D-050a).

## Five-minute start

You need `uv`, `make`, `curl`, docker with the compose plugin and about 4 GB of memory for the Vespa container (`docker-compose.yaml`), network access, and a `MISTRAL_API_KEY`. What each step does and costs, the models behind `make ask`, the tests and the local server's options are in [`docs/api.md`](docs/api.md#running-locally).

```bash
make installdeps
cp .env.example .env    # then fill in MISTRAL_API_KEY
make setup-vespa
make ingest corpus=corpus/mistral-docs variant=sec1024
make ask question="How do I stream a chat completion?" model=ministral-14b-2512
```

The API and the MCP server run in the foreground, so start each in its own terminal (`make api` on `http://127.0.0.1:8080`, `make mcp` on `http://127.0.0.1:8000/mcp`), then ask the API and connect a client:

```bash
curl -s -X POST http://127.0.0.1:8080/ask -H 'content-type: application/json' \
  -d '{"question": "How do I stream a chat completion?", "model": "ministral-14b-2512"}'
claude mcp add --transport http mistral-docs http://127.0.0.1:8000/mcp
```

## Deployment

`deploy/` puts the server on a Linux host behind a Cloudflare tunnel in one command (`make deploy HOST=<ssh-host>`); modes, checks and manual steps are in [`deploy/README.md`](deploy/README.md).

## Repository layout

```text
src/glossator/    corpus adapter, ingest, index, retrieval, answer, surface (what the tools and routes do), eval
  citing.py       section keys and citation links, shared by the surface and the snapshot tools
  history.py      phrase and section history over the stored snapshots (the snapshot diff;
                  surface/history.py only resolves the tool's argument forms onto it)
  changelog.py    the precomputed snapshot changelog and changes under a path
  clients.py      the chat and embedding Mistral clients every model call is built on
  surface/pages.py  page sizes, section keys and paths the tools read without the index;
                  ingest/pages.py is the unrelated reader of the vendored corpus files
src/entrypoints/  FastAPI and MCP servers over glossator.surface (CLIs are python -m glossator.{corpus,ingest,retrieval,answer})
corpus/           vendored corpus, manifest, license, notice
eval/             datasets, committed run directories, corpus stats, replay exports
docs/             architecture, evaluation, retrieval, corpus, stack notes
skills/           the mistral-docs workspace Skill for Mistral Work
deploy/           image, compose file, deploy script, tunnel templates
tests/            offline tests and optional backend integration tests
```

## Read next

- [`docs/alternatives.md`](docs/alternatives.md): the decisions that shaped the product and the alternatives measured against it.
- [`docs/evaluation.md`](docs/evaluation.md): the evaluation story, dataset by dataset, with every run linked; [`docs/eval-status.md`](docs/eval-status.md) is the stage-by-stage table.
- [`docs/failure-classes.md`](docs/failure-classes.md): the four classes of question still answered wrong, with causes, fixes and costs.
- [`docs/mcp.md`](docs/mcp.md): the tool contract and the Mistral Work setup.
- [`docs/architecture.md`](docs/architecture.md): the pipeline in ten lines.
- [`docs/upstream.md`](docs/upstream.md): the defects found in Mistral's packages and documentation, ranked, with where each fix goes.
- [`docs/search-toolkit.md`](docs/search-toolkit.md): the Mistral Search Toolkit kept, wrapped, replaced, skipped.
- [`docs/mistral-stack.md`](docs/mistral-stack.md): every Mistral component with its version, defects and constraints.
- [`docs/api.md`](docs/api.md): the HTTP routes, environment variables, local model servers and running locally.
- [`docs/retrieval.md`](docs/retrieval.md): index variants, the retrieval grid, ingestion guards.
- [`docs/corpus.md`](docs/corpus.md): where the corpus comes from and how it is checked.
- [`deploy/README.md`](deploy/README.md): deployment, the tunnel, Connector registration; the refresh gate is D-045.
- [`DECISIONS.md`](DECISIONS.md): every choice with the facts that decided it; append an entry when a change reverses one.
