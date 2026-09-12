# mined2-022 (single_page, 11 connector calls)

## Question

Creating an agent with `tool_choice: 'required'` fails with `Can't create an agent with 'tool_choice' set to 'required' and using built in connectors` — how do I make it always search the web?

## Thinking

The user is encountering an error when trying to create an agent with `tool_choice: 'required'` and built-in connectors. They want the agent to always search the web. I need to search the Mistral documentation for information about this error and how to configure agents to always use web search.

Let me search for the specific error message and related concepts.

The search returned some results but I need more specific information about the error and web search configuration. Let me search for more details about tool_choice options and web_search specifically.

I need to read the actual documentation page to understand the constraints and error message better. Let me fetch the full content of the connectors conversations page.

Now I need to find information about the tool_choice parameter and its constraints, particularly the error about not being able to use 'required' with built-in connectors. Let me search for tool_choice documentation.

Let me read the agent-tools page to understand the built-in tools and their constraints better.

I need to find the specific documentation about tool_choice parameter and its allowed values. Let me search for that.

Let me read the agents-api page to find the tool_choice parameter details and its constraints.

I need to find the specific error message and understand the constraint. Let me search for the exact error text in the documentation.

Let me search for more general information about tool_choice and its valid values. The error suggests that 'required' is not compatible with built-in connectors, so I need to find what values are allowed and what the workaround is.

Let me read the build-an-agent quickstart to understand the tool_choice parameter better.

Now I have enough information. Based on the documentation I've reviewed:

1. The error message indicates that `tool_choice: 'required'` cannot be used with built-in connectors
2. From the quickstart guide, I learned that `tool_choice` can be set to `"any"` to force the model to always call a tool, or `"auto"` (default) to let the model decide
3. The error specifically mentions "built in connectors" - but the user wants to use web_search which is a built-in tool, not a connector
4. The documentation shows that built-in tools like `web_search` can be used in agents and conversations

The issue is that `tool_choice: 'required'` is not a valid value for the Mistral API. The valid values appear to be `"auto"` (default) and `"any"`. The `"any"` value forces the model to always call a tool.

So the solution is:
- Use `tool_choice: "any"` instead of `"required"`
- Include `web_search` in the tools array
- This will force the model to always call a tool, and since web_search is the only tool available (or the most appropriate one), it will use that

Let me verify this understanding by checking if there's any documentation about the exact valid values for tool_choice.

Perfect! Now I have the information I need. From the documentation:

1. The error occurs because `tool_choice: 'required'` is not a valid value - the valid values are `"auto"` (default) and `"any"`
2. From the quickstart: "Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide."
3. From the known limitations: "`tool_choice: "any"` forces a tool call but does not guarantee which tool is selected."

So to make an agent always search the web:
- Use `tool_choice: "any"` in the `completion_args`
- Include `web_search` as the only tool (or the primary tool) in the tools array

This will force the model to always call a tool, and if `web_search` is the only tool available, it will use that. If there are multiple tools, the model will still decide which one to use, but it will always call at least one.

The answer should be:
1. Use `tool_choice: "any"` instead of `"required"`
2. Include `web_search` in the tools array
3. Optionally, to guarantee web search is always used, only include `web_search` as the tool

Let me formulate the final answer.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Can't create an agent with 'tool_choice' set to 'required' and using built in connectors", "max_hits": 5}
```

Result:

```
q: "Can't create an agent with 'tool_choice' set to 'required' and using built in connectors"

[1] https://docs.mistral.ai/studio/connectors/conversations | section: agents-with-connectors
    Using Connectors in conversations > Add Connectors to an Agent
    You can also attach Connectors directly to an Agent at creation time. Every conversation started with that Agent then has access to the Connector tools automatically, without passing a `tools` array each time. > **Tip** > > This is useful when an Agent always needs the same external tools (for example, a support Agent that always queries a CRM). **Python** ```python import asyncio from mistralai.c …
    cite: https://docs.mistral.ai/studio/connectors/conversations#agents-with-connectors

[2] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[3] https://docs.mistral.ai/studio/connectors/conversations | section: combining-tools
    Using Connectors in conversations > Use built-in tools alongside Connectors
    Mistral provides [built-in tools](https://docs.mistral.ai/studio/agents/agent-tools) such as `web_search`, `code_interpreter`, `image_generation`, and `document_library`. You can pass them alongside Connectors in the same `tools` array. The model decides which tool to call **based on the query**. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversati …
    cite: https://docs.mistral.ai/studio/connectors/conversations#combining-tools

[4] https://docs.mistral.ai/studio/agents/agents-api | section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 0, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:16:16.726718Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": null, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=agent%2C%20you%20will
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") reads this section

[5] https://docs.mistral.ai/studio/connectors/conversations | section: using-connectors-in-conversations
    Using Connectors in conversations
    After a Connector is [registered](https://docs.mistral.ai/studio/connectors/management) and [authenticated](https://docs.mistral.ai/studio/connectors/management#get-auth-url) (if required), you can attach it to any conversation. You can mix Connectors with built-in tools like `web_search`, filter which tools the model can use, and configure Connectors on Agents so they're available in every conver …
    cite: https://docs.mistral.ai/studio/connectors/conversations

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/connectors/conversations") to read hit 1 on its page
```

### 2. mistral_docs_search

```json
{"q": "tool_choice required built in connectors web_search", "max_hits": 5}
```

Result:

```
q: "tool_choice required built in connectors web_search"

[1] https://docs.mistral.ai/studio/connectors/conversations | section: combining-tools
    Using Connectors in conversations > Use built-in tools alongside Connectors
    Mistral provides [built-in tools](https://docs.mistral.ai/studio/agents/agent-tools) such as `web_search`, `code_interpreter`, `image_generation`, and `document_library`. You can pass them alongside Connectors in the same `tools` array. The model decides which tool to call **based on the query**. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversati …
    cite: https://docs.mistral.ai/studio/connectors/conversations#combining-tools

[2] https://docs.mistral.ai/vibe/work/web-search-open-url | section: search-the-web
    Search the web
    Work can browse the internet in real time and read specific web pages as part of a task. **Web search** answers questions with up-to-date, sourced information. **Open URL** lets Work read and analyze a page you already have the link to. > **Info** > > **Knowledge cutoff**: every language model is trained on data collected up to a fixed date. After that date, the model has no built-in knowledge of …
    cite: https://docs.mistral.ai/vibe/work/web-search-open-url

[3] https://docs.mistral.ai/vibe/work/web-search-open-url | section: choosing-the-right-tool
    Search the web > Choosing the right tool
    Pick the option that fits your situation: | You want to... | Use | |----------------|-----| | Get a quick, up-to-date answer with sources | **Web search** | | Analyze a specific page you already have the link to | **Open URL** | | Get a structured, cited report pulling from many sources | **[Deep Research](https://docs.mistral.ai/vibe/chat-legacy/deep-research)** Skill in Work | | Search trusted i …
    cite: https://docs.mistral.ai/vibe/work/web-search-open-url#choosing-the-right-tool

[4] https://docs.mistral.ai/studio/connectors/conversations | section: using-connectors-in-conversations
    Using Connectors in conversations
    After a Connector is [registered](https://docs.mistral.ai/studio/connectors/management) and [authenticated](https://docs.mistral.ai/studio/connectors/management#get-auth-url) (if required), you can attach it to any conversation. You can mix Connectors with built-in tools like `web_search`, filter which tools the model can use, and configure Connectors on Agents so they're available in every conver …
    cite: https://docs.mistral.ai/studio/connectors/conversations

[5] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: built-in-tools
    Durable agents > Built-in tools
    Use Mistral's built-in tools alongside activities: **Python** ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai as workflows_mistralai from mistralai.client.models import WebSearchTool agent = workflows_mistralai.Agent( model="mistral-medium-latest", name="web-search-agent", description="Agent with web search capability", instructions="Use web search to …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#built-in-tools

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/connectors/conversations") to read hit 1 on its page
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/connectors/conversations"}
```

