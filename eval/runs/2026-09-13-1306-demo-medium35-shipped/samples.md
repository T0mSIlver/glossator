# Answer samples

Ten seeded questions (seed 0) for consumer `work-proxy-mistral-medium-3-5-high`, the arms'
answers side by side with the judge's verdicts.

## mined2-070 (api_reference)

Can I set instructions on a conversation when the agent already carries its own instructions?

### A0: not run

### A1 (judge: not judged)

Yes, you can set **Custom Instructions** on a conversation, but when an **Agent** is active, **its instructions take precedence** over your Custom Instructions.

### How it works in Work:
- **Custom Instructions** apply globally to all your tasks/conversations as persistent preferences (tone, role, formatting, etc.) custom instructions > Setting up custom instructions.
- **Agents** override Custom Instructions when active in a conversation. This is explicitly stated: *"Agents override these when active"* > Related features.
- **Projects** can also have their own instructions, which apply to all chats within them alongside other context tasks with Projects > Project instructions and context.
- **Skills** similarly take precedence over Custom Instructions when activated for a task custom instructions > Interactions with other features.

### Practical implication:
If you start a conversation with an Agent, the Agent's instructions will be used instead of your Custom Instructions. If you want the Agent to follow additional rules, you should include them in the **Agent's own instructions** rather than relying on Custom Instructions.

### A2: not run

## mined-063 (single_page)

How many model calls does the LLM reranker make, and how should I keep its cost down?

### A0: not run

### A1 (judge: not judged)

The Mistral LLM reranker makes **1 LLM call per chunk** it evaluates. To keep its cost down, you should:

- **Pre-filter with a vector retriever**: Have the vector retriever return a large candidate set (e.g., top 100) and then only rerank those 100 with the LLM, rather than sending every chunk in your corpus to the LLM.
- **Limit the reranker’s `top_k`**: Only ask the reranker to return the final top-*k* results (e.g., 10) instead of rescoring everything.

[LLM ReRanker – Cost optimization](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)

### A2: not run

## mined2-055 (unanswerable)

What is the maximum number of MCP tools the Vibe CLI can hold at once? It crashes past 128.

### A0: not run

### A1 (judge: not judged)

The maximum number of MCP tools the Vibe CLI can hold at once is **128**. This is a documented limit for tools per request in the function calling system.

