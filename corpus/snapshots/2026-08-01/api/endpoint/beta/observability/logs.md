---
url: https://docs.mistral.ai/api/endpoint/beta/observability/logs
title: Beta Observability Logs API
breadcrumbs: [API, Beta Observability Logs]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
openapi_md5: 1ae55facb05ef4d5bf803842b3033337
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Observability Logs API

Reference for the Beta Observability Logs endpoints of the Mistral API, generated from the OpenAPI specification.

## Search logs {#operation-search_logs_v1_observability_logs_search_post}

`POST /v1/observability/logs/search`

- Operation id: `search_logs_v1_observability_logs_search_post`
- Tag: beta/observability/logs

### Parameters

- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)
- `page_size` (integer, optional, in query)
- `cursor` (string or null, optional, in query)

### Request body

`application/json` (required), schema `LogsRequest`

- `search_expression` (string or null, optional)
- `order` (enum: 'asc', 'desc', optional)

### Responses

- `200` — Successful Response (application/json, schema GetLogs)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get log field definitions {#operation-get_log_fields_v1_observability_logs_fields_get}

`GET /v1/observability/logs/fields`

- Operation id: `get_log_fields_v1_observability_logs_fields_get`
- Tag: beta/observability/logs

### Responses

- `200` — Successful Response (application/json, schema GetLogFields)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get options for a log field {#operation-get_log_field_options_v1_observability_logs_fields_field_name_options_get}

`GET /v1/observability/logs/fields/{field_name}/options`

- Operation id: `get_log_field_options_v1_observability_logs_fields__field_name__options_get`
- Tag: beta/observability/logs

### Parameters

- `field_name` (string, required, in path)
- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema GetLogFieldOptions)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)
