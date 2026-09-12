# Answer samples

Ten seeded questions (seed 0) for consumer `work-proxy-mistral-medium-3-5-high`, the arms'
answers side by side with the judge's verdicts.

## mined2-070 (api_reference)

Can I set instructions on a conversation when the agent already carries its own instructions?

### A0: not run

### A1 (judge: partial)

Yes, you can set instructions on a conversation even when the agent already carries its own instructions.

According to the **Beta Conversations API** documentation, the `POST /v1/conversations` endpoint (used to start a conversation) accepts an **`instructions` parameter** in its request body. This allows you to provide conversation-specific instructions that apply to that particular conversation, regardless of the agent's predefined instructions.

### Key Details:
- The `instructions` parameter is **optional** and of type `string | null`.
- It is available when **starting** a conversation (`POST /v1/conversations`), but **not** when appending to an existing one (`POST /v1/conversations/{conversation_id}`).
- The API does not explicitly state the precedence between conversation-level and agent-level instructions. However, the existence of this parameter implies that conversation-specific instructions can be set and will likely **override or supplement** the agent's default instructions for that conversation.

### Example Usage:
When starting a conversation, you can include:
```json
{
  "agent_id": "<agent_id>",
  "inputs": "Your user message",
  "instructions": "Your conversation-specific instructions here"
}
```

For full details, refer to the [Beta Conversations API documentation](https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start/request-body).

### A2: not run

## mined-063 (single_page)

How many model calls does the LLM reranker make, and how should I keep its cost down?

### A0: not run

### A1 (judge: correct)

The Mistral **LLM Reranker makes 1 LLM call per chunk** it evaluates. To keep costs down, use a fast vector retriever to fetch a larger initial set (e.g., top 100), then pass only that subset to the LLM reranker, so it scores fewer chunks and incurs fewer calls.

[LLM ReRanker: How it works and cost optimization](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)

### A2: not run

## mined2-055 (unanswerable)

What is the maximum number of MCP tools the Vibe CLI can hold at once? It crashes past 128.

### A0: not run

### A1 (judge: wrong)

The maximum number of MCP tools the Vibe CLI can hold at once is **128**. This is a documented limitation for function calling in the Mistral platform:

