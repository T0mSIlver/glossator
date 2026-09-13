# mined2-049 (cross_page, 2 connector calls)

## Question

Which transports can an MCP server use with the Vibe CLI, and how are its tools named for permissions?

## Thinking

The user is asking about MCP server transports and tool naming conventions for permissions in the Vibe CLI. This is a specific technical question about Mistral's Vibe CLI implementation. I need to search the documentation for information about MCP (Model Context Protocol) server configurations and how tool permissions are handled. Let me start with a search query that covers both aspects.

The search returned relevant results. I can see there's a page about MCP servers in the Vibe CLI documentation. The results mention:
- A section about permissions with tool naming pattern `{server_name}_{tool_name}`
- A section about supported transports with a table
- A section about common fields

I need to read the full page to get complete and accurate information about both transports and tool naming conventions. Let me fetch the entire MCP servers page.

Now I have the complete information from the MCP servers documentation page. Let me extract the key details:

**Transports:**
From the "Supported transports" section, there are three transports:
1. `http` - for servers reachable over standard HTTP
2. `streamable-http` - for servers reachable over HTTP with streaming responses
3. `stdio` - for local processes started from a command

**Tool Naming for Permissions:**
From the "Tool naming and permissions" section, MCP tools are exposed under the pattern `{server_name}_{tool_name}`. The `name` field in the configuration is used as the prefix. Examples include `fetch_server_get` and `my_http_server_query`.

I should also verify if there are any additional details about the fields or configuration that might be relevant. The common fields section confirms that `name` is used as a prefix in tool names and `transport` can be one of the three values mentioned.

The answer should be structured clearly with the transports listed and the naming convention explained. I should cite the specific sections from the documentation.

Let me format this properly:
- List the three transports in a clear way
- Explain the tool naming pattern
- Provide examples
- Include the citations

The user wants a concise but complete answer. I'll make sure to include all the information they asked for.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Vibe CLI MCP server transports and tool permissions naming"}
```

Result:

```
q: "Vibe CLI MCP server transports and tool permissions naming"

[1] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: permissions
    MCP servers > Tool naming and permissions
    MCP tools are exposed under the pattern `{server_name}_{tool_name}`. Configure permissions per tool just like built-in tools: ```toml [tools.fetch_server_get] permission = "always" [tools.my_http_server_query] permission = "ask" ``` You can also restrict which MCP tools are active using `enabled_tools` and `disabled_tools`: ```toml # Only enable serena's tools enabled_tools = ["serena_*"] # Disabl …
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#permissions

[2] https://docs.mistral.ai/vibe/code/safety-approvals-permissions | section: mcp-and-connector-tools
    Safety, approvals, and permissions > Per-tool permissions > MCP and connector tools
    MCP tools are addressed as `{server_name}_{tool_name}`. For example, to always allow a `get` tool exposed by an MCP server named `fetch_server`: ```toml [tools.fetch_server_get] permission = "always" ``` See [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for the full configuration model and [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) for the precedence be …
    cite: https://docs.mistral.ai/vibe/code/safety-approvals-permissions#mcp-and-connector-tools

[3] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: transports
    MCP servers > Supported transports
    | Transport | Use it when | |---|---| | `http` | The server is reachable over standard HTTP. | | `streamable-http` | The server is reachable over HTTP and supports streaming responses. | | `stdio` | The server is a local process you start from a command. |
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#transports

[4] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: fields
    MCP servers > Common fields
    | Field | Purpose | |---|---| | `name` | Short alias for the server. Used as a prefix in tool names. | | `transport` | One of `http`, `streamable-http`, or `stdio`. | | `url` | Base URL for HTTP transports. | | `command` / `args` | Command and arguments for the stdio transport. | | `headers` | Extra HTTP headers for HTTP transports. | | `api_key_env` | Environment variable that holds the API key. …
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#fields

[5] https://docs.mistral.ai/resources/mcp | section: next-steps
    MCP > Next steps
    - [Create a Skill in Studio](https://docs.mistral.ai/getting-started/quickstarts/studio/create-skill) to give the agent something to work with. - [MCP servers in the Vibe Code CLI](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for per-tool permissions and filtering. - [API keys](https://docs.mistral.ai/admin/identity-access/api-keys) to create and rotate the key you connect with.
    cite: https://docs.mistral.ai/resources/mcp#next-steps

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

The Vibe CLI supports **three transports** for MCP servers:

- `http` – for servers reachable over standard HTTP
- `streamable-http` – for servers reachable over HTTP with streaming responses
- `stdio` – for local processes started from a command
  *[Supported transports](https://docs.mistral.ai/vibe/code/cli/mcp-servers#transports)*

---

MCP tools are named for permissions using the pattern **`{server_name}_{tool_name}`**, where `server_name` is the value of the `name` field in the MCP server configuration. For example, if the server is named `fetch_server` and exposes a `get` tool, the permission key is `tools.fetch_server_get`.
*[Tool naming and permissions](https://docs.mistral.ai/vibe/code/cli/mcp-servers#permissions)*