[Maximum number of tools per request: 128](https://docs.mistral.ai/resources/known-limitations#function-calling)

### A2: not run

## mined-074 (single_page)

What does agentic search require of the index, and which navigation tools does it expose?

### A0: not run

### A1 (judge: not judged)

Agentic Search requires the index to be a **`NavigableIndex`** with the schema migration set to **`IndexingMode.DOCUMENT_PER_CHUNK`** so that chunks carry source offsets and can be traversed in order.
[Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

It exposes the following navigation tools, each operating on the search index and returning chunks with content, score, and position metadata:

| Tool | What it does |
|------|-------------|
| `search(query, top_k, exclude_ids)` | Runs semantic or hybrid retrieval across the collection; use `exclude_ids` to avoid repeating chunks. |
| `open(source_id, start_offset, end_offset, window)` | Expands context around a retrieved chunk; returns adjacent chunks in reading order. |
| `navigate(source_id, start_offset, end_offset, direction, top_k)` | Steps forward or backward through a document from a known position. |
| `read(source_id, start_offset, end_offset, top_k)` | Reads chunks from a known source range returned by search or navigation results. |
| `grep(source_id, pattern, mode, top_k)` | Lexical search for an exact term or phrase within a single document. |
| `ingest(uri)` | Adds a document to the index (local path, `file://` URI, or `http(s)://` URL). |
| `delete(source_id)` | Removes a document and all its chunks from the index. |
[Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

### A2: not run

## hist-002 (history)

Since when does Mistral's documentation have a model page for Z.ai GLM 5.2?

### A0: not run

### A1 (judge: not judged)

The model page for **Z.ai GLM 5.2** was added to Mistral's documentation **between August 1, 2026, and August 15, 2026** (first appearing in the snapshot interval after 2026-08-01).

*Source: [Documentation history for /models/zai-glm-5-2](https://docs.mistral.ai/models/zai-glm-5-2)*

### A2: not run

## mined-032 (single_page)

How do I connect an agent to a remote MCP server?

### A0: not run

### A1 (judge: not judged)

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

### A2: not run

## mined2-022 (single_page)

Creating an agent with `tool_choice: 'required'` fails with `Can't create an agent with 'tool_choice' set to 'required' and using built in connectors` — how do I make it always search the web?

### A0: not run

### A1 (judge: not judged)

To make an agent **always search the web**, you cannot use `tool_choice: "required"` with built-in tools like `web_search` — this combination is explicitly blocked and returns the error you saw.

Instead, use **`tool_choice: "any"`** in the agent's `completion_args`. This forces the model to always call *a* tool. If `web_search` is the only tool you provide, the model will always use it.

### How to do it

When creating the agent, set:
- `tools: [{"type": "web_search"}]` (only include `web_search`)
- `completion_args: { "tool_choice": "any" }`

**Example (Python):**
```python
websearch_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    name="Websearch Agent",
    description="Agent that always searches the web",
    tools=[{"type": "web_search"}],
    completion_args={
        "tool_choice": "any",  # forces a tool call
        "temperature": 0.3,
    }
)
```

### Why this works
- `tool_choice: "any"` forces the model to call a tool on every turn.
- With only `web_search` in `tools`, that’s the tool it must use.
- `tool_choice: "required"` is not supported with built-in tools, hence the error.

> **Note:** `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected if multiple tools are available. To guarantee web search, only include `web_search` in the `tools` array.
> [Known limitations: Function calling](https://docs.mistral.ai/resources/known-limitations#function-calling)
> [Set `tool_choice: "any"` to force the model to always call a tool](https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify)

### A2: not run

## mined2-010 (single_page)

Mistral announced a model called Devstral 2 but the API lists `devstral-2512`, `devstral-latest`, `devstral-medium-latest` and more — which identifier is Devstral 2?

### A0: not run

### A1 (judge: not judged)

The model **Devstral 2** is exposed under the API identifiers:
`devstral-2512`, `devstral-latest`, and `devstral-medium-latest`.

[Devstral 2 > Overview](https://docs.mistral.ai/models/devstral-2-25-12)

### A2: not run

## mined2-075 (single_page)

What is the difference between a Connector and an MCP server in the Vibe CLI, and who sets each one up?

### A0: not run

### A1 (judge: not judged)

Here’s the difference between a **Connector** and an **MCP server** in the Vibe CLI, and who sets each up:

---

### **Connector**
- **What it is**: A **Mistral-managed integration** for supported first- and third-party services (e.g., GitHub, Gmail, Notion).
  [Connectors give the Vibe Code CLI access to supported first-party and third-party services from inside a coding session. Unlike MCP servers, which you wire up yourself, Connectors are Mistral-managed integrations.](https://docs.mistral.ai/vibe/code/cli/connectors#connectors)
- **Who sets it up**: **Mistral** provides and maintains the integration. You only need to authenticate (e.g., via OAuth) or enable/disable it in the CLI.
  [Configured by: Mistral, as integrated services](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)
- **Auth model**: Account or service login (e.g., OAuth 2.0).
  [Auth model: Account or service login](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)
- **Best for**: Common services with managed, curated integrations.
  [Best for: Common services with managed integrations](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)

---

### **MCP Server**
- **What it is**: A **user-configured** external tool or service that extends the Vibe CLI via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io). You define it in `config.toml` under `mcp_servers`.
  [MCP servers extend the Vibe Code CLI with external tools through the Model Context Protocol. You configure them in `config.toml` under `mcp_servers`, then their tools become available to Vibe like any built-in tool. MCP servers are user-configured.](https://docs.mistral.ai/vibe/code/cli/mcp-servers#mcp-servers)
- **Who sets it up**: **You** (the user) configure and manage the server, including its transport (HTTP, stdio, etc.), URL, and credentials.
  [Configured by: You, in `config.toml`](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)
- **Auth model**: Headers, environment variables, or API keys.
  [Auth model: Headers, environment variables, or API keys](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)
- **Best for**: Custom tools, private servers, or experimental integrations.
  [Best for: Custom tools, private servers, experimental tools](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)

---
---
### **Summary Table**
| Aspect               | **Connector**                          | **MCP Server**                          |
|----------------------|----------------------------------------|-----------------------------------------|
| **Setup by**         | Mistral (pre-integrated)               | You (user-configured in `config.toml`)   |
| **Auth**             | OAuth/account login                    | API keys, headers, or env vars          |
| **Discoverability**  | Curated, listed in the CLI             | Any service that speaks MCP             |
| **Use case**         | Common services (e.g., GitHub, Gmail) | Custom/private tools or servers         |

---
For more details, see:
- [Connectors in Vibe Code CLI](https://docs.mistral.ai/vibe/code/cli/connectors)
- [MCP Servers in Vibe Code CLI](https://docs.mistral.ai/vibe/code/cli/mcp-servers)

### A2: not run

## mined-052 (unanswerable)

Can an agent combine the built-in web search tool with a JSON response format?

### A0: not run

### A1 (judge: not judged)

Yes, an agent can combine the built-in **`web_search`** tool with a **JSON response format**.

### How to do it
When creating or updating an agent via the **Agents API** or **Conversations API**, you can:
1. **Add the `web_search` tool** to the `tools` array.
2. **Set `response_format: {"type": "json_object"}`** in the `completion_args` to enforce JSON output.

#### Example (Python)
```python
websearch_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    name="Websearch Agent with JSON",
    description="Agent that searches the web and returns results in JSON",
    tools=[{"type": "web_search"}],
    completion_args={
        "temperature": 0.3,
        "response_format": {"type": "json_object"},  # Enforces JSON output
    },
)
```
> **Note**: The `response_format` field is part of `completion_args` in the agent configuration, as shown in the [Creating an Agent](https://docs.mistral.ai/studio/agents/agents-api#creating-an-agent) documentation.

---

### Key Details
- **JSON Mode**: When `response_format` is set to `{"type": "json_object"}`, the model **always returns valid JSON** (as a stringified object in the `content` field). This is documented in the [JSON Mode](https://docs.mistral.ai/studio/conversations/structured-output/json_mode) section.
- **Tool Compatibility**: The `web_search` tool works with the **Agents API** and **Conversations API** (but not the Chat Completions API). You can combine it with other tools (e.g., Connectors) in the same `tools` array, as described in [Combining Tools](https://docs.mistral.ai/studio/connectors/conversations#combining-tools).

---
### Practical Tip
Explicitly instruct the agent in its `instructions` to return JSON (e.g., *"Always respond in JSON format"*) for best results, as JSON mode ensures validity but not schema adherence. See [Known Limitations](https://docs.mistral.ai/resources/known-limitations#json-mode).

### A2: not run