> - Maximum number of tools per request: **128**.
> [Function calling > Known limitations](https://docs.mistral.ai/resources/known-limitations#function-calling) 

This aligns with your observation that the CLI crashes when exceeding this number.

### A2: not run

## mined-074 (single_page)

What does agentic search require of the index, and which navigation tools does it expose?

### A0: not run

### A1 (judge: correct)

Agentic Search requires the index to be a **`NavigableIndex`** with the schema migration set to **`IndexingMode.DOCUMENT_PER_CHUNK`**, so that chunks carry source offsets and can be traversed in order.
[Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

It exposes **seven navigation tools** that operate on the search index and return chunks with their content, score, and position metadata:

| Tool | What it does |
|------|-------------|
| `search(query, top_k, exclude_ids)` | Runs semantic or hybrid retrieval across the collection. Pass `exclude_ids` to avoid returning chunks the agent already inspected. |
| `open(source_id, start_offset, end_offset, window)` | Expands context around a retrieved chunk. Returns adjacent chunks in reading order. |
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

### A1 (judge: partial)

The Mistral documentation has had a model page for **Z.ai GLM 5.2** since **August 15, 2026** ([model page](https://docs.mistral.ai/models/zai-glm-5-2)).

### A2: not run

## mined-032 (single_page)

How do I connect an agent to a remote MCP server?

### A0: not run

### A1 (judge: wrong)

To connect an agent to a **remote MCP server**, you can use one of the following transport protocols, depending on how the MCP server is configured:

---

### **1. Server-Sent Events (SSE) MCP Server**
For remote MCP servers that use the **SSE transport** (e.g., `https://your-mcp-server.com/sse`), use the `MCPSSEConfig` class. This is ideal for servers that stream updates over SSE.

**Python Example:**
```python
from mistralai.workflows.plugins.mistralai import MCPSSEConfig, Agent

mcp_config = MCPSSEConfig(
    url="https://your-mcp-server.com/sse",
    timeout=60,  # Optional: timeout in seconds
    name="remote-tools",  # Optional: name for the MCP client
    headers={"Authorization": "Bearer your-token"},  # Optional: authentication headers
)

agent = Agent(
    model="mistral-medium-latest",
    name="sse-mcp-agent",
    description="Agent with access to remote MCP tools",
    mcp_clients=[mcp_config],  # Pass the MCP config to the agent
)
```
[SSE MCP server configuration](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#sse-mcp-server)

---

---

### **2. Streamable HTTP MCP Server**
For remote MCP servers that use the **Streamable HTTP transport** (e.g., `https://your-mcp-server.com/mcp` with `--transport http`), use the `MCPStreamableHTTPConfig` class. This requires `mistralai>=2.8.0`.

**Python Example:**
```python
from mistralai.workflows.plugins.mistralai import MCPStreamableHTTPConfig, Agent

mcp_config = MCPStreamableHTTPConfig(
    url="https://your-mcp-server.com/mcp",
    name="remote-tools",  # Optional: name for the MCP client
    auth_token_env="MCP_ENDPOINT_TOKEN",  # Optional: environment variable for bearer token
    header_mapping={"Notion-Token": "NOTION_TOKEN_BOT_A"},  # Optional: map headers to env vars
)

agent = Agent(
    model="mistral-medium-latest",
    name="streamable-http-mcp-agent",
    description="Agent with access to a Streamable HTTP MCP server",
    mcp_clients=[mcp_config],
)
```
[Streamable HTTP MCP server configuration](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#streamable-http-mcp-server)

> **Note:**
> - Use `auth_token_env` to pass a bearer token (e.g., `Authorization: Bearer <value>`) from an environment variable.
> - Use `header_mapping` to pass other secrets (e.g., API keys) as headers. Only the variable names are serialized, not the values.

---

---
### **3. Stdio MCP Server (Local Only)**
If the MCP server runs locally (e.g., via CLI), use `MCPStdioConfig`. This is **not for remote servers** but included for completeness:
```python
from mistralai.workflows.plugins.mistralai import MCPStdioConfig, Agent

mcp_config = MCPStdioConfig(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-everything"],
    name="server-everything",
    env_mapping={"NOTION_TOKEN": "NOTION_TOKEN_BOT_A"},  # Forward env vars
)

agent = Agent(
    model="mistral-medium-latest",
    name="stdio-mcp-agent",
    mcp_clients=[mcp_config],
)
```
[Stdio MCP server configuration](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#stdio-mcp-server)

---

---
### **Key Notes**
- **Remote vs. Local**: Use **SSE** or **Streamable HTTP** for remote servers. Use **Stdio** for local servers.
- **Authentication**: For remote servers, pass credentials via `headers` (SSE) or `auth_token_env`/`header_mapping` (Streamable HTTP). Avoid hardcoding secrets.
- **Dependencies**: For Streamable HTTP, ensure `mistralai>=2.8.0` is installed.
- **Agent Integration**: Add the MCP config to the `mcp_clients` list in the `Agent` constructor.

For more details, refer to the [MCP Integration](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#mcp-integration) section in the Mistral documentation.

### A2: not run

## mined2-022 (single_page)

Creating an agent with `tool_choice: 'required'` fails with `Can't create an agent with 'tool_choice' set to 'required' and using built in connectors` — how do I make it always search the web?

### A0: not run

### A1 (judge: wrong)

To make your agent **always search the web**, you must:

1. **Use `tool_choice: "any"`** (not `"required"` – this value is not supported by Mistral's API).
   This forces the model to call *a* tool on every turn.
   `[Set tool_choice: "any" to force the model to always call a tool](https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify)`

2. **Only include the `web_search` built-in tool** in the agent’s `tools` array.
   Because the model is forced to call a tool and `web_search` is the only one available, it will use web search every time.
   `[Built-in tools like web_search can be attached to an Agent](https://docs.mistral.ai/studio/agents/agents-api#creating-an-agent)`

Example agent creation:

```python
agent = client.beta.agents.create(
    model="mistral-medium-latest",
    name="Web-Search-Only Agent",
    instructions="Always use web search to answer the user.",
    tools=[{"type": "web_search"}],
    completion_args={"tool_choice": "any"}
)
```

> ⚠️ Note: `tool_choice: "any"` guarantees *a* tool will be called, but if you provide multiple tools the model may pick a different one. To ensure it always uses web search, keep `web_search` as the **only** tool in the list.

### A2: not run

## mined2-010 (single_page)

Mistral announced a model called Devstral 2 but the API lists `devstral-2512`, `devstral-latest`, `devstral-medium-latest` and more — which identifier is Devstral 2?

### A0: not run

### A1 (judge: partial)

The model **Devstral 2** (version 25.12) is identified in the API by all of the following names:

- `devstral-2512`
- `devstral-latest`
- `devstral-medium-latest`

[Devstral 2 > Overview](https://docs.mistral.ai/models/devstral-2-25-12)

### A2: not run

## mined2-075 (single_page)

What is the difference between a Connector and an MCP server in the Vibe CLI, and who sets each one up?

### A0: not run

### A1 (judge: correct)

In the **Vibe Code CLI**, **Connectors** and **MCP servers** both expose tools to the agent, but they differ in who manages them and how they're set up:

---

### **Connectors**
- **What they are**: Mistral-managed integrations for supported first-party and third-party services (e.g., GitHub, Slack, or Mistral's own tools).
- **Who sets them up**: **Mistral** provides and maintains these integrations. They are curated, pre-configured, and listed directly in the CLI.
- **Authentication**: Typically uses **account or service login** (e.g., OAuth or Mistral account credentials).
- **Discoverability**: Automatically detected and available in the CLI. Users can enable/disable them from the session (e.g., via `/connectors`).
- **Best for**: Common services with managed, tested integrations.
  *[Connectors](https://docs.mistral.ai/vibe/code/cli/connectors)*

---

### **MCP Servers**
- **What they are**: Custom integrations built on the **Model Context Protocol (MCP)**, allowing you to connect any external tool or server that speaks MCP (e.g., a private API, local script, or third-party MCP server).
- **Who sets them up**: **You**, the user. Configured manually in `~/.vibe/config.toml` under the `[[mcp_servers]]` section, where you define the transport (`http`, `stdio`, etc.), URL, commands, and credentials.
- **Authentication**: Uses **headers, environment variables, or API keys** (static credentials). *Note*: The CLI does not yet support OAuth for MCP servers.
- **Discoverability**: Any service that implements MCP can be connected. Tools are exposed under the pattern `{server_name}_{tool_name}`.
- **Best for**: Custom tools, private servers, or experimental integrations.
  *[MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers)*

---

### **Key Difference Summary**
| Aspect               | Connectors                          | MCP Servers                          |
|----------------------|-------------------------------------|--------------------------------------|
| **Managed by**       | Mistral (pre-built)                 | You (user-configured)                |
| **Setup**            | Automatic (listed in CLI)           | Manual (`config.toml`)               |
| **Auth**             | Account/service login               | API keys, headers, or env vars        |
| **Use case**         | Supported services                  | Custom/private tools or servers      |

---
For a side-by-side comparison, see the official table: *[Connectors vs. MCP servers](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)*.

### A2: not run

## mined-052 (unanswerable)

Can an agent combine the built-in web search tool with a JSON response format?

### A0: not run

### A1 (judge: wrong)

Yes, an agent can combine the built-in **web search tool** with a **JSON response format**.

When creating an agent, you can:
1. **Add the `web_search` tool** to enable web search capabilities.
2. **Set `response_format` in `completion_args`** to `{"type": "json_object"}` to enforce JSON output.

### Example (Python)
```python
websearch_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    name="Websearch Agent with JSON",
    description="Agent that searches the web and returns results in JSON format.",
    instructions="Use web_search to find up-to-date information and return the answer as a JSON object.",
    tools=[{"type": "web_search"}],
    completion_args={
        "temperature": 0.3,
        "top_p": 0.95,
        "response_format": {"type": "json_object"}  # Enforces JSON output
    }
)
```

### Key Points
- The `response_format` field is explicitly supported in `completion_args` for agents (as shown in the [Agents API documentation](https://docs.mistral.ai/studio/agents/agents-api#creating-an-agent)).
- JSON mode ensures the agent's response is a **valid JSON object**, even when using tools like `web_search`.
- All Mistral models (except `codestral-mamba`) support JSON mode, as confirmed in the [JSON Mode documentation](https://docs.mistral.ai/studio/conversations/structured-output/json_mode#which-models-support-json-mode).

For consistency, include a prompt like *"Return the answer as a JSON object"* in the agent's instructions.

### A2: not run
