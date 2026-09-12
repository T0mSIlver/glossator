# mined2-028 (single_page, 4 connector calls)

## Question

Every run of my app creates another agent with the same name — how am I meant to keep one agent and update it instead?

## Thinking

The user is asking about how to keep a single agent and update it instead of creating a new agent with the same name on every run. This is a specific technical question about Mistral AI's agent management. I need to search the documentation for information about agent persistence, updating agents, and avoiding duplicate creation.

Let me search for relevant terms like "agent", "update", "persist", "keep", "same name", "duplicate", etc.

The search results show a relevant section about durable agents and agent lifecycle. The third hit mentions that when a `RemoteSession` initializes a conversation, it either creates or updates agents via the Agents API, and specifically mentions that `Agent(id="existing-id")` will update an existing remote agent. This seems directly relevant to the user's question.

Let me read that section more carefully to get the full details.

Perfect! This section directly answers the user's question. The documentation explains that:

1. When `Agent(id=None)` is used, a new remote agent is created with `beta.agents.create()`. The returned ID is stored back on the Agent object, so subsequent runs with the **same instance** reuse it.

2. When `Agent(id="existing-id")` is used, the existing remote agent is updated with `beta.agents.update()`. No new agent is created.

3. To reuse a pre-existing agent across workflow executions, you need to set `agent.id` before calling `Runner.run()`.

4. There's a warning that agents created by `RemoteSession` are not cleaned up automatically after a run completes. If you create agents dynamically (without setting `id`), a new remote agent will be created on every workflow execution.

This is exactly what the user needs to know. They should assign a fixed `id` to their agent so that subsequent runs will update the existing agent instead of creating new ones.

Let me also check if there's more information about the Agents API itself to provide a complete answer.

Now I have enough information to answer the user's question. Let me also search for information about updating agents to provide a complete answer.

I have enough information now. The documentation clearly explains:

1. In workflows, when using `RemoteSession`, if you create an `Agent` without an `id` (or with `id=None`), it creates a new remote agent each time.
2. If you provide an `id` (like `Agent(id="existing-id")`), it will update the existing agent instead of creating a new one.
3. The warning explicitly states: "If you create agents dynamically (without setting `id`), a new remote agent will be created on every workflow execution."

For the Agents API directly, you can:
- Create an agent with `client.beta.agents.create()` which returns an agent object with an `id`
- Update an existing agent with `client.beta.agents.update(agent_id, ...)`

So the solution is: **Assign a fixed ID to your agent**. Either:
- In workflows: Set `agent.id = "your-fixed-id"` before calling `Runner.run()`
- With the API: Use the same `agent_id` when calling `update()`

Let me provide a clear, actionable answer with examples.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "keep one agent and update it instead of creating a new agent with the same name", "max_hits": 5}
```

Result:

```
q: "keep one agent and update it instead of creating a new agent with the same name"

[1] https://docs.mistral.ai/studio/agents/agents-api | section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    **Output** ```json { "instructions": "Use your websearch abilities when answering requests you don't know.", "tools": [ { "type": "web_search" } ], "completionArgs": { "stop": null, "presencePenalty": null, "frequencyPenalty": null, "temperature": null, "topP": null, "maxTokens": null, "randomSeed": null, "prediction": null, "responseFormat": null, "toolChoice": "auto" }, "model": "mistral-medium- …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=can%20find%20more
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") reads this section

