# mined2-022 (single_page, 14 connector calls)

## Question

Creating an agent with `tool_choice: 'required'` fails with `Can't create an agent with 'tool_choice' set to 'required' and using built in connectors` — how do I make it always search the web?

## Thinking

The user is asking about an error when creating an agent with `tool_choice: 'required'`. The error message says: "Can't create an agent with 'tool_choice' set to 'required' and using built in connectors". They want to make the agent always search the web.

This seems like a specific limitation or constraint in Mistral's agent creation system. I need to search the documentation to understand:
1. What `tool_choice` means and its valid values
2. What built-in connectors are
3. Why this combination is not allowed
4. How to make an agent always search the web

Let me search the Mistral documentation for information about `tool_choice` and built-in connectors.

The search returned some results about agents and tools. I can see references to `web_search` and built-in tools. Let me look at the agent creation documentation more closely. I need to find information about `tool_choice` parameter and its interaction with built-in connectors.

Let me search more specifically for `tool_choice` and its valid values.

I can see from the search results that there's information about `tool_choice` in the quickstart guide. It mentions:
- `tool_choice: "any"` to force the model to always call a tool
- `tool_choice: "auto"` (default) to let the model decide

But I need to understand the specific error about `tool_choice: 'required'` with built-in connectors. Let me read the full page to get more context.

I see that the documentation mentions `tool_choice: "any"` and `tool_choice: "auto"`, but not `tool_choice: "required"`. The error message suggests that `tool_choice: 'required'` is not compatible with built-in connectors.

Let me search for more specific information about the `tool_choice` parameter and its valid values, and also look for information about built-in connectors.

I need to look at the API reference for agents to understand the `tool_choice` parameter better. Let me check the beta agents API endpoint documentation.

Great! I found it. In the API documentation, I can see that `tool_choice` is indeed an enum with values: `'auto'`, `'none'`, `'any'`, `'required'`. So `required` is a valid value.

Now I need to understand why the error occurs when using `tool_choice: 'required'` with built-in connectors. Let me search for more specific information about this combination.

Let me read the section about combining tools to understand the relationship between built-in tools and connectors.

Now I understand the issue better. The documentation shows that built-in tools like `web_search` can be used alongside connectors. But the error message says "Can't create an agent with 'tool_choice' set to 'required' and using built in connectors".

Let me search for more specific information about this restriction. Maybe there's a limitation that `tool_choice: 'required'` cannot be used with built-in tools or connectors.

Let me search more specifically for the error message or the restriction. The error message is: "Can't create an agent with 'tool_choice' set to 'required' and using built in connectors". This suggests there's a specific incompatibility.

Let me try searching for this exact error message or similar phrasing.

The search results aren't directly giving me the answer. Let me think about this differently. The error message is very specific: "Can't create an agent with 'tool_choice' set to 'required' and using built in connectors".

From what I've learned:
1. `tool_choice` has values: `auto`, `none`, `any`, `required`
2. Built-in tools like `web_search` can be used with the Agents API
3. The error suggests that `tool_choice: 'required'` is incompatible with built-in connectors

The user wants to make the agent always search the web. Looking at the quickstart guide, it says:
- `tool_choice: "any"` to force the model to always call a tool
- `tool_choice: "auto"` (default) to let the model decide

So maybe the solution is to use `tool_choice: "any"` instead of `tool_choice: "required"`?

But the user specifically asked about `tool_choice: 'required'`. Let me check if there's any documentation about the difference between `required` and `any`.

Actually, looking at the API documentation again, I see that `tool_choice` is defined as: `tool_choice` (enum: 'auto', 'none', 'any', 'required', optional)

But the error message suggests that `required` cannot be used with built-in connectors. This might be a specific restriction that's not explicitly documented, or it might be that the user is using it incorrectly.

Let me search for information about the difference between these tool_choice values.

I found a useful piece of information in the known limitations:
- `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.

This is helpful! So `tool_choice: "any"` forces the model to always call a tool, which is what the user wants.

But the user is asking specifically about `tool_choice: 'required'`. The error message suggests this combination is not allowed. Let me check if there's any documentation that explains the difference between `required` and `any`.

Actually, looking at the quickstart guide again, it only mentions `tool_choice: "any"` and `tool_choice: "auto"`. It doesn't mention `required` at all. This suggests that maybe `required` is not the right value to use, or it's meant for a different purpose.

Let me search for the OpenAPI specification or more detailed documentation about `tool_choice`.

Let me check the Conversations API documentation to see if it has more details about tool_choice.

I can see that `tool_choice` is also available in the Conversations API with the same enum values: `'auto', 'none', 'any', 'required'`.

Now, based on all the information I've gathered:

1. The error message is: "Can't create an agent with 'tool_choice' set to 'required' and using built in connectors"
2. The documentation shows that `tool_choice: "any"` forces the model to always call a tool
3. The user wants to make the agent always search the web

The issue seems to be that `tool_choice: 'required'` is not compatible with built-in connectors (like `web_search`). The solution is likely to use `tool_choice: "any"` instead.

But let me verify this by checking if there's any explicit documentation about this restriction. Let me search for more information about the relationship between tool_choice and built-in tools.

Based on my research, I can now provide a clear answer:

1. The error occurs because `tool_choice: 'required'` is not compatible with built-in connectors (like `web_search`)
2. The documentation explicitly states that `tool_choice: "any"` forces the model to always call a tool
3. The known limitations also confirm: `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected

So the solution is to use `tool_choice: "any"` instead of `tool_choice: "required"`. This will make the agent always call a tool, and if `web_search` is the only tool available (or the most appropriate one), it will be used.

However, the user wants to make the agent **always search the web**. With `tool_choice: "any"`, the model will always call *a* tool, but it doesn't guarantee it will be the web search tool. To ensure it always uses web search, they should:
1. Use `tool_choice: "any"`
2. Only include the `web_search` tool in the agent's tools array

Let me verify this by checking the websearch agent creation example.

Perfect! Now I have a complete picture. Looking at the websearch agent creation example, I can see that:

1. The agent is created with `tools=[{"type": "web_search"}]`
2. The `completion_args` in the output shows `"tool_choice": "auto"` (which is the default)

The documentation states:
- `tool_choice: "any"` forces the model to always call a tool
- `tool_choice: "auto"` (default) lets the model decide

The error message "Can't create an agent with 'tool_choice' set to 'required' and using built in connectors" indicates that `tool_choice: "required"` is not allowed when using built-in tools like `web_search`.

To make an agent always search the web, the user should:
1. Use `tool_choice: "any"` in the `completion_args`
2. Include only the `web_search` tool in the `tools` array (or include it along with other tools, but the model will always call one)