Result:

```
page: https://docs.mistral.ai/studio/connectors/conversations | "Using Connectors in conversations"

## section: using-connectors-in-conversations
    Using Connectors in conversations
    cite: https://docs.mistral.ai/studio/connectors/conversations
# Using Connectors in conversations

After a Connector is [registered](https://docs.mistral.ai/studio/connectors/management) and [authenticated](https://docs.mistral.ai/studio/connectors/management#get-auth-url) (if required), you can attach it to any conversation.

You can mix Connectors with built-in tools like `web_search`, filter which tools the model can use, and configure Connectors on Agents so they're available in every conversation.

> **Info**
>
> Tools are [MCP server executable functions](https://modelcontextprotocol.io/docs/learn/architecture#primitives) the model can call. When you attach a Connector, the model discovers these tools automatically and calls the right ones based on the query.

## section: basic-usage
    Using Connectors in conversations > Attach Connectors to a conversation > Basic usage
    cite: https://docs.mistral.ai/studio/connectors/conversations#basic-usage
### Basic usage {#basic-usage}

Pass any Connector as a `tool` to a conversation using `type: "connector"` and the Connector's name or UUID as `connector_id`.

> **Note**
>
> All tools the Connector exposes are available to the model. To restrict which tools the model can call, see [Filter tools](https://docs.mistral.ai/studio/connectors/conversations#filtering-tools).

**Python**

```python
import asyncio
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")


async def main() -> None:
    response = await client.beta.conversations.start_async(
        model="mistral-small-latest",
        inputs=[
            {
                "role": "user",
                "content": "Using deepwiki, tell me about the structure of the sqlite/sqlite repository.",
            }
        ],
        tools=[
            {
                "type": "connector",
                "connector_id": "my_deepwiki",  # name or UUID
            },
        ],
    )
    for output in response.outputs:
        if output.type == "message.output":
            print(output.content)


asyncio.run(main())
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const client = new Mistral({ apiKey: "your-api-key" });

async function main(): Promise<void> {
  const response = await client.beta.conversations.start({
    model: "mistral-small-latest",
    inputs: [
      {
        role: "user",
        content: "Using deepwiki, tell me about the structure of the sqlite/sqlite repository.",
      },
    ],
    tools: [
      {
        type: "connector",
        connectorId: "my_deepwiki", // name or UUID
      },
    ],
  });

  for (const output of response.outputs ?? []) {
    if (output.type === "message.output") {
      console.log(output.content);
    }
  }
}

main();
```

**cURL**

**cURL**

```bash
curl -X POST "https://api.mistral.ai/v1/conversations" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-small-latest",
    "inputs": [{"role": "user", "content": "Using deepwiki, tell me about the structure of the sqlite/sqlite repository."}],
    "tools": [{"type": "connector", "connector_id": "my_deepwiki"}]
  }'
```

## section: filtering-tools
    Using Connectors in conversations > Attach Connectors to a conversation > Filter tools
    cite: https://docs.mistral.ai/studio/connectors/conversations#filtering-tools
### Filter tools {#filtering-tools}

To control which tools from a Connector the model can use, add a `tool_configuration` object. Set `include` to allowlist specific tools, or `exclude` to block them. You can use one or the other, but not both at the same time.

**Python**

```python
import asyncio
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")


async def main() -> None:
    # Exclude specific tools
    response = await client.beta.conversations.start_async(
        model="mistral-small-latest",
        inputs=[{"role": "user", "content": "What tools do you have access to?"}],
        tools=[
            {
                "type": "connector",
                "connector_id": "my_deepwiki",
                "tool_configuration": {
                    "exclude": ["read_wiki_structure"],
                },
            },
        ],
    )

    # Include only specific tools
    response = await client.beta.conversations.start_async(
        model="mistral-small-latest",
        inputs=[{"role": "user", "content": "What tools do you have access to?"}],
        tools=[
            {
                "type": "connector",
                "connector_id": "my_deepwiki",
                "tool_configuration": {
                    "include": ["ask_question"],
                },
            },
        ],
    )


asyncio.run(main())
```

**TypeScript**

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const client = new Mistral({ apiKey: "your-api-key" });

async function main(): Promise<void> {
  // Exclude specific tools
  await client.beta.conversations.start({
    model: "mistral-small-latest",
    inputs: [{ role: "user", content: "What tools do you have access to?" }],
    tools: [
      {
        type: "connector",
        connectorId: "my_deepwiki",
        toolConfiguration: {
          exclude: ["read_wiki_structure"],
        },
      },
    ],
  });

  // Include only specific tools
  await client.beta.conversations.start({
    model: "mistral-small-latest",
    inputs: [{ role: "user", content: "What tools do you have access to?" }],
    tools: [
      {
        type: "connector",
        connectorId: "my_deepwiki",
        toolConfiguration: {
          include: ["ask_question"],
        },
      },
    ],
  });
}

main();
```

**cURL**

**cURL**

```bash
# Exclude specific tools
curl -X POST "https://api.mistral.ai/v1/conversations" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-small-latest",
    "inputs": [{"role": "user", "content": "What tools do you have access to?"}],
    "tools": [{
      "type": "connector",
      "connector_id": "my_deepwiki",
      "tool_configuration": { "exclude": ["read_wiki_structure"] }
    }]
  }'

# Include only specific tools
curl -X POST "https://api.mistral.ai/v1/conversations" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-small-latest",
    "inputs": [{"role": "user", "content": "What tools do you have access to?"}],
    "tools": [{
      "type": "connector",
      "connector_id": "my_deepwiki",
      "tool_configuration": { "include": ["ask_question"] }
    }]
  }'
```