[2] https://docs.mistral.ai/vibe/chat-legacy/agents | section: creating-an-agent
    Agents > Creating an Agent
    Creating an Agent is simple and accessible to all users: 1. Select the **Chat** tab in the sidebar. 2. Click `Agents` in the left sidebar. 3. Click `Create Agent` to start from scratch, or pick a **pre-built template** as a starting point. 4. Configure the Agent (see [next section](https://docs.mistral.ai/vibe/chat-legacy/agents#configuration)). 5. Test it in the **preview panel** on the right sid …
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#creating-an-agent

[3] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: agent-lifecycle
    Durable agents > Session types > Agent lifecycle
    When a `RemoteSession` initializes a conversation, it iterates over every agent in the handoff graph and either creates or updates it via the Agents API: - **`Agent(id=None)`**: a new remote agent is created with `beta.agents.create()`. The returned ID is stored back on the `Agent` object, so subsequent runs with the **same instance** reuse it. - **`Agent(id="existing-id")`**: the existing remote …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent-lifecycle

[4] https://docs.mistral.ai/studio/agents/agent-tools/function-calling | section: creating-an-agent-with-function-calling
    Function Calling > Creating an Agent
    To use function calling, we can either create an Agent or use the Conversations API directly without. Below we will show you how to create an Agent with function calling and use it.
    cite: https://docs.mistral.ai/studio/agents/agent-tools/function-calling#creating-an-agent-with-function-calling

[5] https://docs.mistral.ai/studio/agents/agent-tools/function-calling | section: define-the-function
    Function Calling > Creating an Agent > Define the Function
    Once defined, we provide a Shema corresponding to the same function. **Python** ```py ecb_interest_rate_agent = client.beta.agents.create( model="mistral-medium-latest", description="Can find the current interest rate of the European central bank", name="ecb-interest-rate-agent", tools=[ { "type": "function", "function": { "name": "get_european_central_bank_interest_rate", "description": "Retrieve …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/function-calling#define-the-function:~:text=Once%20defined%2C%20we

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents", "section": "agent-lifecycle"}
```

Result:

```
page: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | "Durable agents" | section: agent-lifecycle

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

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents", section="local-session") for the section after it
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/agents/agents-api", "section": "creating-an-agent"}
```

Result:

```
page: https://docs.mistral.ai/studio/agents/agents-api | "Agents & Conversations" | section: creating-an-agent

## section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    cite: https://docs.mistral.ai/studio/agents/agents-api
### Creating an Agent

**Python**

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

(V1 identical)

(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")

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

(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")


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

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="create-a-new-version") for the section after it
```

### 4. mistral_docs_search

```json
{"q": "update an existing agent beta.agents.update", "max_hits": 5}
```

Result:

```
q: "update an existing agent beta.agents.update"

[1] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_update
    Beta Agents API > Update an agent entity.
    `PATCH /v1/agents/{agent_id}` Update an agent attributes and create a new version. - Operation id: `agents_api_v1_agents_update` - Tag: beta/agents
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_update

[2] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_create_or_update_alias
    Beta Agents API > Create or update an agent version alias.
    `PUT /v1/agents/{agent_id}/aliases` Create a new alias or update an existing alias to point to a specific version. Aliases are unique per agent and can be reassigned to different versions. - Operation id: `agents_api_v1_agents_create_or_update_alias` - Tag: beta/agents
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_create_or_update_alias

[3] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_update_version
    Beta Agents API > Update an agent version.
    `PATCH /v1/agents/{agent_id}/version` Switch the version of an agent. - Operation id: `agents_api_v1_agents_update_version` - Tag: beta/agents
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_update_version

[4] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_update/parameters
    Beta Agents API > Update an agent entity. > Parameters
    - `agent_id` (string, required, in path)
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_update

[5] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_update/request-body
    Beta Agents API > Update an agent entity. > Request body
    `application/json` (required), schema `UpdateAgentRequest`
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_update

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/agents") to read hit 1 on its page
```

## Answer

To keep a single agent and update it instead of creating a new one on every run, **assign a fixed `id` to the agent**.

- In **workflows**, when you declare an `Agent`:
  - **Without an `id`** (`Agent(id=None)`): a new remote agent is created each time.
  - **With an `id`** (`Agent(id="ag_abc123")`): the existing agent is updated via `beta.agents.update()` and no new agent is created.
  - > **Warning**: Agents created by `RemoteSession` are **not cleaned up automatically**. If you omit `id`, a new remote agent is created on every workflow execution.
    [Durable agents > Agent lifecycle](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent-lifecycle)

- With the **Agents API**, after the first creation you receive an `id`; use that same `id` in subsequent calls to `beta.agents.update()` to modify the existing agent.
  [Agents & Conversations > Creating an Agent](https://docs.mistral.ai/studio/agents/agents-api#creating-an-agent)

### Practical fix
1. Create the agent once (or pick an existing one) and note its `id`.
2. In your code, always pass that same `id` when constructing the agent so the platform updates it instead of creating duplicates.

**Workflow example**
```python
agent = workflows_mistralai.Agent(
    id="ag_abc123",  # fixed ID → reuse/update instead of create
    model="mistral-medium-latest",
    name="my-agent",
    instructions="...",
    tools=[...],
)
```
[Durable agents > Agent lifecycle](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent-lifecycle)