However, there's a nuance: `tool_choice: "any"` forces a tool call but doesn't guarantee which tool. If you want to **always** use web search specifically, you should:
- Use `tool_choice: "any"`
- Only provide the `web_search` tool in the tools array

This way, when the model is forced to call a tool, and `web_search` is the only tool available, it will always use web search.

Let me now formulate the answer based on all this information.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "tool_choice required built in connectors agent creation error", "max_hits": 10}
```

Result:

```
q: "tool_choice required built in connectors agent creation error"

[1] https://docs.mistral.ai/studio/agents/agents-api | section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 0, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:16:16.726718Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": null, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=agent%2C%20you%20will
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") reads this section

[2] https://docs.mistral.ai/studio/agents/agents-api | section: agent-creation-and-management
    Agents & Conversations > Agent Creation and Management
    Agents are a set of pre-selected values, such as tools, instructions, and completion parameters, that will define the behavior of the model. **Agent Creation** When creating an Agent, there are multiple parameters and values that need to be set in advance. These are: - `model`: The model your agent will use among our available models for chat completion. - `description`: The agent description, rel …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="agent-creation-and-management") reads this section

[3] https://docs.mistral.ai/studio/agents/agent-tools | section: general-usage
    Agents Tools Overview > Tools > Built-in tools > General usage
    Built-in tool support depends on the API you use. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#general-usage

[4] https://docs.mistral.ai/studio/agents/agents-api | section: create-a-new-version
    Agents & Conversations > Agent Creation and Management > Create a new Version
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 1, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:17:19.872254Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": 0.95, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="create-a-new-version") reads this section

