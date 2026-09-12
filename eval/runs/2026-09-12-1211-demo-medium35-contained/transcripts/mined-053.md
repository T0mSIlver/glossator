# mined-053 (api_reference, 8 connector calls)

## Question

What does `tool_choice: "none"` do when tools are still declared on the request?

## Thinking

The user is asking about the behavior of `tool_choice: "none"` when tools are still declared in the request. This is a specific technical question about Mistral AI's API or SDK configuration. I need to search the official documentation to find the exact definition and behavior of this parameter.

I'll search for "tool_choice none" in the Mistral documentation to find relevant information about this parameter and its behavior.

The first search returned some results but they seem to be about general tool usage rather than the specific `tool_choice: "none"` parameter. Let me try a more targeted search to find the exact definition. I'll search for just "tool_choice" to see all the documentation about this parameter.

The search results are still not giving me the specific information about `tool_choice: "none"`. The results mention `tool_choice: "any"` and `tool_choice: "auto"` but not the "none" option. Let me search more specifically for the API reference or parameter documentation. I'll try searching for "tool_choice none auto any" to see if there's a section that lists all possible values.

I'm still not finding the specific documentation for `tool_choice: "none"`. The search results keep pointing to the same quickstart guide. Let me try reading the actual page content directly. I'll read the "build-an-agent" page which was mentioned in the search results, as it might contain the tool_choice parameter documentation.

The build-an-agent page doesn't seem to have the detailed parameter documentation I need. Let me search more specifically for the API reference. I'll try searching for "tool_choice parameter" to find the actual parameter definition in the API documentation.

The search results are still not giving me the specific information. Let me try searching for the API endpoint documentation directly. I'll search for "chat.complete tool_choice" to find the chat completion API reference which should contain the tool_choice parameter documentation.

I'm getting closer. The search results mention function-calling and chat-completion pages. Let me try to find the actual API reference for the chat completion endpoint. I'll search for the API endpoint path directly.

Good, I found the API endpoint documentation. The search result shows "API chat completions tool_choice" with a hit on the chat endpoint. Let me read the chat API endpoint page directly to find the tool_choice parameter documentation.

Perfect! I found the relevant documentation. The chat API endpoint page contains the tool_choice parameter definition. From the page content, I can see that tool_choice is an optional object that controls which (if any) tool is called by the model. The documentation explicitly states:

- `none` means the model will not call any tool and instead generates a message
- `auto` means the model can pick between generating a message or calling one or more tools
- `any` or `required` means the model must call one or more tools
- Specifying a particular tool via `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool

This directly answers the user's question. Even though tools are declared on the request, setting `tool_choice: "none"` explicitly prevents the model from calling any tools and forces it to generate a regular text message instead. This is useful when you want to provide tool definitions for context but don't want the model to use them for a specific request.

I should format this answer clearly and include the citation link as required by the documentation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "tool_choice none", "max_hits": 5}
```

Result:

```
q: "tool_choice none"

[1] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[2] https://docs.mistral.ai/studio/conversations/function-calling | section: five-steps/generate-function-arguments
    Function Calling > Five Steps > Generate Function Arguments
    ![functioncalling_step3](https://docs.mistral.ai/img/fc_step3.png) How do models know about these functions and know which function to use? We provide both the user query and the tools specifications to models. The goal in this step is not for the Mistral model to run the function directly. It's to: - Determine the appropriate function to use. - Identify if there is any essential information missi …
    cite: https://docs.mistral.ai/studio/conversations/function-calling#five-steps:~:text=How%20do%20models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/function-calling", section="five-steps/generate-function-arguments") reads this section

[3] https://docs.mistral.ai/resources/known-limitations | section: function-calling
    Known limitations > Function calling
    - Maximum number of tools per request: **128**. - Tool descriptions are included in the token count. Long descriptions reduce available context for messages. - Parallel function calls are supported but may return calls in any order. - `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.
    cite: https://docs.mistral.ai/resources/known-limitations#function-calling

[4] https://docs.mistral.ai/studio/workflows/building-workflows/workflows | section: optional-union-none
    Workflows > Workflow input > Optional union (`| None`)
    Append `| None` (or use `Optional` from `typing`) to make the input optional: ```python @workflow.define(name="optional_workflow") class OptionalWorkflow: @workflow.entrypoint async def run(self, params: PromptInput | CountInput | None) -> str: if params is None: return "no input" if isinstance(params, PromptInput): return f"prompt: {params.prompt}" return f"count: {params.count}" ```
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/workflows#optional-union-none

[5] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_append_stream/request-body
    Beta Conversations API > Append new entries to an existing conversation. > Request body
    - `inputs` (ConversationInputs, optional) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: True, optional) - `store` (boolean, optional) — Whether to store the results into our servers or not. - `handoff_execution` (enum: 'client', 'server', optional) - `completion_args` (CompletionArgs, optional) — Completion arguments that will be used to generate assistant responses. Can be overrid …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append_stream

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 2. mistral_docs_search

