# mined2-028 (single_page, 3 connector calls)

## Question

Every run of my app creates another agent with the same name — how am I meant to keep one agent and update it instead?

## Thinking

The user is asking about managing agents in their app, specifically how to update an existing agent instead of creating a new one with the same name on each run. This sounds like a question about Mistral's agent framework or SDK. I need to search the documentation for information about agent persistence, updating agents, or avoiding duplicate agent creation.

Let me search for relevant terms like "agent", "update", "persist", "same name", "duplicate", etc.

The search returned some relevant results. Hit #2 about "Durable agents" and "Agent lifecycle" seems very relevant - it mentions that when a RemoteSession initializes, it either creates or updates agents, and specifically mentions that if you use `Agent(id=None)` it creates a new agent, but if you use `Agent(id="existing-id")` it updates the existing one. This is exactly what the user needs.

Let me read that section to get the full details.

Perfect! This section directly answers the user's question. The documentation clearly states:

1. When `Agent(id=None)` is used, a new remote agent is created with `beta.agents.create()`. The returned ID is stored back on the Agent object, so subsequent runs with the **same instance** reuse it.

2. When `Agent(id="existing-id")` is used, the existing remote agent is updated with `beta.agents.update()`. No new agent is created.

3. To reuse a pre-existing agent across workflow executions, you need to set `agent.id` before calling `Runner.run()`.

4. There's a warning: Agents created by `RemoteSession` are **not cleaned up automatically** after a run completes. If you create agents dynamically (without setting `id`), a new remote agent will be created on every workflow execution.

So the solution is: The user needs to either:
- Use the same Agent instance across runs (the ID is stored and reused)
- Or explicitly set the `id` parameter when creating the Agent to reference an existing one

Let me also check if there's more information about the Agents API to provide a complete answer.

I have enough information now. The documentation clearly explains how to avoid creating duplicate agents:

1. **Reuse the same Agent instance**: When you create an `Agent` without specifying an `id`, it creates a new remote agent and stores the returned ID on the Agent object. Subsequent runs with the **same instance** will reuse it.

2. **Explicitly set an agent ID**: To reuse a pre-existing agent across workflow executions, set `agent.id` before calling `Runner.run()`. For example:
   ```python
   agent = workflows_mistralai.Agent(
       id="ag_abc123",  # Reuse an existing remote agent
       model="mistral-medium-latest",
       name="finance-agent",
       instructions="Use tools to answer financial questions.",
       tools=[get_interest_rate],
   )
   ```

3. **Warning**: If you create agents dynamically (without setting `id`), a new remote agent will be created on every workflow execution.

So the answer is: The user needs to either persist and reuse the Agent instance, or explicitly provide the ID of an existing agent when creating a new Agent instance.

Let me formulate a clear, actionable answer.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "update existing agent instead of creating new agent with same name", "max_hits": 10}
```

Result:

```
q: "update existing agent instead of creating new agent with same name"

[1] https://docs.mistral.ai/studio/agents/agents-api | section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    **Output** ```json { "instructions": "Use your websearch abilities when answering requests you don't know.", "tools": [ { "type": "web_search" } ], "completionArgs": { "stop": null, "presencePenalty": null, "frequencyPenalty": null, "temperature": null, "topP": null, "maxTokens": null, "randomSeed": null, "prediction": null, "responseFormat": null, "toolChoice": "auto" }, "model": "mistral-medium- …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=can%20find%20more
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") reads this section

[2] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: agent-lifecycle
    Durable agents > Session types > Agent lifecycle
    When a `RemoteSession` initializes a conversation, it iterates over every agent in the handoff graph and either creates or updates it via the Agents API: - **`Agent(id=None)`**: a new remote agent is created with `beta.agents.create()`. The returned ID is stored back on the `Agent` object, so subsequent runs with the **same instance** reuse it. - **`Agent(id="existing-id")`**: the existing remote …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent-lifecycle

[3] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_create_or_update_alias
    Beta Agents API > Create or update an agent version alias.
    `PUT /v1/agents/{agent_id}/aliases` Create a new alias or update an existing alias to point to a specific version. Aliases are unique per agent and can be reassigned to different versions. - Operation id: `agents_api_v1_agents_create_or_update_alias` - Tag: beta/agents
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_create_or_update_alias

