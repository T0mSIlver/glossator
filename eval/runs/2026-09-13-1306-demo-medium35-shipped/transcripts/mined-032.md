# mined-032 (single_page, 5 connector calls)

## Question

How do I connect an agent to a remote MCP server?

## Thinking

The user is asking how to connect an agent to a remote MCP server. This is a specific technical question about Mistral's agent infrastructure. I need to search the documentation for information about MCP (Model Context Protocol) server connections. Let me start by searching for relevant documentation.

The search returned several relevant results. I can see there are sections about SSE MCP server and Streamable HTTP MCP Server in the durable agents documentation. Let me read the full page to get comprehensive information about connecting agents to remote MCP servers.

I got the SSE MCP server section, but I also saw there's a Streamable HTTP MCP Server section mentioned. Let me read that as well to provide complete information. The user wants to know how to connect to a remote MCP server, and there appear to be multiple transport methods.

Now I have information about both SSE and Streamable HTTP MCP servers. Let me also check the general MCP resource page to see if there's additional context about connecting agents to MCP servers. This will help me provide a more complete answer.

I now have comprehensive information from the documentation. Let me also check the Vibe Work MCP connectors page to see if there's additional information about connecting agents to MCP servers in different contexts.

Now I have all the information I need. The documentation shows multiple ways to connect an agent to a remote MCP server:

1. For durable agents in Studio workflows, there are two main approaches:
   - SSE MCP Server (Server-Sent Events transport)
   - Streamable HTTP MCP Server (HTTP transport, requires mistralai>=2.8.0)

2. For Vibe Work, there are MCP Connectors that can connect to third-party MCP servers

3. For connecting to Mistral's own MCP server, there are specific endpoints and authentication methods

I should structure my answer to cover:
- The different methods based on the context (Studio workflows vs Vibe Work)
- Code examples for each method
- Authentication considerations
- Troubleshooting tips

Let me organize this into a clear, actionable answer.

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

### 4. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/resources/mcp"}
```

Result:

```
page: https://docs.mistral.ai/resources/mcp | "MCP"

## section: mcp
    MCP
    cite: https://docs.mistral.ai/resources/mcp
# MCP

