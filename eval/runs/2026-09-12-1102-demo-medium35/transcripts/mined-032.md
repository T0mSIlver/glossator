# mined-032 (single_page, 2 connector calls)

## Question

How do I connect an agent to a remote MCP server?

## Thinking

The user is asking how to connect an agent to a remote MCP server. This is a technical question about Mistral's agent infrastructure and MCP (Model Context Protocol) servers. I need to search the Mistral documentation for information about this specific topic. Let me use the mistral_docs_search tool with a query that captures the key concepts.

The search returned results about durable agents and MCP integration. The first result mentions "Durable agents > MCP integration > SSE MCP server" which seems directly relevant. I should read the full page to get comprehensive information about connecting agents to remote MCP servers. Let me fetch the durable_agents documentation page.

Now I have the documentation content. The page covers durable agents and MCP integration. I can see there are sections about SSE MCP server, Streamable HTTP MCP Server, and Stdio MCP server. The user wants to connect to a **remote** MCP server, so I should focus on the remote options (SSE and Streamable HTTP) rather than the local stdio option.

Let me extract the relevant information:
1. For SSE MCP servers: Use `MCPSSEConfig` with url, timeout, name, and headers
2. For Streamable HTTP MCP servers: Use `MCPStreamableHTTPConfig` with url, name, and optional auth_token_env/header_mapping
3. Both require adding the config to the agent's `mcp_clients` parameter

I should also mention the requirements:
- For SSE: no specific version mentioned
- For Streamable HTTP: requires `mistralai>=2.8.0`

I need to structure this clearly with code examples for each transport type. I should also mention the security considerations for passing credentials.

Let me organize the answer:
- Start with an overview of the two main transport types for remote MCP servers
- Provide code examples for each
- Mention the version requirement for Streamable HTTP
- Include security best practices
- Add links to the documentation

The user asked "How do I connect an agent to a remote MCP server?" so I should be direct and provide actionable steps.

I'll structure it as:
1. Introduction
2. SSE MCP Server (with code)
3. Streamable HTTP MCP Server (with code)
4. Security considerations
5. Additional notes

Make sure to include the proper citations from the documentation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "connect an agent to a remote MCP server"}
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
{"page_url": "https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents"}
```

Result:

```
page: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | "Durable agents"

## section: durable-agents
    Durable agents
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents
# Durable agents

A durable agent is an LLM agent whose loop (model calls, tool use, and handoffs) runs **inside a workflow**, so its state survives crashes and restarts. The Mistral plugin (`mistralai-workflows[mistralai]`) provides the primitives for building them: `Agent`, `Runner`, `RemoteSession`, and `LocalSession` (experimental).

What you get on top of a regular agent loop:

- **Durability**: agent state is preserved across worker crashes and restarts
- **Tool integration**: workflow activities can be passed directly as agent tools
- **Multi-agent handoffs**: agents can delegate tasks to specialized agents
- **MCP support**: connect to external tools with the Model Context Protocol (stdio or SSE)
- **Telemetry and observability**: the plugin uses [`get_mistral_client()`](https://docs.mistral.ai/studio/workflows/building-workflows/mistral_client) under the hood, so all LLM calls include telemetry and workflow tracing metadata by default

## section: installation
    Durable agents > Installation
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#installation
## Installation {#installation}

To use Durable Agents, install the Mistral plugin:

```bash
uv add 'mistralai-workflows[mistralai]'
```

## section: agent
    Durable agents > Core components > Agent
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent
### Agent {#agent}

The `Agent` class defines an LLM agent with its model, instructions, tools, and handoffs:

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="my-agent",
    description="Agent that performs specific tasks",
    instructions="Use tools to complete the user's request.",
    tools=[my_activity],  # Workflows activities as tools
    handoffs=[other_agent],  # Agents to delegate to
)
```

## section: runner
    Durable agents > Core components > Runner
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#runner
### Runner {#runner}

The `Runner` executes an agent with user inputs and manages the conversation loop. It calls the model, processes tool calls, and repeats until the agent produces a final response or reaches `max_turns`. If `max_turns` is reached, the runner returns whatever outputs have been collected so far.

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai

outputs = await workflows_mistralai.Runner.run(
    agent=agent,
    inputs="What is the interest rate for 2024?",
    session=session,
    max_turns=10,  # Maximum model call iterations before stopping
)
```

The returned `outputs` is a list of output items produced by the agent during the run (text responses, tool results, handoff results).

## section: sessions
    Durable agents > Core components > Sessions
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#sessions
### Sessions {#sessions}

Sessions manage agent state and API communication. Two session types are available:

| Session         | Use case                   | Backend               |
| --------------- | -------------------------- | --------------------- |
| `RemoteSession` | Production (recommended)   | Mistral Agents SDK    |
| `LocalSession`  | Experimental / On-premises | Direct completion API |

`RemoteSession` lazily creates an agent server-side (or reuses an existing one if `agent.id` is set) and delegates completions to it. `LocalSession` runs the agent loop in your worker process using the chat completions API directly.

## section: basic-example
    Durable agents > Basic example
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#basic-example
## Basic example {#basic-example}

