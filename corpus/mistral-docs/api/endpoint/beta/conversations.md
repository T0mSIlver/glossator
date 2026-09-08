---
url: https://docs.mistral.ai/api/endpoint/beta/conversations
title: Beta Conversations API
breadcrumbs: [API, Beta Conversations]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
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

- Not documented.

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

- Not documented.

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

- Not documented.

### Responses

- `200` — Successful Response (application/json, schema ConversationResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create a conversation and append entries to it. {#operation-agents_api_v1_conversations_start_stream}

`POST /v1/conversations#stream`

Create a new conversation, using a base model or an agent and append entries. Completion and tool executions are run and the response is appended to the conversation.Use the returned conversation_id to continue the conversation.

- Operation id: `agents_api_v1_conversations_start_stream`
- Tag: beta/conversations

### Request body

`application/json` (required), schema `ConversationStreamRequest`

- Not documented.

### Responses

- `200` — Successful Response (text/event-stream, schema ConversationEvents)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Append new entries to an existing conversation. {#operation-agents_api_v1_conversations_append_stream}

`POST /v1/conversations/{conversation_id}#stream`

Run completion on the history of the conversation and the user entries. Return the new created entries.

- Operation id: `agents_api_v1_conversations_append_stream`
- Tag: beta/conversations

### Parameters

- `conversation_id` (string, required, in path) — ID of the conversation to which we append entries.

### Request body

`application/json` (required), schema `ConversationAppendStreamRequest`

- Not documented.

### Responses

- `200` — Successful Response (text/event-stream, schema ConversationEvents)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Restart a conversation starting from a given entry. {#operation-agents_api_v1_conversations_restart_stream}

`POST /v1/conversations/{conversation_id}/restart#stream`

Given a conversation_id and an id, recreate a conversation from this point and run completion. A new conversation is returned with the new entries returned.

- Operation id: `agents_api_v1_conversations_restart_stream`
- Tag: beta/conversations

### Parameters

- `conversation_id` (string, required, in path) — ID of the original conversation which is being restarted.

### Request body

`application/json` (required), schema `ConversationRestartStreamRequest`

- Not documented.

### Responses

- `200` — Successful Response (text/event-stream, schema ConversationEvents)
- `422` — Validation Error (application/json, schema HTTPValidationError)