The Mistral MCP server connects an AI agent to your Studio workspace over the [Model Context Protocol](https://modelcontextprotocol.io). It exposes your workspace as MCP tools and authenticates each request with your Mistral API key.

Use it from wherever your agent runs: a coding CLI, an IDE, a desktop assistant, or your own application.

| | |
|---|---|
| **Endpoint** | `https://api.mistral.ai/mcp` |
| **Transport** | Streamable HTTP |
| **Authentication** | `Authorization: Bearer <MISTRAL_API_KEY>` |

## section: before-you-begin
    MCP > Before you begin
    cite: https://docs.mistral.ai/resources/mcp#before-you-begin
## Before you begin {#before-you-begin}

- A Mistral [API key](https://docs.mistral.ai/admin/identity-access/api-keys). Keys are workspace-scoped, so the agent gets the access that key already has.
- An MCP client that supports the streamable HTTP transport and static request headers.

Export the key in the environment that launches your client:

```bash
export MISTRAL_API_KEY="your_api_key"
```

## section: connect
    MCP > Connect a client
    cite: https://docs.mistral.ai/resources/mcp#connect
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

## section: tools
    MCP > What the server exposes
    cite: https://docs.mistral.ai/resources/mcp#tools
## What the server exposes {#tools}

**Skills**, the reusable instruction sets you manage in [Skills](https://console.mistral.ai/build/skills). An agent browses the workspace catalog, reads a Skill and the files shipped with it, creates a new Skill version, changes who it is shared with, or deletes it. A Skill written from your editor appears in Studio, and a Skill written in Studio is available to the agent.

Skills is the first capability, and more follow. The server lists the tools available to your key, so ask your client for its tool list, or call `tools/list`. Each tool describes its own arguments.

## section: permissions
    MCP > Access and permissions
    cite: https://docs.mistral.ai/resources/mcp#permissions
## Access and permissions {#permissions}

Every call uses your API key's permissions.

Some tools write: they add Skill versions, change sharing, and delete Skills. Configure per-tool approval in your client to review those calls before they run.

## section: troubleshooting
    MCP > Troubleshooting
    cite: https://docs.mistral.ai/resources/mcp#troubleshooting
## Troubleshooting {#troubleshooting}

| Problem | Cause | Solution |
|---|---|---|
| `401 {"detail":"Invalid API Key"}` | The key is missing, misspelled, or revoked. | Export the variable in the environment that launches your client, and check the key is active in the console. |
| A tool call returns a permission error. | The operation requires additional workspace access. | Ask a workspace admin for the matching access, then retry. |

## section: next-steps
    MCP > Next steps
    cite: https://docs.mistral.ai/resources/mcp#next-steps
## Next steps {#next-steps}

- [Create a Skill in Studio](https://docs.mistral.ai/getting-started/quickstarts/studio/create-skill) to give the agent something to work with.
- [MCP servers in the Vibe Code CLI](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for per-tool permissions and filtering.
- [API keys](https://docs.mistral.ai/admin/identity-access/api-keys) to create and rotate the key you connect with.

Results: 7 sections, the whole page.
```

### 5. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/work/connectors/mcp-connectors"}
```

Result:

```
page: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors | "MCP Connectors"

## section: mcp-connectors
    MCP Connectors
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors
# MCP Connectors

Beyond our [featured Connectors](https://docs.mistral.ai/vibe/work/connectors), you can connect Work to third-party and custom services built on the **Model Context Protocol (MCP)**.

> **Info**
>
> MCP is an open standard that lets language models call tools and read data from external services through a common interface. Any service that exposes an MCP server — whether built by a third party or by your own team — can be plugged into Work. See the [MCP introduction](https://modelcontextprotocol.io/docs/getting-started/intro) for the full background.

There are two ways to add an MCP Connector: pick one from the **pre-configured directory**, or point Work at **your own MCP-compatible server**. Both require an administrator.

> **Warning**
>
> MCP Connectors aren't Mistral products. We don't control third-party servers and can't guarantee their behavior or data handling. Connect only to servers you trust.

## section: directory
    MCP Connectors > Browsing the directory
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#directory
## Browsing the directory {#directory}

The MCP Connectors directory is a curated collection of pre-configured third-party Connectors your administrator can add to your organization.

1. Open the `Connectors` page.
2. Click `+ Add Connector`.
3. Browse the directory or search for a specific Connector.
4. Click a Connector to view its details and add it to your organization.
5. Complete the authentication flow if required.

Some Connectors in the directory require additional configuration (a custom URL or API key). You'll be prompted during setup.

> **Note**
>
> This is an administrator-only feature. On Free, Pro, and Student plans, the account owner is the administrator by default.

## section: custom-connectors
    MCP Connectors > Configuring a custom Connector
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#custom-connectors
## Configuring a custom Connector {#custom-connectors}

Custom Connectors let you connect Work to any MCP-compatible server. This is useful for internal tools, private APIs, or services that aren't in the directory.

1. Open the `Connectors` page.
2. Click `+ Add Connector` and switch to the `Custom MCP Connector` tab.
3. Fill in the required fields:
   - **Connector name**: a unique identifier (no spaces or special characters).
   - **Server URL**: the full URL of your MCP-compatible server.
   - **Description** (optional): a short explanation of what this Connector does.
4. Click `Connect`. The platform detects the server's authentication method automatically.
5. Complete the authentication flow if prompted.

## section: supported-auth
    MCP Connectors > Configuring a custom Connector > Supported authentication methods
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#supported-auth
### Supported authentication methods {#supported-auth}

Our platform auto-detects the authentication method when you provide the server URL:

- **No authentication**: for publicly accessible or trusted internal servers.
- **HTTP Bearer Token / Basic Auth**: for servers that require credentials in the `Authorization` header.
- **OAuth 2.1** (with dynamic client registration): for servers using standard OAuth 2.1 delegated access. You'll be guided through the consent flow.

## section: per-function-permissions
    MCP Connectors > Per-function permissions
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#per-function-permissions
## Per-function permissions {#per-function-permissions}

After setup, every user can control whether Work asks for permission each time it calls a Connector function, or whether it should be pre-authorized.

1. Go to `Connectors` and select the `My Connectors` tab.
2. Click the Connector card to open its details.
3. Open the `Functions` tab.
4. Toggle `Always allow` for each function you want to pre-authorize.

MCP Connectors expose two types of functions:

- **Read functions**: retrieve information (list events, search files, get data). Lower risk.
- **Write functions**: perform actions (send emails, create events, modify records). Higher risk.

> **Tip**
>
> Pre-authorize read functions you use frequently to reduce approval prompts. Keep write functions on manual approval until you're confident in the Connector's behavior.

## section: security
    MCP Connectors > Security best practices
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#security
## Security best practices {#security}

Since MCP Connectors connect Work to servers we haven't reviewed, you're responsible for vetting them. Keep these practices in mind:

- **Vet every server you connect.** Check the publisher, review documentation, and verify the server's purpose before adding it.
- **Watch for unexpected changes.** Server developers can update tools at any time, which may change behavior. Monitor Connector outputs periodically.
- **Guard against prompt injection.** A malicious server could attempt to inject hidden instructions. Work has built-in protections, but review tool inputs and outputs for anything unexpected.
- **Grant only the permissions you need.** Use the per-function `Always allow` toggle deliberately. Start with manual approval and only pre-authorize functions you trust.

If you discover a malicious MCP server, report it to our support team.

## section: limitations
    MCP Connectors > Current limitations
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#limitations
## Current limitations {#limitations}

Custom MCP Connectors don't yet support all MCP capabilities:

- [Dynamic tool discovery](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [Resources](https://modelcontextprotocol.io/specification/2025-06-18/server/resources)
- [Automatic prompt templates](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts#prompts)

We plan to add support for these in future updates.

## section: troubleshooting
    MCP Connectors > Troubleshooting
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#troubleshooting
## Troubleshooting {#troubleshooting}

If you see *"MCP connection requires additional information or is invalid"*, check the following:

- **Endpoint URL**: make sure you're using the correct path (some servers use `/mcp` or `/sse`). Streamable HTTP is the current standard.
- **Server reachability**: the server must be accessible over HTTPS with a valid TLS certificate.
- **Authentication**: verify your credentials. OAuth servers should return a `401` with a `WWW-Authenticate` header; API key servers should return `200` on a valid request.
- **MCP handshake**: the server must respond correctly to the `initialize` JSON-RPC call.

> **Tip**
>
> Use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) to test your server's compatibility before configuring it in Work.

## section: curl-checks
    MCP Connectors > Troubleshooting > Quick checks with curl
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#curl-checks
### Quick checks with curl {#curl-checks}

**Test reachability:**

```bash
curl -I https://your-server.example.com/mcp
```

**Test API key authentication:**

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://your-server.example.com/mcp
```

**Test MCP initialize handshake:**

```bash
curl -X POST https://your-server.example.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{}}}'
```

A successful response includes `"result"` with the server's capabilities. An error response or timeout indicates a configuration issue on the server side.

Results: 9 sections, the whole page.
```

## Answer

To connect an agent to a **remote MCP server**, Mistral supports two main transports in its workflows: **Server-Sent Events (SSE)** and **Streamable HTTP**. Here’s how to do it in each case, with code examples and key details.

---

---

### **1. Server-Sent Events (SSE) MCP Server**
Use this for remote MCP servers that expose an SSE endpoint (e.g., `https://your-mcp-server.com/sse`).

**Python Example:**
```python
from mistralai.workflows.plugins.mistralai import MCPSSEConfig

mcp_config = MCPSSEConfig(
    url="https://your-mcp-server.com/sse",  # SSE endpoint
    timeout=60,
    name="remote-tools",  # Identifier for the MCP client
    headers={"Authorization": "Bearer your-token"},  # Optional auth
)

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="sse-mcp-agent",
    description="Agent with access to remote MCP tools",
    mcp_clients=[mcp_config],  # Attach the MCP config
)
```
[SSE MCP server configuration](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#sse-mcp-server)

---

---

### **2. Streamable HTTP MCP Server**
Use this for remote MCP servers that use the **Streamable HTTP transport** (e.g., `https://your-mcp-server.com/mcp`).
**Requires `mistralai>=2.8.0`.**

#### **Basic Setup**
```python
from mistralai.workflows.plugins.mistralai import MCPStreamableHTTPConfig

mcp_config = MCPStreamableHTTPConfig(
    url="https://your-mcp-server.com/mcp",  # HTTP endpoint
    name="remote-tools",
)

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="streamable-http-mcp-agent",
    description="Agent with access to a Streamable HTTP MCP server",
    mcp_clients=[mcp_config],
)
```
[Streamable HTTP MCP server configuration](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#streamable-http-mcp-server)

#### **Authentication**
To securely forward credentials (e.g., bearer tokens or API keys) **without hardcoding secrets**:
- Use `auth_token_env` for the `Authorization: Bearer` header.
- Use `header_mapping` for other headers (maps an HTTP header name to an environment variable).

```python
mcp_config = MCPStreamableHTTPConfig(
    url="https://your-mcp-server.com/mcp",
    name="notion",
    auth_token_env="MCP_ENDPOINT_TOKEN",  # Reads `Authorization: Bearer <MCP_ENDPOINT_TOKEN>`
    header_mapping={"Notion-Token": "NOTION_TOKEN_BOT_A"},  # Maps `Notion-Token` header to env var
)
```
> **Note:** Only the *variable names* are serialized into the workflow’s event history. The actual values are read from the worker’s environment at runtime.
> If a required environment variable is missing, the workflow fails fast.
> [Streamable HTTP authentication](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#streamable-http-mcp-server)

#### **HTTP Redirects**
By default, the client **does not follow redirects** (`follow_redirects=False`).
Set `follow_redirects=True` **only if your server relies on redirects** (e.g., `/mcp` → `/mcp/`) and you trust the redirect targets.
[Redirects behavior](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#streamable-http-mcp-server)

---

---

---

### **3. Connecting to Mistral’s MCP Server**
If you want to connect an agent to **Mistral’s official MCP server** (e.g., to access your Studio workspace as tools), use the following endpoint and authentication:

| **Setting**       | **Value**                          |
|-------------------|------------------------------------|
| Endpoint          | `https://api.mistral.ai/mcp`       |
| Transport         | Streamable HTTP                    |
| Authentication    | `Authorization: Bearer <API_KEY>`  |

**Example (Vibe Code CLI):**
```bash
vibe mcp add mistralai \
  --url https://api.mistral.ai/mcp \
  --transport streamable-http \
  --api-key-env MISTRAL_API_KEY
```
This writes the configuration to `~/.vibe/config.toml` and uses the `MISTRAL_API_KEY` environment variable for authentication.
[Mistral MCP server setup](https://docs.mistral.ai/resources/mcp#connect)

---

---

### **4. Vibe Work: Custom MCP Connectors**
In **Mistral Work**, you can connect to third-party or custom MCP servers via the **Connectors** page:
1. Go to **Connectors** > **+ Add Connector** > **Custom MCP Connector**.
2. Provide:
   - **Connector name** (unique identifier).
   - **Server URL** (e.g., `https://your-server.com/mcp`).
   - **Description** (optional).
3. Complete the authentication flow (auto-detected: **No Auth**, **Bearer Token**, **Basic Auth**, or **OAuth 2.1**).
4. Configure **per-function permissions** (manual approval or pre-authorization for read/write functions).

> **Security Note:** Vet all custom MCP servers before connecting. Start with manual approval for write functions.
> [Custom MCP Connectors in Work](https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#custom-connectors)

---

---
---
### **Troubleshooting**
| **Issue**                          | **Solution**                                                                                     |
|------------------------------------|--------------------------------------------------------------------------------------------------|
| `401 Invalid API Key`               | Ensure the `MISTRAL_API_KEY` (or custom token) is set in the environment and is valid.          |
| MCP handshake fails                | Verify the server responds to `initialize` with a `200` and valid capabilities. Use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) to test. |
| Redirect loops or missing headers  | Disable `follow_redirects` (default) or ensure headers are preserved for trusted redirects.       |
| Missing environment variables      | Confirm the worker’s environment includes the required variables (e.g., `MCP_ENDPOINT_TOKEN`). |

**Quick `curl` Check:**
```bash
# Test MCP initialize handshake
curl -X POST https://your-server.example.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{}}}'
```
A successful response includes a `"result"` with the server’s capabilities.
[MCP troubleshooting](https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#troubleshooting)

---
---
### **Summary**
| **Use Case**               | **Transport**       | **Config Class**               | **Key Auth Options**                          |
|---------------------------|---------------------|--------------------------------|-----------------------------------------------|
| Remote SSE MCP server     | SSE                 | `MCPSSEConfig`                | `headers` (e.g., `Authorization: Bearer`)      |
| Remote Streamable HTTP    | HTTP                | `MCPStreamableHTTPConfig`     | `auth_token_env`, `header_mapping`             |
| Mistral’s MCP server      | Streamable HTTP     | CLI/Config file               | `MISTRAL_API_KEY` env var                      |
| Vibe Work Connectors      | HTTP/SSE            | UI (Custom MCP Connector)     | Bearer Token, Basic Auth, OAuth 2.1           |

