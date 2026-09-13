---
url: https://docs.mistral.ai/api/endpoint/beta/observability/traces
title: Beta Observability Traces API
breadcrumbs: [API, Beta Observability Traces]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Observability Traces API

Reference for the Beta Observability Traces endpoints of the Mistral API, generated from the OpenAPI specification.

## Search traces {#operation-search_traces_v1_observability_traces_search_post}

`POST /v1/observability/traces/search`

- Operation id: `search_traces_v1_observability_traces_search_post`
- Tag: beta/observability/traces

### Parameters

- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)
- `page_size` (integer, optional, in query)
- `cursor` (string or null, optional, in query)

### Request body

`application/json` (required), schema `TracesRequest`

- `search_expression` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema GetTraces)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Aggregate traces {#operation-aggregate_traces_v1_observability_traces_aggregate_post}

`POST /v1/observability/traces/aggregate`

- Operation id: `aggregate_traces_v1_observability_traces_aggregate_post`
- Tag: beta/observability/traces

### Parameters

- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)

### Request body

`application/json` (required), schema `AggregationRequest`

- `metric` (MetricDefinition, required)
  - `measure` (string, required)
  - `aggregation` (enum: 'count', 'count_distinct', 'sum', 'avg', 'min', 'max', 'p50', 'p90', 'p95', 'p99', required)
- `dimensions` (array of string, optional)
- `time_dimension` (object or null, optional)
  - `granularity` (enum: 'auto', 'second', 'minute', 'hour', 'day', 'week', 'month', optional)
- `search_expression` (string or null, optional)
- `order_by` (array of OrderByClause or null, optional)
  - `field` (string, required)
  - `direction` (enum: 'asc', 'desc', optional)
- `limit` (integer, optional)

### Responses

- `200` — Successful Response (application/json, schema Aggregation)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get trace field definitions {#operation-get_trace_fields_v1_observability_traces_fields_get}

`GET /v1/observability/traces/fields`

- Operation id: `get_trace_fields_v1_observability_traces_fields_get`
- Tag: beta/observability/traces

### Responses

- `200` — Successful Response (application/json, schema GetTraceFields)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get trace by id {#operation-get_trace_by_id_v1_observability_traces_trace_id_get}

`GET /v1/observability/traces/{trace_id}`

- Operation id: `get_trace_by_id_v1_observability_traces__trace_id__get`
- Tag: beta/observability/traces

### Parameters

- `trace_id` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema GetTrace)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get trace spans {#operation-get_trace_spans_v1_observability_traces_trace_id_spans_get}

`GET /v1/observability/traces/{trace_id}/spans`

- Operation id: `get_trace_spans_v1_observability_traces__trace_id__spans_get`
- Tag: beta/observability/traces

### Parameters

- `trace_id` (string, required, in path)
- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)
- `page_size` (integer, optional, in query)
- `cursor` (string or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema GetSpans)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get options for a trace field {#operation-get_trace_field_options_v1_observability_traces_fields_field_name_options_get}

`GET /v1/observability/traces/fields/{field_name}/options`

- Operation id: `get_trace_field_options_v1_observability_traces_fields__field_name__options_get`
- Tag: beta/observability/traces

### Parameters

- `field_name` (string, required, in path)
- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema GetTraceFieldOptions)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get span by id {#operation-get_span_by_id_v1_observability_traces_trace_id_spans_span_id_get}

`GET /v1/observability/traces/{trace_id}/spans/{span_id}`

- Operation id: `get_span_by_id_v1_observability_traces__trace_id__spans__span_id__get`
- Tag: beta/observability/traces

### Parameters

- `trace_id` (string, required, in path)
- `span_id` (string, required, in path)
- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema GetSpan)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)
