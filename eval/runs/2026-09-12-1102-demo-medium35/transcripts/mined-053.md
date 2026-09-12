# mined-053 (api_reference, 10 connector calls)

## Question

What does `tool_choice: "none"` do when tools are still declared on the request?

## Thinking

The user is asking about the behavior of `tool_choice: "none"` when tools are declared in a request. This is a specific technical question about Mistral's API or SDK configuration. I need to search the Mistral documentation to find the exact definition and behavior of this parameter. I'll use the mistral_docs_search tool with a precise query to locate the relevant documentation section.

The first search returned a quickstart guide but didn't explicitly explain the `tool_choice: "none"` behavior. I need to search more specifically for this parameter. Let me try a broader search focusing just on `tool_choice: "none"` to find where it's documented in the API reference.

The search results are still not giving me the direct answer. The hits seem to be about general tool usage rather than the specific `tool_choice` parameter. I should look at the actual API endpoint documentation where this parameter would be defined. Let me try reading the conversations endpoint documentation which likely contains the tool_choice parameter definition.

I've read the conversations endpoint documentation which mentions tool_choice but doesn't explicitly define the "none" value. I need to find a more specific explanation of the tool_choice enum values. Let me try searching for a description of the tool_choice parameter and its possible values, particularly focusing on the "none" option.

The search results are still not giving me a clear definition. Let me try searching for the Chat Completions API documentation, as the tool_choice parameter might be defined there. The user's question is about the behavior when tools are declared but tool_choice is set to "none", so I need to find the exact semantics of this value.

The conversations API documentation confirms that tool_choice is an enum with values including "none", but I need to find the actual definition of what "none" means. Let me search the Chat Completions API documentation specifically, as that's likely where the tool_choice parameter is originally defined for Mistral's API.

I need to find the actual Chat Completions API reference. Let me search more specifically for the API endpoint documentation that would contain the tool_choice parameter definition.

Let me try searching for the API endpoint reference directly. The tool_choice parameter should be documented in the Chat Completions API endpoint reference.

The search results are pointing to the chat-completion page but not giving me the endpoint reference. Let me try a more direct search for the API endpoint path.

Good, I found a reference to the Chat API endpoint. Let me read that page to find the tool_choice parameter definition.

Perfect! I found the definition in the Chat API documentation. The tool_choice parameter is described there with its enum values. The documentation clearly states that `tool_choice: "none"` means the model will not call any tool and instead generates a message, even if tools are declared. This directly answers the user's question. I can now provide a clear, authoritative answer with the proper citation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "tool_choice: \"none\" behavior when tools are declared"}
```

Result:

```
q: "tool_choice: \"none\" behavior when tools are declared"

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

[4] https://docs.mistral.ai/studio/agents/agent-tools | section: general-usage
    Agents Tools Overview > Tools > Built-in tools > General usage
    Built-in tool support depends on the API you use. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#general-usage

