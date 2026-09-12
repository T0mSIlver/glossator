# mined-032 (single_page, 3 connector calls)

## Question

How do I connect an agent to a remote MCP server?

## Thinking

The user is asking about connecting an agent to a remote MCP server. This is a specific technical question about Mistral's MCP (Model Context Protocol) implementation. I need to search the documentation to find the exact procedure and requirements.

Let me search for information about MCP server connections, particularly focusing on remote connections.

I got some search results. The first result mentions "Durable agents > MCP integration > SSE MCP server" which seems relevant. Let me read the full page to get complete information about connecting agents to MCP servers.

Good, I found information about SSE MCP server configuration. Now let me also check the Streamable HTTP MCP Server section to provide a complete answer, as there might be multiple transport protocols supported.

Perfect. Now I have information about both SSE and Streamable HTTP MCP server configurations. Let me also check if there's any additional context in the built-in tools section or other parts that might be relevant. But I think I have enough to provide a comprehensive answer.

The user wants to know how to connect an agent to a remote MCP server. From the documentation, I can see there are at least two ways:
1. SSE MCP server (Server-Sent Events)
2. Streamable HTTP MCP Server

I should structure the answer clearly, showing both methods with code examples, and mention the requirements and considerations for each. I should also include the citations as shown in the documentation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "connect an agent to a remote MCP server", "max_hits": 5}
```

Result:

```
q: "connect an agent to a remote MCP server"

[1] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: sse-mcp-server
    Durable agents > MCP integration > SSE MCP server
    For remote MCP servers over Server-Sent Events: **Python** ```python from mistralai.workflows.plugins.mistralai import MCPSSEConfig mcp_config = MCPSSEConfig( url="https://your-mcp-server.com/sse", timeout=60, name="remote-tools", headers={"Authorization": "Bearer your-token"}, # Optional ) agent = workflows_mistralai.Agent( model="mistral-medium-latest", name="sse-mcp-agent", description="Agent w …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#sse-mcp-server

[2] https://docs.mistral.ai/studio/search/agentic-search | section: register-agent
    Agentic Search > Use Agentic Search as MCP tools > Register with an agent
    - **Vibe**: The `.mcp.json` file in the generated project registers the server. Run `vibe --trust` in the project directory and Vibe discovers it. - **Studio**: Add the server as a connector or MCP server in the agent configuration. - **Custom agents**: Connect any MCP-compatible client to the server's stdio or HTTP endpoint. The MCP server includes instructions that describe the retrieval loop, s …
    cite: https://docs.mistral.ai/studio/search/agentic-search#register-agent

[3] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: streamable-http-mcp-server
    Durable agents > MCP integration > Streamable HTTP MCP Server
    For remote MCP servers that speak the Streamable HTTP transport (`--transport http`), such as a self-hosted server behind an HTTP endpoint: > **Note** > > Requires `mistralai>=2.8.0` (the release that ships the Streamable HTTP client). If you use `MCPStreamableHTTPConfig`, pin `mistralai>=2.8.0` in your project's dependencies. **Python** ```python from mistralai.workflows.plugins.mistralai import …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#streamable-http-mcp-server

