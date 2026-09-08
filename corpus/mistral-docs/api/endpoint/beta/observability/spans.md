---
url: https://docs.mistral.ai/api/endpoint/beta/observability/spans
title: Beta Observability Spans API
breadcrumbs: [API, Beta Observability Spans]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Beta Observability Spans API

Reference for the Beta Observability Spans endpoints of the Mistral API, generated from the OpenAPI specification.

## Search spans {#operation-search_spans_v1_observability_spans_search_post}

`POST /v1/observability/spans/search`

- Operation id: `search_spans_v1_observability_spans_search_post`
- Tag: beta/observability/spans

### Parameters

- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)
- `page_size` (integer, optional, in query)
- `cursor` (string or null, optional, in query)

### Request body

`application/json` (required), schema `SpansRequest`

- `search_expression` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema GetSpans)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Aggregate spans {#operation-aggregate_spans_v1_observability_spans_aggregate_post}

`POST /v1/observability/spans/aggregate`

- Operation id: `aggregate_spans_v1_observability_spans_aggregate_post`
- Tag: beta/observability/spans

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

## Search span evaluations {#operation-search_span_evaluations_v1_observability_spans_evaluations_search_post}

`POST /v1/observability/spans/evaluations/search`

- Operation id: `search_span_evaluations_v1_observability_spans_evaluations_search_post`
- Tag: beta/observability/spans

### Parameters

- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)
- `page_size` (integer, optional, in query)
- `cursor` (string or null, optional, in query)

### Request body

`application/json` (required), schema `SpanEvaluationsRequest`

- `search_expression` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema GetSpanEvaluations)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Search latest span evaluations {#operation-search_latest_span_evaluations_v1_observability_spans_evaluations_search_latest_post}

`POST /v1/observability/spans/evaluations/search/latest`

- Operation id: `search_latest_span_evaluations_v1_observability_spans_evaluations_search_latest_post`
- Tag: beta/observability/spans

### Parameters

- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)
- `page_size` (integer, optional, in query)
- `cursor` (string or null, optional, in query)

### Request body

`application/json` (required), schema `SpanEvaluationsRequest`

- `search_expression` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema GetSpanEvaluations)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get span field definitions {#operation-get_span_fields_v1_observability_spans_fields_get}

`GET /v1/observability/spans/fields`

- Operation id: `get_span_fields_v1_observability_spans_fields_get`
- Tag: beta/observability/spans

### Responses

- `200` — Successful Response (application/json, schema GetSpanFields)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get span evaluation field definitions {#operation-get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get}

`GET /v1/observability/spans/evaluations/fields`

- Operation id: `get_span_evaluation_fields_v1_observability_spans_evaluations_fields_get`
- Tag: beta/observability/spans

### Responses

- `200` — Successful Response (application/json, schema GetSpanEvaluationFields)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get options for a span field {#operation-get_span_field_options_v1_observability_spans_fields_field_name_options_get}

`GET /v1/observability/spans/fields/{field_name}/options`

- Operation id: `get_span_field_options_v1_observability_spans_fields__field_name__options_get`
- Tag: beta/observability/spans

### Parameters

- `field_name` (string, required, in path)
- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema GetSpanFieldOptions)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get options for a span evaluation field {#operation-get_span_evaluation_field_options_v1_observability_spans_evaluations_fields_field_name_options_get}

`GET /v1/observability/spans/evaluations/fields/{field_name}/options`

- Operation id: `get_span_evaluation_field_options_v1_observability_spans_evaluations_fields__field_name__options_get`
- Tag: beta/observability/spans

### Parameters

- `field_name` (string, required, in path)
- `from` (string (date-time) or null, optional, in query)
- `to` (string (date-time) or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema GetSpanEvaluationFieldOptions)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)
