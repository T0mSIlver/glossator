---
url: https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events/fields
title: Beta Observability Chat Completion Events Fields API
breadcrumbs: [API, Beta Observability Chat Completion Events Fields]
kind: api
locale: en
source_path: openapi.yaml
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
openapi_md5: 3c3c0d6b147730e71376c46aaca996cc
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Observability Chat Completion Events Fields API

Reference for the Beta Observability Chat Completion Events Fields endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Chat Completion Fields {#operation-get_chat_completion_fields_v1_observability_chat_completion_fields_get}

`GET /v1/observability/chat-completion-fields`

- Operation id: `get_chat_completion_fields_v1_observability_chat_completion_fields_get`
- Tag: beta/observability/chat_completion_events/fields

### Responses

- `200` — Successful Response (application/json, schema ChatCompletionFields)
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

- `200` — Successful Response (application/json, schema ChatCompletionFieldOptions)
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

`application/json` (required), schema `FieldOptionCountsInSchema`

- `filter_params` (object or null, optional)
  - `filters` (object, required)
    - one of 3 (anyOf):
      - FilterGroup
      - FilterCondition
      - null

### Responses

- `200` — Successful Response (application/json, schema FieldOptionCounts)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)
