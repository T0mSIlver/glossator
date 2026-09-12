# mined2-049 (cross_page, 4 connector calls)

## Question

Which transports can an MCP server use with the Vibe CLI, and how are its tools named for permissions?

## Thinking

The user is asking about MCP (Model Context Protocol) server transports for the Vibe CLI and how tools are named for permissions. I need to search the Mistral documentation for this information. Let me start with a search query about MCP server transports and Vibe CLI.

I got search results that mention MCP servers and transports. The first hit shows a table with transports. Let me read the full page to get complete information about transports and tool naming.

Good, I have the transports information. Now I need to find information about how tools are named for permissions. Let me search for tool naming conventions.

Perfect! I found the information. The search results show that:
1. Transports are `http`, `streamable-http`, and `stdio`
2. Tool naming follows the pattern `{server_name}_{tool_name}`

Let me read the permissions page to confirm the exact naming convention for permissions.

I have all the information I need now. Let me compile the answer:

1. **Transports**: The Vibe CLI supports three transports for MCP servers:
   - `http` - for servers reachable over standard HTTP
   - `streamable-http` - for servers reachable over HTTP with streaming responses
   - `stdio` - for local processes started from a command

2. **Tool naming for permissions**: Tools are named using the pattern `{server_name}_{tool_name}`. For example, if you have an MCP server named `fetch_server` with a tool called `get`, the permission would be configured as `[tools.fetch_server_get]`.

I should present this clearly with the proper citations from the documentation.

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
{"page_url": "https://docs.mistral.ai/vibe/code/cli/mcp-servers", "section": "transports"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/mcp-servers | "MCP servers" | section: transports

## section: transports
    MCP servers > Supported transports
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#transports
## Supported transports {#transports}

| Transport | Use it when |
|---|---|
| `http` | The server is reachable over standard HTTP. |
| `streamable-http` | The server is reachable over HTTP and supports streaming responses. |
| `stdio` | The server is a local process you start from a command. |

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/mcp-servers", section="add") for the section after it
```

### 3. mistral_docs_search

```json
{"q": "MCP server tool names permissions Vibe CLI", "max_hits": 5}
```

Result:

```
q: "MCP server tool names permissions Vibe CLI"

[1] https://docs.mistral.ai/vibe/code/safety-approvals-permissions | section: mcp-and-connector-tools
    Safety, approvals, and permissions > Per-tool permissions > MCP and connector tools
    MCP tools are addressed as `{server_name}_{tool_name}`. For example, to always allow a `get` tool exposed by an MCP server named `fetch_server`: ```toml [tools.fetch_server_get] permission = "always" ``` See [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for the full configuration model and [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) for the precedence be …
    cite: https://docs.mistral.ai/vibe/code/safety-approvals-permissions#mcp-and-connector-tools

[2] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: permissions
    MCP servers > Tool naming and permissions
    MCP tools are exposed under the pattern `{server_name}_{tool_name}`. Configure permissions per tool just like built-in tools: ```toml [tools.fetch_server_get] permission = "always" [tools.my_http_server_query] permission = "ask" ``` You can also restrict which MCP tools are active using `enabled_tools` and `disabled_tools`: ```toml # Only enable serena's tools enabled_tools = ["serena_*"] # Disabl …
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#permissions

[3] https://docs.mistral.ai/resources/mcp | section: next-steps
    MCP > Next steps
    - [Create a Skill in Studio](https://docs.mistral.ai/getting-started/quickstarts/studio/create-skill) to give the agent something to work with. - [MCP servers in the Vibe Code CLI](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for per-tool permissions and filtering. - [API keys](https://docs.mistral.ai/admin/identity-access/api-keys) to create and rotate the key you connect with.
    cite: https://docs.mistral.ai/resources/mcp#next-steps

[4] https://docs.mistral.ai/vibe/code/cli/configuration | section: tool-permissions
    Configuration > Common configuration sections > Tool permissions and filters
    Restrict which tools the agent can use: ```toml enabled_tools = ["serena_*"] disabled_tools = ["mcp_*", "grep"] ``` Tool filters support **exact names**, **glob patterns**, and **regex** with the `re:` prefix. Per-tool permissions can also be set in `[tools.<tool_name>]` blocks. See [Safety, approvals, and permissions](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#tool-permissions …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#tool-permissions

[5] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: mcp-servers
    MCP servers
    MCP servers extend the Vibe Code CLI with **external tools** through the [Model Context Protocol](https://modelcontextprotocol.io). You configure them in `config.toml` under `mcp_servers`, then their tools become available to Vibe like any built-in tool. MCP servers are **user-configured**. For Mistral-managed integrations, see [Connectors](https://docs.mistral.ai/vibe/code/cli/connectors) instead …
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/safety-approvals-permissions") to read hit 1 on its page
```

### 4. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/safety-approvals-permissions", "section": "mcp-and-connector-tools"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/safety-approvals-permissions | "Safety, approvals, and permissions" | section: mcp-and-connector-tools

## section: mcp-and-connector-tools
    Safety, approvals, and permissions > Per-tool permissions > MCP and connector tools
    cite: https://docs.mistral.ai/vibe/code/safety-approvals-permissions#mcp-and-connector-tools
### MCP and connector tools {#mcp-and-connector-tools}

MCP tools are addressed as `{server_name}_{tool_name}`. For example, to always allow a `get` tool exposed by an MCP server named `fetch_server`:

```toml
[tools.fetch_server_get]
permission = "always"
```

See [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for the full configuration model and [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) for the precedence between user and project settings.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/safety-approvals-permissions", section="approval-model") for the section after it
```

## Answer

The Vibe CLI supports the following transports for an MCP server:

| Transport | Use it when |
|---|---|
| `http` | The server is reachable over standard HTTP. |
| `streamable-http` | The server is reachable over HTTP and supports streaming responses. |
| `stdio` | The server is a local process you start from a command. |
[Supported transports](https://docs.mistral.ai/vibe/code/cli/mcp-servers#transports)

For permissions, each tool provided by an MCP server is named using the pattern **`{server_name}_{tool_name}`**. For example, a `get` tool on a server named `fetch_server` is referenced as `fetch_server_get` in configuration:
```toml
[tools.fetch_server_get]
permission = "always"
```
[MCP and connector tools](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#mcp-and-connector-tools)

