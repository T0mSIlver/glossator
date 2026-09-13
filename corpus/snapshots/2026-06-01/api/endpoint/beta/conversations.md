---
url: https://docs.mistral.ai/api/endpoint/beta/conversations
title: Beta Conversations API
breadcrumbs: [API, Beta Conversations]
kind: api
locale: en
source_path: openapi.yaml
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
openapi_md5: 3c3c0d6b147730e71376c46aaca996cc
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Conversations API

Reference for the Beta Conversations endpoints of the Mistral API, generated from the OpenAPI specification.

## List all created conversations. {#operation-agents_api_v1_conversations_list}

`GET /v1/conversations`

Retrieve a list of conversation entities sorted by creation time.

- Operation id: `agents_api_v1_conversations_list`
- Tag: beta/conversations

### Parameters

- `page` (integer, optional, in query)
- `page_size` (integer, optional, in query)
- `metadata` (object, optional, in query)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create a conversation and append entries to it. {#operation-agents_api_v1_conversations_start}

`POST /v1/conversations`

Create a new conversation, using a base model or an agent and append entries. Completion and tool executions are run and the response is appended to the conversation.Use the returned conversation_id to continue the conversation.

- Operation id: `agents_api_v1_conversations_start`
- Tag: beta/conversations

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
  - `reasoning_effort` (enum: 'high', 'none', optional) — Controls the reasoning effort level for reasoning models. "high" enables comprehensive reasoning traces, "none" disables reasoning effort.
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

### Responses

- `200` — Successful Response (application/json, schema ConversationResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Retrieve a conversation information. {#operation-agents_api_v1_conversations_get}

`GET /v1/conversations/{conversation_id}`

Given a conversation_id retrieve a conversation entity with its attributes.

- Operation id: `agents_api_v1_conversations_get`
- Tag: beta/conversations

### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation from which we are fetching metadata.

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Append new entries to an existing conversation. {#operation-agents_api_v1_conversations_append}

`POST /v1/conversations/{conversation_id}`

Run completion on the history of the conversation and the user entries. Return the new created entries.

- Operation id: `agents_api_v1_conversations_append`
- Tag: beta/conversations

### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation to which we append entries.

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
  - `reasoning_effort` (enum: 'high', 'none', optional) — Controls the reasoning effort level for reasoning models. "high" enables comprehensive reasoning traces, "none" disables reasoning effort.
- `tool_confirmations` (array of ToolCallConfirmation or null, optional)
  - `tool_call_id` (string, required)
  - `confirmation` (enum: 'allow', 'deny', required)

### Responses

- `200` — Successful Response (application/json, schema ConversationResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete a conversation. {#operation-agents_api_v1_conversations_delete}

`DELETE /v1/conversations/{conversation_id}`

Delete a conversation given a conversation_id.

- Operation id: `agents_api_v1_conversations_delete`
- Tag: beta/conversations

### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation from which we are fetching metadata.

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Retrieve all entries in a conversation. {#operation-agents_api_v1_conversations_history}

`GET /v1/conversations/{conversation_id}/history`

Given a conversation_id retrieve all the entries belonging to that conversation. The entries are sorted in the order they were appended, those can be messages, connectors or function_call.

- Operation id: `agents_api_v1_conversations_history`
- Tag: beta/conversations

### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation from which we are fetching entries.

### Responses

- `200` — Successful Response (application/json, schema ConversationHistory)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Retrieve all messages in a conversation. {#operation-agents_api_v1_conversations_messages}

`GET /v1/conversations/{conversation_id}/messages`

Given a conversation_id retrieve all the messages belonging to that conversation. This is similar to retrieving all entries except we filter the messages only.

- Operation id: `agents_api_v1_conversations_messages`
- Tag: beta/conversations

### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation from which we are fetching messages.

### Responses

- `200` — Successful Response (application/json, schema ConversationMessages)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Restart a conversation starting from a given entry. {#operation-agents_api_v1_conversations_restart}

`POST /v1/conversations/{conversation_id}/restart`

Given a conversation_id and an id, recreate a conversation from this point and run completion. A new conversation is returned with the new entries returned.

- Operation id: `agents_api_v1_conversations_restart`
- Tag: beta/conversations

### Parameters

- `conversation_id` (string, required, in path) — ID of the original conversation which is being restarted.

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
  - `reasoning_effort` (enum: 'high', 'none', optional) — Controls the reasoning effort level for reasoning models. "high" enables comprehensive reasoning traces, "none" disables reasoning effort.
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

### Responses

- `200` — Successful Response (application/json, schema ConversationResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create a conversation and append entries to it. {#operation-agents_api_v1_conversations_start_stream}

`POST /v1/conversations`

Create a new conversation, using a base model or an agent and append entries. Completion and tool executions are run and the response is appended to the conversation.Use the returned conversation_id to continue the conversation.

- Operation id: `agents_api_v1_conversations_start_stream`
- Tag: beta/conversations

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
  - `reasoning_effort` (enum: 'high', 'none', optional) — Controls the reasoning effort level for reasoning models. "high" enables comprehensive reasoning traces, "none" disables reasoning effort.
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

### Responses

- `200` — Successful Response (text/event-stream, schema ConversationEvents)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Append new entries to an existing conversation. {#operation-agents_api_v1_conversations_append_stream}

`POST /v1/conversations/{conversation_id}`

Run completion on the history of the conversation and the user entries. Return the new created entries.

- Operation id: `agents_api_v1_conversations_append_stream`
- Tag: beta/conversations

### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation to which we append entries.

### Request body

`application/json` (required), schema `ConversationAppendStreamRequest`

- `inputs` (ConversationInputs, optional)
  - one of 2 (anyOf):
    - string
    - InputEntries
- `stream` (enum: True, optional)
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
  - `reasoning_effort` (enum: 'high', 'none', optional) — Controls the reasoning effort level for reasoning models. "high" enables comprehensive reasoning traces, "none" disables reasoning effort.
- `tool_confirmations` (array of ToolCallConfirmation or null, optional)
  - `tool_call_id` (string, required)
  - `confirmation` (enum: 'allow', 'deny', required)

### Responses

- `200` — Successful Response (text/event-stream, schema ConversationEvents)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Restart a conversation starting from a given entry. {#operation-agents_api_v1_conversations_restart_stream}

`POST /v1/conversations/{conversation_id}/restart`

Given a conversation_id and an id, recreate a conversation from this point and run completion. A new conversation is returned with the new entries returned.

- Operation id: `agents_api_v1_conversations_restart_stream`
- Tag: beta/conversations

### Parameters

- `conversation_id` (string, required, in path) — ID of the original conversation which is being restarted.

### Request body

`application/json` (required), schema `ConversationRestartStreamRequest`

- `inputs` (ConversationInputs, optional)
  - one of 2 (anyOf):
    - string
    - InputEntries
- `stream` (enum: True, optional)
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
  - `reasoning_effort` (enum: 'high', 'none', optional) — Controls the reasoning effort level for reasoning models. "high" enables comprehensive reasoning traces, "none" disables reasoning effort.
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

### Responses

- `200` — Successful Response (text/event-stream, schema ConversationEvents)
- `422` — Validation Error (application/json, schema HTTPValidationError)
