---
url: https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events
title: Beta Observability Chat Completion Events API
breadcrumbs: [API, Beta Observability Chat Completion Events]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Observability Chat Completion Events API

Reference for the Beta Observability Chat Completion Events endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Chat Completion Events {#operation-get_chat_completion_events_v1_observability_chat_completion_events_search_post}

`POST /v1/observability/chat-completion-events/search`

- Operation id: `get_chat_completion_events_v1_observability_chat_completion_events_search_post`
- Tag: beta/observability/chat_completion_events

### Parameters

- `page_size` (integer, optional, in query)
- `cursor` (string or null, optional, in query)

### Request body

`application/json` (required), schema `SearchChatCompletionEventsRequest`

- `search_params` (FilterPayload, required)
  - `filters` (object, required)
    - one of 3 (anyOf):
      - FilterGroup
      - FilterCondition
      - null
- `extra_fields` (array of string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema SearchChatCompletionEventsResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Alternative to /search that returns only the IDs and that can return many IDs at once {#operation-get_chat_completion_event_ids_v1_observability_chat_completion_events_search_ids_post}

`POST /v1/observability/chat-completion-events/search-ids`

- Operation id: `get_chat_completion_event_ids_v1_observability_chat_completion_events_search_ids_post`
- Tag: beta/observability/chat_completion_events

### Request body

`application/json` (required), schema `SearchChatCompletionEventIdsRequest`

- `search_params` (FilterPayload, required)
  - `filters` (object, required)
    - one of 3 (anyOf):
      - FilterGroup
      - FilterCondition
      - null
- `extra_fields` (array of string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema SearchChatCompletionEventIdsResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get Chat Completion Event {#operation-get_chat_completion_event_v1_observability_chat_completion_events_event_id_get}

`GET /v1/observability/chat-completion-events/{event_id}`

- Operation id: `get_chat_completion_event_v1_observability_chat_completion_events__event_id__get`
- Tag: beta/observability/chat_completion_events

### Parameters

- `event_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema ChatCompletionEvent)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get Similar Chat Completion Events {#operation-get_similar_chat_completion_events_v1_observability_chat_completion_events_event_id_similar_events_get}

`GET /v1/observability/chat-completion-events/{event_id}/similar-events`

- Operation id: `get_similar_chat_completion_events_v1_observability_chat_completion_events__event_id__similar_events_get`
- Tag: beta/observability/chat_completion_events

### Parameters

- `event_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema SearchChatCompletionEventsResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Run Judge on an event based on the given options {#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post}

`POST /v1/observability/chat-completion-events/{event_id}/live-judging`

- Operation id: `judge_chat_completion_event_v1_observability_chat_completion_events__event_id__live_judging_post`
- Tag: beta/observability/chat_completion_events

### Parameters

- `event_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `JudgeChatCompletionEventRequest`

- `judge_definition` (CreateJudgeRequest, required)
  - `name` (string, required)
  - `description` (string, required)
  - `model_name` (string, required)
  - `output` (object, required)
    - one of 2 (oneOf):
      - JudgeClassificationOutput
      - JudgeRegressionOutput
  - `instructions` (string, required)
  - `tools` (array of string, required)

### Responses

- `200` — Successful Response (application/json, schema JudgeOutput)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)
