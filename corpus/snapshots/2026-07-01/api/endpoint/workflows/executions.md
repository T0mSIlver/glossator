---
url: https://docs.mistral.ai/api/endpoint/workflows/executions
title: Workflows Executions API
breadcrumbs: [API, Workflows Executions]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
openapi_md5: a48c7e7248a7d23ff0ece7147ffa1a80
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Workflows Executions API

Reference for the Workflows Executions endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Workflow Execution {#operation-get_workflow_execution_v1_workflows_executions_execution_id_get}

`GET /v1/workflows/executions/{execution_id}`

- Operation id: `get_workflow_execution_v1_workflows_executions__execution_id__get`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowExecutionResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Execution History {#operation-get_workflow_execution_history_v1_workflows_executions_execution_id_history_get}

`GET /v1/workflows/executions/{execution_id}/history`

- Operation id: `get_workflow_execution_history_v1_workflows_executions__execution_id__history_get`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)
- `decode_payloads` (boolean, optional, in query)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Signal Workflow Execution {#operation-signal_workflow_execution_v1_workflows_executions_execution_id_signals_post}

`POST /v1/workflows/executions/{execution_id}/signals`

- Operation id: `signal_workflow_execution_v1_workflows_executions__execution_id__signals_post`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Request body

`application/json` (required), schema `SignalInvocationBody`

- `name` (string, required) — The name of the signal to send
- `input` (object, optional) — Input data for the signal, matching its schema
  - one of 3 (anyOf):
    - NetworkEncodedInput
      - `b64payload` (string, required) — The encoded payload
      - `encoding_options` (array of EncodedPayloadOptions, optional) — The encoding of the payload
      - `empty` (boolean, optional) — Whether the payload is empty
    - object
    - null

### Responses

- `202` — Successful Response (application/json, schema SignalWorkflowResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Query Workflow Execution {#operation-query_workflow_execution_v1_workflows_executions_execution_id_queries_post}

`POST /v1/workflows/executions/{execution_id}/queries`

- Operation id: `query_workflow_execution_v1_workflows_executions__execution_id__queries_post`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Request body

`application/json` (required), schema `QueryInvocationBody`

- `name` (string, required) — The name of the query to request
- `input` (object, optional) — Input data for the query, matching its schema
  - one of 3 (anyOf):
    - NetworkEncodedInput
      - `b64payload` (string, required) — The encoded payload
      - `encoding_options` (array of EncodedPayloadOptions, optional) — The encoding of the payload
      - `empty` (boolean, optional) — Whether the payload is empty
    - object
    - null

### Responses

- `200` — Successful Response (application/json, schema QueryWorkflowResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Terminate Workflow Execution {#operation-terminate_workflow_execution_v1_workflows_executions_execution_id_terminate_post}

`POST /v1/workflows/executions/{execution_id}/terminate`

- Operation id: `terminate_workflow_execution_v1_workflows_executions__execution_id__terminate_post`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Batch Terminate Workflow Executions {#operation-batch_terminate_workflow_executions_v1_workflows_executions_terminate_post}

`POST /v1/workflows/executions/terminate`

- Operation id: `batch_terminate_workflow_executions_v1_workflows_executions_terminate_post`
- Tag: workflows/executions

### Request body

`application/json` (required), schema `BatchExecutionBody`

- `execution_ids` (array of string, required) — List of execution IDs to process

### Responses

- `200` — Successful Response (application/json, schema BatchExecutionResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Cancel Workflow Execution {#operation-cancel_workflow_execution_v1_workflows_executions_execution_id_cancel_post}

`POST /v1/workflows/executions/{execution_id}/cancel`

- Operation id: `cancel_workflow_execution_v1_workflows_executions__execution_id__cancel_post`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Batch Cancel Workflow Executions {#operation-batch_cancel_workflow_executions_v1_workflows_executions_cancel_post}

`POST /v1/workflows/executions/cancel`

- Operation id: `batch_cancel_workflow_executions_v1_workflows_executions_cancel_post`
- Tag: workflows/executions

### Request body

`application/json` (required), schema `BatchExecutionBody`

- `execution_ids` (array of string, required) — List of execution IDs to process

### Responses

- `200` — Successful Response (application/json, schema BatchExecutionResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Reset Workflow {#operation-reset_workflow_v1_workflows_executions_execution_id_reset_post}

`POST /v1/workflows/executions/{execution_id}/reset`

- Operation id: `reset_workflow_v1_workflows_executions__execution_id__reset_post`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Request body

`application/json` (required), schema `ResetInvocationBody`

- `event_id` (integer, required) — The event ID to reset the workflow execution to
- `reason` (string or null, optional) — Reason for resetting the workflow execution
- `exclude_signals` (boolean, optional) — Whether to exclude signals that happened after the reset point
- `exclude_updates` (boolean, optional) — Whether to exclude updates that happened after the reset point

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update Workflow Execution {#operation-update_workflow_execution_v1_workflows_executions_execution_id_updates_post}

`POST /v1/workflows/executions/{execution_id}/updates`

- Operation id: `update_workflow_execution_v1_workflows_executions__execution_id__updates_post`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Request body

`application/json` (required), schema `UpdateInvocationBody`

- `name` (string, required) — The name of the update to request
- `input` (object, optional) — Input data for the update, matching its schema
  - one of 3 (anyOf):
    - NetworkEncodedInput
      - `b64payload` (string, required) — The encoded payload
      - `encoding_options` (array of EncodedPayloadOptions, optional) — The encoding of the payload
      - `empty` (boolean, optional) — Whether the payload is empty
    - object
    - null

### Responses

- `200` — Successful Response (application/json, schema UpdateWorkflowResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Execution Trace Otel {#operation-get_workflow_execution_trace_otel}

`GET /v1/workflows/executions/{execution_id}/trace/otel`

- Operation id: `get_workflow_execution_trace_otel`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowExecutionTraceOTelResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Execution Trace Summary {#operation-get_workflow_execution_trace_summary}

`GET /v1/workflows/executions/{execution_id}/trace/summary`

- Operation id: `get_workflow_execution_trace_summary`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowExecutionTraceSummaryResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Execution Trace Events {#operation-get_workflow_execution_trace_events}

`GET /v1/workflows/executions/{execution_id}/trace/events`

- Operation id: `get_workflow_execution_trace_events`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)
- `merge_same_id_events` (boolean, optional, in query)
- `include_internal_events` (boolean, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema WorkflowExecutionTraceEventsResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Stream {#operation-stream_v1_workflows_executions_execution_id_stream_get}

`GET /v1/workflows/executions/{execution_id}/stream`

- Operation id: `stream_v1_workflows_executions__execution_id__stream_get`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)
- `event_source` (enum: 'DATABASE', 'LIVE', 'HYBRID', optional, in query)
- `last_event_id` (string or null, optional, in query)

### Responses

- `200` — Stream of Server-Sent Events (SSE) (text/event-stream)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Execution Logs {#operation-get_workflow_execution_logs}

`GET /v1/workflows/executions/{execution_id}/logs`

Retrieve logs for a workflow execution.

Use `after`/`before`/`order` on the first request to set the time range and sort order; for
the next pages pass the `cursor` from the previous response (it remembers the range and order).

- Operation id: `get_workflow_execution_logs`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)
- `run_id` (string (uuid) or null, optional, in query) — Filter logs by workflow run ID
- `activity_id` (string or null, optional, in query) — Filter logs by activity ID
- `after` (string (date-time) or null, optional, in query) — Only return logs at or after this timestamp
- `before` (string (date-time) or null, optional, in query) — Only return logs before this timestamp
- `order` (enum: 'asc', 'desc', optional, in query) — First-page sort order: 'asc' (oldest first) or 'desc'. Ignored when `cursor` is set.
- `cursor` (string or null, optional, in query) — Pagination cursor from a previous response's `next_cursor`; carries the window and order
- `limit` (integer, optional, in query) — Maximum number of logs to return

### Responses

- `200` — Successful Response (application/json, schema ExecutionLogSearchResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Stream Workflow Execution Logs {#operation-stream_workflow_execution_logs}

`GET /v1/workflows/executions/{execution_id}/logs/stream`

Stream logs for a workflow execution via SSE.

Resume cursor comes from the `Last-Event-ID` header or `last_event_id` query param (header wins)
and takes precedence over `after`; omit all to tail from the execution start.

- Operation id: `stream_workflow_execution_logs`
- Tag: workflows/executions

### Parameters

- `execution_id` (string, required, in path)
- `run_id` (string (uuid) or null, optional, in query) — Filter logs by workflow run ID
- `activity_id` (string or null, optional, in query) — Filter logs by activity ID
- `after` (string (date-time) or null, optional, in query) — Start a fresh stream at this timestamp (ignored when resuming via last_event_id)
- `last_event_id` (string or null, optional, in query) — Resume from this cursor (a prior response's SSE id)
- `Last-Event-ID` (string or null, optional, in header) — Resume from this cursor (a prior response's SSE id). Takes precedence over the query parameter.

### Responses

- `200` — Stream of Server-Sent Events (SSE): `log` events carry an ExecutionLogRecord; `error` events carry a StreamError payload. (text/event-stream)
- `404` — Execution not found
- `503` — Logs backend unavailable
- `422` — Validation Error (application/json, schema HTTPValidationError)
