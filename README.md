# glossator

glossator gives agents Mistral's documentation through a Model Context Protocol
(MCP) server. It exposes three read-only tools over 411 pages from a pinned
[docs.mistral.ai](https://docs.mistral.ai) commit. Search results name sections by
key and print the link to cite; the other tools read pages by key and compare
dated snapshots.
The calling agent researches and writes the answer.

A separate FastAPI service retains the evaluated generated-answer baseline. It
checks each numbered citation and quote against the retrieved documentation.

## Try it

The deployed server is at `https://glossator.tomvaucourt.com/mcp` (Streamable
HTTP; the bearer token is supplied on request). The health endpoint
`https://glossator.tomvaucourt.com/health` is open and reports the served
variant, the index counts and the embedding probe.

- Mistral Work: open `Connectors`, click `+ Add Connector`, and select
  `Custom MCP Connector`. Enter the server URL above. Work detects bearer
  authentication automatically. Pre-authorise the three read functions. See
  [`docs/mcp.md`](docs/mcp.md) for setup and the workspace Skill.
- Claude Code:

  ```bash
  claude mcp add --transport http mistral-docs https://glossator.tomvaucourt.com/mcp --header "Authorization: Bearer <token>"
  ```

- Any other MCP client (for example MCP Inspector): Streamable HTTP transport
  against the URL above with an `Authorization: Bearer <token>` header.

| Tool | Purpose |
|---|---|
| `mistral_docs_search(q, max_hits=5, under)` | The sections that state something: one hit per section with its key, heading path, snippet and the link to cite. `under` keeps the hits to the pages under a URL, or lists those pages when `q` is empty. |
| `mistral_docs_read_page(page_url, section)` | A whole page in reading order, or one section of a large page with its neighbours. |
| `mistral_docs_history(text \| page_url + section \| under + since)` | When a phrase appeared, how a page or section changed across the dated snapshots, or what changed under a path between stored dates. Every change is a bound between two snapshot dates, never a day. |

## Why an MCP server, and what decided its shape

Agents inside Mistral Work, Le Chat, scheduled tasks and chat bots have no
filesystem or `grep`. They can reach external systems through Connectors. A
coding agent can search an SDK checkout for a parameter name, but product facts
often live elsewhere.

This gap appears in `eval/mined.jsonl`. Of its 85 real questions, 54 came from
GitHub issues opened by SDK users (`DECISIONS.md` D-038, D-039). The server
provides documentation from a pinned commit and prints, beside every section,
the link a reader opens. Snapshot search also shows when a fact changed.

Every choice is in `DECISIONS.md` with the run that decided it. The ones that
shaped the product:

| Decision | Evidence | Entry |
|---|---|---|
| Source the docs repo at a commit, not `llms.txt` or HTML | all 75 `llms.txt` links return 404; rendered HTML is 1.7% text with empty tab panels | D-001 |
| Section chunks with tested anchors, not whole pages | whole-page chunks cannot return an exact section link and use twice the answer prompt tokens | D-034, D-035a |
| Vector-heavy hybrid ranking inside Vespa | best exact-section retrieval on a 13-configuration grid over 294 questions | D-034 |
| The agent writes the answer; nothing generates inside the server | with retrieval tools a capable agent scored 0.77, against 0.78 for server-side generation at three times the latency and with a second model | D-040b, D-044 |
| No reranker on the agent path | it accounted for 91% of search latency and mainly improved which result ranked first, which an agent that reads several hits does not need | D-015b |
| Medium 3.5 as the answer model | replay changed correctness by -2, 0, +4 and -2 points across four sets | D-017b |
| Three tools, no ids | 97% of pages fit one read under 8,000 tokens; the Work session never used the other five tools | D-043, D-044 |
| Every section has a key, and the link to cite is printed beside it | 1,823 of 4,016 headings have no anchor on the live site, so anchors alone collapse sibling sections and land a click far from the text; a text fragment is printed only when it moves the landing | D-047 |
| Read-only tool annotations | without them Work asks for approval on every call and a headless consumer never calls at all | D-037b, D-037c |
| A time axis: eight biweekly snapshots and a history tool | the docs renamed their API section in August; `-latest` aliases moved under users' feet | D-041, D-041a |
| GLM 5.3 as the primary judge | four judges were compared; the primary agreed with 35 of 40 labels by the author | D-021a, D-021b, D-021c |

### Why not the alternatives

#### Put the whole documentation in a one-million-token context

The corpus contains 765,646 Medium 3.5 tokens (`eval/corpus-stats/`). It exceeds
Medium 3.5's 256,000-token context window. It fits Z.ai GLM 5.2's one-million-token
window. The vendored model card prices input at 1.4 USD per million tokens, or
0.14 USD for cached input. Reading the corpus would therefore cost about 1.07
USD uncached or 0.11 USD cached per question. Search returns a much smaller
passage with its exact section link.

#### Generate inside the server

The FastAPI `POST /ask` route implements retrieval-augmented generation. The
repository keeps it as the measured baseline. On the same questions, Sonnet
scored 0.77 with the retrieval tools and 0.78 with `answer`. The
server-side answer took three times as long and required a second model
(D-040b). Medium 3.5 also produced no significant correctness change when it
replaced Ministral 3 14B (D-017b).

The MCP server now provides the parts that calling agents lack: a pinned
corpus, tested section anchors and dated history. Agents can reformulate a
search with their own reasoning.

#### Use Libraries or web search

Libraries index uploaded files for the `document_library` tool and cite the
document. They do not retain docs.mistral.ai section anchors, source commits or
dated changes. In the consumer run, built-in web search resolved 0.86 of its
links. Its correctness was 0.52 to 0.58, compared with 0.77 for the retrieval
tools (D-040b). The live site has no history, and all 75
links in its `llms.txt` returned 404 (D-001).

[`docs/search-toolkit.md`](docs/search-toolkit.md) records what the project kept,
wrapped, replaced or skipped. [`docs/mistral-stack.md`](docs/mistral-stack.md)
lists each Mistral dependency, its version and known defects.
[`docs/eval-status.md`](docs/eval-status.md) summarises the evaluation.

## Evaluation in five lines

Every number below names its model; the runs and the judge study are in
[`docs/evaluation.md`](docs/evaluation.md).

- The generated-answer baseline scores 0.93, 0.84 and 0.76 on the tuned, fresh and mined sets. Ministral 3 14B generated; GLM 5.3 judged without seeing the configuration.
- Medium 3.5 replay changed correctness by -2, 0, +4 and -2 points. Fabricated quotes per answer fell by about half on all four sets.
- Sonnet scored 0.77 with the retrieval tools and 0.78 with server-side generation, which took three times as long. The run predates the three-tool cut.
- Across 575 answers, generation caused 77 of 164 failures. Retrieval misses were 1% to 3% on well-written questions; no context misses occurred.
- The demo itself, measured where it runs: Medium 3.5 at high reasoning through the Work Connector and the Skill scored 0.60 on thirty questions, 0.80 on the five that need the history tool and 0.20 on the five the documentation cannot answer, where it fills the gap; GLM 5.3 judged (D-049a).
- Tool results are most of a session's tokens, so a read prints one language tab, no repeated sample and no pasted output beyond its head: 36% fewer characters per read on the same thirty questions, correctness 0.62 against 0.60, inside the noise of two runs (D-050, D-050a).
- Each directory under `eval/runs/` stores its inputs, model calls, records, metrics and figures.

## Five-minute start

You need `uv`, `make`, `curl`, docker with the compose plugin and about 4 GB of
memory for the Vespa container (`docker-compose.yaml`), network access, and a
`MISTRAL_API_KEY`.

```bash
make installdeps
cp .env.example .env    # then fill in MISTRAL_API_KEY
make setup-vespa
make ingest corpus=corpus/mistral-docs variant=sec1024
make ask question="How do I stream a chat completion?" model=ministral-14b-2512
make api
make mcp
```

`make setup-vespa` starts Vespa with its query API on `localhost:18080` and its
config server on `localhost:19072`, then deploys the schemas. `make ingest`
splits the 411 pages into 4,440 section chunks and embeds them with
`mistral-embed`: about one million tokens, about 0.10 USD (D-011a). On the free
tier the embedding API rate-limits the run, so it takes a few minutes; embeddings
are cached, so a re-run after a rate-limit failure only embeds what is missing.

`make ask` calls two models: the generation model named by `model=` (Mistral
Medium 3.5 when omitted) and the reranker, `mistral-small-2603` by default and
overridable with `GLOSSATOR_RERANK_MODEL`. A key without Mistral Small quota sets
`GLOSSATOR_RERANK_MODEL=ministral-14b-2512` in `.env`.

`make api` and `make mcp` are foreground servers; run each in its own terminal.
The API listens on `127.0.0.1:8080`. MCP uses `127.0.0.1:8000/mcp` by default;
override either with `host=` and `port=`. Run the stdio transport with
`uv run python -m entrypoints.mcp_server`. The history tool reads the vendored
`corpus/snapshots/` directories, so the five-minute start needs no snapshot step.
`make test` runs the offline tests; `make test-all` adds the container image build.

Mistral Medium 3.5 is the generation default. The project API key had zero
quota for Medium 3.5 and Small 4 until 12 September 2026 (D-017a, D-049), so
the reported API runs use `ministral-14b-2512`, D-017b measures Medium 3.5 by
replay, and the demo run of D-049a is the first on Medium 3.5 end to end. See
[`docs/api.md`](docs/api.md) for environment variables and local model servers.

## Deployment

`deploy/` puts the server on a Linux host behind a Cloudflare tunnel in one
command (`make deploy HOST=<ssh-host>`). Modes, checks and the manual steps:
[`deploy/README.md`](deploy/README.md).

## Repository layout

```text
src/glossator/    corpus adapter, ingest, index, retrieval, answer, surface (what the tools and routes do), eval
src/entrypoints/  FastAPI and MCP servers over glossator.surface (CLIs are python -m glossator.{corpus,ingest,retrieval,answer})
corpus/           vendored corpus, manifest, license, notice
eval/             datasets, committed run directories, corpus stats, replay exports
docs/             architecture, evaluation, retrieval, corpus, stack notes
skills/           the mistral-docs workspace Skill for Mistral Work
deploy/           image, compose file, deploy script, tunnel templates
tests/            offline tests and optional backend integration tests
```

## Read next

- [`docs/evaluation.md`](docs/evaluation.md): the evaluation story, dataset by dataset, with every run linked; [`docs/eval-status.md`](docs/eval-status.md) is the stage-by-stage table.
- [`docs/failure-classes.md`](docs/failure-classes.md): the four classes of question still answered wrong, with question ids, causes, fixes and costs; the refresh gate that decides whether a new docs commit is served is D-045 and `deploy/README.md`.
- [`docs/mcp.md`](docs/mcp.md): the tool contract and the Mistral Work setup; [`docs/architecture.md`](docs/architecture.md): the pipeline in ten lines.
- [`docs/upstream.md`](docs/upstream.md): the defects found in Mistral's packages and documentation, ranked, with where each fix goes.
- [`docs/search-toolkit.md`](docs/search-toolkit.md): the Mistral Search Toolkit kept, wrapped, replaced, skipped.
- [`docs/mistral-stack.md`](docs/mistral-stack.md): every Mistral component with its version, defects and constraints.
- [`docs/api.md`](docs/api.md): the HTTP routes, environment variables and local model servers.
- [`docs/retrieval.md`](docs/retrieval.md): index variants, the retrieval grid, ingestion guards.
- [`docs/corpus.md`](docs/corpus.md): where the corpus comes from and how it is checked.
- [`deploy/README.md`](deploy/README.md): deployment, the tunnel, Connector registration.
- [`DECISIONS.md`](DECISIONS.md): every choice with the facts that decided it; append an entry when a change reverses one.