[5] https://docs.mistral.ai/studio/connectors/conversations | section: combining-tools
    Using Connectors in conversations > Use built-in tools alongside Connectors
    Mistral provides [built-in tools](https://docs.mistral.ai/studio/agents/agent-tools) such as `web_search`, `code_interpreter`, `image_generation`, and `document_library`. You can pass them alongside Connectors in the same `tools` array. The model decides which tool to call **based on the query**. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversati …
    cite: https://docs.mistral.ai/studio/connectors/conversations#combining-tools

[6] https://docs.mistral.ai/studio/connectors/conversations | section: agents-with-connectors
    Using Connectors in conversations > Add Connectors to an Agent
    You can also attach Connectors directly to an Agent at creation time. Every conversation started with that Agent then has access to the Connector tools automatically, without passing a `tools` array each time. > **Tip** > > This is useful when an Agent always needs the same external tools (for example, a support Agent that always queries a CRM). **Python** ```python import asyncio from mistralai.c …
    cite: https://docs.mistral.ai/studio/connectors/conversations#agents-with-connectors

[7] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[8] https://docs.mistral.ai/studio/agents/agent-tools/function-calling | section: define-the-function
    Function Calling > Creating an Agent > Define the Function
    **Output** ```json { "model": "mistral-medium-latest", "name": "ecb-interest-rate-agent", "description": "Can find the current interest rate of the European central bank", "id": "ag_06835a34f2c476518000c372a505c2c4", "version": 0, "created_at": "2025-05-27T11:34:39.175924Z", "updated_at": "2025-05-27T11:34:39.175926Z", "instructions": "You can provide interest rate and information regarding the Eu …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/function-calling#define-the-function:~:text=The%20output%20of

[9] https://docs.mistral.ai/studio/agents/agents-api | section: change-version
    Agents & Conversations > Agent Creation and Management > Change version
    Change manually the version of the Agent. **Python** ```py simple_agent = client.beta.agents.update_version( agent_id=simple_agent.id, version=0 ) ``` **TypeScript** ```typescript websearchAgent = await client.beta.agents.updateVersion({ agentId: websearchAgent.id, version: 0 }); ``` **cURL** ```bash curl --location "https://api.mistral.ai/v1/agents/<agent_id>/version" \ --header 'Content-Type: ap …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=Change%20manually%20the
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="change-version") reads this section

[10] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: built-in-tools
    Durable agents > Built-in tools
    Use Mistral's built-in tools alongside activities: **Python** ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai as workflows_mistralai from mistralai.client.models import WebSearchTool agent = workflows_mistralai.Agent( model="mistral-medium-latest", name="web-search-agent", description="Agent with web search capability", instructions="Use web search to …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#built-in-tools

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") to read hit 1 on its page
```

### 2. mistral_docs_search

```json
{"q": "tool_choice parameter required auto any agent tools", "max_hits": 10}
```

Result:

```
q: "tool_choice parameter required auto any agent tools"

[1] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[2] https://docs.mistral.ai/studio/agents/agents-api | section: create-a-new-version
    Agents & Conversations > Agent Creation and Management > Create a new Version
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 1, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:17:19.872254Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": 0.95, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="create-a-new-version") reads this section

[3] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: create-a-code-interpreter-agent
    Code Interpreter > Create a Code Interpreter Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Coding Agent", "description": "Agent used to execute code using the interpreter tool.", "id": "ag_06830595b7ea7e70800087c4ec8a74e7", "version": 0, "created_at": "2025-05-23T11:17:47.497956Z", "updated_at": "2025-05-23T11:17:47.497959Z", "instructions": "Use the code interpreter tool when you have to run code.", "tools": [ { "type": "c …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#create-a-code-interpreter-agent:~:text=As%20for%20other

[4] https://docs.mistral.ai/studio/agents/agent-tools/function-calling | section: define-the-function
    Function Calling > Creating an Agent > Define the Function
    **Output** ```json { "model": "mistral-medium-latest", "name": "ecb-interest-rate-agent", "description": "Can find the current interest rate of the European central bank", "id": "ag_06835a34f2c476518000c372a505c2c4", "version": 0, "created_at": "2025-05-27T11:34:39.175924Z", "updated_at": "2025-05-27T11:34:39.175926Z", "instructions": "You can provide interest rate and information regarding the Eu …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/function-calling#define-the-function:~:text=The%20output%20of

[5] https://docs.mistral.ai/studio/agents/agent-tools/image_generation | section: create-an-image-generation-agent
    Image Generation > Create an Image Generation Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Image Generation Agent", "description": "Agent used to generate images.", "id": "ag_068359b1d997713480003c77113b8119", "version": 0, "created_at": "2025-05-27T10:59:41.602844Z", "updated_at": "2025-05-27T10:59:41.602846Z", "instructions": "Use the image generation tool when you have to create images.", "tools": [ { "type": "image_gene …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/image_generation#create-an-image-generation-agent:~:text=As%20with%20other

[6] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: build-an-agent-with-tools
    Build an agent with tools
    Give a Mistral model access to external functions it can call mid-conversation. - Define a tool schema that describes your function - Send a message that triggers a tool call - Execute the function locally and feed the result back to the model The pattern works for any data source: APIs, databases, or internal services. **Time to complete:** ~10 minutes
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent

[7] https://docs.mistral.ai/studio/conversations/function-calling | section: five-steps/generate-function-arguments
    Function Calling > Five Steps > Generate Function Arguments
    ![functioncalling_step3](https://docs.mistral.ai/img/fc_step3.png) How do models know about these functions and know which function to use? We provide both the user query and the tools specifications to models. The goal in this step is not for the Mistral model to run the function directly. It's to: - Determine the appropriate function to use. - Identify if there is any essential information missi …
    cite: https://docs.mistral.ai/studio/conversations/function-calling#five-steps:~:text=How%20do%20models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/function-calling", section="five-steps/generate-function-arguments") reads this section

[8] https://docs.mistral.ai/studio/agents/agent-tools | section: general-usage
    Agents Tools Overview > Tools > Built-in tools > General usage
    Built-in tool support depends on the API you use. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#general-usage

[9] https://docs.mistral.ai/vibe/code/vs-code-extension/agents | section: built-in-agents
    Agents > Built-in agents
    | Agent | Behavior | |---|---| | `Default` | General-purpose agent. Asks for approval before running tools. | | `Plan` | Read-only agent for exploration and planning. Auto-approves safe read tools. | | `Accept Edits` | Auto-approves file edits in the working directory. Still asks for approval for other actions (for example, shell commands). | | `Auto Approve` | Auto-approves all tool execution. Us …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/agents#built-in-agents

[10] https://docs.mistral.ai/studio/agents/agents-api | section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 0, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:16:16.726718Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": null, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=agent%2C%20you%20will
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") reads this section

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent", "section": "verify"}
```

Result:

```
page: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | "Build an agent with tools" | section: verify

## section: verify
    Build an agent with tools > Verify
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify
## Verify {#verify}

A successful run prints a natural-language response that includes the tool's return value. The model:

- Detected the request needed external data
- Generated a structured `tool_calls` request
- Incorporated your function's result into a conversational answer

Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent", section="whats-next") for the section after it
```

### 4. mistral_docs_search

```json
{"q": "tool_choice required parameter value agents API", "max_hits": 10}
```

Result:

```
q: "tool_choice required parameter value agents API"

[1] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[2] https://docs.mistral.ai/studio/agents/agents-api | section: create-a-new-version
    Agents & Conversations > Agent Creation and Management > Create a new Version
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 1, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:17:19.872254Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": 0.95, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="create-a-new-version") reads this section

[3] https://docs.mistral.ai/studio/agents/agents-api | section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 0, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:16:16.726718Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": null, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=agent%2C%20you%20will
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") reads this section

[4] https://docs.mistral.ai/studio/agents/agents-api | section: available-conversations
    Agents & Conversations > Conversations > Available conversations
    ```json [ { "id": "conv_0684fe18cbc57ba6800065acdd2b6c85", "created_at": "2025-06-16T09:19:08.735790Z", "updated_at": "2025-06-16T09:20:03.273654Z", "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986", "name": null, "description": null, "object": "conversation" }, { "id": "conv_0684fd306df172f2800051d4f82d4a8b", "created_at": "2025-06-16T08:17:10.871401Z", "updated_at": "2025-06-16T08:17:10.871402Z" …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="available-conversations") reads this section

[5] https://docs.mistral.ai/studio/agents/agents-api | section: change-version
    Agents & Conversations > Agent Creation and Management > Change version
    Change manually the version of the Agent. **Python** ```py simple_agent = client.beta.agents.update_version( agent_id=simple_agent.id, version=0 ) ``` **TypeScript** ```typescript websearchAgent = await client.beta.agents.updateVersion({ agentId: websearchAgent.id, version: 0 }); ``` **cURL** ```bash curl --location "https://api.mistral.ai/v1/agents/<agent_id>/version" \ --header 'Content-Type: ap …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=Change%20manually%20the
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="change-version") reads this section

[6] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_get
    Beta Agents API > Retrieve an agent entity.
    `GET /v1/agents/{agent_id}` Given an agent, retrieve an agent entity with its attributes. The agent_version parameter can be an integer version number or a string alias. - Operation id: `agents_api_v1_agents_get` - Tag: beta/agents
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_get

[7] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_create/request-body
    Beta Agents API > Create a agent that can be used within a conversation. > Request body
    - `instructions` (string or null, optional) — Instruction prompt the model will follow during the conversation. - `tools` (array of object, optional) — List of tools which are available to the model during the conversation. - one of 7 (oneOf): - FunctionTool - WebSearchTool - WebSearchPremiumTool - CodeInterpreterTool - ImageGenerationTool - DocumentLibraryTool - CustomConnector - `completion_args …
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_create

[8] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_create_or_update_alias/parameters
    Beta Agents API > Create or update an agent version alias. > Parameters
    - `agent_id` (string, required, in path) - `alias` (string, required, in query) - `version` (integer, required, in query)
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_create_or_update_alias

[9] https://docs.mistral.ai/api/endpoint/deprecated/agents | section: operation-agents_completion_v1_agents_completions_post/request-body
    Deprecated Agents API > Agents Completion > Request body
    - `max_tokens` (integer or null, optional) — The maximum number of tokens to generate in the completion. The token count of your prompt plus `max_tokens` cannot exceed the model's context length. - `stream` (boolean, optional) — Whether to stream back partial progress. If set, tokens will be sent as data-only server-side events as they become available, with the stream terminated by a data: [DONE] …
    cite: https://docs.mistral.ai/api/endpoint/deprecated/agents#operation-agents_completion_v1_agents_completions_post

[10] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_update_version/parameters
    Beta Agents API > Update an agent version. > Parameters
    - `agent_id` (string, required, in path) - `version` (integer, required, in query)
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_update_version

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 5. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/api/endpoint/beta/agents", "section": "operation-agents_api_v1_agents_create/request-body"}
```

Result:

```
page: https://docs.mistral.ai/api/endpoint/beta/agents | "Beta Agents API" | section: operation-agents_api_v1_agents_create/request-body

## section: operation-agents_api_v1_agents_create/request-body
    Beta Agents API > Create a agent that can be used within a conversation. > Request body
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_create
### Request body

`application/json` (required), schema `CreateAgentRequest`

- `instructions` (string or null, optional) — Instruction prompt the model will follow during the conversation.
- `tools` (array of object, optional) — List of tools which are available to the model during the conversation.
  - one of 7 (oneOf):
    - FunctionTool
    - WebSearchTool
    - WebSearchPremiumTool
    - CodeInterpreterTool
    - ImageGenerationTool
    - DocumentLibraryTool
    - CustomConnector
- `completion_args` (CompletionArgs, optional) — Completion arguments that will be used to generate assistant responses. Can be overridden at each message request.
  - `stop` (CompletionArgsStop, optional)
    - one of 3 (anyOf):
      - string
      - array of string
      - null
  - `presence_penalty` (number or null, optional)
  - `frequency_penalty` (number or null, optional)
  - `temperature` (number or null, optional)
  - `top_p` (number or null, optional)
  - `max_tokens` (integer or null, optional)
  - `random_seed` (integer or null, optional)
  - `prediction` (object or null, optional) — Enable users to specify an expected completion, optimizing response times by leveraging known or predictable content.
    - `type` (string, optional)
    - `content` (string, optional)
  - `response_format` (object or null, optional) — Specify the format that the model must output. By default it will use `{ "type": "text" }`. Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is in JSON. When using JSON mode you MUST also instruct the model to produce JSON yourself with a system or a user message. Setting to `{ "type": "json_schema" }` enables JSON schema mode, which guarantees the message the model generates is in JSON and follows the schema you provide.
    - `type` (enum: 'text', 'json_object', 'json_schema', optional)
    - `json_schema` (object or null, optional)
  - `tool_choice` (enum: 'auto', 'none', 'any', 'required', optional)
  - `reasoning_effort` (enum: 'none', 'minimal', 'low', 'medium', 'high', 'xhigh', optional)
- `guardrails` (array of GuardrailConfig or null, optional)
  - `block_on_error` (boolean, optional) — If true, return HTTP 403 and block request in the event of a server-side error
  - `moderation_llm_v1` (object or null, optional)
  - `moderation_llm_v2` (object or null, optional)
- `model` (string, required)
- `name` (string, required)
- `description` (string or null, optional)
- `handoffs` (array of string or null, optional)
- `metadata` (object or null, optional) — Custom type for metadata with embedded validation.
- `version_message` (string or null, optional)

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/agents", section="operation-agents_api_v1_agents_create/responses") for the section after it
```

### 6. mistral_docs_search

```json
{"q": "built in connectors web_search tool_choice required error", "max_hits": 10}
```

Result:

```
q: "built in connectors web_search tool_choice required error"

[1] https://docs.mistral.ai/studio/connectors/conversations | section: combining-tools
    Using Connectors in conversations > Use built-in tools alongside Connectors
    Mistral provides [built-in tools](https://docs.mistral.ai/studio/agents/agent-tools) such as `web_search`, `code_interpreter`, `image_generation`, and `document_library`. You can pass them alongside Connectors in the same `tools` array. The model decides which tool to call **based on the query**. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversati …
    cite: https://docs.mistral.ai/studio/connectors/conversations#combining-tools

[2] https://docs.mistral.ai/vibe/work/web-search-open-url | section: search-the-web
    Search the web
    Work can browse the internet in real time and read specific web pages as part of a task. **Web search** answers questions with up-to-date, sourced information. **Open URL** lets Work read and analyze a page you already have the link to. > **Info** > > **Knowledge cutoff**: every language model is trained on data collected up to a fixed date. After that date, the model has no built-in knowledge of …
    cite: https://docs.mistral.ai/vibe/work/web-search-open-url

[3] https://docs.mistral.ai/studio/connectors/conversations | section: using-connectors-in-conversations
    Using Connectors in conversations
    After a Connector is [registered](https://docs.mistral.ai/studio/connectors/management) and [authenticated](https://docs.mistral.ai/studio/connectors/management#get-auth-url) (if required), you can attach it to any conversation. You can mix Connectors with built-in tools like `web_search`, filter which tools the model can use, and configure Connectors on Agents so they're available in every conver …
    cite: https://docs.mistral.ai/studio/connectors/conversations

[4] https://docs.mistral.ai/vibe/work/web-search-open-url | section: choosing-the-right-tool
    Search the web > Choosing the right tool
    Pick the option that fits your situation: | You want to... | Use | |----------------|-----| | Get a quick, up-to-date answer with sources | **Web search** | | Analyze a specific page you already have the link to | **Open URL** | | Get a structured, cited report pulling from many sources | **[Deep Research](https://docs.mistral.ai/vibe/chat-legacy/deep-research)** Skill in Work | | Search trusted i …
    cite: https://docs.mistral.ai/vibe/work/web-search-open-url#choosing-the-right-tool

[5] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: built-in-tools
    Durable agents > Built-in tools
    Use Mistral's built-in tools alongside activities: **Python** ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai as workflows_mistralai from mistralai.client.models import WebSearchTool agent = workflows_mistralai.Agent( model="mistral-medium-latest", name="web-search-agent", description="Agent with web search capability", instructions="Use web search to …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#built-in-tools

[6] https://docs.mistral.ai/studio/agents/agent-tools | section: general-usage
    Agents Tools Overview > Tools > Built-in tools > General usage
    Built-in tool support depends on the API you use. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#general-usage

[7] https://docs.mistral.ai/studio/agents/agent-tools/websearch | section: websearch
    Websearch
    Websearch is the capability to **browse the web in search of information**, this tool does not only fix the limitations of models of not being up to date due to their training data, but also allows them to actually retrieve recent information or access specific websites. A handy tool for any agent that needs to be up to date with the world. ![websearch_graph](https://docs.mistral.ai/img/websearch_ …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/websearch

[8] https://docs.mistral.ai/vibe/work/skills | section: example-deep-research
    Reuse work with Skills > Built-in Skills > Example: `/deep-research`
    To see a built-in Skill in action, trigger `deep-research` explicitly: > `/deep-research` What are the main approaches to long-context LLMs in 2026? Work plans the search, runs multiple web queries, synthesizes the sources, and returns a structured brief with citations, opened in [Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas).
    cite: https://docs.mistral.ai/vibe/work/skills#example-deep-research

[9] https://docs.mistral.ai/studio/agents/agent-tools | section: tool-types
    Agents Tools Overview > Tools > Tool types
    We provide a variety of different **types** of tools agents can use. |Type|Description| |---|---| |[Web Search](https://docs.mistral.ai/studio/agents/agent-tools/websearch)| Built-in. Search the web for up-to-date information not in the agent's knowledge.| |[Code Interpreter](https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter)| Built-in. Run code and generate plots, useful for data …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#tool-types

[10] https://docs.mistral.ai/studio/agents/agents-api | section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 0, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:16:16.726718Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": null, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=agent%2C%20you%20will
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") reads this section

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/connectors/conversations") to read hit 1 on its page
```

### 7. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/connectors/conversations", "section": "combining-tools"}
```

Result:

```
page: https://docs.mistral.ai/studio/connectors/conversations | "Using Connectors in conversations" | section: combining-tools

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

(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")



Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/connectors/conversations", section="agents-with-connectors") for the section after it
```

### 8. mistral_docs_search

```json
{"q": "\"tool_choice\" \"required\" built-in tools connectors restriction", "max_hits": 10}
```

Result:

```
q: "\"tool_choice\" \"required\" built-in tools connectors restriction"

[1] https://docs.mistral.ai/studio/connectors/conversations | section: combining-tools
    Using Connectors in conversations > Use built-in tools alongside Connectors
    Mistral provides [built-in tools](https://docs.mistral.ai/studio/agents/agent-tools) such as `web_search`, `code_interpreter`, `image_generation`, and `document_library`. You can pass them alongside Connectors in the same `tools` array. The model decides which tool to call **based on the query**. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversati …
    cite: https://docs.mistral.ai/studio/connectors/conversations#combining-tools

[2] https://docs.mistral.ai/studio/agents/agent-tools | section: built-in-tools
    Agents Tools Overview > Tools > Built-in tools
    ![built_in_graph](https://docs.mistral.ai/img/built_in_graph.png) Built-in tools are ready out of the box. They can be called at any point, and all execution happens in our internal environment. They're also available for users to use directly via Conversations without creating an Agent first.
    cite: https://docs.mistral.ai/studio/agents/agent-tools#built-in-tools

[3] https://docs.mistral.ai/studio/agents/agent-tools | section: general-usage
    Agents Tools Overview > Tools > Built-in tools > General usage
    Built-in tool support depends on the API you use. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#general-usage

[4] https://docs.mistral.ai/studio/connectors/conversations | section: using-connectors-in-conversations
    Using Connectors in conversations
    After a Connector is [registered](https://docs.mistral.ai/studio/connectors/management) and [authenticated](https://docs.mistral.ai/studio/connectors/management#get-auth-url) (if required), you can attach it to any conversation. You can mix Connectors with built-in tools like `web_search`, filter which tools the model can use, and configure Connectors on Agents so they're available in every conver …
    cite: https://docs.mistral.ai/studio/connectors/conversations

[5] https://docs.mistral.ai/studio/agents/agent-tools | section: tool-types
    Agents Tools Overview > Tools > Tool types
    We provide a variety of different **types** of tools agents can use. |Type|Description| |---|---| |[Web Search](https://docs.mistral.ai/studio/agents/agent-tools/websearch)| Built-in. Search the web for up-to-date information not in the agent's knowledge.| |[Code Interpreter](https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter)| Built-in. Run code and generate plots, useful for data …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#tool-types

[6] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: built-in-tools
    Durable agents > Built-in tools
    Use Mistral's built-in tools alongside activities: **Python** ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai as workflows_mistralai from mistralai.client.models import WebSearchTool agent = workflows_mistralai.Agent( model="mistral-medium-latest", name="web-search-agent", description="Agent with web search capability", instructions="Use web search to …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#built-in-tools

[7] https://docs.mistral.ai/vibe/work/connectors | section: available-connectors
    Connect tools with Connectors > Available Connectors
    **Featured** Featured Connectors use a direct OAuth flow. Click `Connect` on the card and authenticate. Administrators can disable specific Connectors for the whole organization on a case-by-case basis. | Connector | What it does | |-----------|-------------| | Atlassian | Connect to Confluence and Jira to search, summarize, and perform project actions. | | Box | Search, analyze, and get insights …
    cite: https://docs.mistral.ai/vibe/work/connectors#available-connectors

[8] https://docs.mistral.ai/vibe/code/vs-code-extension/agents | section: built-in-agents
    Agents > Built-in agents
    | Agent | Behavior | |---|---| | `Default` | General-purpose agent. Asks for approval before running tools. | | `Plan` | Read-only agent for exploration and planning. Auto-approves safe read tools. | | `Accept Edits` | Auto-approves file edits in the working directory. Still asks for approval for other actions (for example, shell commands). | | `Auto Approve` | Auto-approves all tool execution. Us …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/agents#built-in-agents

[9] https://docs.mistral.ai/admin/identity-access/connectors | section: permissions-tab
    Connectors > Manage all Connectors > Set Connector permissions
    The **Permissions** tab controls which tools can be used by the model. | Permission | Effect | | --- | --- | | **Allowed** | All tools are available for users in this Workspace. | | **Restricted** | Only selected tools are available for users in this Workspace. | | **Blocked** | The Connector is turned off for users in this Workspace. | Use **Restricted** when a Connector includes tools that must …
    cite: https://docs.mistral.ai/admin/identity-access/connectors#permissions-tab

[10] https://docs.mistral.ai/studio/connectors/management | section: list-tools
    Managing Connectors > List tools
    List the tools a Connector exposes. This helps verify available tool names before using them in [conversations](https://docs.mistral.ai/studio/connectors/conversations) or [calling them directly](https://docs.mistral.ai/studio/connectors/tool_calling). > **Note** > > If the Connector requires authentication, the user must complete the [auth flow](https://docs.mistral.ai/studio/connectors/managemen …
    cite: https://docs.mistral.ai/studio/connectors/management#list-tools

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/connectors/conversations") to read hit 1 on its page
```

### 9. mistral_docs_search

```json
{"q": "\"Can't create an agent\" tool_choice required built in connectors", "max_hits": 10}
```

Result:

```
q: "\"Can't create an agent\" tool_choice required built in connectors"

[1] https://docs.mistral.ai/studio/connectors/conversations | section: combining-tools
    Using Connectors in conversations > Use built-in tools alongside Connectors
    Mistral provides [built-in tools](https://docs.mistral.ai/studio/agents/agent-tools) such as `web_search`, `code_interpreter`, `image_generation`, and `document_library`. You can pass them alongside Connectors in the same `tools` array. The model decides which tool to call **based on the query**. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversati …
    cite: https://docs.mistral.ai/studio/connectors/conversations#combining-tools

[2] https://docs.mistral.ai/studio/connectors/conversations | section: using-connectors-in-conversations
    Using Connectors in conversations
    After a Connector is [registered](https://docs.mistral.ai/studio/connectors/management) and [authenticated](https://docs.mistral.ai/studio/connectors/management#get-auth-url) (if required), you can attach it to any conversation. You can mix Connectors with built-in tools like `web_search`, filter which tools the model can use, and configure Connectors on Agents so they're available in every conver …
    cite: https://docs.mistral.ai/studio/connectors/conversations

[3] https://docs.mistral.ai/studio/agents/agent-tools | section: built-in-tools
    Agents Tools Overview > Tools > Built-in tools
    ![built_in_graph](https://docs.mistral.ai/img/built_in_graph.png) Built-in tools are ready out of the box. They can be called at any point, and all execution happens in our internal environment. They're also available for users to use directly via Conversations without creating an Agent first.
    cite: https://docs.mistral.ai/studio/agents/agent-tools#built-in-tools

[4] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: built-in-tools
    Durable agents > Built-in tools
    Use Mistral's built-in tools alongside activities: **Python** ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai as workflows_mistralai from mistralai.client.models import WebSearchTool agent = workflows_mistralai.Agent( model="mistral-medium-latest", name="web-search-agent", description="Agent with web search capability", instructions="Use web search to …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#built-in-tools

[5] https://docs.mistral.ai/api/endpoint/beta/connectors | section: operation-connector_call_tool_v1/parameters
    Beta Connectors API > Call Connector Tool > Parameters
    - `tool_name` (string, required, in path) - `connector_id_or_name` (object, required, in path) - `credentials_name` (string or null, optional, in query)
    cite: https://docs.mistral.ai/api/endpoint/beta/connectors#operation-connector_call_tool_v1

[6] https://docs.mistral.ai/vibe/code/vs-code-extension/agents | section: built-in-agents
    Agents > Built-in agents
    | Agent | Behavior | |---|---| | `Default` | General-purpose agent. Asks for approval before running tools. | | `Plan` | Read-only agent for exploration and planning. Auto-approves safe read tools. | | `Accept Edits` | Auto-approves file edits in the working directory. Still asks for approval for other actions (for example, shell commands). | | `Auto Approve` | Auto-approves all tool execution. Us …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/agents#built-in-agents

[7] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[8] https://docs.mistral.ai/studio/agents/agent-tools | section: general-usage
    Agents Tools Overview > Tools > Built-in tools > General usage
    Built-in tool support depends on the API you use. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#general-usage

[9] https://docs.mistral.ai/vibe/code/cli/agents | section: built-in-agents
    Agents > Built-in agents
    | Agent | Behavior | |---|---| | `default` | General-purpose agent. Asks for approval before running tools. | | `plan` | Read-only agent for exploration and planning. Auto-approves safe read tools. | | `accept-edits` | Auto-approves file edits in the working directory. Still asks for approval for other actions (for example, shell commands). | | `auto-approve` | Auto-approves all tool execution. Us …
    cite: https://docs.mistral.ai/vibe/code/cli/agents#built-in-agents

[10] https://docs.mistral.ai/vibe/work/connectors/mcp-connectors | section: mcp-connectors
    MCP Connectors
    Beyond our [featured Connectors](https://docs.mistral.ai/vibe/work/connectors), you can connect Work to third-party and custom services built on the **Model Context Protocol (MCP)**. > **Info** > > MCP is an open standard that lets language models call tools and read data from external services through a common interface. Any service that exposes an MCP server — whether built by a third party or b …
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/connectors/conversations") to read hit 1 on its page
```

### 10. mistral_docs_search

```json
{"q": "tool_choice any required auto none difference", "max_hits": 10}
```

Result:

```
q: "tool_choice any required auto none difference"

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

[6] https://docs.mistral.ai/getting-started/platform-overview | section: whats-the-difference-between-vibe-and-studio
    Platform overview > Common questions > What's the difference between Vibe and Studio?
    Vibe is the end-user product. You use it to get things done, in the chat UI, in your editor, or in your terminal. Studio is the developer console. You use it to generate API keys, test prompts, run evaluations, and ship applications built on the Mistral API. Most organizations use both: knowledge workers in Vibe, developers in Studio.
    cite: https://docs.mistral.ai/getting-started/platform-overview#whats-the-difference-between-vibe-and-studio

[7] https://docs.mistral.ai/api/endpoint/beta/agents | section: operation-agents_api_v1_agents_create/request-body
    Beta Agents API > Create a agent that can be used within a conversation. > Request body
    - `instructions` (string or null, optional) — Instruction prompt the model will follow during the conversation. - `tools` (array of object, optional) — List of tools which are available to the model during the conversation. - one of 7 (oneOf): - FunctionTool - WebSearchTool - WebSearchPremiumTool - CodeInterpreterTool - ImageGenerationTool - DocumentLibraryTool - CustomConnector - `completion_args …
    cite: https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_create

[8] https://docs.mistral.ai/vibe/code/cli/offline-models | section: vllm
    Using offline models > Deploy with vLLM
    We recommend [vLLM](https://github.com/vllm-project/vllm) to serve Devstral. Start Devstral Small 2 on port 8080: ```bash vllm serve mistralai/Devstral-Small-2-24B-Instruct-2512 \ --tool-call-parser mistral \ --enable-auto-tool-choice \ --port 8080 ``` The CLI uses port 8080 as the default local server port. Useful flags: - `--tensor-parallel-size` to use multiple GPUs. - `--dtype` to use a lower …
    cite: https://docs.mistral.ai/vibe/code/cli/offline-models#vllm

[9] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_start_stream/request-body
    Beta Conversations API > Create a conversation and append entries to it. > Request body
    - `inputs` (ConversationInputs, required) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: True, optional) - `store` (boolean or null, optional) - `handoff_execution` (enum: 'client', 'server', optional) - `instructions` (string or null, optional) - `tools` (array of object or null, optional) - one of 7 (oneOf): - FunctionTool - WebSearchTool - WebSearchPremiumTool - CodeInterpreterTo …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start_stream

[10] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_start/request-body
    Beta Conversations API > Create a conversation and append entries to it. > Request body
    - `inputs` (ConversationInputs, required) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: False, optional) - `store` (boolean or null, optional) - `handoff_execution` (enum: 'client', 'server', optional) - `instructions` (string or null, optional) - `tools` (array of object or null, optional) - one of 7 (oneOf): - FunctionTool - WebSearchTool - WebSearchPremiumTool - CodeInterpreterT …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 11. mistral_docs_search

```json
{"q": "\"tool_choice\" \"required\" enum value meaning", "max_hits": 10}
```

Result:

```
q: "\"tool_choice\" \"required\" enum value meaning"

[1] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_append_stream/request-body
    Beta Conversations API > Append new entries to an existing conversation. > Request body
    - `inputs` (ConversationInputs, optional) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: True, optional) - `store` (boolean, optional) — Whether to store the results into our servers or not. - `handoff_execution` (enum: 'client', 'server', optional) - `completion_args` (CompletionArgs, optional) — Completion arguments that will be used to generate assistant responses. Can be overrid …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append_stream

[2] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_append/request-body
    Beta Conversations API > Append new entries to an existing conversation. > Request body
    - `inputs` (ConversationInputs, optional) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: False, optional) - `store` (boolean, optional) — Whether to store the results into our servers or not. - `handoff_execution` (enum: 'client', 'server', optional) - `completion_args` (CompletionArgs, optional) — Completion arguments that will be used to generate assistant responses. Can be overri …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append

[3] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[4] https://docs.mistral.ai/api/endpoint/beta/admin/users | section: operation-users_api_admin_users_update_user/request-body
    Beta Admin Users API > Update User > Request body
    `application/json` (required), schema `AdminOrganizationMemberUpdate` - `role_names` (array of enum: 'member', 'billing_manager', 'organization_admin' or null, optional) — Simplified role names to assign. Mutually exclusive with 'roles'. - `roles` (object, optional) — Role values to assign. Mutually exclusive with 'role_names'. - one of 3 (anyOf): - array of UserRole - array of StaticOrganizationR …
    cite: https://docs.mistral.ai/api/endpoint/beta/admin/users#operation-users_api_admin_users_update_user

[5] https://docs.mistral.ai/api/endpoint/beta/admin/users | section: operation-users_api_admin_users_create_users/request-body
    Beta Admin Users API > Create Users > Request body
    `application/json` (required) - `role_names` (array of enum: 'member', 'billing_manager', 'organization_admin' or null, optional) — Simplified role names to assign. Mutually exclusive with 'roles'. - `roles` (object, optional) — Role values to assign. Mutually exclusive with 'role_names'. - one of 3 (anyOf): - array of UserRole - array of StaticOrganizationRoles - null - `role_name` (enum: 'member …
    cite: https://docs.mistral.ai/api/endpoint/beta/admin/users#operation-users_api_admin_users_create_users

[6] https://docs.mistral.ai/api/endpoint/beta/admin/user-groups | section: operation-users_api_admin_user_groups_provision_group_to_workspace/request-body
    Beta Admin User Groups API > Provision Group To Workspace > Request body
    `application/json` (required), schema `AdminProvisionGroupToWorkspaceIn` - `user_group_uuid` (string (uuid), required) — User group ID to provision. - `workspace_uuid` (string (uuid), required) — Workspace ID where the group is provisioned. - `workspace_role` (object, optional) — Workspace role value to assign to the group. Mutually exclusive with 'workspace_role_name'. - one of 3 (anyOf): - Works …
    cite: https://docs.mistral.ai/api/endpoint/beta/admin/user-groups#operation-users_api_admin_user_groups_provision_group_to_workspace

[7] https://docs.mistral.ai/api/endpoint/beta/admin/users | section: operation-users_api_admin_users_invite_users/request-body
    Beta Admin Users API > Invite Users > Request body
    `application/json` (required), schema `OrganizationInviteIN` - `role_names` (array of enum: 'member', 'billing_manager', 'organization_admin' or null, optional) — Simplified role names to assign. Mutually exclusive with 'roles'. - `roles` (object, optional) — Role values to assign. Mutually exclusive with 'role_names'. - one of 3 (anyOf): - array of UserRole - array of StaticOrganizationRoles - nu …
    cite: https://docs.mistral.ai/api/endpoint/beta/admin/users#operation-users_api_admin_users_invite_users

[8] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_start_stream/request-body
    Beta Conversations API > Create a conversation and append entries to it. > Request body
    - `inputs` (ConversationInputs, required) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: True, optional) - `store` (boolean or null, optional) - `handoff_execution` (enum: 'client', 'server', optional) - `instructions` (string or null, optional) - `tools` (array of object or null, optional) - one of 7 (oneOf): - FunctionTool - WebSearchTool - WebSearchPremiumTool - CodeInterpreterTo …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start_stream

[9] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_start/request-body
    Beta Conversations API > Create a conversation and append entries to it. > Request body
    - `inputs` (ConversationInputs, required) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: False, optional) - `store` (boolean or null, optional) - `handoff_execution` (enum: 'client', 'server', optional) - `instructions` (string or null, optional) - `tools` (array of object or null, optional) - one of 7 (oneOf): - FunctionTool - WebSearchTool - WebSearchPremiumTool - CodeInterpreterT …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start

[10] https://docs.mistral.ai/api/endpoint/beta/admin/user-groups | section: operation-users_api_admin_user_groups_assign_group_to_workspace/request-body
    Beta Admin User Groups API > Assign Group To Workspace > Request body
    `application/json` (required), schema `AssignGroupToWorkspaceIn` - `role_names` (array of enum: 'billing', 'user', 'contributor', 'dev', 'dev_contributor', 'mistral_code_user', 'cloud_user', 'workspace_contributor', 'workspace_admin', 'observability_viewer', 'workflow_executor' or null, optional) — Simplified role names to assign. Mutually exclusive with 'roles'. - `roles` (array of object or null …
    cite: https://docs.mistral.ai/api/endpoint/beta/admin/user-groups#operation-users_api_admin_user_groups_assign_group_to_workspace

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/conversations") to read hit 1 on its page
```

### 12. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/api/endpoint/beta/conversations", "section": "operation-agents_api_v1_conversations_append/request-body"}
```

Result:

```
page: https://docs.mistral.ai/api/endpoint/beta/conversations | "Beta Conversations API" | section: operation-agents_api_v1_conversations_append/request-body

## section: operation-agents_api_v1_conversations_append/request-body
    Beta Conversations API > Append new entries to an existing conversation. > Request body
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append
### Request body

`application/json` (required), schema `ConversationAppendRequest`

- `inputs` (ConversationInputs, optional)
  - one of 2 (anyOf):
    - string
    - InputEntries
- `stream` (enum: False, optional)
- `store` (boolean, optional) — Whether to store the results into our servers or not.
- `handoff_execution` (enum: 'client', 'server', optional)
- `completion_args` (CompletionArgs, optional) — Completion arguments that will be used to generate assistant responses. Can be overridden at each message request.
  - `stop` (CompletionArgsStop, optional)
    - one of 3 (anyOf):
      - string
      - array of string
      - null
  - `presence_penalty` (number or null, optional)
  - `frequency_penalty` (number or null, optional)
  - `temperature` (number or null, optional)
  - `top_p` (number or null, optional)
  - `max_tokens` (integer or null, optional)
  - `random_seed` (integer or null, optional)
  - `prediction` (object or null, optional) — Enable users to specify an expected completion, optimizing response times by leveraging known or predictable content.
    - `type` (string, optional)
    - `content` (string, optional)
  - `response_format` (object or null, optional) — Specify the format that the model must output. By default it will use `{ "type": "text" }`. Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is in JSON. When using JSON mode you MUST also instruct the model to produce JSON yourself with a system or a user message. Setting to `{ "type": "json_schema" }` enables JSON schema mode, which guarantees the message the model generates is in JSON and follows the schema you provide.
    - `type` (enum: 'text', 'json_object', 'json_schema', optional)
    - `json_schema` (object or null, optional)
  - `tool_choice` (enum: 'auto', 'none', 'any', 'required', optional)
  - `reasoning_effort` (enum: 'none', 'minimal', 'low', 'medium', 'high', 'xhigh', optional)
- `tool_confirmations` (array of ToolCallConfirmation or null, optional)
  - `tool_call_id` (string, required)
  - `confirmation` (enum: 'allow', 'deny', required)

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/conversations", section="operation-agents_api_v1_conversations_append/responses") for the section after it
```

### 13. mistral_docs_search

```json
{"q": "web_search tool always call tool_choice any", "max_hits": 10}
```

Result:

```
q: "web_search tool always call tool_choice any"

[1] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[2] https://docs.mistral.ai/vibe/work/safety-and-approvals | section: tool-transparency
    Safety and approvals > Tool-call transparency
    Every tool Work calls (such as a web search, a file read, a Connector function or an image generation) is shown in the chat with: - **Which tool** was called (for example, `Linear: Get Issue`, `Web Search`, `Gmail: List Messages`). - **What inputs** Work passed. - **What outputs** came back. - **Status**: pending, succeeded, or failed. You can expand any tool call to inspect the details. Use this …
    cite: https://docs.mistral.ai/vibe/work/safety-and-approvals#tool-transparency

[3] https://docs.mistral.ai/resources/known-limitations | section: function-calling
    Known limitations > Function calling
    - Maximum number of tools per request: **128**. - Tool descriptions are included in the token count. Long descriptions reduce available context for messages. - Parallel function calls are supported but may return calls in any order. - `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.
    cite: https://docs.mistral.ai/resources/known-limitations#function-calling

[4] https://docs.mistral.ai/studio/conversations/function-calling | section: five-steps/generate-function-arguments
    Function Calling > Five Steps > Generate Function Arguments
    ![functioncalling_step3](https://docs.mistral.ai/img/fc_step3.png) How do models know about these functions and know which function to use? We provide both the user query and the tools specifications to models. The goal in this step is not for the Mistral model to run the function directly. It's to: - Determine the appropriate function to use. - Identify if there is any essential information missi …
    cite: https://docs.mistral.ai/studio/conversations/function-calling#five-steps:~:text=How%20do%20models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/function-calling", section="five-steps/generate-function-arguments") reads this section

[5] https://docs.mistral.ai/studio/agents/agent-tools/websearch | section: websearch
    Websearch
    Websearch is the capability to **browse the web in search of information**, this tool does not only fix the limitations of models of not being up to date due to their training data, but also allows them to actually retrieve recent information or access specific websites. A handy tool for any agent that needs to be up to date with the world. ![websearch_graph](https://docs.mistral.ai/img/websearch_ …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/websearch

[6] https://docs.mistral.ai/studio/agents/agent-tools/websearch | section: create-a-websearch-agent
    Websearch > Create a Websearch Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Websearch Agent", "description": "Agent able to search information over the web, such as news, weather, sport results...", "id": "ag_06835b734cc47dec8000b5f8f860b672", "version": 0, "created_at": "2025-05-27T12:59:32.803403Z", "updated_at": "2025-05-27T12:59:32.803405Z", "instructions": "You have the ability to perform web searches wi …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/websearch#create-a-websearch-agent:~:text=As%20for%20other

[7] https://docs.mistral.ai/studio/connectors/tool_calling | section: call-tool
    Direct tool calling with Connectors > Direct tool calling > Call a tool directly
    To call a tool, pass the Connector name (or UUID), the tool name, and the arguments the tool expects. **Python** ```python import asyncio from mistralai.client import Mistral client = Mistral(api_key="your-api-key") async def main() -> None: result = await client.beta.connectors.call_tool_async( connector_id_or_name="my_deepwiki", tool_name="read_wiki_structure", arguments={"repoName": "sqlite/sql …
    cite: https://docs.mistral.ai/studio/connectors/tool_calling#call-tool

[8] https://docs.mistral.ai/api/endpoint/beta/connectors | section: operation-connector_call_tool_v1
    Beta Connectors API > Call Connector Tool
    `POST /v1/connectors/{connector_id_or_name}/tools/{tool_name}/call` Call a tool on an MCP connector. - Operation id: `connector_call_tool_v1` - Tag: beta/connectors
    cite: https://docs.mistral.ai/api/endpoint/beta/connectors#operation-connector_call_tool_v1

[9] https://docs.mistral.ai/studio/connectors/confirmation | section: configuration
    Human-in-the-loop > Configuration
    Add `requires_confirmation` to the `tool_configuration` of any Connector or built-in tool, and list the tool names that require approval: ```json [ { "type": "connector", "connector_id": "gmail", "tool_configuration": { "requires_confirmation": ["gmail_search"] } }, { "type": "web_search_premium", "tool_configuration": { "requires_confirmation": ["web_search", "news_search"] } } ] ```
    cite: https://docs.mistral.ai/studio/connectors/confirmation#configuration

[10] https://docs.mistral.ai/studio/agents/agents-api | section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 0, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:16:16.726718Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": null, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=agent%2C%20you%20will
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") reads this section

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 14. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/agents/agent-tools/websearch", "section": "create-a-websearch-agent"}
```

Result:

```
page: https://docs.mistral.ai/studio/agents/agent-tools/websearch | "Websearch" | section: create-a-websearch-agent

## section: create-a-websearch-agent
    Websearch > Create a Websearch Agent
    cite: https://docs.mistral.ai/studio/agents/agent-tools/websearch#create-a-websearch-agent
## Create a Websearch Agent {#create-a-websearch-agent}

You can create an agent with access to websearch by providing it as one of the tools.
Note that you can still add more tools to the agent, the model is free to search the web or not on demand.

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
  "model": "mistral-medium-latest",
  "name": "Websearch Agent",
  "description": "Agent able to search information over the web, such as news, weather, sport results...",
  "id": "ag_06835b734cc47dec8000b5f8f860b672",
  "version": 0,
  "created_at": "2025-05-27T12:59:32.803403Z",
  "updated_at": "2025-05-27T12:59:32.803405Z",
  "instructions": "You have the ability to perform web searches with `web_search` to find up-to-date information.",
  "tools": [
    {
      "type": "web_search"
    }
  ],
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
  "handoffs": null,
  "object": "agent"
}
```

As for other agents, when creating one you will receive an agent id corresponding to the created agent that you can use to start a conversation.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agent-tools/websearch", section="how-it-works") for the section after it
```

## Answer

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

