# HTTP API

Run `make api`, then open `/docs` for Swagger UI or `/openapi.json` for the
schema.

| Route | Input | Output |
|---|---|---|
| `POST /ask` | `question`; optional `strategy`, `variant`, `model` | answer Markdown, verified citations, the rendered `sources_markdown` block, trace, usage, cost, latency |
| `POST /search` | `query`; optional `top_k`, `kinds`, `locales`, `exclude_ids`, `variant` | ranked hits with citation URL, heading path, preview, score, ID, and offsets |
| `POST /cite` | `draft`, `quotes` (`n`, `quote`, plus `chunk_id` or page `url`); optional `variant` | per-quote verdicts, uncovered markers, deduplicated sources, the rendered `sources_markdown` block |
| `GET /pages/{path}` | documentation path; optional `variant`, `start_offset`, `top_k` | up to 100 page sections in reading order; `truncated` says whether more exist |
| `GET /history` | `text` with an optional page or path, `page_url` with an optional section, or `under` with an optional date | a phrase's first and last stored snapshot, a page or section's state and diff, or changes below a path |
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
API server also reads `GLOSSATOR_CORPUS_DIR`, and the MCP server reads
`GLOSSATOR_VARIANT`, `GLOSSATOR_CORPUS_DIR`, `GLOSSATOR_MCP_TOKEN`, and
`GLOSSATOR_MCP_TOOLS`. Both read `GLOSSATOR_SNAPSHOT_MANIFEST` for the `history`
forms. Do not put schema names in `.env`.

Chat completions -- the answer model, the listwise reranker, and the translation
and rewrite calls -- go to a local OpenAI-compatible server when
`GLOSSATOR_CHAT_SERVER_URL` is set, with `GLOSSATOR_CHAT_API_KEY` if it wants a
key, `GLOSSATOR_CHAT_REASONING_EFFORT` to set or disable its thinking, and
`GLOSSATOR_CHAT_SAMPLING` (`temperature`, `top_p` and `min_tokens` as `key=value`
pairs) to override the pipeline's sampling. Embeddings always go to the Mistral API. Every run records which server and
which effort it used.

Mistral Medium 3.5 is the shipped generation default. The project key had a zero
request quota for that model until 12 September 2026, so most recorded checks and
evaluations use `ministral-14b-2512` (D-017a).
