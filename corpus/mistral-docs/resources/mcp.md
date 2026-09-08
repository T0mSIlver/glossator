---
url: https://docs.mistral.ai/resources/mcp
title: MCP
breadcrumbs: [Resources]
kind: doc
locale: en
source_path: src/content/en/docs/resources/mcp/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# MCP

The Mistral MCP server connects an AI agent to your Studio workspace over the [Model Context Protocol](https://modelcontextprotocol.io). It exposes your workspace as MCP tools and authenticates each request with your Mistral API key.

Use it from wherever your agent runs: a coding CLI, an IDE, a desktop assistant, or your own application.

| | |
|---|---|
| **Endpoint** | `https://api.mistral.ai/mcp` |
| **Transport** | Streamable HTTP |
| **Authentication** | `Authorization: Bearer <MISTRAL_API_KEY>` |

## Before you begin {#before-you-begin}

- A Mistral [API key](https://docs.mistral.ai/admin/identity-access/api-keys). Keys are workspace-scoped, so the agent gets the access that key already has.
- An MCP client that supports the streamable HTTP transport and static request headers.

Export the key in the environment that launches your client:

```bash
export MISTRAL_API_KEY="your_api_key"
```

## Connect a client {#connect}

**Vibe Code CLI**

```bash
vibe mcp add mistralai \
  --url https://api.mistral.ai/mcp \
  --transport streamable-http \
  --api-key-env MISTRAL_API_KEY
```

This writes the entry to `~/.vibe/config.toml`:

```toml
[[mcp_servers]]
name = "mistralai"
transport = "streamable-http"
url = "https://api.mistral.ai/mcp"

[mcp_servers.auth]
type = "static"
api_key_env = "MISTRAL_API_KEY"
```

The configuration stores the variable name and the environment holds the key. Run `/mcp mistralai` in a session to list the tools. See [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for permissions and tool filtering.

**Claude Code**

```bash
claude mcp add --transport http mistral https://api.mistral.ai/mcp \
  --header 'Authorization: Bearer ${MISTRAL_API_KEY}'
```

Run `/mcp` to check the connection.

**Codex**

```bash
codex mcp add mistral \
  --url https://api.mistral.ai/mcp \
  --bearer-token-env-var MISTRAL_API_KEY
```

This writes the entry to `~/.codex/config.toml`:

```toml
[mcp_servers.mistral]
url = "https://api.mistral.ai/mcp"
bearer_token_env_var = "MISTRAL_API_KEY"
```

Run `codex mcp list` to check the connection.

**Other clients**

Clients such as Cursor read a JSON block:

```json
{
  "mcpServers": {
    "mistral": {
      "type": "http",
      "url": "https://api.mistral.ai/mcp",
      "headers": {
        "Authorization": "Bearer ${MISTRAL_API_KEY}"
      }
    }
  }
}
```

Each client has its own config path and its own rules for expanding `${...}`. Check its documentation, then reload the client and open its tool list to check the connection.

**cURL**

Probe the endpoint to confirm the key works. The server replies as a server-sent event stream:

```bash
curl https://api.mistral.ai/mcp \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

## What the server exposes {#tools}

**Skills**, the reusable instruction sets you manage in [Skills](https://console.mistral.ai/build/skills). An agent browses the workspace catalog, reads a Skill and the files shipped with it, creates a new Skill version, changes who it is shared with, or deletes it. A Skill written from your editor appears in Studio, and a Skill written in Studio is available to the agent.

Skills is the first capability, and more follow. The server lists the tools available to your key, so ask your client for its tool list, or call `tools/list`. Each tool describes its own arguments.

## Access and permissions {#permissions}

Every call uses your API key's permissions.

Some tools write: they add Skill versions, change sharing, and delete Skills. Configure per-tool approval in your client to review those calls before they run.

## Troubleshooting {#troubleshooting}

| Problem | Cause | Solution |
|---|---|---|
| `401 {"detail":"Invalid API Key"}` | The key is missing, misspelled, or revoked. | Export the variable in the environment that launches your client, and check the key is active in the console. |
| A tool call returns a permission error. | The operation requires additional workspace access. | Ask a workspace admin for the matching access, then retry. |

## Next steps {#next-steps}

- [Create a Skill in Studio](https://docs.mistral.ai/getting-started/quickstarts/studio/create-skill) to give the agent something to work with.
- [MCP servers in the Vibe Code CLI](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for per-tool permissions and filtering.
- [API keys](https://docs.mistral.ai/admin/identity-access/api-keys) to create and rotate the key you connect with.