[4] https://docs.mistral.ai/resources/mcp | section: mcp
    MCP
    The Mistral MCP server connects an AI agent to your Studio workspace over the [Model Context Protocol](https://modelcontextprotocol.io). It exposes your workspace as MCP tools and authenticates each request with your Mistral API key. Use it from wherever your agent runs: a coding CLI, an IDE, a desktop assistant, or your own application. | | | |---|---| | **Endpoint** | `https://api.mistral.ai/mcp …
    cite: https://docs.mistral.ai/resources/mcp

[5] https://docs.mistral.ai/vibe/work/connectors/mcp-connectors | section: mcp-connectors
    MCP Connectors
    Beyond our [featured Connectors](https://docs.mistral.ai/vibe/work/connectors), you can connect Work to third-party and custom services built on the **Model Context Protocol (MCP)**. > **Info** > > MCP is an open standard that lets language models call tools and read data from external services through a common interface. Any service that exposes an MCP server — whether built by a third party or b …
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents", "section": "sse-mcp-server"}
```

Result:

```
page: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | "Durable agents" | section: sse-mcp-server

## section: sse-mcp-server
    Durable agents > MCP integration > SSE MCP server
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#sse-mcp-server
### SSE MCP server {#sse-mcp-server}

For remote MCP servers over Server-Sent Events:

**Python**

```python
from mistralai.workflows.plugins.mistralai import MCPSSEConfig

mcp_config = MCPSSEConfig(
    url="https://your-mcp-server.com/sse",
    timeout=60,
    name="remote-tools",
    headers={"Authorization": "Bearer your-token"},  # Optional
)

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="sse-mcp-agent",
    description="Agent with access to remote MCP tools",
    mcp_clients=[mcp_config],
)
```

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents", section="streamable-http-mcp-server") for the section after it
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents", "section": "streamable-http-mcp-server"}
```

Result:

```
page: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | "Durable agents" | section: streamable-http-mcp-server

## section: streamable-http-mcp-server
    Durable agents > MCP integration > Streamable HTTP MCP Server
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#streamable-http-mcp-server
### Streamable HTTP MCP Server {#streamable-http-mcp-server}

For remote MCP servers that speak the Streamable HTTP transport (`--transport http`), such as a self-hosted server behind an HTTP endpoint:

> **Note**
>
> Requires `mistralai>=2.8.0` (the release that ships the Streamable HTTP client). If you use `MCPStreamableHTTPConfig`, pin `mistralai>=2.8.0` in your project's dependencies.

**Python**

```python
from mistralai.workflows.plugins.mistralai import MCPStreamableHTTPConfig

mcp_config = MCPStreamableHTTPConfig(
    url="https://your-mcp-server.com/mcp",
    name="remote-tools",
)

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="streamable-http-mcp-agent",
    description="Agent with access to a Streamable HTTP MCP server",
    mcp_clients=[mcp_config],
)
```

**Forwarding credentials to a Streamable HTTP server**

A Streamable HTTP server usually needs credentials on every request: a bearer token gating the endpoint and/or a per-request integration token. Set them from the worker's environment so no secret is serialized into the workflow's [event history](https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events).

Use `auth_token_env` for the endpoint bearer (the SDK reads the raw token from that worker variable and adds the `Bearer` scheme). Use `header_mapping` for any other per-request secret header, mapping an HTTP header name to a worker variable name:

**Python**

```python
from mistralai.workflows.plugins.mistralai import MCPStreamableHTTPConfig

mcp_config = MCPStreamableHTTPConfig(
    url="https://your-mcp-server.com/mcp",
    name="notion",
    auth_token_env="MCP_ENDPOINT_TOKEN",                    # -> Authorization: Bearer <value>
    header_mapping={"Notion-Token": "NOTION_TOKEN_BOT_A"},  # header <- whole env value
)
```

Only the variable names are serialized into activity params and event history; the secret values are read from the worker's environment inside the activity and never leave it. Put only non-secret values in the static `headers` field. If a declared worker variable is missing from the environment, the activity fails fast.

**Redirects**

By default the client does not follow HTTP redirects (`follow_redirects=False`). On a redirect, `httpx` only strips the `Authorization` header on cross-origin hops, so the per-request secret headers above (e.g. `Notion-Token`) would be resent to the redirect target. Set `follow_redirects=True` only if your MCP server relies on redirects (for example `/mcp` -> `/mcp/`) and you trust every host it can redirect to.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents", section="built-in-tools") for the section after it
```

## Answer

To connect an agent to a **remote MCP server**, Mistral supports two transport protocols: **Server-Sent Events (SSE)** and **Streamable HTTP**. Below are the configurations for both, as documented in the [Durable Agents MCP integration](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents) guide.

---

### 1. **SSE MCP Server**
For remote MCP servers using **Server-Sent Events (SSE)**:
```python
from mistralai.workflows.plugins.mistralai import MCPSSEConfig

mcp_config = MCPSSEConfig(
    url="https://your-mcp-server.com/sse",  # Remote SSE endpoint
    timeout=60,                              # Optional timeout (seconds)
    name="remote-tools",                     # Identifier for the MCP client
    headers={"Authorization": "Bearer your-token"},  # Optional auth headers
)

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="sse-mcp-agent",
    description="Agent with access to remote MCP tools",
    mcp_clients=[mcp_config],  # Attach the MCP client to the agent
)
```
*Source: [SSE MCP server](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#sse-mcp-server)*

---

### 2. **Streamable HTTP MCP Server**
For remote MCP servers using **Streamable HTTP** (requires `mistralai>=2.8.0`):
```python
from mistralai.workflows.plugins.mistralai import MCPStreamableHTTPConfig

mcp_config = MCPStreamableHTTPConfig(
    url="https://your-mcp-server.com/mcp",  # Remote HTTP endpoint
    name="remote-tools",                     # Identifier for the MCP client
)

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="streamable-http-mcp-agent",
    description="Agent with access to a Streamable HTTP MCP server",
    mcp_clients=[mcp_config],
)
```
*Source: [Streamable HTTP MCP Server](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#streamable-http-mcp-server)*

---

### **Forwarding Credentials (Streamable HTTP)**
If your server requires authentication (e.g., bearer tokens or custom headers), use **environment variables** to avoid hardcoding secrets:
```python
mcp_config = MCPStreamableHTTPConfig(
    url="https://your-mcp-server.com/mcp",
    name="notion",
    auth_token_env="MCP_ENDPOINT_TOKEN",       # Reads `Bearer <value>` from env
    header_mapping={"Notion-Token": "NOTION_TOKEN_BOT_A"},  # Maps header to env var
)
```
- **`auth_token_env`**: Automatically adds `Authorization: Bearer <value>` from the specified environment variable.
- **`header_mapping`**: Maps custom headers (e.g., `Notion-Token`) to environment variables.
- *Note*: Only variable names are serialized; secrets are read at runtime from the worker's environment.
*Source: [Forwarding credentials](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#streamable-http-mcp-server)*

---
### **Key Notes**
- **SSE vs. Streamable HTTP**: Choose the protocol based on your MCP server's transport layer.
- **Security**: Use environment variables for credentials to avoid exposing secrets in workflow logs.
- **Redirects**: For Streamable HTTP, set `follow_redirects=True` only if your server relies on redirects and you trust the targets.

