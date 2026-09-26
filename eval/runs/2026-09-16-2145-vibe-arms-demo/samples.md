# Answer samples

Ten seeded questions (seed 0) for consumer `vibe-medium35-high`, the arms'
answers side by side with the judge's verdicts.

## mined2-070 (api_reference)

Can I set instructions on a conversation when the agent already carries its own instructions?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: partial)

Yes. Conversation instructions can be set regardless of the agent’s own instructions and will be used in addition to them.

[Instructions](https://docs.mistral.ai/studio/agents/introduction#instructions)

### VA (judge: correct)

Yes. A conversation started with an agent can still carry its own `instructions` parameter, which will apply to that conversation.
The `instructions` field is part of the `ConversationRequestBase` used when starting or appending to a conversation, so you can set or override instructions at the conversation level even when the agent has its own instructions.

[ConversationRequestBase](https://docs.mistral.ai/api/endpoint/v1/conversations#post)

### VB (judge: correct)

Yes. When you start a conversation you can pass an `instructions` parameter at the conversation level. This allows you to override or supplement the agent's own instructions for that specific conversation.

[Create a conversation and append entries to it.](https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start)

### VC (judge: correct)

Yes. The Beta Conversations API lets you pass `instructions` when you start a conversation, even if you also supply an `agent_id`. The request body for `POST /v1/conversations` includes both `agent_id` (optional) and `instructions` (optional string or null).

[Beta Conversations API > Create a conversation and append entries to it > Request body](https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start/request-body)

### VD (judge: correct)

Yes. The Conversations API accepts an `instructions` parameter (string, optional) in the request body, so you can set instructions on a conversation even when the agent already has its own instructions.

[Create a conversation and append entries to it > Request body](https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start/request-body)

## mined-063 (single_page)

How many model calls does the LLM reranker make, and how should I keep its cost down?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: partial)

The LLM reranker makes **one model call** to rerank a list of documents.
To keep its cost down, use it only on the top-k results from a first-stage (classical) reranker, and avoid reranking long documents—supply only the relevant passages you need scored [Reranking](https://docs.mistral.ai/studio/reranking#reranking).

### VA (judge: correct)

The LLM reranker makes **1 LLM call per chunk**. To keep its cost down, retrieve a larger set cheaply with a vector retriever (e.g., top 100) and then pass only that subset to the LLM reranker, so you pay for only 1 call per candidate instead of per full index.

[LLM ReRanker](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)

### VB (judge: correct)

The LLM reranker makes **1 LLM call per chunk** it scores.

To keep cost down, first retrieve many results cheaply (e.g., top 100 from the vector retriever), then send only that reduced set to the LLM reranker (e.g., `top_k=10`), so the LLM only scores 100 chunks instead of the full corpus. [LLM ReRanker](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)

### VC (judge: correct)

The Mistral LLM reranker makes **1 LLM call per chunk** it scores.

To keep its cost down, first retrieve many candidates with a fast vector retriever, then send only a limited set (e.g., top 100) to the LLM reranker so it makes fewer calls.

[LLM ReRanker](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)

### VD (judge: correct)

The LLM reranker makes **1 LLM call per chunk**.

To keep its cost down, have the vector retriever return a limited, higher number of results (e.g., top 100) to the reranker instead of sending every chunk to the LLM, then let the reranker select the final top-k from that smaller set.

[LLM ReRanker](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#llm-reranker)

## mined2-055 (unanswerable)

What is the maximum number of MCP tools the Vibe CLI can hold at once? It crashes past 128.

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: wrong)

128 [Vibe CLI MCP tools limit](https://docs.mistral.ai/platform/vibe-cli#mcp-tools)

### VA (judge: wrong)

The maximum number of MCP tools the Vibe CLI can hold at once is **128**.

[Function calling](https://docs.mistral.ai/resources/known-limitations#function-calling)

### VB (judge: wrong)

The maximum number of MCP tools the Vibe CLI can hold at once is **128**.

[Function calling](https://docs.mistral.ai/resources/known-limitations#function-calling)

### VC (judge: wrong)

128. The maximum number of tools per request is documented as 128 in Mistral's function calling limitations.

[Function calling](https://docs.mistral.ai/resources/known-limitations#function-calling)

### VD (judge: wrong)

**128** [Known limitations > Function calling](https://docs.mistral.ai/resources/known-limitations#function-calling)

## mined-074 (single_page)

What does agentic search require of the index, and which navigation tools does it expose?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: wrong)

Agentic search requires a **vector index with embeddings**.

It exposes the navigation tools **`navigate_to_url`** and **`search`**.

[Requirements](https://docs.mistral.ai/studio/agents/agentic-search#requirements)
[Navigation tools](https://docs.mistral.ai/studio/agents/agentic-search#navigation-tools)

### VA (judge: correct)

Agentic search requires a `NavigableIndex` with `IndexingMode.DOCUMENT_PER_CHUNK` and exposes seven navigation tools: `search`, `open`, `navigate`, `read`, `grep`, `ingest`, and `delete`. [Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

### VB (judge: correct)

Agentic search requires a `NavigableIndex` with `IndexingMode.DOCUMENT_PER_CHUNK` so that chunks carry source offsets and can be walked in order. [How Agentic Search works](https://docs.mistral.ai/studio/search/agentic-search#how-it-works)

It exposes these navigation tools: `search`, `open`, `navigate`, `read`, `grep`, `ingest`, `delete`. [Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

### VC (judge: correct)

Agentic Search requires the index to be a **`NavigableIndex`** with schema migration set to **`IndexingMode.DOCUMENT_PER_CHUNK`** so chunks carry source offsets and can be traversed in order.
[NavigableIndex](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)
[IndexingMode.DOCUMENT_PER_CHUNK](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migration-helpers#enums)

It exposes these navigation tools: `search`, `open`, `navigate`, `read`, `grep`, `ingest`, and `delete`.
[Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

### VD (judge: correct)

Agentic Search requires the index to be a **`NavigableIndex` with `IndexingMode.DOCUMENT_PER_CHUNK`** so that chunks carry source offsets and can be traversed in order.
[Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

It exposes **7 navigation tools**:

- `search(query, top_k, exclude_ids)`
- `open(source_id, start_offset, end_offset, window)`
- `navigate(source_id, start_offset, end_offset, direction, top_k)`
- `read(source_id, start_offset, end_offset, top_k)`
- `grep(source_id, pattern, mode, top_k)`
- `ingest(uri)`
- `delete(source_id)`
[Navigation tools](https://docs.mistral.ai/studio/search/agentic-search#navigation-tools)

## hist-002 (history)

Since when does Mistral's documentation have a model page for Z.ai GLM 5.2?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: correct)

The documentation does not answer this question. It covers which models are supported at [Which models are supported?](https://docs.mistral.ai/studio/agents/introduction#which-models-are-supported)

### VA (judge: wrong)

Between 2026-08-04 and 2026-08-11.

### VB (judge: correct)

The model page for Z.ai GLM 5.2 appears between **2026-08-01** (not present) and **2026-08-15** (present).

### VC (judge: correct)

The model page for Z.ai GLM 5.2 first appears in Mistral’s documentation between **2026-08-01 (absent) and 2026-08-15 (present)**.

[Z.ai GLM 5.2](https://docs.mistral.ai/models/zai-glm-5-2)

### VD (judge: correct)

The model page for **Z.ai GLM 5.2** first appeared in Mistral's documentation **between 2026-08-01 and 2026-08-15**.

[Models](https://docs.mistral.ai/models)

## mined-032 (single_page)

How do I connect an agent to a remote MCP server?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: partial)

To connect an agent to a remote MCP server, use the **`mcpServers`** configuration in your agent's YAML. Specify the remote server's URL under `url` and include any required headers (like authentication) under `headers`.

[Agents Configuration](https://docs.mistral.ai/studio/agents/agent-yaml-reference#mcpservers)

### VA (judge: partial)

To connect a Mistral Studio **Agent** to a remote MCP server, you must first **register the MCP server as a Connector** and then attach that Connector to the Agent.

### 1. Register the MCP server as a Connector
Create a Connector by calling the API with the MCP server URL and authentication details:

```bash
curl -X POST "https://api.mistral.ai/v1/connectors" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_mcp_server",
    "description": "My remote MCP server",
    "server": "https://your-remote-mcp-server.com/mcp",
    "visibility": "private"
  }'
```

[Managing Connectors](https://docs.mistral.ai/studio/connectors/management)

### 2. Authenticate the Connector (if required)
If the MCP server requires OAuth or API keys, authenticate via the Studio UI or API:

```bash
curl "https://api.mistral.ai/v1/connectors/my_mcp_server/auth_url?app_return_url=https://myapp.example.com/oauth/callback" \
  -H "Authorization: Bearer $MISTRAL_API_KEY"
```

[Managing Connectors: Authenticate a Connector](https://docs.mistral.ai/studio/connectors/management#get-auth-url)

### 3. Attach the Connector to an Agent
Add the Connector as a tool when creating or updating the Agent:

```bash
curl -X POST "https://api.mistral.ai/v1/agents" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-medium-latest",
    "name": "My Agent",
    "tools": [
      {"type": "connector", "connector_id": "my_mcp_server"}
    ]
  }'
```

[Agents Tools Overview: Connectors](https://docs.mistral.ai/studio/agents/agent-tools#tool-types)

### VB (judge: partial)

To connect an agent to a remote MCP server, you first register the MCP server as a **Connector**, then reference that Connector in your agent's tools.

1. **Create a Connector** with your remote MCP server URL:
   - Use `name`, `server` (the MCP server URL), and `visibility` (`private`, `shared_workspace`, or `shared_org`).
   - Example server: `"https://mcp.deepwiki.com/mcp"`.

   [Create a Connector](https://docs.mistral.ai/studio/connectors/management#create)

2. **Attach the Connector to your Agent** by including it in the `tools` array with `type: "connector"` and the Connector's name or UUID as `connector_id`:

   ```json
   {
     "tools": [
       {
         "type": "connector",
         "connector_id": "my_deepwiki"
       }
     ]
   }
   ```

   [Using Connectors in conversations](https://docs.mistral.ai/studio/connectors/conversations#using-connectors)
   [Tool types for Agents](https://docs.mistral.ai/studio/agents/agent-tools#tool-types)

### VC (judge: partial)

To connect an agent to a **remote MCP server over Server-Sent Events**, use `MCPSSEConfig`:

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
[SSE MCP server](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#sse-mcp-server)

---

To connect to a **remote MCP server over Streamable HTTP** (transport `http`), use `MCPStreamableHTTPConfig` (requires `mistralai>=2.8.0`):

```python
from mistralai.workflows.plugins.mistralai import MCPStreamableHTTPConfig

mcp_config = MCPStreamableHTTPConfig(
    url="https://your-mcp-server.com/mcp",
    name="remote-tools",
)
```
[Streamable HTTP MCP Server](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#streamable-http-mcp-server)

### VD (judge: partial)

To connect a **durable agent** to a remote MCP server you have two supported transports:

- **Server-Sent Events (SSE)** – use `MCPSSEConfig`
- **Streamable HTTP** – use `MCPStreamableHTTPConfig` (requires `mistralai>=2.8.0`)

**SSE example:**
```python
from mistralai.workflows.plugins.mistralai import MCPSSEConfig
import mistralai.workflows as workflows_mistralai

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
[SSE MCP server](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#sse-mcp-server)

**Streamable HTTP example:**
```python
from mistralai.workflows.plugins.mistralai import MCPStreamableHTTPConfig
import mistralai.workflows as workflows_mistralai

mcp_config = MCPStreamableHTTPConfig(
    url="https://your-mcp-server.com/mcp",
    name="remote-tools",
    auth_token_env="MCP_ENDPOINT_TOKEN",          # reads bearer from env
    header_mapping={"Notion-Token": "NOTION_TOKEN_BOT_A"},  # other per-request secrets
)

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="streamable-http-mcp-agent",
    description="Agent with access to a Streamable HTTP MCP server",
    mcp_clients=[mcp_config],
)
```
[Streamable HTTP MCP Server](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#streamable-http-mcp-server)

## mined2-022 (single_page)

Creating an agent with `tool_choice: 'required'` fails with `Can't create an agent with 'tool_choice' set to 'required' and using built in connectors` — how do I make it always search the web?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: wrong)

To always search the web, add `"web_search"` to your agent's `tools` array and set `tool_choice` to `"required"`. Do not use the `built_in_connectors` parameter.

[Agent parameters](https://docs.mistral.ai/studio/agents/introduction#agent-parameters)
[Built-in connectors](https://docs.mistral.ai/studio/connectors/built-in)

### VA (judge: wrong)

To always force a web search, use `tool_choice: "any"` in the agent's `completion_args` instead of `tool_choice: "required"`. The platform does not allow `tool_choice: "required"` with built-in connector tools like `web_search`; the supported way to force a tool call is `tool_choice: "any"`, which makes the model always call a tool (though it doesn't guarantee which tool if multiple are provided).

[`tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.](https://docs.mistral.ai/resources/known-limitations#function-calling)

[Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.](https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify)

Example for a web‑search agent:
```python
agent = client.beta.agents.create(
    model="mistral-medium-latest",
    name="Websearch Agent",
    tools=[{"type": "web_search"}],
    completion_args={"tool_choice": "any"}
)
```

### VB (judge: wrong)

To make an agent always search the web, **use `tool_choice: "any"` instead of `tool_choice: "required"`** when the agent uses built‑in tools such as `web_search`. The platform prevents `tool_choice: "required"` with built‑in connectors, so switch to `"any"` to force the model to call a tool on every turn.

[Function Calling — tool_choice options](https://docs.mistral.ai/studio/conversations/function-calling#step-3)
[Agent Tools — Websearch](https://docs.mistral.ai/studio/agents/agent-tools/websearch)

### VC (judge: wrong)

**`tool_choice: "any"` with the built-in `web_search` tool.**

To always search the web you must use the built‑in **`web_search`** tool (not a Connector) and set `tool_choice: "any"` in the agent’s completion arguments; this forces the model to call a tool on every turn, and because `web_search` is the only tool the agent will always search the web.
Example (Python):

```python
client.beta.agents.create(
    model="mistral-medium-latest",
    name="Web-Search Agent",
    tools=[{"type": "web_search"}],
    completion_args={"tool_choice": "any"}
)
```

- `tool_choice: "any"` forces a tool call every time
  [Build an agent with tools > Verify](https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify)

- `web_search` is a built‑in tool you can attach to an agent
  [Create a Websearch Agent](https://docs.mistral.ai/studio/agents/agent-tools/websearch#create-a-websearch-agent)

- Web Search is listed as a built‑in tool type
  [Agents Tools Overview > Tools > Tool types](https://docs.mistral.ai/studio/agents/agent-tools#tool-types)

- Built‑in tools (including `web_search`) can be used alongside Connectors, but the restriction you hit only applies when using built‑in **Connectors** with `tool_choice: "required"`; using the built‑in tool avoids that conflict
  [Using Connectors in conversations > Use built-in tools alongside Connectors](https://docs.mistral.ai/studio/connectors/conversations#combining-tools)

### VD (judge: wrong)

To make an agent always search the web, **use `tool_choice: "any"`** instead of `tool_choice: "required"`.

`tool_choice: "any"` forces the model to always call a tool, whereas `tool_choice: "required"` cannot be used with built-in tools such as `web_search`.

[Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.](https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify)

## mined2-010 (single_page)

Mistral announced a model called Devstral 2 but the API lists `devstral-2512`, `devstral-latest`, `devstral-medium-latest` and more — which identifier is Devstral 2?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: partial)

`devstral-2512` [Available models](https://docs.mistral.ai/api/models#available-models)

### VA (judge: wrong)

The identifier for **Devstral 2** is **`devstral-2512`** (it is also exposed under the aliases `devstral-latest` and `devstral-medium-latest`).

[Devstral 2](https://docs.mistral.ai/models/devstral-2-25-12#devstral-2)

### VB (judge: wrong)

`devstral-2512`, `devstral-latest` and `devstral-medium-latest` all identify Devstral 2.

[All models](https://docs.mistral.ai/models#all-models)

### VC (judge: wrong)

`devstral-2512` is Devstral 2.

[Devstral 2 > Overview](https://docs.mistral.ai/models/devstral-2-25-12#overview)

### VD (judge: partial)

The identifier for **Devstral 2** is `devstral-2512`. The aliases `devstral-latest` and `devstral-medium-latest` also point to the same model.

[Overview](https://docs.mistral.ai/models/devstral-2-25-12#overview)

## mined2-075 (single_page)

What is the difference between a Connector and an MCP server in the Vibe CLI, and who sets each one up?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: partial)

A Connector is a built-in integration provided and set up by Mistral in the Vibe CLI for specific services [Connectors](https://docs.mistral.ai/platform/vibe-cli/connectors). An MCP server is any external server implementing the Model Context Protocol that developers set up and connect to the Vibe CLI [Model Context Protocol](https://docs.mistral.ai/platform/vibe-cli/mcp).

### VA (judge: partial)

- A **Connector** is a Mistral-managed integration that gives the Vibe Code CLI access to supported first-party and third-party services; **Mistral sets it up**. An **MCP server** is a user-configured external tool that extends the Vibe Code CLI via the Model Context Protocol; **the user sets it up** in `config.toml`.
  [Connectors vs. MCP servers](https://docs.mistral.ai/vibe/code/cli/connectors#connectors-vs-mcp-servers)
  [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers#mcp-servers)

### VB (judge: partial)

- **Connector**: A Mistral‑managed integration that gives the Vibe Code CLI access to supported first‑party and third‑party services; **Mistral sets it up** for you. [Connectors vs. MCP servers](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)

- **MCP server**: A user‑configured external tool that extends the CLI via the Model Context Protocol; **you set it up** in `config.toml`. [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers)

### VC (judge: partial)

- **Connector**: A Mistral‑managed integration for supported first‑party and third‑party services; Mistral sets it up and keeps it updated. [Connectors](https://docs.mistral.ai/vibe/code/cli/connectors)

- **MCP server**: A user‑configured external tool that speaks the Model Context Protocol; you add and configure it yourself in `config.toml`. [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers)

### VD (judge: correct)

- **Difference**: Connectors are Mistral‑managed integrations that expose supported first/third‑party services to the Vibe Code CLI, whereas MCP servers are user‑configured external tools that speak the Model Context Protocol and are wired up in your `config.toml`.
- **Who sets them up**: Mistral sets up Connectors; you set up MCP servers.

[Connectors vs. MCP servers](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)
[MCP servers are user-configured](https://docs.mistral.ai/vibe/code/cli/mcp-servers)

## mined-052 (unanswerable)

Can an agent combine the built-in web search tool with a JSON response format?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: correct)

The documentation does not answer whether an agent can combine the built-in web search tool with a JSON response format; it only lists the available tools and response formats separately.
[Tools](https://docs.mistral.ai/studio/agents/tools)
[Response format](https://docs.mistral.ai/studio/agents/configuration#response-format)

### VA (judge: wrong)

Yes. An agent can combine the built-in web search tool with a JSON response format. Websearch is a built-in agent tool [Create a Websearch Agent](https://docs.mistral.ai/studio/agents/agent-tools/websearch#create-a-websearch-agent), and the handoffs example shows agents using tools together with `response_format` in `completion_args` [Create Multiple Agents](https://docs.mistral.ai/studio/agents/handoffs#create-multiple-agents).

### VB (judge: wrong)

Yes. An agent can use the built-in web search tool together with a JSON response format; the documentation provides no restriction against combining them, and the [Handoffs guide](https://docs.mistral.ai/studio/agents/handoffs) shows agents with tools (like `web_search`) and agents with `completion_args.response_format` (JSON schema) working side‑by‑side in the same workflow.

[Handoffs](https://docs.mistral.ai/studio/agents/handoffs)
[Websearch](https://docs.mistral.ai/studio/agents/agent-tools/websearch)
[Agents & Conversations](https://docs.mistral.ai/studio/agents/agents-api)

### VC (judge: wrong)

Yes.
The Conversations API supports the built-in `web_search` tool and, in the same request, you can set `completion_args.response_format = {"type": "json_object"}` to get a JSON response.

[Use built-in tools alongside Connectors](https://docs.mistral.ai/studio/connectors/conversations#combining-tools)
[`response_format` in ConversationRequest](https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start/request-body)

### VD (judge: wrong)

Yes. An agent can combine the built‑in `web_search` tool with a JSON response format by setting `response_format: {"type": "json_object"}` in `completion_args` when creating the agent.

[JSON Mode](https://docs.mistral.ai/studio/conversations/structured-output/json_mode#json-mode)
[Creating an Agent](https://docs.mistral.ai/studio/agents/agents-api#creating-an-agent)
