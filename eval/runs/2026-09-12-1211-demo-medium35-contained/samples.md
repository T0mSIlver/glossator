# Answer samples

Ten seeded questions (seed 0) for consumer `work-proxy-mistral-medium-3-5-high`, the arms'
answers side by side with the judge's verdicts.

## mined2-070 (api_reference)

Can I set instructions on a conversation when the agent already carries its own instructions?

### A0: not run

### A1 (judge: correct)

Yes, you **can set instructions on a conversation even when the agent already carries its own instructions**.

In the **Beta Agents & Conversations API**, the [`POST /v1/conversations`](https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start) endpoint accepts both:
- `agent_id` (optional): to use a pre-configured agent with its own instructions
- `instructions` (optional, string or null): to provide conversation-specific instructions

Both parameters can be provided simultaneously, meaning you can start a conversation with an existing agent *and* supply additional or overriding instructions for that specific conversation. The API is designed to support this combination, allowing you to customize behavior at the conversation level without modifying the agent itself.

> **Note**: While the API supports providing both, the exact merging behavior (whether conversation instructions override, prepend, or append to agent instructions) is not explicitly documented in the sources checked. However, the presence of the `instructions` parameter alongside `agent_id` confirms that conversation-level instructions are intended to work with agent-level instructions.

### A2: not run

## mined-063 (single_page)

How many model calls does the LLM reranker make, and how should I keep its cost down?

### A0: not run

### A1 (judge: correct)

The **LLM reranker makes one LLM call per chunk** it scores for relevance.
To keep its cost down, first retrieve a larger set of results (e.g., top 100) with a fast vector retriever, then only pass that smaller subset to the LLM reranker for final scoring—this limits the number of LLM calls to the size of that subset rather than the entire corpus.

[LLM ReRanker – How it works & Cost optimization](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)

### A2: not run

## mined2-055 (unanswerable)

What is the maximum number of MCP tools the Vibe CLI can hold at once? It crashes past 128.

### A0: not run

### A1 (judge: wrong)