[5] https://docs.mistral.ai/studio/agents/agent-tools | section: built-in-tools
    Agents Tools Overview > Tools > Built-in tools
    ![built_in_graph](https://docs.mistral.ai/img/built_in_graph.png) Built-in tools are ready out of the box. They can be called at any point, and all execution happens in our internal environment. They're also available for users to use directly via Conversations without creating an Agent first.
    cite: https://docs.mistral.ai/studio/agents/agent-tools#built-in-tools

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 2. mistral_docs_search

```json
{"q": "tool_choice: \"none\""}
```

Result:

```
q: "tool_choice: \"none\""

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

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/api/endpoint/beta/conversations"}
```

Result:

```
page: https://docs.mistral.ai/api/endpoint/beta/conversations | "Beta Conversations API"

## section: beta-conversations-api
    Beta Conversations API
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations
# Beta Conversations API

Reference for the Beta Conversations endpoints of the Mistral API, generated from the OpenAPI specification.

## section: operation-agents_api_v1_conversations_list
    Beta Conversations API > List all created conversations.
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_list
## List all created conversations. {#operation-agents_api_v1_conversations_list}

`GET /v1/conversations`

Retrieve a list of conversation entities sorted by creation time.

- Operation id: `agents_api_v1_conversations_list`
- Tag: beta/conversations

## section: operation-agents_api_v1_conversations_list/parameters
    Beta Conversations API > List all created conversations. > Parameters
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_list
### Parameters

- `page` (integer, optional, in query)
- `page_size` (integer, optional, in query)
- `metadata` (object, optional, in query)

## section: operation-agents_api_v1_conversations_list/responses
    Beta Conversations API > List all created conversations. > Responses
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_list
### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## section: operation-agents_api_v1_conversations_start
    Beta Conversations API > Create a conversation and append entries to it.
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start
## Create a conversation and append entries to it. {#operation-agents_api_v1_conversations_start}

`POST /v1/conversations`

Create a new conversation, using a base model or an agent and append entries. Completion and tool executions are run and the response is appended to the conversation.Use the returned conversation_id to continue the conversation.

- Operation id: `agents_api_v1_conversations_start`
- Tag: beta/conversations

## section: operation-agents_api_v1_conversations_start/request-body
    Beta Conversations API > Create a conversation and append entries to it. > Request body
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start
### Request body

`application/json` (required), schema `ConversationRequest`

- `inputs` (ConversationInputs, required)
  - one of 2 (anyOf):
    - string
    - InputEntries
- `stream` (enum: False, optional)
- `store` (boolean or null, optional)
- `handoff_execution` (enum: 'client', 'server', optional)
- `instructions` (string or null, optional)
- `tools` (array of object or null, optional)
  - one of 7 (oneOf):
    - FunctionTool
    - WebSearchTool
    - WebSearchPremiumTool
    - CodeInterpreterTool
    - ImageGenerationTool
    - DocumentLibraryTool
    - CustomConnector
- `completion_args` (object or null, optional) — White-listed arguments from the completion API
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
- `name` (string or null, optional)
- `description` (string or null, optional)
- `metadata` (object or null, optional) — Custom type for metadata with embedded validation.
- `agent_id` (string or null, optional)
- `agent_version` (object, optional)
  - one of 3 (anyOf):
    - string
    - integer
    - null
- `model` (string or null, optional)

## section: operation-agents_api_v1_conversations_start/responses
    Beta Conversations API > Create a conversation and append entries to it. > Responses
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start
### Responses

- `200` — Successful Response (application/json, schema ConversationResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## section: operation-agents_api_v1_conversations_get
    Beta Conversations API > Retrieve a conversation information.
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_get
## Retrieve a conversation information. {#operation-agents_api_v1_conversations_get}

`GET /v1/conversations/{conversation_id}`

Given a conversation_id retrieve a conversation entity with its attributes.

- Operation id: `agents_api_v1_conversations_get`
- Tag: beta/conversations

## section: operation-agents_api_v1_conversations_get/parameters
    Beta Conversations API > Retrieve a conversation information. > Parameters
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_get
### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation from which we are fetching metadata.

## section: operation-agents_api_v1_conversations_get/responses
    Beta Conversations API > Retrieve a conversation information. > Responses
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_get
### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## section: operation-agents_api_v1_conversations_append
    Beta Conversations API > Append new entries to an existing conversation.
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append
## Append new entries to an existing conversation. {#operation-agents_api_v1_conversations_append}

`POST /v1/conversations/{conversation_id}`

Run completion on the history of the conversation and the user entries. Return the new created entries.

- Operation id: `agents_api_v1_conversations_append`
- Tag: beta/conversations

## section: operation-agents_api_v1_conversations_append/parameters
    Beta Conversations API > Append new entries to an existing conversation. > Parameters
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append
### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation to which we append entries.

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

## section: operation-agents_api_v1_conversations_append/responses
    Beta Conversations API > Append new entries to an existing conversation. > Responses
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append
### Responses

- `200` — Successful Response (application/json, schema ConversationResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## section: operation-agents_api_v1_conversations_delete
    Beta Conversations API > Delete a conversation.
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_delete
## Delete a conversation. {#operation-agents_api_v1_conversations_delete}

`DELETE /v1/conversations/{conversation_id}`

Delete a conversation given a conversation_id.

- Operation id: `agents_api_v1_conversations_delete`
- Tag: beta/conversations

## section: operation-agents_api_v1_conversations_delete/parameters
    Beta Conversations API > Delete a conversation. > Parameters
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_delete
### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation from which we are fetching metadata.

## section: operation-agents_api_v1_conversations_delete/responses
    Beta Conversations API > Delete a conversation. > Responses
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_delete
### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## section: operation-agents_api_v1_conversations_history
    Beta Conversations API > Retrieve all entries in a conversation.
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_history
## Retrieve all entries in a conversation. {#operation-agents_api_v1_conversations_history}

`GET /v1/conversations/{conversation_id}/history`

Given a conversation_id retrieve all the entries belonging to that conversation. The entries are sorted in the order they were appended, those can be messages, connectors or function_call.

- Operation id: `agents_api_v1_conversations_history`
- Tag: beta/conversations

## section: operation-agents_api_v1_conversations_history/parameters
    Beta Conversations API > Retrieve all entries in a conversation. > Parameters
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_history
### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation from which we are fetching entries.

## section: operation-agents_api_v1_conversations_history/responses
    Beta Conversations API > Retrieve all entries in a conversation. > Responses
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_history
### Responses

- `200` — Successful Response (application/json, schema ConversationHistory)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## section: operation-agents_api_v1_conversations_messages
    Beta Conversations API > Retrieve all messages in a conversation.
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_messages
## Retrieve all messages in a conversation. {#operation-agents_api_v1_conversations_messages}

`GET /v1/conversations/{conversation_id}/messages`

Given a conversation_id retrieve all the messages belonging to that conversation. This is similar to retrieving all entries except we filter the messages only.

- Operation id: `agents_api_v1_conversations_messages`
- Tag: beta/conversations

## section: operation-agents_api_v1_conversations_messages/parameters
    Beta Conversations API > Retrieve all messages in a conversation. > Parameters
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_messages
### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation from which we are fetching messages.

## section: operation-agents_api_v1_conversations_messages/responses
    Beta Conversations API > Retrieve all messages in a conversation. > Responses
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_messages
### Responses

- `200` — Successful Response (application/json, schema ConversationMessages)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## section: operation-agents_api_v1_conversations_restart
    Beta Conversations API > Restart a conversation starting from a given entry.
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_restart
## Restart a conversation starting from a given entry. {#operation-agents_api_v1_conversations_restart}

`POST /v1/conversations/{conversation_id}/restart`

Given a conversation_id and an id, recreate a conversation from this point and run completion. A new conversation is returned with the new entries returned.

- Operation id: `agents_api_v1_conversations_restart`
- Tag: beta/conversations

## section: operation-agents_api_v1_conversations_restart/parameters
    Beta Conversations API > Restart a conversation starting from a given entry. > Parameters
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_restart
### Parameters

- `conversation_id` (string, required, in path) — ID of the original conversation which is being restarted.

## section: operation-agents_api_v1_conversations_restart/request-body
    Beta Conversations API > Restart a conversation starting from a given entry. > Request body
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_restart
### Request body

`application/json` (required), schema `ConversationRestartRequest`

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
- `guardrails` (array of GuardrailConfig or null, optional)
  - `block_on_error` (boolean, optional) — If true, return HTTP 403 and block request in the event of a server-side error
  - `moderation_llm_v1` (object or null, optional)
  - `moderation_llm_v2` (object or null, optional)
- `metadata` (object or null, optional) — Custom metadata for the conversation.
- `from_entry_id` (string, required)
- `agent_version` (object, optional) — Specific version of the agent to use when restarting. If not provided, uses the current version.
  - one of 3 (anyOf):
    - string
    - integer
    - null

## section: operation-agents_api_v1_conversations_restart/responses
    Beta Conversations API > Restart a conversation starting from a given entry. > Responses
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_restart
### Responses

- `200` — Successful Response (application/json, schema ConversationResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## section: operation-agents_api_v1_conversations_start_stream
    Beta Conversations API > Create a conversation and append entries to it.
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start_stream
## Create a conversation and append entries to it. {#operation-agents_api_v1_conversations_start_stream}

`POST /v1/conversations`

Create a new conversation, using a base model or an agent and append entries. Completion and tool executions are run and the response is appended to the conversation.Use the returned conversation_id to continue the conversation.

- Operation id: `agents_api_v1_conversations_start_stream`
- Tag: beta/conversations

## section: operation-agents_api_v1_conversations_start_stream/request-body
    Beta Conversations API > Create a conversation and append entries to it. > Request body
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start_stream
### Request body

`application/json` (required), schema `ConversationStreamRequest`

- `inputs` (ConversationInputs, required)
  - one of 2 (anyOf):
    - string
    - InputEntries
- `stream` (enum: True, optional)
- `store` (boolean or null, optional)
- `handoff_execution` (enum: 'client', 'server', optional)
- `instructions` (string or null, optional)
- `tools` (array of object or null, optional)
  - one of 7 (oneOf):
    - FunctionTool
    - WebSearchTool
    - WebSearchPremiumTool
    - CodeInterpreterTool
    - ImageGenerationTool
    - DocumentLibraryTool
    - CustomConnector
- `completion_args` (object or null, optional) — White-listed arguments from the completion API
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
- `name` (string or null, optional)
- `description` (string or null, optional)
- `metadata` (object or null, optional) — Custom type for metadata with embedded validation.
- `agent_id` (string or null, optional)
- `agent_version` (object, optional)
  - one of 3 (anyOf):
    - string
    - integer
    - null
- `model` (string or null, optional)

## section: operation-agents_api_v1_conversations_start_stream/responses
    Beta Conversations API > Create a conversation and append entries to it. > Responses
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start_stream
### Responses

- `200` — Successful Response (text/event-stream, schema ConversationEvents)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## section: operation-agents_api_v1_conversations_append_stream
    Beta Conversations API > Append new entries to an existing conversation.
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_append_stream
## Append new entries to an existing conversation. {#operation-agents_api_v1_conversations_append_stream}

`POST /v1/conversations/{conversation_id}`

Run completion on the history of the conversation and the user entries. Return the new created entries.

- Operation id: `agents_api_v1_conversations_append_stream`
- Tag: beta/conversations

Results: 31 of 38 sections; the page continues.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/conversations", section="operation-agents_api_v1_conversations_append_stream/parameters") continues; remaining sections: operation-agents_api_v1_conversations_append_stream/parameters, operation-agents_api_v1_conversations_append_stream/request-body, operation-agents_api_v1_conversations_append_stream/responses, operation-agents_api_v1_conversations_restart_stream, operation-agents_api_v1_conversations_restart_stream/parameters, operation-agents_api_v1_conversations_restart_stream/request-body, operation-agents_api_v1_conversations_restart_stream/responses
```

### 4. mistral_docs_search

```json
{"q": "tool_choice parameter description and values"}
```

Result:

```
q: "tool_choice parameter description and values"

[1] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[2] https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows/forms_and_confirmations | section: field-types
    Forms and confirmations > Structured form inputs > Field types
    | Field Type | Description | Properties | | --------------- | ---------------- | ------------------------------------------------------------------------------------------------- | | `TextField` | Text input | `description`, `pattern` (optional regex), `prefilled_value` | | `NumberField` | Numeric input | `description`, `minimum`, `maximum`, `exclusive_minimum`, `exclusive_maximum`, `prefilled_val …
    cite: https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows/forms_and_confirmations#field-types

[3] https://docs.mistral.ai/studio/agents/agents-api | section: available-conversations
    Agents & Conversations > Conversations > Available conversations
    ```json [ { "id": "conv_0684fe18cbc57ba6800065acdd2b6c85", "created_at": "2025-06-16T09:19:08.735790Z", "updated_at": "2025-06-16T09:20:03.273654Z", "agent_id": "ag_0684fe0e0b98773e8000323fc71a3986", "name": null, "description": null, "object": "conversation" }, { "id": "conv_0684fd306df172f2800051d4f82d4a8b", "created_at": "2025-06-16T08:17:10.871401Z", "updated_at": "2025-06-16T08:17:10.871402Z" …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="available-conversations") reads this section

[4] https://docs.mistral.ai/resources/known-limitations | section: function-calling
    Known limitations > Function calling
    - Maximum number of tools per request: **128**. - Tool descriptions are included in the token count. Long descriptions reduce available context for messages. - Parallel function calls are supported but may return calls in any order. - `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.
    cite: https://docs.mistral.ai/resources/known-limitations#function-calling

[5] https://docs.mistral.ai/studio/connectors/management | section: list-tools
    Managing Connectors > List tools
    The endpoint supports these query parameters: | Parameter | Default | Description | |-----------|---------|-------------| | `page` | `1` | Page number (offset-based pagination). | | `page_size` | `100` | Number of tools per page. | | `refresh` | `false` | Re-fetch tools from the MCP server instead of using the cache. | | `pretty` | `false` | Return a simplified payload with only `name`, `descripti …
    cite: https://docs.mistral.ai/studio/connectors/management#list-tools

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 5. mistral_docs_search

```json
{"q": "tool_choice enum values auto none any required"}
```

Result:

```
q: "tool_choice enum values auto none any required"

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

[4] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_start_stream/request-body
    Beta Conversations API > Create a conversation and append entries to it. > Request body
    - `inputs` (ConversationInputs, required) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: True, optional) - `store` (boolean or null, optional) - `handoff_execution` (enum: 'client', 'server', optional) - `instructions` (string or null, optional) - `tools` (array of object or null, optional) - one of 7 (oneOf): - FunctionTool - WebSearchTool - WebSearchPremiumTool - CodeInterpreterTo …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start_stream

