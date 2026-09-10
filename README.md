# glossator

glossator gives agents Mistral's documentation: an MCP server with three
read-only tools over the 411 pages of [docs.mistral.ai](https://docs.mistral.ai)
at a pinned commit, a search that returns sections addressed by their
`url#anchor`, whole-page reads, and a history of what changed across dated
snapshots. The agent does the research and writes the answer. A FastAPI
service keeps the generated-answer path, with `[n]` markers and quotes checked
against the retrieved chunks, as the evaluated baseline.

## Try it

The deployed server is at `https://glossator.tomvaucourt.com/mcp` (Streamable
HTTP; the bearer token is supplied on request). The health endpoint
`https://glossator.tomvaucourt.com/health` is open and reports the served
variant, the index counts and the embedding probe.

- Mistral Work: open `Connectors`, click `+ Add Connector`, switch to the
  `Custom MCP Connector` tab and enter the server URL above. Bearer
  authentication is detected automatically; pre-authorize the three read
  functions. The full walkthrough, with the workspace Skill: [`docs/mcp.md`](docs/mcp.md).
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
filesystem and no grep. What they can reach is a Connector. A coding agent with
the SDK checked out can grep a parameter name, but not a rate limit, a price, a
deprecation date, the capability matrix or what changed last month; 54 of the
85 real questions in `eval/mined.jsonl` were asked by people who had the SDK
and still failed (`DECISIONS.md` D-038, D-039). This server gives those agents
the documentation at a pinned commit, addressed by the same `url#anchor` a
reader clicks, plus the one thing the live site cannot show: how a fact
changed over time.

Every choice is in `DECISIONS.md` with the run that decided it. The ones that
shaped the product:

| Decision | Evidence | Entry |
|---|---|---|
| Source the docs repo at a commit, not `llms.txt` or HTML | all 75 `llms.txt` links return 404; rendered HTML is 1.7% text with empty tab panels | D-001 |
| Section chunks with tested anchors, not whole pages | page chunks score section recall 0 and cost twice the tokens at answer time | D-034, D-035a |
| Vector-heavy hybrid weights inside Vespa | best section recall on a 13-configuration grid over 294 questions | D-034 |
| The agent does the research; no generation inside the server | a capable consumer reaches the same correctness with the tools as with a server-side answer (0.77 against 0.78), one model instead of two, a third of the latency, and its own reasoning to reformulate | D-040b, D-044 |
| No reranker on the agent path | it was 91% of a search's latency for rank-1 precision an agent that reads several hits does not need | D-015b |
| Swapping the generator changes nothing | Medium 3.5 replayed on the recorded prompts: correctness unchanged within the interval on four sets | D-017b |
| Three tools, addressed by `url#anchor`, no ids | 97% of pages fit one read under 8,000 tokens; the Work session never used the other five tools | D-043, D-044 |
| Read-only tool annotations | without them Work asks for approval on every call and a headless consumer never calls at all | D-037b, D-037c |
| A time axis: eight biweekly snapshots and a history tool | the docs renamed their API section in August; `-latest` aliases moved under users' feet | D-041, D-041a |
| Judges: GLM 5.3 primary, checked against four judges and 40 human labels | every primary-judge disagreement with the reader is in the strict direction, so its numbers are floors | D-021a, D-021b, D-021c |

### Why not the alternatives

**Put the whole documentation in a 1M context.** The corpus is 765,646 tokens
in Medium 3.5's tokenizer (`eval/corpus-stats/`). It does not fit Medium 3.5's
256k window, and Work runs on Medium 3.5. It fits the 1M window of Z.ai GLM 5.2,
which Mistral serves at 1.4 USD per million input tokens, 0.14 cached: about
1.07 USD per question uncached and 0.11 cached, against about 0.005 for the
agent path, with no section link behind any claim and no way to say the
documentation does not answer. A search returns the right thousand tokens of
the right page; that is the whole trade.

**Old-school RAG: retrieve, stuff, generate inside the server.** This
repository built it, measured it, and keeps it as the baseline (`POST /ask`).
On the same questions a capable agent given search and read tools reaches the
same correctness (0.77 against 0.78) at a third of the latency, with one model
instead of two, and it can reformulate when the first search misses, which is
where the server-side loop won on badly worded questions (D-035b, D-040b). The
generator was not the ceiling either: Medium 3.5 in place of Ministral 3 14B
moved nothing (D-017b). What is left in the server is what an agent cannot do
for itself: a pinned corpus, tested section anchors, and history.

**Mistral's own retrieval: Libraries and web search.** Libraries index uploaded
files for an agent's `document_library` tool and cite the document; they do not
know docs.mistral.ai's section anchors, a commit, or what changed since June.
Web search finds the live page: a consumer with its own web search resolved
links well (0.86) and answered at 0.52 to 0.58, against 0.77 with these tools
(D-040b). The live site also has no history, and its `llms.txt` points at 75
pages that return 404 (D-001).

What was kept from the Mistral Search Toolkit, what was wrapped, replaced or
skipped, and why, is in `docs/search-toolkit.md`; every Mistral component with
its version, defects and constraints is in `docs/mistral-stack.md`; the state
of the evaluation in one page is `docs/eval-status.md`.

## Evaluation in five lines

- The generated-answer baseline scores 0.93, 0.84 and 0.76 judged correctness on 60 tuned, 60 fresh and 85 mined questions, with Ministral 3 14B generating and GLM 5.3 judging blind ([`docs/evaluation.md`](docs/evaluation.md)).
- Mistral Medium 3.5 replayed over the same recorded prompts (GLM 5.3 judging blind) changes correctness by at most four points, inside the interval, and halves fabricated quotes: the generator is not the ceiling ([`docs/evaluation.md`](docs/evaluation.md)).
- Claude Sonnet at low effort answers 0.77 with the three tools against 0.78 with the server-side answer at three times the latency, judged blind by GLM 5.3 ([`docs/evaluation.md`](docs/evaluation.md)).
- Across 575 answers (Ministral 3 14B, verdicts by GLM 5.3), 47% of failures are the generator's, 1 to 3% retrieval misses, none context misses ([`docs/evaluation.md`](docs/evaluation.md)).
- Every evaluation is a committed directory under `eval/runs/` with its records, calls, metrics and figures, so each number traces to the model output that produced it ([`docs/evaluation.md`](docs/evaluation.md)).

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

The API listens on `127.0.0.1:8080`; the MCP HTTP transport on
`127.0.0.1:8000/mcp` (override with `host=` and `port=`; the stdio transport
runs with `uv run python -m entrypoints.mcp_server`). Mistral Medium 3.5 is the
shipped generation default; the key this repository was built with had no
quota for it (D-017a), so the recorded runs use `ministral-14b-2512` and Medium
was measured by replay (D-017b). Environment variables and
local model servers are listed in [`docs/api.md`](docs/api.md).

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
