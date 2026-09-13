# glossator

glossator is a Model Context Protocol (MCP) server that gives agents Mistral's documentation: 411 pages from a pinned [docs.mistral.ai](https://docs.mistral.ai) commit.
The agent you already use, in Work, the Vibe CLI, Claude Code, or a bot, queries the documentation mid-task instead of going through a separate RAG system or a copy of the docs uploaded into every agent and every chat.
It searches sections, reads pages and compares dated snapshots through three read-only tools, then writes the answer and cites the link each tool prints beside the text.

## Try it

The deployed server is `https://glossator.tomvaucourt.com/mcp` (Streamable HTTP; the bearer token is supplied on request).
It announces itself as `mistral-docs` and its tools as `mistral_docs_*`.

```bash
claude mcp add --transport http mistral-docs https://glossator.tomvaucourt.com/mcp --header "Authorization: Bearer <token>"
```

In the Vibe CLI, append a server to `config.toml`; `name` becomes the prefix of the tool names ([MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers#add)):

```toml
[[mcp_servers]]
name = "mistral_docs"
transport = "streamable-http"
url = "https://glossator.tomvaucourt.com/mcp"
headers = { "Authorization" = "Bearer <token>" }
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

- The generated-answer baseline scores 0.93, 0.84 and 0.76 on the tuned, fresh and mined sets. Ministral 3 14B generated; GLM 5.3 judged without seeing the configuration. Medium 3.5 replayed on Mistral's API cut fabricated quotes per answer from 0.40–0.59 to 0.17–0.19 on all four sets, at 0.0045 to 0.0061 USD per question; judged correctness is 0.90, 0.82, 0.73 and 0.65, inside the interval of the 14B's (D-017c).
- Sonnet scored 0.77 with the retrieval tools and 0.78 with server-side generation, which took three times as long. The run predates the three-tool cut.
- Across 575 answers, generation caused 77 of 164 failures. Retrieval misses were 1% to 3% on well-written questions; no context misses occurred.
- The demo itself, measured where it runs: Medium 3.5 at high reasoning through the Work Connector and the Skill scored 0.60 on thirty questions, 0.80 on the five that need the history tool and 0.20 on the five the documentation cannot answer, where it fills the gap; GLM 5.3 judged (D-049a).
- Tool results are most of a session's tokens, so a read prints one language tab, no repeated sample and no pasted output beyond its head: 36% fewer characters per read on the same thirty questions, correctness 0.62 against 0.60, inside the noise of two runs (D-050, D-050a). On the shipped server with the scoped history forms and vendored snapshots the thirty score 0.60 again: 0.80 on the history rows, 0.40 on the unanswerable ones, 4,309 characters per tool result (D-049b).

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

Everything else, including the repository layout and deployment, is indexed in [`docs/README.md`](docs/README.md).