> **Tip**
>
> You can require user approval before a tool runs by adding `requires_confirmation` to the `tool_configuration`. This is useful for sensitive actions like sending emails or modifying data. See [Human-in-the-loop](https://docs.mistral.ai/studio/connectors/confirmation) for the full confirmation flow.

## section: combining-tools
    Using Connectors in conversations > Use built-in tools alongside Connectors
    cite: https://docs.mistral.ai/studio/connectors/conversations#combining-tools
## Use built-in tools alongside Connectors {#combining-tools}

Mistral provides [built-in tools](https://docs.mistral.ai/studio/agents/agent-tools) such as `web_search`, `code_interpreter`, `image_generation`, and `document_library`. You can pass them alongside Connectors in the same `tools` array. The model decides which tool to call **based on the query**.

> **Warning**
>
> `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported in the Chat Completions API.

**Python**

```python
import asyncio
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")


async def main() -> None:
    response = await client.beta.conversations.start_async(
        model="mistral-small-latest",
        inputs=[
            {
                "role": "user",
                "content": "Search the web for the latest SQLite release, then use deepwiki to find where the version is defined in the sqlite/sqlite repo.",
            }
        ],
        tools=[
            {"type": "web_search"},
            {"type": "connector", "connector_id": "my_deepwiki"},
        ],
    )
    for output in response.outputs:
        if output.type == "message.output":
            print(output.content)


asyncio.run(main())
```

**TypeScript**

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const client = new Mistral({ apiKey: "your-api-key" });

async function main(): Promise<void> {
  const response = await client.beta.conversations.start({
    model: "mistral-small-latest",
    inputs: [
      {
        role: "user",
        content: "Search the web for the latest SQLite release, then use deepwiki to find where the version is defined in the sqlite/sqlite repo.",
      },
    ],
    tools: [
      { type: "web_search" },
      { type: "connector", connectorId: "my_deepwiki" },
    ],
  });

  for (const output of response.outputs ?? []) {
    if (output.type === "message.output") {
      console.log(output.content);
    }
  }
}

main();
```

**cURL**

```bash
curl -X POST "https://api.mistral.ai/v1/conversations" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-small-latest",
    "inputs": [{"role": "user", "content": "Search the web for the latest SQLite release, then use deepwiki to find where the version is defined in the sqlite/sqlite repo."}],
    "tools": [
      {"type": "web_search"},
      {"type": "connector", "connector_id": "my_deepwiki"}
    ]
  }'
```

## section: agents-with-connectors
    Using Connectors in conversations > Add Connectors to an Agent
    cite: https://docs.mistral.ai/studio/connectors/conversations#agents-with-connectors
## Add Connectors to an Agent {#agents-with-connectors}

You can also attach Connectors directly to an Agent at creation time. Every conversation started with that Agent then has access to the Connector tools automatically, without passing a `tools` array each time.

> **Tip**
>
> This is useful when an Agent always needs the same external tools (for example, a support Agent that always queries a CRM).

**Python**

```python
import asyncio
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")


async def main() -> None:
    # Create the agent with a connector
    agent = await client.beta.agents.create_async(
        name="deepwiki_agent",
        description="Agent with DeepWiki access for code repository exploration",
        model="mistral-small-latest",
        instructions="You are a helpful assistant that can explore code repositories using DeepWiki. Be concise.",
        tools=[
            {
                "type": "connector",
                "connector_id": "my_deepwiki",
            },
        ],
    )

    # Start a conversation using the agent. No tools needed here
    response = await client.beta.conversations.start_async(
        agent_id=agent.id,
        inputs=[
            {"role": "user", "content": "What is the main purpose of the sqlite repository?"}
        ],
    )
    for output in response.outputs:
        if output.type == "message.output":
            print(output.content)


asyncio.run(main())
```

**TypeScript**

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const client = new Mistral({ apiKey: "your-api-key" });

async function main(): Promise<void> {
  // Create the agent with a connector
  const agent = await client.beta.agents.create({
    name: "deepwiki_agent",
    description: "Agent with DeepWiki access for code repository exploration",
    model: "mistral-small-latest",
    instructions: "You are a helpful assistant that can explore code repositories using DeepWiki. Be concise.",
    tools: [
      {
        type: "connector",
        connectorId: "my_deepwiki",
      },
    ],
  });

  // Start a conversation using the agent. No tools needed here
  const response = await client.beta.conversations.start({
    agentId: agent.id,
    inputs: [
      { role: "user", content: "What is the main purpose of the sqlite repository?" },
    ],
  });

  for (const output of response.outputs ?? []) {
    if (output.type === "message.output") {
      console.log(output.content);
    }
  }
}

main();
```

**cURL**

**cURL**

```bash
# Create agent
curl -X POST "https://api.mistral.ai/v1/agents" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "deepwiki_agent",
    "model": "mistral-small-latest",
    "instructions": "You are a helpful assistant that can explore code repositories using DeepWiki. Be concise.",
    "tools": [{"type": "connector", "connector_id": "my_deepwiki"}]
  }'

# Start conversation with the agent (use agent_id from response above)
curl -X POST "https://api.mistral.ai/v1/conversations" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "<agent-id>",
    "inputs": [{"role": "user", "content": "What is the main purpose of the sqlite repository?"}]
  }'
```

> **Caution**
>
> Use `agent_id` **instead of** `model` when starting a conversation. You cannot pass both.

Results: 5 sections, the whole page.
```

### 4. mistral_docs_search

```json
{"q": "tool_choice required agents built-in tools", "max_hits": 5}
```

Result:

```
q: "tool_choice required agents built-in tools"

[1] https://docs.mistral.ai/studio/agents/agent-tools | section: built-in-tools
    Agents Tools Overview > Tools > Built-in tools
    ![built_in_graph](https://docs.mistral.ai/img/built_in_graph.png) Built-in tools are ready out of the box. They can be called at any point, and all execution happens in our internal environment. They're also available for users to use directly via Conversations without creating an Agent first.
    cite: https://docs.mistral.ai/studio/agents/agent-tools#built-in-tools

[2] https://docs.mistral.ai/studio/agents/agent-tools | section: general-usage
    Agents Tools Overview > Tools > Built-in tools > General usage
    Built-in tool support depends on the API you use. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#general-usage

[3] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: built-in-tools
    Durable agents > Built-in tools
    Use Mistral's built-in tools alongside activities: **Python** ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai as workflows_mistralai from mistralai.client.models import WebSearchTool agent = workflows_mistralai.Agent( model="mistral-medium-latest", name="web-search-agent", description="Agent with web search capability", instructions="Use web search to …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#built-in-tools

[4] https://docs.mistral.ai/studio/agents/agent-tools | section: tool-types
    Agents Tools Overview > Tools > Tool types
    We provide a variety of different **types** of tools agents can use. |Type|Description| |---|---| |[Web Search](https://docs.mistral.ai/studio/agents/agent-tools/websearch)| Built-in. Search the web for up-to-date information not in the agent's knowledge.| |[Code Interpreter](https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter)| Built-in. Run code and generate plots, useful for data …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#tool-types

[5] https://docs.mistral.ai/vibe/code/vs-code-extension/agents | section: built-in-agents
    Agents > Built-in agents
    | Agent | Behavior | |---|---| | `Default` | General-purpose agent. Asks for approval before running tools. | | `Plan` | Read-only agent for exploration and planning. Auto-approves safe read tools. | | `Accept Edits` | Auto-approves file edits in the working directory. Still asks for approval for other actions (for example, shell commands). | | `Auto Approve` | Auto-approves all tool execution. Us …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/agents#built-in-agents

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agent-tools") to read hit 1 on its page
```

### 5. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/agents/agent-tools"}
```

Result:

```
page: https://docs.mistral.ai/studio/agents/agent-tools | "Agents Tools Overview"

## section: tools
    Agents Tools Overview > Tools
    cite: https://docs.mistral.ai/studio/agents/agent-tools
# Tools

Agents can use tools to interact with the external world, these can be APIs, databases, or other services, increasing the capabilities of your agent and extending its functionality beyond its own knowledge base and fixed environment.

