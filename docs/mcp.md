# MCP server

`make mcp` starts the streamable HTTP transport. Run the module without
`--http` for stdio:

```bash
uv run python -m entrypoints.mcp_server
```

The server is named `mistral-docs` and exposes three read-only tools. The calling
agent researches and writes the answer. No model writes an answer inside the
MCP server (D-044).

| Tool | Purpose |
|---|---|
| `mistral_docs_search(q, max_hits=5, under)` | The sections that state something: one hit per section with its key, heading path, snippet and the link to cite. `under` keeps the hits to the pages under a URL, or lists those pages when `q` is empty. |
| `mistral_docs_read_page(page_url, section)` | A whole page in reading order, or one section by its key; a read that stops early names the key to continue at. |
| `mistral_docs_history(text \| page_url + section \| under + since)` | When a phrase appeared, how a page or section changed, or what changed under a path between stored dates. |

Every section has a key: the heading's anchor when it has one, otherwise a
generated `ancestor-anchor/heading-slug` name. A hit or a section header prints
the key and, on a `cite:` line, the link to cite: `url#anchor`, plus a
`:~:text=` fragment when the text sits more than a screen below where the
anchor lands (D-047). Models copy the key and the link; they never build
either, and never need a chunk ID. A single `read_page` call holds 399
of 411 pages, or 97.08%
([`../eval/corpus-stats/`](../eval/corpus-stats/)). Search results for the other
12 pages name the section to read.

Tools are marked read-only and safe to repeat. They are also marked as unable
to access anything outside the documentation corpus. These annotations prevent
unnecessary approval prompts (D-037b, D-037c). Unknown parameters return
`E_BAD_PARAM` with a likely replacement. Work's undeclared arguments beginning
with an underscore are ignored.

The MCP server cannot ingest or delete content. Corpus changes go through the
adapter, manifest checks and ingestion command. `GLOSSATOR_MCP_TOOLS` can
register a subset of the three tools.

The package and HTTP API retain generated answers, quote checks, model-based
result reordering and the multi-search answer strategy. `POST /ask` and
`POST /cite` expose that evaluated baseline (D-040b, D-017b). None is an MCP
tool. [`api.md`](api.md) lists the routes and inputs.

The D-040b consumer run predates D-044. Its retrieval configuration included
the retired quote-verification tool. It motivated the three-tool design but did
not evaluate this exact tool set.

## Mistral Work

Serve the MCP endpoint over HTTPS, then register it as a custom MCP Connector:

1. Open the `Connectors` page.
2. Click `+ Add Connector` and switch to the `Custom MCP Connector` tab.
3. Enter a unique connector name without spaces or special characters.
4. Enter the full MCP server URL and an optional description.
5. Click `Connect`. Work detects the authentication method from the server.

Set `GLOSSATOR_MCP_TOKEN` on the server. MCP requests must then carry
`Authorization: Bearer <token>`. A missing header returns HTTP 401. Work detects
bearer authentication during registration.

Pre-authorise all three functions to avoid approval prompts. The server has no
write functions. `GET /health` needs no header. It reports the index variant,
page and chunk counts, embedding probe and registered tools. `GET /` and
`/favicon.svg` are also public.

`skills/mistral-docs/SKILL.md` tells Work how to use the connector. It searches
first, reads the best page and links each claim to a returned section. It uses
history for change questions and refuses when the documentation lacks an
answer.

The Skill's `README.md` explains workspace installation.
`custom-instructions.md` contains the shorter workspace instructions. Work does
not read MCP resources, prompts or changing tool lists. The server therefore
puts essential rules in tool descriptions, with the Skill supplying the full
workflow (D-037a).
