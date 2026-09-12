# mined2-049 (cross_page, 2 connector calls)

## Question

Which transports can an MCP server use with the Vibe CLI, and how are its tools named for permissions?

## Thinking

The user is asking about MCP (Model Context Protocol) server transports for the Vibe CLI and how tools are named for permissions. This is a specific technical question about Mistral AI's Vibe CLI integration with MCP servers.

I need to search the Mistral documentation for information about:
1. What transports MCP servers can use with Vibe CLI
2. How tools are named for permissions in this context

Let me start by searching for MCP server transports in the Vibe CLI documentation.

The search results show that there's a page about MCP servers in the Vibe CLI documentation. The first hit mentions "Supported transports" and lists `http`, `streamable-http`, and `stdio`. This directly answers the first part of the question.

Now I need to find information about how tools are named for permissions. Let me read the full page to get more details.

Perfect! I now have the complete information from the documentation. Let me analyze what I found:

1. **Transports**: The documentation clearly states that MCP servers with Vibe CLI support three transports:
   - `http` - for servers reachable over standard HTTP
   - `streamable-http` - for servers reachable over HTTP with streaming responses
   - `stdio` - for local processes started from a command

2. **Tool naming for permissions**: The documentation states that MCP tools are exposed under the pattern `{server_name}_{tool_name}`. This means if you have a server named "fetch_server" with a tool named "get", the full tool name would be `fetch_server_get`.

The documentation also shows examples of how to configure permissions:
```toml
[tools.fetch_server_get]
permission = "always"

[tools.my_http_server_query]
permission = "ask"
```

And it mentions that you can use `enabled_tools` and `disabled_tools` to filter which MCP tools are active, supporting exact names, glob patterns, and regex.

So the answer is:
- Transports: http, streamable-http, stdio
- Tool naming pattern: `{server_name}_{tool_name}`

Now I need to format this answer properly with citations to the documentation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "MCP server transports Vibe CLI", "max_hits": 5}
```

Result:

```
q: "MCP server transports Vibe CLI"

[1] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: transports
    MCP servers > Supported transports
    | Transport | Use it when | |---|---| | `http` | The server is reachable over standard HTTP. | | `streamable-http` | The server is reachable over HTTP and supports streaming responses. | | `stdio` | The server is a local process you start from a command. |
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#transports

[2] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: browse
    MCP servers > Browse MCP servers from the CLI
    From a CLI session: ```text /mcp ``` Pass a server name to list its tools: ```text /mcp fetch_server ``` > **Note** > > `/connectors` is an alias for `/mcp`.
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#browse

[3] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: fields
    MCP servers > Common fields
    | Field | Purpose | |---|---| | `name` | Short alias for the server. Used as a prefix in tool names. | | `transport` | One of `http`, `streamable-http`, or `stdio`. | | `url` | Base URL for HTTP transports. | | `command` / `args` | Command and arguments for the stdio transport. | | `headers` | Extra HTTP headers for HTTP transports. | | `api_key_env` | Environment variable that holds the API key. …
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#fields