```json
{"q": "tool_choice", "max_hits": 10}
```

Result:

```
q: "tool_choice"

[1] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[2] https://docs.mistral.ai/resources/known-limitations | section: function-calling
    Known limitations > Function calling
    - Maximum number of tools per request: **128**. - Tool descriptions are included in the token count. Long descriptions reduce available context for messages. - Parallel function calls are supported but may return calls in any order. - `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.
    cite: https://docs.mistral.ai/resources/known-limitations#function-calling

[3] https://docs.mistral.ai/studio/conversations/function-calling | section: five-steps/generate-function-arguments
    Function Calling > Five Steps > Generate Function Arguments
    ![functioncalling_step3](https://docs.mistral.ai/img/fc_step3.png) How do models know about these functions and know which function to use? We provide both the user query and the tools specifications to models. The goal in this step is not for the Mistral model to run the function directly. It's to: - Determine the appropriate function to use. - Identify if there is any essential information missi …
    cite: https://docs.mistral.ai/studio/conversations/function-calling#five-steps:~:text=How%20do%20models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/function-calling", section="five-steps/generate-function-arguments") reads this section

[4] https://docs.mistral.ai/resources/migration-guides | section: does-mistral-support-the-openai-function-calling-format
    Migration guides > Common questions > Does Mistral support the OpenAI function calling format?
    Yes. We support the same tool/function calling schema as OpenAI. Your existing tool definitions, tool_choice parameters, and tool result messages should work without changes. Test with `mistral-large-latest`, which has the strongest function calling support.
    cite: https://docs.mistral.ai/resources/migration-guides#does-mistral-support-the-openai-function-calling-format

[5] https://docs.mistral.ai/vibe/code/cli/offline-models | section: vllm
    Using offline models > Deploy with vLLM
    We recommend [vLLM](https://github.com/vllm-project/vllm) to serve Devstral. Start Devstral Small 2 on port 8080: ```bash vllm serve mistralai/Devstral-Small-2-24B-Instruct-2512 \ --tool-call-parser mistral \ --enable-auto-tool-choice \ --port 8080 ``` The CLI uses port 8080 as the default local server port. Useful flags: - `--tensor-parallel-size` to use multiple GPUs. - `--dtype` to use a lower …
    cite: https://docs.mistral.ai/vibe/code/cli/offline-models#vllm

[6] https://docs.mistral.ai/studio/agents/agents-api | section: available-conversations
    Agents & Conversations > Conversations > Available conversations
    ```json [ { "id": "conv_0684fe18cbc57ba6800065acdd2b6c85", "created_at": "2025-06-16T09:19:08.735790Z", "updated_at": "2025-06-16T09:20:03.273654Z", "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986", "name": null, "description": null, "object": "conversation" }, { "id": "conv_0684fd306df172f2800051d4f82d4a8b", "created_at": "2025-06-16T08:17:10.871401Z", "updated_at": "2025-06-16T08:17:10.871402Z" …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="available-conversations") reads this section

[7] https://docs.mistral.ai/vibe/code/vs-code-extension/commands-slash-commands | section: hotkeys
    Commands and slash commands > Keyboard shortcuts
    Inside the Vibe panel, `Mod` means `Command` on macOS and `Ctrl` on Windows or Linux. | Shortcut | Action | |---|---| | `Mod+Y` | Approve a tool action. | | `Mod+Alt+Y` | Approve an alternate tool action. | | `Mod+Shift+Y` | Approve and apply a broader permission choice. | | `Mod+Alt+N` | Reject a tool action. | | `Mod+N` | Start a new conversation. | | `Escape` | Cancel or blur the current input …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/commands-slash-commands#hotkeys

[8] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: create-a-code-interpreter-agent
    Code Interpreter > Create a Code Interpreter Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Coding Agent", "description": "Agent used to execute code using the interpreter tool.", "id": "ag_06830595b7ea7e70800087c4ec8a74e7", "version": 0, "created_at": "2025-05-23T11:17:47.497956Z", "updated_at": "2025-05-23T11:17:47.497959Z", "instructions": "Use the code interpreter tool when you have to run code.", "tools": [ { "type": "c …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#create-a-code-interpreter-agent:~:text=As%20for%20other

[9] https://docs.mistral.ai/studio/search/libraries | section: connecting-libraries-to-agents
    Libraries > Connecting Libraries to agents
    **Output** ```json { "model": "mistral-medium-latest", "name": "Document Library Agent", "description": "Agent used to access documents from the document library.", "id": "ag_06835bb196f9720680004fb1873efbae", "version": 0, "created_at": "2025-05-27T13:16:09.438785Z", "updated_at": "2025-05-27T13:16:09.438787Z", "instructions": "Use the library tool to access external documents.", "tools": [ { "li …
    cite: https://docs.mistral.ai/studio/search/libraries#connecting-libraries-to-agents:~:text=When%20you%20create

[10] https://docs.mistral.ai/studio/agents/agent-tools/image_generation | section: create-an-image-generation-agent
    Image Generation > Create an Image Generation Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Image Generation Agent", "description": "Agent used to generate images.", "id": "ag_068359b1d997713480003c77113b8119", "version": 0, "created_at": "2025-05-27T10:59:41.602844Z", "updated_at": "2025-05-27T10:59:41.602846Z", "instructions": "Use the image generation tool when you have to create images.", "tools": [ { "type": "image_gene …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/image_generation#create-an-image-generation-agent:~:text=As%20with%20other

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 3. mistral_docs_search

```json
{"q": "tool_choice none auto any", "max_hits": 10}
```

Result:

```
q: "tool_choice none auto any"

[1] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[2] https://docs.mistral.ai/studio/conversations/function-calling | section: five-steps/generate-function-arguments
    Function Calling > Five Steps > Generate Function Arguments
    ![functioncalling_step3](https://docs.mistral.ai/img/fc_step3.png) How do models know about these functions and know which function to use? We provide both the user query and the tools specifications to models. The goal in this step is not for the Mistral model to run the function directly. It's to: - Determine the appropriate function to use. - Identify if there is any essential information missi …
    cite: https://docs.mistral.ai/studio/conversations/function-calling#five-steps:~:text=How%20do%20models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/function-calling", section="five-steps/generate-function-arguments") reads this section

[3] https://docs.mistral.ai/resources/known-limitations | section: function-calling
    Known limitations > Function calling
    - Maximum number of tools per request: **128**. - Tool descriptions are included in the token count. Long descriptions reduce available context for messages. - Parallel function calls are supported but may return calls in any order. - `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.
    cite: https://docs.mistral.ai/resources/known-limitations#function-calling

[4] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_append_stream/request-body
    Beta Conversations API > Append new entries to an existing conversation. > Request body
    - `inputs` (ConversationInputs, optional) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: True, optional) - `store` (boolean, optional) — Whether to store the results into our servers or not. - `handoff_execution` (enum: 'client', 'server', optional) - `completion_args` (CompletionArgs, optional) — Completion arguments that will be used to generate assistant responses. Can be overrid …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append_stream

[5] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_append/request-body
    Beta Conversations API > Append new entries to an existing conversation. > Request body
    - `inputs` (ConversationInputs, optional) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: False, optional) - `store` (boolean, optional) — Whether to store the results into our servers or not. - `handoff_execution` (enum: 'client', 'server', optional) - `completion_args` (CompletionArgs, optional) — Completion arguments that will be used to generate assistant responses. Can be overri …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append

[6] https://docs.mistral.ai/vibe/code/cli/offline-models | section: vllm
    Using offline models > Deploy with vLLM
    We recommend [vLLM](https://github.com/vllm-project/vllm) to serve Devstral. Start Devstral Small 2 on port 8080: ```bash vllm serve mistralai/Devstral-Small-2-24B-Instruct-2512 \ --tool-call-parser mistral \ --enable-auto-tool-choice \ --port 8080 ``` The CLI uses port 8080 as the default local server port. Useful flags: - `--tensor-parallel-size` to use multiple GPUs. - `--dtype` to use a lower …
    cite: https://docs.mistral.ai/vibe/code/cli/offline-models#vllm

[7] https://docs.mistral.ai/studio/agents/agents-api | section: available-conversations
    Agents & Conversations > Conversations > Available conversations
    ```json [ { "id": "conv_0684fe18cbc57ba6800065acdd2b6c85", "created_at": "2025-06-16T09:19:08.735790Z", "updated_at": "2025-06-16T09:20:03.273654Z", "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986", "name": null, "description": null, "object": "conversation" }, { "id": "conv_0684fd306df172f2800051d4f82d4a8b", "created_at": "2025-06-16T08:17:10.871401Z", "updated_at": "2025-06-16T08:17:10.871402Z" …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="available-conversations") reads this section

[8] https://docs.mistral.ai/studio/agents/agents-api | section: create-a-new-version
    Agents & Conversations > Agent Creation and Management > Create a new Version
    **Output** ```json { "model": "mistral-medium-latest", "name": "Simple Agent", "id": "ag_0684fe0e0b98773e8000323fc71a3986", "version": 1, "created_at": "2025-06-16T09:16:16.726715Z", "updated_at": "2025-06-16T09:17:19.872254Z", "instructions": null, "tools": [], "completion_args": { "stop": null, "presence_penalty": null, "frequency_penalty": null, "temperature": 0.3, "top_p": 0.95, "max_tokens": …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="create-a-new-version") reads this section

[9] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: create-a-code-interpreter-agent
    Code Interpreter > Create a Code Interpreter Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Coding Agent", "description": "Agent used to execute code using the interpreter tool.", "id": "ag_06830595b7ea7e70800087c4ec8a74e7", "version": 0, "created_at": "2025-05-23T11:17:47.497956Z", "updated_at": "2025-05-23T11:17:47.497959Z", "instructions": "Use the code interpreter tool when you have to run code.", "tools": [ { "type": "c …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#create-a-code-interpreter-agent:~:text=As%20for%20other

[10] https://docs.mistral.ai/studio/search/libraries | section: connecting-libraries-to-agents
    Libraries > Connecting Libraries to agents
    **Output** ```json { "model": "mistral-medium-latest", "name": "Document Library Agent", "description": "Agent used to access documents from the document library.", "id": "ag_06835bb196f9720680004fb1873efbae", "version": 0, "created_at": "2025-05-27T13:16:09.438785Z", "updated_at": "2025-05-27T13:16:09.438787Z", "instructions": "Use the library tool to access external documents.", "tools": [ { "li …
    cite: https://docs.mistral.ai/studio/search/libraries#connecting-libraries-to-agents:~:text=When%20you%20create

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 4. mistral_docs_read_page

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

(sample in TypeScript omitted: pass lang="typescript")

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

(sample in TypeScript omitted: pass lang="typescript")

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

(sample in TypeScript omitted: pass lang="typescript")

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

### 5. mistral_docs_search

```json
{"q": "tool_choice parameter", "max_hits": 10}
```

Result:

```
q: "tool_choice parameter"

[1] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[2] https://docs.mistral.ai/resources/known-limitations | section: function-calling
    Known limitations > Function calling
    - Maximum number of tools per request: **128**. - Tool descriptions are included in the token count. Long descriptions reduce available context for messages. - Parallel function calls are supported but may return calls in any order. - `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.
    cite: https://docs.mistral.ai/resources/known-limitations#function-calling

[3] https://docs.mistral.ai/studio/conversations/function-calling | section: five-steps/generate-function-arguments
    Function Calling > Five Steps > Generate Function Arguments
    ![functioncalling_step3](https://docs.mistral.ai/img/fc_step3.png) How do models know about these functions and know which function to use? We provide both the user query and the tools specifications to models. The goal in this step is not for the Mistral model to run the function directly. It's to: - Determine the appropriate function to use. - Identify if there is any essential information missi …
    cite: https://docs.mistral.ai/studio/conversations/function-calling#five-steps:~:text=How%20do%20models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/function-calling", section="five-steps/generate-function-arguments") reads this section

[4] https://docs.mistral.ai/studio/workflows/building-workflows/workflows | section: primitive-and-multi-parameter-inputs
    Workflows > Workflow input > Primitive and multi-parameter inputs
    ```python @workflow.define(name="report_workflow") class ReportWorkflow: @workflow.entrypoint async def run(self, report_type: str, include_details: bool = False) -> dict: ... ``` Input: ```json {"report_type": "daily", "include_details": false} ```
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/workflows#primitive-and-multi-parameter-inputs

[5] https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/concurrency | section: understanding-parameter-interactions
    Concurrency Patterns > Concurrency patterns: scale your workflows > Offset Pagination Executor Best Practices > Understanding Parameter Interactions
    The Offset Pagination Executor uses two key parameters: 1. **`max_concurrent_executions_per_worker`**: Controls how many items are processed together in a single activity execution. 2. **`max_concurrent_scheduled_tasks`**: Controls how many of these activity executions can run concurrently. **Example**: If you have 1000 items with `max_concurrent_executions_per_worker=10` and `max_concurrent_sched …
    cite: https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/concurrency#understanding-parameter-interactions

[6] https://docs.mistral.ai/resources/migration-guides | section: does-mistral-support-the-openai-function-calling-format
    Migration guides > Common questions > Does Mistral support the OpenAI function calling format?
    Yes. We support the same tool/function calling schema as OpenAI. Your existing tool definitions, tool_choice parameters, and tool result messages should work without changes. Test with `mistral-large-latest`, which has the strongest function calling support.
    cite: https://docs.mistral.ai/resources/migration-guides#does-mistral-support-the-openai-function-calling-format

[7] https://docs.mistral.ai/vibe/code/cli/offline-models | section: vllm
    Using offline models > Deploy with vLLM
    We recommend [vLLM](https://github.com/vllm-project/vllm) to serve Devstral. Start Devstral Small 2 on port 8080: ```bash vllm serve mistralai/Devstral-Small-2-24B-Instruct-2512 \ --tool-call-parser mistral \ --enable-auto-tool-choice \ --port 8080 ``` The CLI uses port 8080 as the default local server port. Useful flags: - `--tensor-parallel-size` to use multiple GPUs. - `--dtype` to use a lower …
    cite: https://docs.mistral.ai/vibe/code/cli/offline-models#vllm

[8] https://docs.mistral.ai/vibe/code/vs-code-extension/commands-slash-commands | section: hotkeys
    Commands and slash commands > Keyboard shortcuts
    Inside the Vibe panel, `Mod` means `Command` on macOS and `Ctrl` on Windows or Linux. | Shortcut | Action | |---|---| | `Mod+Y` | Approve a tool action. | | `Mod+Alt+Y` | Approve an alternate tool action. | | `Mod+Shift+Y` | Approve and apply a broader permission choice. | | `Mod+Alt+N` | Reject a tool action. | | `Mod+N` | Start a new conversation. | | `Escape` | Cancel or blur the current input …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/commands-slash-commands#hotkeys

[9] https://docs.mistral.ai/studio/agents/agents-api | section: available-conversations
    Agents & Conversations > Conversations > Available conversations
    ```json [ { "id": "conv_0684fe18cbc57ba6800065acdd2b6c85", "created_at": "2025-06-16T09:19:08.735790Z", "updated_at": "2025-06-16T09:20:03.273654Z", "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986", "name": null, "description": null, "object": "conversation" }, { "id": "conv_0684fd306df172f2800051d4f82d4a8b", "created_at": "2025-06-16T08:17:10.871401Z", "updated_at": "2025-06-16T08:17:10.871402Z" …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="available-conversations") reads this section

[10] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: create-a-code-interpreter-agent
    Code Interpreter > Create a Code Interpreter Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Coding Agent", "description": "Agent used to execute code using the interpreter tool.", "id": "ag_06830595b7ea7e70800087c4ec8a74e7", "version": 0, "created_at": "2025-05-23T11:17:47.497956Z", "updated_at": "2025-05-23T11:17:47.497959Z", "instructions": "Use the code interpreter tool when you have to run code.", "tools": [ { "type": "c …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#create-a-code-interpreter-agent:~:text=As%20for%20other

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 6. mistral_docs_search

```json
{"q": "chat.complete tool_choice", "max_hits": 10}
```

Result:

```
q: "chat.complete tool_choice"

[1] https://docs.mistral.ai/studio/conversations/function-calling | section: five-steps/generate-function-arguments
    Function Calling > Five Steps > Generate Function Arguments
    ![functioncalling_step3](https://docs.mistral.ai/img/fc_step3.png) How do models know about these functions and know which function to use? We provide both the user query and the tools specifications to models. The goal in this step is not for the Mistral model to run the function directly. It's to: - Determine the appropriate function to use. - Identify if there is any essential information missi …
    cite: https://docs.mistral.ai/studio/conversations/function-calling#five-steps:~:text=How%20do%20models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/function-calling", section="five-steps/generate-function-arguments") reads this section

[2] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[3] https://docs.mistral.ai/studio/conversations/chat-completion | section: other-useful-features
    Chat completions > Other useful features
    **V2** ```python import os from mistralai.client import Mistral api_key = os.environ["MISTRAL_API_KEY"] model = "mistral-medium-latest" client = Mistral(api_key=api_key) chat_response = client.chat.complete( model=model, messages=[ { "role": "user", "content": "What is the capital of France?", }, ], stop=["."], ) ``` **TypeScript** ```typescript import { Mistral } from "@mistralai/mistralai"; impo …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion#other-useful-features

[4] https://docs.mistral.ai/studio/conversations/chat-completion | section: chat-completion
    Chat completions > Chat completion
    **Asynchronous** ```py import asyncio import os from mistralai.client import Mistral from mistralai.models import UserMessage async def main(): api_key = os.environ["MISTRAL_API_KEY"] model = "mistral-large-latest" client = Mistral(api_key=api_key) chat_response = await client.chat.complete_async( model=model, messages=[UserMessage(content="How far is the moon from earth?")], ) if __name__ == "__m …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion

[5] https://docs.mistral.ai/studio/conversations/citations | section: make-final-chat-request
    Citations & References > Usage > Make Final Chat Request
    Finally, you can make the final chat request to the model with the updated chat history, providing the **original query**, the models **tool call** and the **tool result**. **Python** ```python chat_response = client.chat.complete( model=model, messages=chat_history, tools=[get_information_tool], ) ``` **cURL**
    cite: https://docs.mistral.ai/studio/conversations/citations#make-final-chat-request

[6] https://docs.mistral.ai/resources/known-limitations | section: function-calling
    Known limitations > Function calling
    - Maximum number of tools per request: **128**. - Tool descriptions are included in the token count. Long descriptions reduce available context for messages. - Parallel function calls are supported but may return calls in any order. - `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.
    cite: https://docs.mistral.ai/resources/known-limitations#function-calling

[7] https://docs.mistral.ai/studio/conversations/chat-completion | section: multi-turn
    Chat completions > Multi-turn
    **TypeScript** ```typescript import { Mistral } from '@mistralai/mistralai'; import * as dotenv from 'dotenv'; dotenv.config(); const apiKey = process.env['MISTRAL_API_KEY']; const client = new Mistral({ apiKey: apiKey }); async function main() { const result = await client.chat.complete({ model: 'mistral-medium-latest', messages: [ { role: 'user', content: 'What is the capital of France?' }, { ro …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion#multi-turn

[8] https://docs.mistral.ai/studio/conversations/chat-completion/prompt-registry | section: basic-usage
    Using prompts in chat completions > Basic usage
    Fetch the prompt by name or ID, extract its content, and pass it as the system message. **Python** **V1** ```python import os from mistralai.client import Mistral client = Mistral(api_key=os.environ["MISTRAL_API_KEY"]) prompt = client.beta.prompts.get(prompt_id="coding-assistant") system_content = prompt.definition.content response = client.chat.complete( model="mistral-large-latest", messages=[ { …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion/prompt-registry#basic-usage

[9] https://docs.mistral.ai/studio/conversations/moderation | section: inline-guardrails
    Moderation & Guardrailing > Custom Guardrails > Chat completions guardrails
    Use `POST /v1/chat/completions` when you want guardrails on a single chat completion request. The request includes the full message list, and the response doesn't create a persistent Conversation. Pass a `guardrails` field in the request body. **Python** **V1** ```python import os from mistralai.client import Mistral api_key = os.environ["MISTRAL_API_KEY"] client = Mistral(api_key=api_key) respons …
    cite: https://docs.mistral.ai/studio/conversations/moderation#inline-guardrails

[10] https://docs.mistral.ai/studio/safety-moderation | section: inline-guardrails
    Moderation & Guardrailing > Custom Guardrails > Chat completions guardrails
    Use `POST /v1/chat/completions` when you want guardrails on a single chat completion request. The request includes the full message list, and the response doesn't create a persistent Conversation. Pass a `guardrails` field in the request body. **Python** **V1** ```python import os from mistralai.client import Mistral api_key = os.environ["MISTRAL_API_KEY"] client = Mistral(api_key=api_key) respons …
    cite: https://docs.mistral.ai/studio/safety-moderation#inline-guardrails

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/function-calling", section="five-steps/generate-function-arguments") to read hit 1 on its page
```

### 7. mistral_docs_search

```json
{"q": "API chat completions tool_choice", "max_hits": 10}
```

Result:

```
q: "API chat completions tool_choice"

[1] https://docs.mistral.ai/studio/conversations/chat-completion | section: chat-completions
    Chat completions
    Large language models (LLMs) are AI systems that generate text and engage in conversational interactions. They follow instructions and respond naturally to prompts: inputs like questions, instructions, or task examples. The model processes the prompt and produces a relevant text output as its response. ![chat_completions_graph](https://docs.mistral.ai/img/chat_completions.png) The use cases around …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion

[2] https://docs.mistral.ai/studio/conversations/chat-completion | section: chat-completion
    Chat completions > Chat completion
    **cURL** ```bash curl --location "https://api.mistral.ai/v1/chat/completions" \ --header 'Content-Type: application/json' \ --header 'Accept: application/json' \ --header "Authorization: Bearer $MISTRAL_API_KEY" \ --data '{ "model": "mistral-large-latest", "messages": [ { "role": "user", "content": "How far is the moon from earth? Answer with the distance in km only." } ], "stream": true }' ``` ** …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion

[3] https://docs.mistral.ai/studio/conversations/chat-completion | section: other-useful-features
    Chat completions > Other useful features
    **V2** ```python import os from mistralai.client import Mistral api_key = os.environ["MISTRAL_API_KEY"] model = "mistral-medium-latest" client = Mistral(api_key=api_key) chat_response = client.chat.complete( model=model, messages=[ { "role": "user", "content": "What is the capital of France?", }, ], stop=["."], ) ``` **TypeScript** ```typescript import { Mistral } from "@mistralai/mistralai"; impo …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion#other-useful-features

[4] https://docs.mistral.ai/studio/conversations/chat-completion | section: more
    Chat completions > More
    This was a simple introduction to our chat completions service, however we have a lot more to offer we recommend taking a look; from [Vision](https://docs.mistral.ai/studio/conversations/vision) capabilities, to [Function Calling](https://docs.mistral.ai/studio/agents/agent-tools/function-calling), [Predicted Outputs](https://docs.mistral.ai/studio/conversations/advanced/predicted-outputs), [Struc …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion#more

[5] https://docs.mistral.ai/studio/conversations/chat-completion | section: multi-turn
    Chat completions > Multi-turn
    **Output** ```json { "id": "b43f553c4988428aa0c615be4c8f9381", "created": 1756907722, "model": "mistral-medium-latest", "usage": { "prompt_tokens": 26, "total_tokens": 36, "completion_tokens": 10 }, "object": "chat.completion", "choices": [ { "index": 0, "finish_reason": "stop", "message": { "role": "assistant", "tool_calls": null, "content": "La capitale de la France est **Paris**." } } ] } ```
    cite: https://docs.mistral.ai/studio/conversations/chat-completion#multi-turn

[6] https://docs.mistral.ai/studio/conversations/chat-completion/prompt-registry | section: using-prompts-in-chat-completions
    Using prompts in chat completions
    The [Prompt Registry](https://docs.mistral.ai/api/#tag/beta.prompts) lets you store, version, and manage prompts centrally in Studio. This guide shows how to retrieve a stored prompt and use it as the system message in a chat completion.
    cite: https://docs.mistral.ai/studio/conversations/chat-completion/prompt-registry

[7] https://docs.mistral.ai/api/endpoint/chat | section: operation-chat_completion_v1_chat_completions_post
    Chat API > Chat Completion
    `POST /v1/chat/completions` - Operation id: `chat_completion_v1_chat_completions_post` - Tag: chat
    cite: https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post

[8] https://docs.mistral.ai/studio/conversations/chat-completion | section: chat-messages
    Chat completions > Chat completion > Chat messages
    Chat `messages` are a collection of prompts or messages, with each message having a specific role assigned to it, such as "system," "user," "assistant," or "tool." - A `system message` is an **optional** message that sets the behavior and context for an AI assistant in a conversation, such as modifying its personality or providing specific instructions. A system message can include task instructio …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion#chat-messages

[9] https://docs.mistral.ai/models | section: chat-completions
    Model capability matrix > Chat completions
    - **[Chat Completions](https://docs.mistral.ai/studio/conversations/chat-completion)** (`chat-completions`), 37 models: Codestral (`codestral-2501`), Codestral (`codestral-2508`), Devstral 2 (`devstral-2512`), Devstral Medium 1.0 (`devstral-medium-2507`), Devstral Small 1.0 (`devstral-small-2505`), Devstral Small 1.1 (`devstral-small-2507`), Devstral Small 2 (`labs-devstral-small-2512`), Leanstral …
    cite: https://docs.mistral.ai/models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/models", section="chat-completions") reads this section

[10] https://docs.mistral.ai/api/endpoint/chat | section: operation-chat_completion_v1_chat_completions_post/request-body
    Chat API > Chat Completion > Request body
    - `model` (string, required) — ID of the model to use. You can use the [List Available Models](https://docs.mistral.ai/api/#tag/models/operation/list_models_v1_models_get) API to see all of your available models, or see our [Model overview](https://docs.mistral.ai/models) for model descriptions. - `temperature` (number or null, optional) — What sampling temperature to use, we recommend between 0.0 …
    cite: https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/chat-completion") to read hit 1 on its page
```

### 8. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/api/endpoint/chat"}
```

Result:

```
page: https://docs.mistral.ai/api/endpoint/chat | "Chat API"

## section: chat-api
    Chat API
    cite: https://docs.mistral.ai/api/endpoint/chat
# Chat API

Reference for the Chat endpoints of the Mistral API, generated from the OpenAPI specification.

## section: operation-chat_completion_v1_chat_completions_post
    Chat API > Chat Completion
    cite: https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post
## Chat Completion {#operation-chat_completion_v1_chat_completions_post}

`POST /v1/chat/completions`

- Operation id: `chat_completion_v1_chat_completions_post`
- Tag: chat

## section: operation-chat_completion_v1_chat_completions_post/request-body
    Chat API > Chat Completion > Request body
    cite: https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post
### Request body

`application/json` (required), schema `ChatCompletionRequest`

- `model` (string, required) — ID of the model to use. You can use the [List Available Models](https://docs.mistral.ai/api/#tag/models/operation/list_models_v1_models_get) API to see all of your available models, or see our [Model overview](https://docs.mistral.ai/models) for model descriptions.
- `temperature` (number or null, optional) — What sampling temperature to use, we recommend between 0.0 and 0.7. Higher values like 0.7 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both. The default value varies depending on the model you are targeting. Call the `/models` endpoint to retrieve the appropriate value.
- `top_p` (number or null, optional) — Nucleus sampling, where the model considers the results of the tokens with `top_p` probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or `temperature` but not both.
- `max_tokens` (integer or null, optional) — The maximum number of tokens to generate in the completion. The token count of your prompt plus `max_tokens` cannot exceed the model's context length.
- `stream` (boolean, optional) — Whether to stream back partial progress. If set, tokens will be sent as data-only server-side events as they become available, with the stream terminated by a data: [DONE] message. Otherwise, the server will hold the request open until the timeout or until completion, with the response containing the full result as JSON.
- `stop` (object, optional) — Stop generation if this token is detected. Or if one of these tokens is detected when providing an array
  - one of 3 (anyOf):
    - string
    - array of string
    - null
- `random_seed` (integer or null, optional) — The seed to use for random sampling. If set, different calls will generate deterministic results.
- `metadata` (object or null, optional)
- `messages` (array of object, required) — The prompt(s) to generate completions for, encoded as a list of dict with role and content.
  - one of 4 (oneOf):
    - SystemMessage
    - UserMessage
    - AssistantMessage
    - ToolMessage
- `response_format` (ResponseFormat, optional) — Specify the format that the model must output. By default it will use `{ "type": "text" }`. Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is in JSON. When using JSON mode you MUST also instruct the model to produce JSON yourself with a system or a user message. Setting to `{ "type": "json_schema" }` enables JSON schema mode, which guarantees the message the model generates is in JSON and follows the schema you provide.
  - `type` (enum: 'text', 'json_object', 'json_schema', optional)
  - `json_schema` (object or null, optional)
    - `name` (string, required)
    - `description` (string or null, optional)
    - `schema` (object, required)
    - `strict` (boolean, optional)
- `tools` (array of object or null, optional) — A list of tools the model may call. Use this to provide a list of functions the model may generate JSON inputs for.
  - one of 7 (oneOf):
    - Tool
    - WebSearchTool
    - WebSearchPremiumTool
    - CodeInterpreterTool
    - ImageGenerationTool
    - DocumentLibraryTool
    - CustomConnector
- `tool_choice` (object, optional) — Controls which (if any) tool is called by the model. `none` means the model will not call any tool and instead generates a message. `auto` means the model can pick between generating a message or calling one or more tools. `any` or `required` means the model must call one or more tools. Specifying a particular tool via `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.
  - one of 2 (anyOf):
    - ToolChoice
      - `type` (enum: 'function', optional)
      - `function` (FunctionName, required) — this restriction of `Function` is used to select a specific function to call
    - ToolChoiceEnum

- `presence_penalty` (number or null, optional) — The `presence_penalty` determines how much the model penalizes the repetition of words or phrases. A higher presence penalty encourages the model to use a wider variety of words and phrases, making the output more diverse and creative.
- `frequency_penalty` (number or null, optional) — The `frequency_penalty` penalizes the repetition of words based on their frequency in the generated text. A higher frequency penalty discourages the model from repeating words that have already appeared frequently in the output, promoting diversity and reducing repetition.
- `n` (integer or null, optional) — Number of completions to return for each request, input tokens are only billed once.
- `prediction` (Prediction, optional) — Enable users to specify expected results, optimizing response times by leveraging known or predictable content. This approach is especially effective for updating text documents or code files with minimal changes, reducing latency while maintaining high-quality results.
  - `type` (string, optional)
  - `content` (string, optional)
- `parallel_tool_calls` (boolean, optional) — Whether to enable parallel function calling during tool use, when enabled the model can call multiple tools in parallel.
- `reasoning_effort` (enum: 'none', 'minimal', 'low', 'medium', 'high', 'xhigh', optional)
- `prompt_mode` (enum: 'reasoning', optional) — Allows toggling between the reasoning mode and no system prompt. When set to `reasoning` the system prompt for reasoning models will be used.
- `guardrails` (array of GuardrailConfig or null, optional)
  - `block_on_error` (boolean, optional) — If true, return HTTP 403 and block request in the event of a server-side error
  - `moderation_llm_v1` (object or null, optional)
  - `moderation_llm_v2` (object or null, optional)
- `prompt_cache_key` (string or null, optional)
- `service_tier` (enum: 'auto', 'standard_only', optional) — Determines whether to serve the request using priority or standard capacity.
- `safe_prompt` (boolean, optional) — Whether to inject a safety prompt before all conversations.

## section: operation-chat_completion_v1_chat_completions_post/responses
    Chat API > Chat Completion > Responses
    cite: https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post
### Responses

- `200` — Successful Response (application/json, text/event-stream, schema ChatCompletionResponse, CompletionEvent)
- `422` — Validation Error (application/json, schema HTTPValidationError)

Results: 4 sections, the whole page.
```

## Answer

When `tools` are declared on the request, setting `tool_choice: "none"` **prevents the model from calling any tool** and forces it to generate a regular text message instead.

This is explicitly documented in the Chat API reference:
> `tool_choice` (object, optional) — Controls which (if any) tool is called by the model. **`none` means the model will not call any tool and instead generates a message.** `auto` means the model can pick between generating a message or calling one or more tools. `any` or `required` means the model must call one or more tools.
[Chat API > Request body](https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post/request-body)

