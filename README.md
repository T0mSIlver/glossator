# glossator

glossator gives agents Mistral's documentation through a Model Context Protocol
(MCP) server. It exposes three read-only tools over 411 pages from a pinned
[docs.mistral.ai](https://docs.mistral.ai) commit. Search results use the page's
`url#anchor`; the other tools read whole pages and compare dated snapshots.
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
| `mistral_docs_search(q, max_hits=5, kind)` | The sections that state something: one hit per section with its `url#anchor`, heading path and snippet. |
| `mistral_docs_read_page(page_url, section)` | A whole page in reading order, or one section of a large page with its neighbours. |
| `mistral_docs_history(text \| section \| question)` | When a phrase appeared, how a section changed across the dated snapshots, or what a question retrieved on each date. |

## Why an MCP server, and what decided its shape

Agents inside Mistral Work, Le Chat, scheduled tasks and chat bots have no
filesystem or `grep`. They can reach external systems through Connectors. A
coding agent can search an SDK checkout for a parameter name, but product facts
often live elsewhere.

This gap appears in `eval/mined.jsonl`. Of its 85 real questions, 54 came from
GitHub issues opened by SDK users (`DECISIONS.md` D-038, D-039). The server
provides documentation from a pinned commit and returns the same `url#anchor`
that a reader opens. Snapshot search also shows when a fact changed.

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
| Three tools, addressed by `url#anchor`, no ids | 97% of pages fit one read under 8,000 tokens; the Work session never used the other five tools | D-043, D-044 |
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
- Each directory under `eval/runs/` stores its inputs, model calls, records, metrics and figures.

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

The API listens on `127.0.0.1:8080`. MCP uses `127.0.0.1:8000/mcp` by default;
override it with `host=` and `port=`. Run the stdio transport with
`uv run python -m entrypoints.mcp_server`.

Mistral Medium 3.5 is the generation default. The project API key had zero
quota for Medium 3.5 and Small 4 (D-017a). The reported API runs therefore use
`ministral-14b-2512`; D-017b measures Medium 3.5 by replay. See
[`docs/api.md`](docs/api.md) for environment variables and local model servers.

## Deployment

`deploy/` puts the server on a Linux host behind a Cloudflare tunnel in one
command (`make deploy HOST=<ssh-host>`). Modes, checks and the manual steps:
[`deploy/README.md`](deploy/README.md).

## Repository layout

```text
src/glossator/    corpus adapter, ingest, index, retrieval, answer, eval
src/entrypoints/  FastAPI and MCP servers (CLIs are python -m glossator.{corpus,ingest,retrieval,answer})
corpus/           vendored corpus, manifest, license, notice
eval/             datasets, committed run directories, corpus stats, replay exports
docs/             architecture, evaluation, retrieval, corpus, stack notes
skills/           the mistral-docs workspace Skill for Mistral Work
deploy/           image, compose file, deploy script, tunnel templates
tests/            offline tests and optional backend integration tests
```

## Read next

- [`docs/evaluation.md`](docs/evaluation.md): the evaluation story, dataset by dataset, with every run linked; [`docs/eval-status.md`](docs/eval-status.md) is the stage-by-stage table.
- [`docs/mcp.md`](docs/mcp.md): the tool contract and the Mistral Work setup; [`docs/architecture.md`](docs/architecture.md): the pipeline in ten lines.
- [`docs/upstream.md`](docs/upstream.md): the defects found in Mistral's packages and documentation, ranked, with where each fix goes.
- [`docs/search-toolkit.md`](docs/search-toolkit.md): the Mistral Search Toolkit kept, wrapped, replaced, skipped.
- [`docs/mistral-stack.md`](docs/mistral-stack.md): every Mistral component with its version, defects and constraints.
- [`docs/api.md`](docs/api.md): the HTTP routes, environment variables and local model servers.
- [`docs/retrieval.md`](docs/retrieval.md): index variants, the retrieval grid, ingestion guards.
- [`docs/corpus.md`](docs/corpus.md): where the corpus comes from and how it is checked.
- [`deploy/README.md`](deploy/README.md): deployment, the tunnel, Connector registration.
- [`DECISIONS.md`](DECISIONS.md): every choice with the facts that decided it; append an entry when a change reverses one.