[5] https://docs.mistral.ai/api/endpoint/beta/conversations | section: operation-agents_api_v1_conversations_start/request-body
    Beta Conversations API > Create a conversation and append entries to it. > Request body
    - `inputs` (ConversationInputs, required) - one of 2 (anyOf): - string - InputEntries - `stream` (enum: False, optional) - `store` (boolean or null, optional) - `handoff_execution` (enum: 'client', 'server', optional) - `instructions` (string or null, optional) - `tools` (array of object or null, optional) - one of 7 (oneOf): - FunctionTool - WebSearchTool - WebSearchPremiumTool - CodeInterpreterT …
    cite: https://docs.mistral.ai/api/endpoint/beta/conversations#operation-agents_api_v1_conversations_start

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/conversations") to read hit 1 on its page
```

### 6. mistral_docs_search

```json
{"q": "Chat Completions API tool_choice"}
```

Result:

```
q: "Chat Completions API tool_choice"

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

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/chat-completion") to read hit 1 on its page
```

### 7. mistral_docs_search

```json
{"q": "Chat Completions API reference tool_choice"}
```

Result:

```
q: "Chat Completions API reference tool_choice"

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

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/chat-completion") to read hit 1 on its page
```

### 8. mistral_docs_search

```json
{"q": "Chat Completions API endpoint reference"}
```

Result:

```
q: "Chat Completions API endpoint reference"

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

