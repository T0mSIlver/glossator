---
url: https://docs.mistral.ai/api/endpoint/beta/workflows/executions
title: Beta Workflows Executions API
breadcrumbs: [API, Beta Workflows Executions]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
openapi_md5: bdb780fc2046eadc8ab1125990abd435
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Workflows Executions API

Reference for the Beta Workflows Executions endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Workflow Execution {#operation-get_workflow_execution_v1_workflows_executions_execution_id_get}

`GET /v1/workflows/executions/{execution_id}`

- Operation id: `get_workflow_execution_v1_workflows_executions__execution_id__get`
- Tag: beta/workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowExecutionResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Execution History {#operation-get_workflow_execution_history_v1_workflows_executions_execution_id_history_get}

`GET /v1/workflows/executions/{execution_id}/history`

- Operation id: `get_workflow_execution_history_v1_workflows_executions__execution_id__history_get`
- Tag: beta/workflows/executions

### Parameters

- `execution_id` (string, required, in path)
- `decode_payloads` (boolean, optional, in query)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Signal Workflow Execution {#operation-signal_workflow_execution_v1_workflows_executions_execution_id_signals_post}

`POST /v1/workflows/executions/{execution_id}/signals`

- Operation id: `signal_workflow_execution_v1_workflows_executions__execution_id__signals_post`
- Tag: beta/workflows/executions

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
- Tag: beta/workflows/executions

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
- Tag: beta/workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Batch Terminate Workflow Executions {#operation-batch_terminate_workflow_executions_v1_workflows_executions_terminate_post}

`POST /v1/workflows/executions/terminate`

- Operation id: `batch_terminate_workflow_executions_v1_workflows_executions_terminate_post`
- Tag: beta/workflows/executions

### Request body

`application/json` (required), schema `BatchExecutionBody`

- `execution_ids` (array of string, required) — List of execution IDs to process

### Responses

- `200` — Successful Response (application/json, schema BatchExecutionResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Cancel Workflow Execution {#operation-cancel_workflow_execution_v1_workflows_executions_execution_id_cancel_post}

`POST /v1/workflows/executions/{execution_id}/cancel`

- Operation id: `cancel_workflow_execution_v1_workflows_executions__execution_id__cancel_post`
- Tag: beta/workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Batch Cancel Workflow Executions {#operation-batch_cancel_workflow_executions_v1_workflows_executions_cancel_post}

`POST /v1/workflows/executions/cancel`

- Operation id: `batch_cancel_workflow_executions_v1_workflows_executions_cancel_post`
- Tag: beta/workflows/executions

### Request body

`application/json` (required), schema `BatchExecutionBody`

- `execution_ids` (array of string, required) — List of execution IDs to process

### Responses

- `200` — Successful Response (application/json, schema BatchExecutionResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Reset Workflow {#operation-reset_workflow_v1_workflows_executions_execution_id_reset_post}

`POST /v1/workflows/executions/{execution_id}/reset`

- Operation id: `reset_workflow_v1_workflows_executions__execution_id__reset_post`
- Tag: beta/workflows/executions

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
- Tag: beta/workflows/executions

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
- Tag: beta/workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowExecutionTraceOTelResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Execution Trace Summary {#operation-get_workflow_execution_trace_summary}

`GET /v1/workflows/executions/{execution_id}/trace/summary`

- Operation id: `get_workflow_execution_trace_summary`
- Tag: beta/workflows/executions

### Parameters

- `execution_id` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowExecutionTraceSummaryResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Execution Trace Events {#operation-get_workflow_execution_trace_events}

`GET /v1/workflows/executions/{execution_id}/trace/events`

- Operation id: `get_workflow_execution_trace_events`
- Tag: beta/workflows/executions

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
- Tag: beta/workflows/executions

### Parameters

- `execution_id` (string, required, in path)
- `event_source` (enum: 'DATABASE', 'LIVE', optional, in query)
- `last_event_id` (string or null, optional, in query)

### Responses

- `200` — Stream of Server-Sent Events (SSE) (text/event-stream)
- `422` — Validation Error (application/json, schema HTTPValidationError)