Here's a simple agent workflow that uses an activity as a tool:

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai
from mistralai.client.models import TextChunk


@workflows.activity()
async def get_interest_rate(year: int) -> dict:
    """Get the interest rate for a given year.

    Args:
        year: The year to get the interest rate for
    """
    # Your implementation here
    return {"interest_rate": 1.62}


@workflows.workflow.define(name="finance_agent_workflow")
class FinanceAgentWorkflow:
    @workflows.workflow.entrypoint
    async def entrypoint(self, question: str) -> dict:
        session = workflows_mistralai.RemoteSession()

        agent = workflows_mistralai.Agent(
            model="mistral-medium-latest",
            name="finance-agent",
            description="Agent for financial queries",
            instructions="Use tools to answer financial questions.",
            tools=[get_interest_rate],
        )

        outputs = await workflows_mistralai.Runner.run(
            agent=agent,
            inputs=question,
            session=session,
        )

        answer = "\n".join([
            output.text for output in outputs
            if isinstance(output, TextChunk)
        ])

        return {"answer": answer}
```

## section: multi-agent-handoffs
    Durable agents > Multi-agent handoffs
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs
## Multi-agent handoffs {#multi-agent-handoffs}

Agents can delegate tasks to specialized agents using handoffs. The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions; the model decides when to hand off based on the user query and the available specialists' descriptions. The system automatically manages the handoff conversation.

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai

# Create a specialized agent for interest rate queries
interest_rate_agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="ecb-interest-rate-agent",
    description="Agent for European Central Bank interest rate research",
    instructions="Use tools to get the interest rate for a given year.",
    tools=[get_interest_rate],
)

# Main agent that can hand off to the specialist
finance_agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="finance-agent",
    description="Agent for financial queries",
    handoffs=[interest_rate_agent],  # Can delegate to interest_rate_agent
)

outputs = await workflows_mistralai.Runner.run(
    agent=finance_agent,
    inputs="What was the ECB interest rate in 2023?",
    session=workflows_mistralai.RemoteSession(),
)
```

When the finance agent receives a query about ECB interest rates, it can automatically hand off to the specialized `interest_rate_agent`.

## section: mcp-integration
    Durable agents > MCP integration
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#mcp-integration
## MCP integration {#mcp-integration}

Connect to external tool servers using the Model Context Protocol. Two transport types are supported:

## section: stdio-mcp-server
    Durable agents > MCP integration > Stdio MCP server
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#stdio-mcp-server
### Stdio MCP server {#stdio-mcp-server}

For local command-line MCP servers:

**Python**

```python
import mistralai.workflows.plugins.mistralai as workflows_mistralai
from mistralai.workflows.plugins.mistralai import MCPStdioConfig

mcp_config = MCPStdioConfig(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-everything"],
    name="server-everything",
)

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="mcp-agent",
    description="Agent with access to MCP tools",
    mcp_clients=[mcp_config],
)
```

**Forwarding credentials to a stdio server**

Some stdio MCP servers need credentials, such as a bot token, to authenticate. Use `env_mapping` to pass them from the worker's environment into the subprocess. Each mapping entry pairs the subprocess variable name with the worker variable name:

**Python**

```python
from mistralai.workflows.plugins.mistralai import MCPStdioConfig

mcp_config = MCPStdioConfig(
    command="npx",
    args=["-y", "@notionhq/notion-mcp-server"],
    name="notion",
    env_mapping={"NOTION_TOKEN": "NOTION_TOKEN_BOT_A"},
)
```

Use a mapping instead of raw values because activity inputs are persisted to the workflow's [event history](https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events). Loading secrets from the worker's environment and passing them directly would expose them there.

With `env_mapping`, only the variable names are serialized. The activity reads the secret values from the worker's environment, and the values never leave the worker. A mapping also lets you run several instances of the same server with different credentials on one worker. If a declared worker variable is missing from the environment, the activity fails fast.

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

## section: built-in-tools
    Durable agents > Built-in tools
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#built-in-tools
## Built-in tools {#built-in-tools}

Use Mistral's built-in tools alongside activities:

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai
from mistralai.client.models import WebSearchTool

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="web-search-agent",
    description="Agent with web search capability",
    instructions="Use web search to answer user questions",
    tools=[WebSearchTool()],
)
```

Available built-in tools:

| Tool | Description |
|------|-------------|
| `WebSearchTool()` | Search the web and return results to the model |
| `CodeInterpreterTool()` | Execute Python code in a sandboxed environment |
| `ImageGenerationTool()` | Generate images from text descriptions |
| `DocumentLibraryTool()` | Analyze and extract information from uploaded documents |

These tools are executed server-side by the Mistral platform; they do not run in your worker process. Pass them in the `tools` list alongside any activity-based tools.

> **Warning**
>
> **Built-in tools require RemoteSession**: `LocalSession` silently drops built-in tools (logs a warning and proceeds without them). Use `RemoteSession` for any agent that relies on `WebSearchTool`, `CodeInterpreterTool`, `ImageGenerationTool`, or `DocumentLibraryTool`.

## section: remote-session
    Durable agents > Session types > RemoteSession (recommended)
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#remote-session
### RemoteSession (recommended) {#remote-session}

Uses the Mistral Agents SDK for production workloads:

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai

session = workflows_mistralai.RemoteSession()

outputs = await workflows_mistralai.Runner.run(
    agent=agent,
    inputs="Your question here",
    session=session,
)
```