The Vibe CLI (and the Mistral platform's function calling in general) has a **hard limit of 128 tools per request**. This means the CLI cannot hold more than 128 MCP tools at once, and it will crash if you exceed this limit.

This is explicitly documented in the [Known limitations > Function calling](https://docs.mistral.ai/resources/known-limitations#function-calling) section:

> Maximum number of tools per request: **128**

### A2: not run

## mined-074 (single_page)

What does agentic search require of the index, and which navigation tools does it expose?

### A0: not run

### A1 (judge: correct)

Agentic Search requires the index to be a **`NavigableIndex`**, with the schema migration explicitly set to **`IndexingMode.DOCUMENT_PER_CHUNK`** so that chunks carry source offsets and can be traversed in order.
[Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

It exposes the following **seven navigation tools** (via an MCP server) that operate on the search index and return chunks with content, score, and position metadata:

| Tool | Purpose |
|------|---------|
| `search(query, top_k, exclude_ids)` | Semantic or hybrid retrieval across the collection; `exclude_ids` prevents re-returning already inspected chunks. |
| `open(source_id, start_offset, end_offset, window)` | Expands context around a retrieved chunk, returning adjacent chunks in reading order. |
| `navigate(source_id, start_offset, end_offset, direction, top_k)` | Steps forward/backward through a document from a known position. |
| `read(source_id, start_offset, end_offset, top_k)` | Reads chunks from a known source range (e.g., returned by search or navigation). |
| `grep(source_id, pattern, mode, top_k)` | Lexical search for an exact term/phrase within a single document. |
| `ingest(uri)` | Adds a document to the index (local path, `file://`, or `http(s)://` URL). |
| `delete(source_id)` | Removes a document and all its chunks from the index. |
[Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

### A2: not run

## hist-002 (history)

Since when does Mistral's documentation have a model page for Z.ai GLM 5.2?

### A0: not run

### A1 (judge: correct)

The Mistral documentation page for **Z.ai GLM 5.2** was added between **August 1, 2026, and August 15, 2026**, as it was absent in the snapshot from August 1, 2026, but present by August 15, 2026. The model's release date is listed as **2026-08-06** in the documentation itself.

[Z.ai GLM 5.2 model page](https://docs.mistral.ai/models/zai-glm-5-2)

### A2: not run

## mined-032 (single_page)

How do I connect an agent to a remote MCP server?

### A0: not run

### A1 (judge: partial)

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

### A2: not run

## mined2-022 (single_page)

Creating an agent with `tool_choice: 'required'` fails with `Can't create an agent with 'tool_choice' set to 'required' and using built in connectors` — how do I make it always search the web?

### A0: not run

### A1 (judge: wrong)

The error occurs because **`tool_choice: "required"` is not supported when using Mistral's built-in tools (like `web_search`) with an Agent**. The built-in tools only support `tool_choice: "auto"` (default) or `tool_choice: "any"` in the Agents API.

To make your agent **always search the web**, set:
```python
completion_args={"tool_choice": "any"}
```
and include `{"type": "web_search"}` in the `tools` array.

Example:
```python
agent = client.beta.agents.create(
    name="Websearch Agent",
    model="mistral-medium-latest",
    tools=[{"type": "web_search"}],
    completion_args={"tool_choice": "any"},  # Forces the model to call a tool
    instructions="Always use web_search to answer user queries."
)
```
This ensures the model **must** call a tool (and with only `web_search` available, it will always search the web).

*Source: [Set `tool_choice: "any"` to force the model to always call a tool](https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify).*

### A2: not run

## mined2-010 (single_page)

Mistral announced a model called Devstral 2 but the API lists `devstral-2512`, `devstral-latest`, `devstral-medium-latest` and more — which identifier is Devstral 2?

### A0: not run

### A1 (judge: wrong)

The model **Devstral 2** is identified in the API by the following names:
- `devstral-2512`
- `devstral-latest`
- `devstral-medium-latest`

All three identifiers refer to the same Devstral 2 model (version 25.12).

[Devstral 2 > Overview](https://docs.mistral.ai/models/devstral-2-25-12)

### A2: not run

## mined2-075 (single_page)

What is the difference between a Connector and an MCP server in the Vibe CLI, and who sets each one up?

### A0: not run

### A1 (judge: correct)

Here’s the difference between **Connectors** and **MCP servers** in the Vibe CLI, and who sets each up:

| **Aspect**          | **Connectors**                          | **MCP servers**                          |
|---------------------|----------------------------------------|----------------------------------------|
| **Configured by**    | Mistral (pre-integrated services)       | You (via `config.toml`)                 |
| **Auth model**      | Account or service login               | Headers, environment variables, or API keys |
| **Discoverability** | Curated, listed in the CLI              | Any service that speaks MCP             |
| **Best for**        | Common services with managed integrations | Custom tools, private servers, or experimental tools |

**Summary**:
- **Connectors** are pre-built, Mistral-managed integrations for common services (e.g., GitHub, Slack). Mistral sets them up, and you enable them via your account or service login.
- **MCP servers** are custom, user-configured integrations for any service that supports the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). You define them in your `config.toml` and handle authentication (e.g., API keys).

Source: [Connectors vs. MCP servers](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)

### A2: not run

## mined-052 (unanswerable)

Can an agent combine the built-in web search tool with a JSON response format?

### A0: not run

### A1 (judge: wrong)

Yes, an agent can combine the built-in **web search tool** with a **JSON response format**.

When creating an agent, you can:
1. Add the `web_search` tool to the agent's `tools` array.
2. Set `response_format` to `{"type": "json_object"}` in the `completion_args` to enable **JSON mode**, which ensures the model's response is a valid JSON object.

Here’s how it works in practice:
- The agent can use `web_search` to fetch up-to-date information from the web.
- By setting `response_format: {"type": "json_object"}`, the agent’s final output will be structured as JSON, even if it includes results from web searches.

**Example (Python):**
```python
websearch_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    name="Websearch Agent with JSON",
    tools=[{"type": "web_search"}],
    completion_args={
        "temperature": 0.3,
        "response_format": {"type": "json_object"}  # Enables JSON mode
    }
)
```

**Key References:**
- [JSON Mode](https://docs.mistral.ai/studio/conversations/structured-output/json_mode#json-mode): Confirms that `response_format: {"type": "json_object"}` enables JSON output.
- [Websearch Agent Creation](https://docs.mistral.ai/studio/agents/agent-tools/websearch#create-a-websearch-agent): Shows how to add the `web_search` tool to an agent.
- [Agent Creation API](https://docs.mistral.ai/studio/agents/agents-api#creating-an-agent): Demonstrates `completion_args` supports `response_format`.

### A2: not run