![tools_graph](https://docs.mistral.ai/img/tools_graph.png)

## section: tool-types
    Agents Tools Overview > Tools > Tool types
    cite: https://docs.mistral.ai/studio/agents/agent-tools#tool-types
## Tool types {#tool-types}

We provide a variety of different **types** of tools agents can use.

|Type|Description|
|---|---|
|[Web Search](https://docs.mistral.ai/studio/agents/agent-tools/websearch)| Built-in. Search the web for up-to-date information not in the agent's knowledge.|
|[Code Interpreter](https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter)| Built-in. Run code and generate plots, useful for data analysis, visualization, or sandboxed execution.|
|[Image Generation](https://docs.mistral.ai/studio/agents/agent-tools/image_generation)| Built-in. Generate images based on a prompt or description.|
|[Document Library](https://docs.mistral.ai/studio/search/libraries#connecting-libraries-to-agents)| Built-in. Search through documents uploaded to your [Libraries](https://docs.mistral.ai/studio/search/libraries), enabling RAG to answer questions based on specific information.|
|[Function Calling](https://docs.mistral.ai/studio/agents/agent-tools/function-calling)| Custom local tools: functions defined in your environment that can be called by the agent. Execution happens locally.|
|[Connectors](https://docs.mistral.ai/studio/connectors)| Register MCP servers as managed Connectors. Tools are discovered automatically and executed server-side.|

## section: built-in-tools
    Agents Tools Overview > Tools > Built-in tools
    cite: https://docs.mistral.ai/studio/agents/agent-tools#built-in-tools
## Built-in tools {#built-in-tools}

![built_in_graph](https://docs.mistral.ai/img/built_in_graph.png)

Built-in tools are ready out of the box. They can be called at any point, and all execution happens in our internal environment. They're also available for users to use directly via Conversations without creating an Agent first.

## section: general-usage
    Agents Tools Overview > Tools > Built-in tools > General usage
    cite: https://docs.mistral.ai/studio/agents/agent-tools#general-usage
### General usage {#general-usage}

Built-in tool support depends on the API you use.

> **Warning**
>
> `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported in the Chat Completions API.

To use them, specify the tool in the `tools` parameter when creating an Agent or calling the Conversations API.

> **Tip**
>
> You can use multiple tools at the same time!

**Python**

**agent creation**

```py
agent = client.beta.agents.create(
    model="<model>",
    name="<name_of_the_agent>",
    description="<description>",
    instructions="<instructions_or_system_prompt>",
    tools=[<list_of_tools>]
)
```

**direct conversation**

```py
response = client.beta.conversations.start(
    model="<model>",
    inputs=[<messages_or_question>],
    tools=[<list_of_tools>],
    # store=False
)
```

**TypeScript**

**agent creation**

```typescript
agent = client.beta.agents.create({
    model:"<model>",
    name:"<name_of_the_agent>",
    description:"<description>",
    instructions:"<instructions_or_system_prompt>",
    tools:[<list_of_tools>]
});
```

**direct conversation**

```typescript
response = client.beta.conversations.start({
    model:"<model>",
    inputs:[<messages_or_question>],
    tools:[<list_of_tools>],
    // store:False
});
```

**cURL**

**agent creation**

**cURL**

**agent creation**

```bash
curl --location "https://api.mistral.ai/v1/agents" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "model": "<model>",
     "name": "<name_of_the_agent>",
     "description": "<description>",
     "instructions": "<instructions_or_system_prompt>",
     "tools": [<list_of_tools>]
  }'
```

**direct conversation**

```bash
curl --location "https://api.mistral.ai/v1/conversations" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "model": "<model>",
     "inputs": [<messages_or_question>],
     "tools": [<list_of_tools>]
  }'
```

Results: 4 sections, the whole page.
```

### 6. mistral_docs_search

```json
{"q": "tool_choice parameter agents API", "max_hits": 5}
```

Result:

```
q: "tool_choice parameter agents API"

[1] https://docs.mistral.ai/studio/agents/agents-api | section: create-a-new-version
    Agents & Conversations > Agent Creation and Management > Create a new Version
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 1, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:17:19.872254Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": 0.95, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="create-a-new-version") reads this section

[2] https://docs.mistral.ai/studio/agents/agents-api | section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 0, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:16:16.726718Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": null, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=agent%2C%20you%20will
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") reads this section

[3] https://docs.mistral.ai/studio/agents/agents-api | section: available-conversations
    Agents & Conversations > Conversations > Available conversations
    ```json [ { "id": "conv_0684fe18cbc57ba6800065acdd2b6c85", "created_at": "2025-06-16T09:19:08.735790Z", "updated_at": "2025-06-16T09:20:03.273654Z", "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986", "name": null, "description": null, "object": "conversation" }, { "id": "conv_0684fd306df172f2800051d4f82d4a8b", "created_at": "2025-06-16T08:17:10.871401Z", "updated_at": "2025-06-16T08:17:10.871402Z" …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="available-conversations") reads this section

[4] https://docs.mistral.ai/studio/agents/agents-api | section: change-version
    Agents & Conversations > Agent Creation and Management > Change version
    Change manually the version of the Agent. **Python** ```py simple_agent = client.beta.agents.update_version( agent_id=simple_agent.id, version=0 ) ``` **TypeScript** ```typescript websearchAgent = await client.beta.agents.updateVersion({ agentId: websearchAgent.id, version: 0 }); ``` **cURL** ```bash curl --location "https://api.mistral.ai/v1/agents/<agent_id>/version" \ --header 'Content-Type: ap …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=Change%20manually%20the
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="change-version") reads this section

[5] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="create-a-new-version") to read hit 1 on its page
```

### 7. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/agents/agents-api"}
```

Result:

```
page: https://docs.mistral.ai/studio/agents/agents-api | "Agents & Conversations"

## section: agents-conversations
    Agents & Conversations
    cite: https://docs.mistral.ai/studio/agents/agents-api
# Agents & Conversations

Agents is a feature that allows developers to create predefined models with their own system prompts and tools. In the other hand, Conversations is a feature that allows developers to create a history of interactions with an assistant that use Agents or our models directly.

## section: objects
    Agents & Conversations > Objects
    cite: https://docs.mistral.ai/studio/agents/agents-api#objects
## Objects {#objects}

We introduce three new main objects that our API makes use of:
- **Agents**: A set of pre-selected values to augment model abilities, such as tools, instructions, and completion parameters.
- **Conversation**: A history of interactions, past events and entries with an assistant, such as messages and tool executions, Conversations can be started by an Agent or a Model.
- **Entry**: An action that can be created by the user or an assistant. It brings a more flexible and expressive representation of interactions between a user and one or multiple assistants. This allows for more control over describing events.

> **Tip**
>
> You can create Conversations without creating Agents. These two APIs are independent.

To find all details visit our [Agents](https://docs.mistral.ai/api/#tag/beta.agents) and [Conversations](https://docs.mistral.ai/api/#tag/beta.conversations) API spec.

## section: agent-creation-and-management
    Agents & Conversations > Agent Creation and Management
    cite: https://docs.mistral.ai/studio/agents/agents-api
## Agent Creation and Management

Agents are a set of pre-selected values, such as tools, instructions, and completion parameters, that will define the behavior of the model.

**Agent Creation**

When creating an Agent, there are multiple parameters and values that need to be set in advance. These are:
- `model`: The model your agent will use among our available models for chat completion.
- `description`: The agent description, related to the task it must accomplish or the use case at stake.
- `name`: The name of your agent.
- `instructions` *optional*: The main instructions of the agent, also known as the system prompt. This must accurately describe the main task of your agent.
- `tools` *optional*: A list of tools the model can make use of. There are currently different `types` of tools:
  - `function`: User-defined tools, with similar usage to the standard function calling used with chat completion.
  - `web_search`/`web_search_premium`: Our built-in tool for web search.
  - `code_interpreter`: Our built-in tool for code execution.
  - `image_generation`: Our built-in tool for image generation.
  - `document_library`: Our built-in RAG tool for knowledge grounding and search on custom data.
- `completion_args` *optional*: Standard chat completion sampler arguments. All chat completion arguments are accepted.

## section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    cite: https://docs.mistral.ai/studio/agents/agents-api
### Creating an Agent

**Python**

**V1**

```py
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key)

simple_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    description="A simple Agent with persistent state.",
    name="Simple Agent"
)
```

**V2**

```py
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key)

simple_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    description="A simple Agent with persistent state.",
    name="Simple Agent"
)
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";
import * as dotenv from 'dotenv';

dotenv.config();

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({ apiKey: apiKey });

async function main() {
  let simpleAgent = await client.beta.agents.create({
      model: "mistral-medium-latest",
      description: "A simple Agent with persistent state.",
      name: "Simple Agent",
  });
}
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/agents" \
    --header 'Content-Type: application/json' \
    --header 'Accept: application/json' \
    --header "Authorization: Bearer $MISTRAL_API_KEY" \
    --data '{
    "model": "mistral-medium-latest",
    "name": "Simple Agent",
    "description": "A simple Agent with persistent state."
  }'
```

**Output**

**Output**

```json
{
  "model": "mistral-medium-latest",
  "name": "Simple Agent",
  "id": "ag_0684fe0e0b98773e8000323fc71a3986",
  "version": 0,
  "created_at": "2025-06-16T09:16:16.726715Z",
  "updated_at": "2025-06-16T09:16:16.726718Z",
  "instructions": null,
  "tools": [],
  "completion_args": {
    "stop": null,
    "presence_penalty": null,
    "frequency_penalty": null,
    "temperature": 0.3,
    "top_p": null,
    "max_tokens": null,
    "random_seed": null,
    "prediction": null,
    "response_format": null,
    "tool_choice": "auto"
  },
  "description": "A simple Agent with persistent state.",
  "handoffs": null,
  "object": "agent"
}
```

When creating an agent, you will receive an Agent object with an agent ID. You can then use that ID to have conversations.

Here is an example of a Web Search Agent using our built-in tool:

**Python**

```py
websearch_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    description="Agent able to search information over the web, such as news, weather, sport results...",
    name="Websearch Agent",
    instructions="You have the ability to perform web searches with `web_search` to find up-to-date information.",
    tools=[{"type": "web_search"}],
    completion_args={
        "temperature": 0.3,
        "top_p": 0.95,
    }
)
```

**TypeScript**

**TypeScript**

```typescript
let websearchAgent = await client.beta.agents.create({
  model: "mistral-medium-latest",
  name: "WebSearch Agent",
  instructions: "Use your websearch abilities when answering requests you don't know.",
  description: "Agent able to fetch new information on the web.",
  tools: [{ type: "web_search" }],
});
```

**cURL**

```bash
curl -X POST "https://api.mistral.ai/v1/agents" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-medium-latest",
    "name": "WebSearch Agent",
    "instructions": "Use your websearch abilities when answering requests you do not know.",
    "description": "Agent able to fetch new information on the web.",
    "tools": [
      {
        "type": "web_search"
      }
    ]
  }'
```

**Output**

**Output**

```json
{
  "instructions": "Use your websearch abilities when answering requests you don't know.",
  "tools": [
    {
      "type": "web_search"
    }
  ],
  "completionArgs": {
    "stop": null,
    "presencePenalty": null,
    "frequencyPenalty": null,
    "temperature": null,
    "topP": null,
    "maxTokens": null,
    "randomSeed": null,
    "prediction": null,
    "responseFormat": null,
    "toolChoice": "auto"
  },
  "model": "mistral-medium-latest",
  "name": "WebSearch Agent",
  "description": "Agent able to fetch new information on the web.",
  "handoffs": null,
  "object": "agent",
  "id": "ag_019905c63b247447a97586fd6184ba5d",
  "version": 0,
  "createdAt": "2025-09-01T14:55:01.417Z",
  "updatedAt": "2025-09-01T14:55:01.417Z"
}
```

You can find more information [here](https://docs.mistral.ai/studio/agents/agent-tools/websearch).

**Agent Update**

After creation, you can update the Agent with new settings if needed. The arguments are the same as those used when creating an Agent.
The result is a new `version` of the Agent with the new settings, you can this way have the previous and new versions available.

## section: create-a-new-version
    Agents & Conversations > Agent Creation and Management > Create a new Version
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=the%20Agent%2C%20will
### Create a new Version

Create a new `version` of the Agent, will be used by default.

**Python**

```py
simple_agent = client.beta.agents.update(
    agent_id=simple_agent.id, 
    description="An edited simple agent.",
    completion_args={
        "temperature": 0.3,
        "top_p": 0.95,
    }
)
```

**TypeScript**

```typescript
websearchAgent = await client.beta.agents.update({
    agentId: websearchAgent.id, 
    agentUpdateRequest: {
        completionArgs: {
            temperature: 0.3,
            topP: 0.95,
        },
        description: "An edited simple agent."
    },
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/agents/<agent_id>" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "completion_args": {
       "temperature": 0.3,
       "top_p": 0.95
     },
     "description": "An edited simple agent."
  }'
```

**Output**

**Output**

```json
{
  "model": "mistral-medium-latest",
  "name": "Simple Agent",
  "id": "ag_0684fe0e0b98773e8000323fc71a3986",
  "version": 1,
  "created_at": "2025-06-16T09:16:16.726715Z",
  "updated_at": "2025-06-16T09:17:19.872254Z",
  "instructions": null,
  "tools": [],
  "completion_args": {
    "stop": null,
    "presence_penalty": null,
    "frequency_penalty": null,
    "temperature": 0.3,
    "top_p": 0.95,
    "max_tokens": null,
    "random_seed": null,
    "prediction": null,
    "response_format": null,
    "tool_choice": "auto"
  },
  "description": "An edited simple agent.",
  "handoffs": null,
  "object": "agent"
}
```

## section: change-version
    Agents & Conversations > Agent Creation and Management > Change version
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=Change%20manually%20the
### Change version

Change manually the version of the Agent.

**Python**

```py
simple_agent = client.beta.agents.update_version(
    agent_id=simple_agent.id, 
    version=0
)
```

**TypeScript**

```typescript
websearchAgent = await client.beta.agents.updateVersion({
    agentId: websearchAgent.id, 
    version: 0
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/agents/<agent_id>/version" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "version": 0
  }'
```

**Output**

```json
{
  "model": "mistral-medium-latest",
  "name": "Simple Agent",
  "id": "ag_0684fe0e0b98773e8000323fc71a3986",
  "version": 0,
  "created_at": "2025-06-16T09:16:16.726715Z",
  "updated_at": "2025-06-16T09:18:04.624549Z",
  "instructions": null,
  "tools": [],
  "completion_args": {
    "stop": null,
    "presence_penalty": null,
    "frequency_penalty": null,
    "temperature": 0.3,
    "top_p": null,
    "max_tokens": null,
    "random_seed": null,
    "prediction": null,
    "response_format": null,
    "tool_choice": "auto"
  },
  "description": "A simple Agent with persistent state.",
  "handoffs": null,
  "object": "agent"
}
```

## section: conversations-2
    Agents & Conversations > Conversations
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=hand%2C%20Conversations%20are
## Conversations

In the other hand, Conversations are a history of interactions with an assistant. They are more flexible and expressive than the Chat Completion API, allowing for more control over describing events.

> **Conversation access**
>
> The public Conversations API can read and modify only the conversations owned by the creator of the API key used in the request.

Once your agent is created, you can **start** conversations at any point while keeping the same conversation persistent. You first start a conversation by providing:
- `agent_id`: The ID of the agent, created during the Agent creation.
- `inputs`: The message to start the conversation with. It can be either a string with the first user message or question, or the history of messages.

> **Tip**
>
> You can start and continue conversations without creating Agents. These two APIs are independent, in that case you can use the `model` parameter instead of `agent_id`.

Creating a Conversation will return a conversation ID.

To **continue** the conversation and append the exchanges as you go, you provide two values:
- `conversation_id`: The ID created during the conversation start or append that maps to the internally stored conversation history.
- `inputs`: The next message or reply. It can be either a string or a list of messages.

A new Conversation ID is provided at each append.

You can also **opt out** from the automatic storing with `store=False`; this will make the new history not being stored on our cloud.

If the agent has guardrails configured, they are automatically applied to all conversations. You can override them by passing a `guardrails` field directly on `POST /v1/conversations` requests with a model. See [Custom guardrails](https://docs.mistral.ai/studio/safety-moderation#custom-guardrails) for details.

We also provide the parameter `handoff_execution`, which currently has two modes: `server` or `client`.
- `server`: Runs the handoff as expected internally on our cloud servers; this is the default setting.
- `client`: When a handoff is triggered, a response is provided directly to the user, enabling them to handle the handoff with control.

For more information regarding handoffs visit [this section](https://docs.mistral.ai/studio/agents/handoffs).

## section: conversations_management
    Agents & Conversations > Conversations > How to manage conversations
    cite: https://docs.mistral.ai/studio/agents/agents-api#conversations_management
### How to manage conversations {#conversations_management}

Below you can find examples of how to create and manage conversations.

**Starting**

As previously mentioned, you can start a conversation at any given point with your custom Agent or with a specific model of your choice.

To start a conversation with an Agent, you need to provide the Agent ID and the inputs.

**Python**

```py
response = client.beta.conversations.start(
    agent_id=simple_agent.id,
    inputs="Who is Albert Einstein?",
    # inputs=[{"role": "user", "content": "Who is Albert Einstein?"}] is also valid
    # store=False
)
```

**TypeScript**

```typescript
let conversationMultipleEntries = await client.beta.conversations.start({
    agentId: websearchAgent.id,
    inputs: "Who is Albert Einstein?,
    // inputs: [{role: "user", content:"Who is Albert Einstein?"}] is also valid
    // store: false
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/conversations" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "inputs": [
       {
         "role": "user",
         "content": "Who is Albert Einstein?",
         "object": "entry",
         "type": "message.input"
       }
     ],
     "stream": false,
     "agent_id": "<agent_id>"
  }'
```

**Output**

**Output**

```json
{
    "model": "mistral-medium-latest",
    "name": "Simple Agent",
    "id": "ag_0684fe0e0b98773e8000323fc71a3986",
    "version": 0,
    "created_at": "2025-06-16T09:16:16.726715Z",
    "updated_at": "2025-06-16T09:16:16.726718Z",
    "instructions": null,
    "tools": [],
    "completion_args": {
        "stop": null,
        "presence_penalty": null,
        "frequency_penalty": null,
        "temperature": 0.3,
        "top_p": null,
        "max_tokens": null,
        "random_seed": null,
        "prediction": null,
        "response_format": null,
        "tool_choice": "auto"
    },
    "description": "A simple Agent with persistent state.",
    "handoffs": null,
    "object": "agent"
}
```

Without an Agent, querying Conversations would look like so:

**Python**

```py
response = client.beta.conversations.start(
    model="mistral-medium-latest",
    inputs=[{"role": "user", "content": "Who is Albert Einstein?"}]
)
```

**TypeScript**

```typescript
let response = await client.beta.conversations.start({
    model: "mistral-medium-latest",
    inputs:[{role: "user", content:"Who is Albert Einstein?"}]
});
```

**cURL**

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/conversations" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "inputs": [
       {
         "role": "user",
         "content": "Who is Albert Einstein?",
         "object": "entry",
         "type": "message.input"
       }
     ],
     "stream": false,
     "model": "mistral-medium-latest"
  }'
```

**Output**

```json
{
    "model": "mistral-medium-latest",
    "name": "Simple Agent",
    "id": "ag_0684fe0e0b98773e8000323fc71a3986",
    "version": 0,
    "created_at": "2025-06-16T09:16:16.726715Z",
    "updated_at": "2025-06-16T09:16:16.726718Z",
    "instructions": null,
    "tools": [],
    "completion_args": {
        "stop": null,
        "presence_penalty": null,
        "frequency_penalty": null,
        "temperature": 0.3,
        "top_p": null,
        "max_tokens": null,
        "random_seed": null,
        "prediction": null,
        "response_format": null,
        "tool_choice": "auto"
    },
    "description": "A simple Agent with persistent state.",
    "handoffs": null,
    "object": "agent"
}
```

**Continue**

Once created, to continue the conversation you will simply provide the next user input, the history of events being stored by default.

**Python**

**Continue**

Once created, to continue the conversation you will simply provide the next user input, the history of events being stored by default.

**Python**

```py 
response = client.beta.conversations.append(
    conversation_id=response.conversation_id,
    inputs="Translate to French.",
    completion_args={
        "temperature": 0.3,
        "top_p": 0.95,
    }
)
```

**TypeScript**

```typescript
conversation = await client.beta.conversations.append({
    conversationId: conversation.conversationId,
    conversationAppendRequest:
    {
        inputs:[{role: "user", content:"Translate to French."}],
        completionArgs: {
            temperature: 0.3,
            topP: 0.95,
        }
    }
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/conversations/<conv_id>" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "inputs": "Translate to French.",
     "stream": false,
     "store": true,
     "handoff_execution": "server"
  }'
```

**Output**

```json
{
  "conversation_id": "conv_0684fe18cbc57ba6800065acdd2b6c85",
  "outputs": [
    {
      "content": "Albert Einstein était un physicien théoricien né en Allemagne, largement considéré comme l'un des scientifiques les plus influents du 20ᵉ siècle. Il est surtout connu pour avoir développé la théorie de la relativité, qui a révolutionné notre compréhension de l'espace, du temps et de l'énergie. Les travaux d'Einstein ont également apporté des contributions significatives au développement de la mécanique quantique et de la mécanique statistique.\n\nParmi ses réalisations les plus notables, on peut citer :\n\n1. **Théorie de la relativité restreinte (1905)** : Cette théorie a introduit l'idée que les lois de la physique sont les mêmes pour tous les observateurs non accélérés et que la vitesse de la lumière dans le vide est constante, indépendamment du mouvement de l'observateur.\n\n2. **Théorie de la relativité générale (1915)** : Cette théorie a étendu les principes de la relativité restreinte pour inclure la gravité, la décrivant comme une propriété de la géométrie de l'espace et du temps.\n\n3. **Équivalence masse-énergie (E=mc²)** : Cette équation célèbre de sa théorie de la relativité restreinte montre que la masse et l'énergie sont interchangeables.\n\n4. **Effet photoélectrique** : L'explication d'Einstein de l'effet photoélectrique, qui suggérait que la lumière pouvait être décrite comme des paquets discrets d'énergie (quanta ou photons), a été une étape décisive dans le développement de la théorie quantique.\n\nEinstein a reçu le prix Nobel de physique en 1921 pour son explication de l'effet photoélectrique. Il était également connu pour ses efforts humanitaires et son engagement en faveur des droits civiques et de la paix. Einstein a émigré aux États-Unis dans les années 1930 pour échapper à la montée du régime nazi en Allemagne et est devenu professeur à l'Institut d'études avancées de Princeton, dans le New Jersey, où il a passé le reste de sa carrière.\n\nLes travaux d'Einstein continuent d'influencer la physique moderne et notre compréhension de l'univers. Il est décédé le 18 avril 1955.",
      "object": "entry",
      "type": "message.output",
      "created_at": "2025-06-16T09:19:56.901953Z",
      "completed_at": "2025-06-16T09:20:03.257737Z",
      "id": "msg_0684fe1bce6e72bc8000f89d886633fe",
      "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986",
      "model": "mistral-medium-latest",
      "role": "assistant"
    }
  ],
  "usage": {
    "prompt_tokens": 384,
    "completion_tokens": 471,
    "total_tokens": 855,
    "connector_tokens": null,
    "connectors": null
  },
  "object": "conversation.response"
}
```

**retrieve**

You can retrieve conversations; both all available already created and the details of each.

## section: available-conversations
    Agents & Conversations > Conversations > Available conversations
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=can%20retrieve%20a
### Available conversations

You can retrieve a list of all available conversations by calling the `list` method.

**Python**

```py 
conversations_list = client.beta.conversations.list(
    page=0, page_size=100
)
```

**TypeScript**

```typescript
let conversationList = await client.beta.conversations.list({
    page: 0,
    pageSize: 100
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/conversations?page=0&page_size=100" \
    --header 'Content-Type: application/json' \
    --header 'Accept: application/json' \
    --header "Authorization: Bearer $MISTRAL_API_KEY"
```

**Output**

Results: 8 of 13 sections; the page continues.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="available-conversations:2") continues; remaining sections: available-conversations, details-of-a-conversation, retrieve-entries-and-history, retrieve-all-messages-from-a-specific-conversation, streaming-output-example
```

### 8. mistral_docs_search

```json
{"q": "\"Can't create an agent with 'tool_choice' set to 'required' and using built in connectors\"", "max_hits": 5}
```

Result:

```
q: "\"Can't create an agent with 'tool_choice' set to 'required' and using built in connectors\""

[1] https://docs.mistral.ai/studio/connectors/conversations | section: agents-with-connectors
    Using Connectors in conversations > Add Connectors to an Agent
    You can also attach Connectors directly to an Agent at creation time. Every conversation started with that Agent then has access to the Connector tools automatically, without passing a `tools` array each time. > **Tip** > > This is useful when an Agent always needs the same external tools (for example, a support Agent that always queries a CRM). **Python** ```python import asyncio from mistralai.c …
    cite: https://docs.mistral.ai/studio/connectors/conversations#agents-with-connectors

[2] https://docs.mistral.ai/studio/workflows/building-workflows/connectors | section: run-as
    Connectors in workflows > Choose the Connector identity (run_as)
    > **Warning** > > - **`deployment` cannot run interactive OAuth.** A `deployment` Connector runs as the worker's service identity, which has no interactive user. If it has no usable credentials and requires OAuth2, the preflight fails fast instead of emitting an auth URL, add the worker's credentials in Studio beforehand. > - **Durable Agents need a single `run_as`.** All Connectors attached to on …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/connectors#run-as:~:text=%2D%20deployment%20cannot

[3] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: build-an-agent-with-tools
    Build an agent with tools
    Give a Mistral model access to external functions it can call mid-conversation. - Define a tool schema that describes your function - Send a message that triggers a tool call - Execute the function locally and feed the result back to the model The pattern works for any data source: APIs, databases, or internal services. **Time to complete:** ~10 minutes
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent

[4] https://docs.mistral.ai/studio/search/libraries | section: connecting-libraries-to-agents
    Libraries > Connecting Libraries to agents
    **Output** ```json { "model": "mistral-medium-latest", "name": "Document Library Agent", "description": "Agent used to access documents from the document library.", "id": "ag_06835bb196f9720680004fb1873efbae", "version": 0, "created_at": "2025-05-27T13:16:09.438785Z", "updated_at": "2025-05-27T13:16:09.438787Z", "instructions": "Use the library tool to access external documents.", "tools": [ { "li …
    cite: https://docs.mistral.ai/studio/search/libraries#connecting-libraries-to-agents:~:text=When%20you%20create

[5] https://docs.mistral.ai/studio/agents/agents-api | section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    **Output** ```json { "instructions": "Use your websearch abilities when answering requests you don't know.", "tools": [ { "type": "web_search" } ], "completionArgs": { "stop": null, "presencePenalty": null, "frequencyPenalty": null, "temperature": null, "topP": null, "maxTokens": null, "randomSeed": null, "prediction": null, "responseFormat": null, "toolChoice": "auto" }, "model": "mistral-medium- …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=can%20find%20more
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") reads this section

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/connectors/conversations") to read hit 1 on its page
```

### 9. mistral_docs_search

```json
{"q": "tool_choice any auto required agents", "max_hits": 5}
```

Result:

```
q: "tool_choice any auto required agents"

[1] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[2] https://docs.mistral.ai/vibe/code/vs-code-extension/agents | section: built-in-agents
    Agents > Built-in agents
    | Agent | Behavior | |---|---| | `Default` | General-purpose agent. Asks for approval before running tools. | | `Plan` | Read-only agent for exploration and planning. Auto-approves safe read tools. | | `Accept Edits` | Auto-approves file edits in the working directory. Still asks for approval for other actions (for example, shell commands). | | `Auto Approve` | Auto-approves all tool execution. Us …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/agents#built-in-agents

[3] https://docs.mistral.ai/vibe/code/cli/agents | section: built-in-agents
    Agents > Built-in agents
    | Agent | Behavior | |---|---| | `default` | General-purpose agent. Asks for approval before running tools. | | `plan` | Read-only agent for exploration and planning. Auto-approves safe read tools. | | `accept-edits` | Auto-approves file edits in the working directory. Still asks for approval for other actions (for example, shell commands). | | `auto-approve` | Auto-approves all tool execution. Us …
    cite: https://docs.mistral.ai/vibe/code/cli/agents#built-in-agents

[4] https://docs.mistral.ai/studio/agents/agents-api | section: create-a-new-version
    Agents & Conversations > Agent Creation and Management > Create a new Version
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 1, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:17:19.872254Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": 0.95, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="create-a-new-version") reads this section

[5] https://docs.mistral.ai/studio/agents/agents-api | section: available-conversations
    Agents & Conversations > Conversations > Available conversations
    ```json [ { "id": "conv_0684fe18cbc57ba6800065acdd2b6c85", "created_at": "2025-06-16T09:19:08.735790Z", "updated_at": "2025-06-16T09:20:03.273654Z", "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986", "name": null, "description": null, "object": "conversation" }, { "id": "conv_0684fd306df172f2800051d4f82d4a8b", "created_at": "2025-06-16T08:17:10.871401Z", "updated_at": "2025-06-16T08:17:10.871402Z" …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="available-conversations") reads this section

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 10. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent"}
```

Result:

```
page: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | "Build an agent with tools"

## section: build-an-agent-with-tools
    Build an agent with tools
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent
# Build an agent with tools

Give a Mistral model access to external functions it can call mid-conversation.

- Define a tool schema that describes your function
- Send a message that triggers a tool call
- Execute the function locally and feed the result back to the model

The pattern works for any data source: APIs, databases, or internal services.

**Time to complete:** ~10 minutes

## section: prerequisites
    Build an agent with tools > Prerequisites
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#prerequisites
## Prerequisites {#prerequisites}

- A Mistral API key (see [Get your API key](https://docs.mistral.ai/getting-started/quickstarts/developer/first-api-request#step-1) if you don't have one yet)
- Python 3.9+ or Node.js 18+ installed
- The Mistral SDK installed (see [Install the SDK](https://docs.mistral.ai/getting-started/quickstarts/developer/first-api-request#step-2) if you haven't yet)

## section: step-1
    Build an agent with tools > Step 1: Define a tool
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#step-1
## Step 1: Define a tool {#step-1}

Define the function the model can call. This example creates a `get_weather` tool that accepts a city name.

**Python**

```python
import json
import os
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# Define the tool schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. 'Paris'."
                    }
                },
                "required": ["city"]
            }
        }
    }
]
```

**TypeScript**

```typescript
import { Mistral } from '@mistralai/mistralai';

const client = new Mistral({ apiKey: process.env.MISTRAL_API_KEY });

const tools = [
  {
    type: 'function' as const,
    function: {
      name: 'get_weather',
      description: 'Get the current weather for a given city.',
      parameters: {
        type: 'object',
        properties: {
          city: {
            type: 'string',
            description: "The city name, e.g. 'Paris'.",
          },
        },
        required: ['city'],
      },
    },
  },
];
```

## section: step-2
    Build an agent with tools > Step 2: Send a request with the tool
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#step-2
## Step 2: Send a request with the tool {#step-2}

Ask the model a question that requires the tool. The model returns a `tool_calls` response instead of a text answer.

**Python**

```python
messages = [
    {"role": "user", "content": "What's the weather in Paris today?"}
]

response = client.chat.complete(
    model="mistral-medium-latest",
    messages=messages,
    tools=tools,
)

tool_call = response.choices[0].message.tool_calls[0]
print(f"Model wants to call: {tool_call.function.name}")
print(f"With arguments: {tool_call.function.arguments}")
```

**TypeScript**

```typescript
const messages = [
  { role: 'user' as const, content: "What's the weather in Paris today?" },
];

const response = await client.chat.complete({
  model: 'mistral-medium-latest',
  messages,
  tools,
});

const toolCall = response.choices[0].message.toolCalls[0];
console.log(`Model wants to call: ${toolCall.function.name}`);
console.log(`With arguments: ${toolCall.function.arguments}`);
```

## section: step-3
    Build an agent with tools > Step 3: Execute the function and return the result
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#step-3
## Step 3: Execute the function and return the result {#step-3}

Run your function with the model's arguments, then send the result back so the model can generate a natural-language answer.

**Python**

```python
# Simulate the function (replace with a real API call)
def get_weather(city: str) -> dict:
    return {"city": city, "temperature": "18°C", "condition": "Partly cloudy"}

# Execute the tool call
args = json.loads(tool_call.function.arguments)
result = get_weather(**args)

# Send the result back to the model
messages.append(response.choices[0].message)
messages.append({
    "role": "tool",
    "name": tool_call.function.name,
    "content": json.dumps(result),
    "tool_call_id": tool_call.id,
})

final_response = client.chat.complete(
    model="mistral-medium-latest",
    messages=messages,
    tools=tools,
)

print(final_response.choices[0].message.content)
# "The weather in Paris is 18°C and partly cloudy."
```

**TypeScript**

```typescript
// Simulate the function (replace with a real API call)
function getWeather(city: string) {
  return { city, temperature: '18°C', condition: 'Partly cloudy' };
}

// Execute the tool call
const args = JSON.parse(toolCall.function.arguments);
const result = getWeather(args.city);

// Send the result back to the model
messages.push(response.choices[0].message);
messages.push({
  role: 'tool' as const,
  name: toolCall.function.name,
  content: JSON.stringify(result),
  toolCallId: toolCall.id,
});

const finalResponse = await client.chat.complete({
  model: 'mistral-medium-latest',
  messages,
  tools,
});

console.log(finalResponse.choices[0].message.content);
// "The weather in Paris is 18°C and partly cloudy."
```

## section: verify
    Build an agent with tools > Verify
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify
## Verify {#verify}

A successful run prints a natural-language response that includes the tool's return value. The model:

- Detected the request needed external data
- Generated a structured `tool_calls` request
- Incorporated your function's result into a conversational answer

Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.

## section: whats-next
    Build an agent with tools > What's next
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#whats-next
## What's next {#whats-next}

- [RAG with document search](https://docs.mistral.ai/getting-started/quickstarts/developer/rag-document-search)

- [All developer quickstarts](https://docs.mistral.ai/#quickstarts)

Results: 7 sections, the whole page.
```

### 11. mistral_docs_search

```json
{"q": "tool_choice valid values \"any\" \"auto\" \"none\" \"required\"", "max_hits": 5}
```

Result:

```
q: "tool_choice valid values \"any\" \"auto\" \"none\" \"required\""

[1] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[2] https://docs.mistral.ai/studio/conversations/function-calling | section: five-steps/generate-function-arguments
    Function Calling > Five Steps > Generate Function Arguments
    ![functioncalling_step3](https://docs.mistral.ai/img/fc_step3.png) How do models know about these functions and know which function to use? We provide both the user query and the tools specifications to models. The goal in this step is not for the Mistral model to run the function directly. It's to: - Determine the appropriate function to use. - Identify if there is any essential information missi …
    cite: https://docs.mistral.ai/studio/conversations/function-calling#five-steps:~:text=How%20do%20models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/function-calling", section="five-steps/generate-function-arguments") reads this section

[3] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_append_stream/request-body
    Beta Conversations API > Append new entries to an existing conversation. > Request body
    - `inputs` (ConversationInputs, optional) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: True, optional) - `store` (boolean, optional) — Whether to store the results into our servers or not. - `handoff_execution` (enum: 'client', 'server', optional) - `completion_args` (CompletionArgs, optional) — Completion arguments that will be used to generate assistant responses. Can be overrid …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append_stream

[4] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_append/request-body
    Beta Conversations API > Append new entries to an existing conversation. > Request body
    - `inputs` (ConversationInputs, optional) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: False, optional) - `store` (boolean, optional) — Whether to store the results into our servers or not. - `handoff_execution` (enum: 'client', 'server', optional) - `completion_args` (CompletionArgs, optional) — Completion arguments that will be used to generate assistant responses. Can be overri …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append

[5] https://docs.mistral.ai/resources/known-limitations | section: function-calling
    Known limitations > Function calling
    - Maximum number of tools per request: **128**. - Tool descriptions are included in the token count. Long descriptions reduce available context for messages. - Parallel function calls are supported but may return calls in any order. - `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.
    cite: https://docs.mistral.ai/resources/known-limitations#function-calling

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

## Answer

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