Features:

- Full Agents SDK integration
- Automatic agent creation and updates
- Managed conversation state
- Production-ready

## section: agent-lifecycle
    Durable agents > Session types > Agent lifecycle
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent-lifecycle
### Agent lifecycle {#agent-lifecycle}

When a `RemoteSession` initializes a conversation, it iterates over every agent in the handoff graph and either creates or updates it via the Agents API:

- **`Agent(id=None)`**: a new remote agent is created with `beta.agents.create()`. The returned ID is stored back on the `Agent` object, so subsequent runs with the **same instance** reuse it.
- **`Agent(id="existing-id")`**: the existing remote agent is updated with `beta.agents.update()`. No new agent is created.

To reuse a pre-existing agent across workflow executions, set `agent.id` before calling `Runner.run()`:

**Python**

```python
agent = workflows_mistralai.Agent(
    id="ag_abc123",  # Reuse an existing remote agent
    model="mistral-medium-latest",
    name="finance-agent",
    instructions="Use tools to answer financial questions.",
    tools=[get_interest_rate],
)
```

> **Warning**
>
> Agents created by `RemoteSession` are **not cleaned up automatically** after a run completes. If you create agents dynamically (without setting `id`), a new remote agent will be created on every workflow execution.

## section: local-session
    Durable agents > Session types > LocalSession (experimental)
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#local-session
### LocalSession (experimental) {#local-session}

Runs agents locally using the completion endpoint:

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai

session = workflows_mistralai.LocalSession()

outputs = await workflows_mistralai.Runner.run(
    agent=agent,
    inputs="Your question here",
    session=session,
)
```

Use cases:

- On-premises or private cloud deployments where the Agents API is not available
- Development and testing
- Full context control

> **Warning**
>
> `LocalSession` is experimental and might be removed in a later version. Use `RemoteSession` for production workloads.

## section: complete-workflow-example
    Durable agents > Complete workflow example
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#complete-workflow-example
## Complete workflow example {#complete-workflow-example}

A full example combining activities, handoffs, and workflow orchestration:

**Python**

```python
import asyncio
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai
from mistralai.client.models import TextChunk


@workflows.activity()
async def calculate_risk_score(deal_type: str, amount: float) -> dict:
    """Calculate financial risk score for a deal.

    Args:
        deal_type: The type of deal being analyzed
        amount: The monetary amount of the deal
    """
    risk_score = min(100.0, amount / 10000.0)
    risk_factors = []
    if amount > 100000:
        risk_factors.append("High value transaction")
    return {"risk_score": risk_score, "risk_factors": risk_factors}


@workflows.workflow.define(name="deal_analysis_workflow")
class DealAnalysisWorkflow:
    @workflows.workflow.entrypoint
    async def entrypoint(self, deal_request: str) -> dict:
        """Analyze a deal request.

        Args:
            deal_request: The deal request to analyze
        """
        session = workflows_mistralai.RemoteSession()

        # Risk assessment agent
        risk_agent = workflows_mistralai.Agent(
            model="mistral-medium-latest",
            name="risk-agent",
            description="Analyzes financial risk of deals",
            instructions="Use the risk calculation tool to assess deal risk.",
            tools=[calculate_risk_score],
        )

        # Main coordinator agent
        coordinator = workflows_mistralai.Agent(
            model="mistral-medium-latest",
            name="deal-coordinator",
            description="Coordinates deal analysis",
            instructions="Analyze the deal request and hand off to specialists.",
            handoffs=[risk_agent],
        )

        outputs = await workflows_mistralai.Runner.run(
            agent=coordinator,
            inputs=deal_request,
            session=session,
        )

        analysis = "\n".join([
            output.text for output in outputs
            if isinstance(output, TextChunk)
        ])

        return {"analysis": analysis}


if __name__ == "__main__":
    asyncio.run(workflows.run_worker([DealAnalysisWorkflow]))
```

## section: observability
    Durable agents > Observability
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#observability
## Observability {#observability}

Agent activity emits the same workflow and activity events as any other workflow. Subscribe to them live via [Streaming](https://docs.mistral.ai/studio/workflows/building-workflows/streaming) and [Consuming Streaming Events](https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events), or replay the full event history after the fact.

## section: best-practices
    Durable agents > Best practices
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#best-practices
## Best practices {#best-practices}

1. **Use `RemoteSession` for production** so the agent runs against the Agents API rather than the raw completion endpoint.
2. **Set `agent.id`** on agents you want to reuse across runs. Otherwise, `RemoteSession` creates a new remote agent on every execution and never cleans them up.
3. **Wrap tool side-effects in activities** so they get retry isolation and appear in the execution history.

Results: 18 sections, the whole page.
```

## Answer

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