[4] https://docs.mistral.ai/studio/agents/agent-tools/function-calling | section: define-the-function
    Function Calling > Creating an Agent > Define the Function
    Once defined, we provide a Shema corresponding to the same function. **Python** ```py ecb_interest_rate_agent = client.beta.agents.create( model="mistral-medium-latest", description="Can find the current interest rate of the European central bank", name="ecb-interest-rate-agent", tools=[ { "type": "function", "function": { "name": "get_european_central_bank_interest_rate", "description": "Retrieve …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/function-calling#define-the-function:~:text=Once%20defined%2C%20we

[5] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_update
    Beta Agents API > Update an agent entity.
    `PATCH /v1/agents/{agent_id}` Update an agent attributes and create a new version. - Operation id: `agents_api_v1_agents_update` - Tag: beta/agents
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_update

[6] https://docs.mistral.ai/studio/agents/agent-tools/function-calling | section: creating-an-agent-with-function-calling
    Function Calling > Creating an Agent
    To use function calling, we can either create an Agent or use the Conversations API directly without. Below we will show you how to create an Agent with function calling and use it.
    cite: https://docs.mistral.ai/studio/agents/agent-tools/function-calling#creating-an-agent-with-function-calling

[7] https://docs.mistral.ai/vibe/chat-legacy/agents | section: creating-an-agent
    Agents > Creating an Agent
    Creating an Agent is simple and accessible to all users: 1. Select the **Chat** tab in the sidebar. 2. Click `Agents` in the left sidebar. 3. Click `Create Agent` to start from scratch, or pick a **pre-built template** as a starting point. 4. Configure the Agent (see [next section](https://docs.mistral.ai/vibe/chat-legacy/agents#configuration)). 5. Test it in the **preview panel** on the right sid …
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#creating-an-agent

[8] https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning | section: what-if-i-upload-an-already-existing-file
    Text & Vision Fine-tuning > FAQ > What if I upload an already existing file?
    If a file is uploaded and matches an existing file in both content and name, the pre-existing file is returned instead of creating a new one.
    cite: https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-if-i-upload-an-already-existing-file

[9] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_update_version
    Beta Agents API > Update an agent version.
    `PATCH /v1/agents/{agent_id}/version` Switch the version of an agent. - Operation id: `agents_api_v1_agents_update_version` - Tag: beta/agents
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_update_version

[10] https://docs.mistral.ai/studio/agents/agents-api | section: create-a-new-version
    Agents & Conversations > Agent Creation and Management > Create a new Version
    Create a new `version` of the Agent, will be used by default. **Python** ```py simple_agent = client.beta.agents.update( agent_id=simple_agent.id, description="An edited simple agent.", completion_args={ "temperature": 0.3, "top_p": 0.95, } ) ``` **TypeScript** ```typescript websearchAgent = await client.beta.agents.update({ agentId: websearchAgent.id, agentUpdateRequest: { completionArgs: { tempe …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=the%20Agent%2C%20will
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="create-a-new-version") reads this section

Results: 10 hits
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
{"page_url": "https://docs.mistral.ai/api/endpoint/beta/agents", "section": "operation-agents_api_v1_agents_update"}
```

Result:

```
page: https://docs.mistral.ai/api/endpoint/beta/agents | "Beta Agents API" | section: operation-agents_api_v1_agents_update

## section: operation-agents_api_v1_agents_update
    Beta Agents API > Update an agent entity.
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_update
## Update an agent entity. {#operation-agents_api_v1_agents_update}

`PATCH /v1/agents/{agent_id}`

Update an agent attributes and create a new version.

- Operation id: `agents_api_v1_agents_update`
- Tag: beta/agents

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/agents", section="operation-agents_api_v1_agents_update/parameters") for the section after it
```

## Answer

To keep a single agent and update it instead of creating a new one on every run, **pass the same `id` when you construct the agent** (or reuse the same `Agent` instance).

- If you do **not** set an `id` (or set it to `None`), a new remote agent is created each time.
- If you **do** set `id="existing-id"`, the existing remote agent is updated via `beta.agents.update()` and no new agent is created.

Example:

```python
agent = workflows_mistralai.Agent(
    id="ag_abc123",  # Reuse an existing remote agent
    model="mistral-medium-latest",
    name="finance-agent",
    instructions="Use tools to answer financial questions.",
    tools=[get_interest_rate],
)
```

> ⚠️ Agents created by `RemoteSession` are **not cleaned up automatically** after a run. If you omit the `id`, a new agent will be created on every execution.
> [Agent lifecycle](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent-lifecycle)