[5] https://docs.mistral.ai/inference/deployment/local-deployment/tgi | section: chat-compatible-endpoint
    TGI > Text Generation Inference > Using the API > With Chat-Compatible Endpoint
    TGI supports the [Messages API](https://huggingface.co/docs/text-generation-inference/en/messages_api), which is compatible with Mistral and OpenAI Chat Completion API. **Using MistralClient** ```python from mistralai.client import MistralClient from mistralai.models.chat_completion import ChatMessage # Initialize the client but point it to TGI client = MistralClient(api_key="-", endpoint="http:// …
    cite: https://docs.mistral.ai/inference/deployment/local-deployment/tgi#chat-compatible-endpoint

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/chat-completion") to read hit 1 on its page
```

### 9. mistral_docs_search

```json
{"q": "/v1/chat/completions reference"}
```

Result:

```
q: "/v1/chat/completions reference"

[1] https://docs.mistral.ai/studio/conversations/chat-completion | section: chat-completion
    Chat completions > Chat completion
    **cURL** ```bash curl --location "https://api.mistral.ai/v1/chat/completions" \ --header 'Content-Type: application/json' \ --header 'Accept: application/json' \ --header "Authorization: Bearer $MISTRAL_API_KEY" \ --data '{ "model": "mistral-large-latest", "messages": [ { "role": "user", "content": "How far is the moon from earth? Answer with the distance in km only." } ], "stream": true }' ``` ** …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion

[2] https://docs.mistral.ai/studio/conversations/chat-completion | section: other-useful-features
    Chat completions > Other useful features
    **V2** ```python import os from mistralai.client import Mistral api_key = os.environ["MISTRAL_API_KEY"] model = "mistral-medium-latest" client = Mistral(api_key=api_key) chat_response = client.chat.complete( model=model, messages=[ { "role": "user", "content": "What is the capital of France?", }, ], stop=["."], ) ``` **TypeScript** ```typescript import { Mistral } from "@mistralai/mistralai"; impo …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion#other-useful-features

[3] https://docs.mistral.ai/api/endpoint/chat | section: operation-chat_completion_v1_chat_completions_post
    Chat API > Chat Completion
    `POST /v1/chat/completions` - Operation id: `chat_completion_v1_chat_completions_post` - Tag: chat
    cite: https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post

[4] https://docs.mistral.ai/studio/conversations/chat-completion | section: multi-turn
    Chat completions > Multi-turn
    **TypeScript** ```typescript import { Mistral } from '@mistralai/mistralai'; import * as dotenv from 'dotenv'; dotenv.config(); const apiKey = process.env['MISTRAL_API_KEY']; const client = new Mistral({ apiKey: apiKey }); async function main() { const result = await client.chat.complete({ model: 'mistral-medium-latest', messages: [ { role: 'user', content: 'What is the capital of France?' }, { ro …
    cite: https://docs.mistral.ai/studio/conversations/chat-completion#multi-turn

[5] https://docs.mistral.ai/studio/conversations/moderation | section: inline-guardrails
    Moderation & Guardrailing > Custom Guardrails > Chat completions guardrails
    Use `POST /v1/chat/completions` when you want guardrails on a single chat completion request. The request includes the full message list, and the response doesn't create a persistent Conversation. Pass a `guardrails` field in the request body. **Python** **V1** ```python import os from mistralai.client import Mistral api_key = os.environ["MISTRAL_API_KEY"] client = Mistral(api_key=api_key) respons …
    cite: https://docs.mistral.ai/studio/conversations/moderation#inline-guardrails

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/chat-completion") to read hit 1 on its page
```

### 10. mistral_docs_read_page

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

When you set `tool_choice: "none"` in a request where tools are still declared, the model **will not call any tool** and will instead generate a natural-language message. This behavior is explicitly defined in the Mistral Chat API documentation:

> `tool_choice` [...] `none` means the model will not call any tool and instead generates a message.
> *[Chat API > Chat Completion > Request body > `tool_choice`](https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post/request-body)*

In short: the presence of `tool_choice: "none"` overrides the tool declarations, and the model responds with a regular text answer.

