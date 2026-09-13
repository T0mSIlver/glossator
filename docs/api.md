# HTTP API

Run `make api`, then open `/docs` for Swagger UI or `/openapi.json` for the
schema.

| Route | Input | Output |
|---|---|---|
| `POST /ask` | `question`; optional `strategy`, `variant`, `model` | answer Markdown, verified citations, the rendered `sources_markdown` block, trace, usage, cost, latency |
| `POST /search` | `query`; optional `top_k`, `kinds`, `locales`, `exclude_ids`, `variant` | ranked hits with citation URL, heading path, preview, score, ID, and offsets |
| `POST /cite` | `draft`, `quotes` (`n`, `quote`, plus `chunk_id` or page `url`); optional `variant` | per-quote verdicts, uncovered markers, deduplicated sources, the rendered `sources_markdown` block |
| `GET /pages/{path}` | documentation path; optional `variant`, `start_offset`, `top_k` | up to 100 page sections in reading order; `truncated` says whether more exist |
| `GET /history` | one form: `text` (optionally with `page_url` or `under`), `page_url` (optionally with `section`), or `under` (optionally with `since`) | a phrase's first and last stored snapshot, a page or section's state and diff, or changes below a path, validated by the same rules as `mistral_docs_history` |
| `GET /health` | none | Vespa counts, corpus commit, readable snapshot count, and embedding-probe status |
| `GET /version` | none | package version, variants, and allowed generation models |

Every error uses `{"error":{"code","message","next"}}`. Unknown field names are
rejected with a suggestion for the right one. Clients can send `X-Request-Id`;
the API echoes it in the response header, the `/ask` body, and error bodies.
When the header is absent, the API creates an ID. When `GET /pages` answers
`truncated: true`, continue from the last returned section's `end_offset`:

```bash
curl -s "http://127.0.0.1:8080/pages/api/endpoint/chat?start_offset=2480&top_k=100"
```

```bash
curl -s http://127.0.0.1:8080/search \
  -H 'content-type: application/json' \
  -d '{"query":"streaming chat completions","top_k":3}'

curl -s http://127.0.0.1:8080/ask \
  -H 'content-type: application/json' \
  -d '{"question":"How do I stream a chat completion?","model":"ministral-14b-2512"}'
```

## Environment and local servers

`.env` holds secrets, ports, and service endpoints only; `.env.example` lists
every variable with its default. Recognised settings are `MISTRAL_API_KEY`,
`MISTRAL_API_URL` (the embedding endpoint), `VESPA_QUERY_PORT`,
`VESPA_CONFIG_PORT`, `VESPA_ENDPOINT`, `VESPA_CONFIG_URL`, and `WORKSPACE_ROOT`
(used by the Bruno API export). The retrieval engine reads
`GLOSSATOR_RERANK_MODEL` for the reranker (default `mistral-small-2603`). The
API server also reads `GLOSSATOR_CORPUS_DIR` and `GLOSSATOR_MODEL` (the
generation model for `POST /ask` when the request names none; blank uses the
shipped default), and the MCP server reads `GLOSSATOR_VARIANT`,
`GLOSSATOR_CORPUS_DIR`, `GLOSSATOR_MCP_TOKEN`, and `GLOSSATOR_MCP_TOOLS`. Both read
`GLOSSATOR_SNAPSHOT_MANIFEST` for the `history` forms. Do not put schema names in
`.env`.

Chat completions -- the answer model, the listwise reranker, and the translation
and rewrite calls -- go to a local OpenAI-compatible server when
`GLOSSATOR_CHAT_SERVER_URL` is set, with `GLOSSATOR_CHAT_API_KEY` if it wants a
key, `GLOSSATOR_CHAT_REASONING_EFFORT` to set or disable its thinking, and
`GLOSSATOR_CHAT_SAMPLING` (`temperature`, `top_p` and `min_tokens` as `key=value`
pairs) to override the pipeline's sampling. Embeddings always go to the Mistral API. Every run records which server and
which effort it used.

## Running locally

The project runs on Python 3.12 to 3.14; on a first run `uv sync` downloads the
packages and, if none of those Pythons is installed, an interpreter, which the
five minutes do not include.

`make setup-vespa` starts Vespa with its query API on `localhost:18080` and its
config server on `localhost:19072`, deploys the schemas, then waits for the
query API, which comes up a minute or so after the config server on a new
container. `make ingest` splits the 411 pages into 4,440 section chunks and
embeds them with `mistral-embed`: about one million tokens, about 0.10 USD
(D-011a). On the free tier the embedding API rate-limits the run, so it takes a
few minutes; embeddings are cached under `~/.cache/glossator/embeddings`, or
`GLOSSATOR_EMBEDDING_CACHE`, so a re-run after a rate-limit failure only embeds
what is missing. Add `verbose=1` for the chunker's debug log. A second checkout
on the same machine sets its own `VESPA_CONTAINER`, `VESPA_QUERY_PORT` and
`VESPA_CONFIG_PORT` in `.env`.

`make ask` calls two models: the generation model named by `model=` (Mistral
Medium 3.5 when omitted) and the reranker, `mistral-small-2603` by default and
overridable with `GLOSSATOR_RERANK_MODEL`. A key without Mistral Small quota sets
`GLOSSATOR_RERANK_MODEL=ministral-14b-2512` in `.env`. The printed cost covers
both calls.

`make api` and `make mcp` take `host=` and `port=` to override their addresses.
Connect an MCP client to the server rather than writing the Streamable HTTP
handshake by hand, for example Claude Code or
`npx @modelcontextprotocol/inspector` pointed at `http://127.0.0.1:8000/mcp`. The
local MCP server accepts any client until `GLOSSATOR_MCP_TOKEN` is set, which
matters once it listens on anything but `127.0.0.1`. Run the stdio transport with
`uv run python -m entrypoints.mcp_server`. The history tool reads the vendored
`corpus/snapshots/` directories, so the five-minute start needs no snapshot step.

`make test` runs the offline tests; `make test-all` adds the container image
build. With Vespa up and `MISTRAL_API_KEY` set, `make test` also runs the
integration tests: they embed a fixture corpus, a fraction of a cent per run, and
write its pages into the `sec128` and `page128` schemas of the Vespa on
`localhost:18080`. Without Vespa or the key those tests skip.

Mistral Medium 3.5 is the generation default. The project API key had zero
quota for Medium 3.5 and Small 4 until 12 September 2026 (D-017a, D-049), so
the reported API runs use `ministral-14b-2512`, D-017c measures Medium 3.5 by
replay on the API, and the demo run of D-049a is the first on Medium 3.5 end to end.
