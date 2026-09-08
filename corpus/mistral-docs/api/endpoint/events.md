---
url: https://docs.mistral.ai/api/endpoint/events
title: Events API
breadcrumbs: [API, Events]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Events API

Reference for the Events endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Stream Events {#operation-get_stream_events_v1_workflows_events_stream_get}

`GET /v1/workflows/events/stream`

- Operation id: `get_stream_events_v1_workflows_events_stream_get`
- Tag: events

### Parameters

- `scope` (enum: 'activity', 'workflow', '*', optional, in query)
- `activity_name` (string, optional, in query)
- `activity_id` (string, optional, in query)
- `workflow_name` (string, optional, in query)
- `workflow_exec_id` (string, optional, in query)
- `root_workflow_exec_id` (string, optional, in query)
- `parent_workflow_exec_id` (string, optional, in query)
- `stream` (string, optional, in query)
- `start_seq` (integer, optional, in query)
- `metadata_filters` (object or null, optional, in query)
- `workflow_event_types` (array of WorkflowEventType or null, optional, in query)
- `last-event-id` (string or null, optional, in header)

### Responses

- `200` — Stream of Server-Sent Events (SSE) (text/event-stream)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Events {#operation-get_workflow_events_v1_workflows_events_list_get}

`GET /v1/workflows/events/list`

- Operation id: `get_workflow_events_v1_workflows_events_list_get`
- Tag: events

### Parameters

- `root_workflow_exec_id` (string or null, optional, in query) — Execution ID of the root workflow that initiated this execution chain.
- `workflow_exec_id` (string or null, optional, in query) — Execution ID of the workflow that emitted this event.
- `workflow_run_id` (string or null, optional, in query) — Run ID of the workflow that emitted this event.
- `limit` (integer, optional, in query) — Maximum number of events to return.
- `cursor` (string or null, optional, in query) — Cursor for pagination.

### Responses

- `200` — Successful Response (application/json, schema ListWorkflowEventResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
