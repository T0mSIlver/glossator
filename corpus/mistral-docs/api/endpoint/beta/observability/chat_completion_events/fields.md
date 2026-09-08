---
url: https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events/fields
title: Beta Observability Chat Completion Events Fields API
breadcrumbs: [API, Beta Observability Chat Completion Events Fields]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Beta Observability Chat Completion Events Fields API

Reference for the Beta Observability Chat Completion Events Fields endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Chat Completion Fields {#operation-get_chat_completion_fields_v1_observability_chat_completion_fields_get}

`GET /v1/observability/chat-completion-fields`

- Operation id: `get_chat_completion_fields_v1_observability_chat_completion_fields_get`
- Tag: beta/observability/chat_completion_events/fields

### Responses

- `200` — Successful Response (application/json, schema ListChatCompletionFieldsResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get Chat Completion Field Options {#operation-get_chat_completion_field_options_v1_observability_chat_completion_fields_field_name_options_get}

`GET /v1/observability/chat-completion-fields/{field_name}/options`

- Operation id: `get_chat_completion_field_options_v1_observability_chat_completion_fields__field_name__options_get`
- Tag: beta/observability/chat_completion_events/fields

### Parameters

- `field_name` (string, required, in path)
- `operator` (enum: 'lt', 'lte', 'gt', 'gte', 'startswith', 'istartswith', 'endswith', 'iendswith', 'contains', 'icontains', 'matches', 'notcontains', ..., required, in query) — The operator to use for filtering options

### Responses

- `200` — Successful Response (application/json, schema FetchChatCompletionFieldOptionsResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get Chat Completion Field Options Counts {#operation-get_chat_completion_field_options_counts_v1_observability_chat_completion_fields_field_name_options_counts_post}

`POST /v1/observability/chat-completion-fields/{field_name}/options-counts`

- Operation id: `get_chat_completion_field_options_counts_v1_observability_chat_completion_fields__field_name__options_counts_post`
- Tag: beta/observability/chat_completion_events/fields

### Parameters

- `field_name` (string, required, in path)

### Request body

`application/json` (required), schema `FetchFieldOptionCountsRequest`

- `filter_params` (object or null, optional)
  - `filters` (object, required)
    - one of (anyOf):
      - FilterGroup
      - FilterCondition
      - null

### Responses

- `200` — Successful Response (application/json, schema FetchFieldOptionCountsResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)
