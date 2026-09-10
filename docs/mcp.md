# The MCP surface

`make mcp` starts the streamable HTTP transport. Run the module without
`--http` for stdio:

```bash
uv run python -m entrypoints.mcp_server
```

The server is named `mistral-docs` and exposes three read-only tools. The agent
calling them does the research and writes the answer; nothing generates text
inside the server (`DECISIONS.md` D-044).

| Tool | Purpose |
|---|---|
| `mistral_docs_search(q, max_hits=5, kind)` | The sections that state something: one hit per section with its `url#anchor`, heading path and snippet. |
| `mistral_docs_read_page(page_url, section)` | A whole page in reading order, or one section of a large page with its neighbours. |
| `mistral_docs_history(text \| section \| question)` | When a phrase appeared, how a section changed across the dated snapshots, or what a question retrieved on each date. |

Every hit and every section is addressed by its `url#anchor` on
docs.mistral.ai, which is also the citation; there is no other identifier for a
model to carry. 97% of pages fit one `read_page` call whole
([`../eval/corpus-stats/`](../eval/corpus-stats/)); a hit on one of the dozen
larger pages names the section to pass. Every tool is annotated read-only,
idempotent and closed-world, so a host can call one without asking (D-037b,
D-037c). Unknown parameters are rejected with `E_BAD_PARAM` naming the likely
one, and host-supplied arguments whose name starts with an underscore are
dropped.

The MCP server cannot ingest or delete content. Corpus changes go through the
adapter, manifest checks, and ingestion command. `GLOSSATOR_MCP_TOOLS` names a
subset of the three tools to register, which the consumer evaluation uses to
serve one arm per deployment.

The generated answer with verified quotes, the listwise reranker and the search
loop remain in the package and the HTTP API (`POST /ask`, `POST /cite`) as the
measured context-injection baseline the agent path is compared against
(D-040b, D-017b); they are not on the MCP surface. Routes and inputs:
[`api.md`](api.md).

## Mistral Work

Serve the MCP server over HTTP behind a tunnel, then register it as a custom
MCP Connector. From the documentation page on MCP Connectors, in its exact
words:

1. Open the `Connectors` page.
2. Click `+ Add Connector` and switch to the `Custom MCP Connector` tab.
3. Fill in the required fields:
   - **Connector name**: a unique identifier (no spaces or special characters).
   - **Server URL**: the full URL of your MCP-compatible server.
   - **Description** (optional): a short explanation of what this Connector does.
4. Click `Connect`. The platform detects the server's authentication method automatically.

Authentication, again in the page's exact words:

> Our platform auto-detects the authentication method when you provide the server URL:
>
> - **No authentication**: for publicly accessible or trusted internal servers.
> - **HTTP Bearer Token / Basic Auth**: for servers that require credentials in the `Authorization` header.
> - **OAuth 2.1** (with dynamic client registration): for servers using standard OAuth 2.1 delegated access. You'll be guided through the consent flow.

Set `GLOSSATOR_MCP_TOKEN` on the server. Every MCP HTTP request must then
carry `Authorization: Bearer <token>`; requests without it get a 401 naming the
missing header. Work detects "bearer" automatically when registering the
Connector. Pre-authorize the three read functions per Connector so they run
without approval prompts; the server exposes no write functions. `GET /health`
needs no header and reports the served variant, the page and chunk counts,
whether the embedding probe passed, and the registered tool names, so the
Connectors Debugger and the tunnel can check the server. `GET /` is a landing
page and `/favicon.svg` the icon, both open.

`skills/mistral-docs/SKILL.md` is a workspace Skill for documentation
questions: search first with the mistral-docs connector, read the page behind
the best hit, link the section behind each claim, use the history tool for
"when did this change" questions, and say when the documentation does not
answer. Its `README.md` explains how to add it as a workspace Skill, and
`custom-instructions.md` holds two sentences a workspace admin can paste into
`Context` > `Instructions`. Custom MCP Connectors do not read MCP resources or
prompts, so the rules reach Work through the tool descriptions and the Skill.