[4] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: mcp-servers
    MCP servers
    MCP servers extend the Vibe Code CLI with **external tools** through the [Model Context Protocol](https://modelcontextprotocol.io). You configure them in `config.toml` under `mcp_servers`, then their tools become available to Vibe like any built-in tool. MCP servers are **user-configured**. For Mistral-managed integrations, see [Connectors](https://docs.mistral.ai/vibe/code/cli/connectors) instead …
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers

[5] https://docs.mistral.ai/vibe/code/cli/configuration-reference | section: mcp-servers
    Configuration reference > MCP servers (`[[mcp_servers]]`)
    One `[[mcp_servers]]` table per server. Required fields depend on the `transport` (`http`, `streamable-http`, or `stdio`). | Key | Type | Default | Description | |---|---|---|---| | `name` | string | Required | Short alias; prefixes this server's tool names | | `transport` | string | Required | One of `http`, `streamable-http`, or `stdio` | | `url` | string | | Base URL for HTTP transports | | `co …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference#mcp-servers

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/mcp-servers") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/mcp-servers"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/mcp-servers | "MCP servers"

## section: mcp-servers
    MCP servers
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers
# MCP servers

MCP servers extend the Vibe Code CLI with **external tools** through the [Model Context Protocol](https://modelcontextprotocol.io). You configure them in `config.toml` under `mcp_servers`, then their tools become available to Vibe like any built-in tool.

MCP servers are **user-configured**. For Mistral-managed integrations, see [Connectors](https://docs.mistral.ai/vibe/code/cli/connectors) instead.

> **Info**
>
> **Known limitation:** the CLI does not yet support MCP servers that require OAuth authentication. Use the `stdio` or `http` transport with an API key or other static credential.

## section: transports
    MCP servers > Supported transports
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#transports
## Supported transports {#transports}

| Transport | Use it when |
|---|---|
| `http` | The server is reachable over standard HTTP. |
| `streamable-http` | The server is reachable over HTTP and supports streaming responses. |
| `stdio` | The server is a local process you start from a command. |

## section: add
    MCP servers > Add an MCP server
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#add
## Add an MCP server {#add}

Append a `[[mcp_servers]]` table to `config.toml`. Required fields depend on the transport.

**HTTP**

```toml
[[mcp_servers]]
name = "my_http_server"
transport = "http"
url = "http://localhost:8000"
headers = { "Authorization" = "Bearer my_token" }
api_key_env = "MY_API_KEY_ENV_VAR"
api_key_header = "Authorization"
api_key_format = "Bearer {token}"
```

**Streamable HTTP**

```toml
[[mcp_servers]]
name = "my_streamable_server"
transport = "streamable-http"
url = "http://localhost:8001"
headers = { "X-API-Key" = "my_api_key" }
```

**Local process (stdio)**

```toml
[[mcp_servers]]
name = "fetch_server"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
env = { "DEBUG" = "1", "LOG_LEVEL" = "info" }
```

## section: fields
    MCP servers > Common fields
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#fields
## Common fields {#fields}

| Field | Purpose |
|---|---|
| `name` | Short alias for the server. Used as a prefix in tool names. |
| `transport` | One of `http`, `streamable-http`, or `stdio`. |
| `url` | Base URL for HTTP transports. |
| `command` / `args` | Command and arguments for the stdio transport. |
| `headers` | Extra HTTP headers for HTTP transports. |
| `api_key_env` | Environment variable that holds the API key. |
| `env` | Environment variables passed to the server process (stdio). |
| `startup_timeout_sec` | How long to wait for the server to start. |
| `tool_timeout_sec` | How long to wait for a tool call to complete. |

## section: permissions
    MCP servers > Tool naming and permissions
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#permissions
## Tool naming and permissions {#permissions}

MCP tools are exposed under the pattern `{server_name}_{tool_name}`. Configure permissions per tool just like built-in tools:

```toml
[tools.fetch_server_get]
permission = "always"

[tools.my_http_server_query]
permission = "ask"
```

You can also restrict which MCP tools are active using `enabled_tools` and `disabled_tools`:

```toml
# Only enable serena's tools
enabled_tools = ["serena_*"]

# Disable all MCP tools and grep
disabled_tools = ["mcp_*", "grep"]
```

Filters support **exact names**, **glob patterns**, and **regex** with the `re:` prefix.

## section: browse
    MCP servers > Browse MCP servers from the CLI
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#browse
## Browse MCP servers from the CLI {#browse}

From a CLI session:

```text
/mcp
```

Pass a server name to list its tools:

```text
/mcp fetch_server
```

> **Note**
>
> `/connectors` is an alias for `/mcp`.

Results: 6 sections, the whole page.
```

## Answer

The Vibe CLI supports **three transports** for MCP servers: `http`, `streamable-http`, and `stdio`.
[Supported transports](https://docs.mistral.ai/vibe/code/cli/mcp-servers#transports)

For permissions, MCP tools are named using the pattern **`{server_name}_{tool_name}`** (e.g., `fetch_server_get` or `my_http_server_query`).
[Tool naming and permissions](https://docs.mistral.ai/vibe/code/cli/mcp-servers#permissions)

