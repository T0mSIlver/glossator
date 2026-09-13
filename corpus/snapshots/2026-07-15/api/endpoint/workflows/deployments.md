---
url: https://docs.mistral.ai/api/endpoint/workflows/deployments
title: Workflows Deployments API
breadcrumbs: [API, Workflows Deployments]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
openapi_md5: c28e3a674c73b4319d99305d173a6656
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Workflows Deployments API

Reference for the Workflows Deployments endpoints of the Mistral API, generated from the OpenAPI specification.

## List Deployments {#operation-list_deployments_v1_workflows_deployments_get}

`GET /v1/workflows/deployments`

- Operation id: `list_deployments_v1_workflows_deployments_get`
- Tag: workflows/deployments

### Parameters

- `active_only` (boolean, optional, in query)
- `is_hardened` (boolean or null, optional, in query) — Filter deployments by hardened status
- `workflow_name` (string or null, optional, in query)
- `search` (string or null, optional, in query) — Filter deployments by name or ID prefix
- `limit` (integer or null, optional, in query) — Maximum number of deployments to return
- `cursor` (string or null, optional, in query) — Cursor from a previous response for pagination
- `workspace_id` (string (uuid) or null, optional, in query) — Workspace ID to scope the request to. Defaults to the caller's context.

### Responses

- `200` — Successful Response (application/json, schema DeploymentListResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Deployment {#operation-get_deployment_v1_workflows_deployments_name_get}

`GET /v1/workflows/deployments/{name}`

- Operation id: `get_deployment_v1_workflows_deployments__name__get`
- Tag: workflows/deployments

### Parameters

- `name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema DeploymentDetailResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Deployment Logs {#operation-get_deployment_logs}

`GET /v1/workflows/deployments/{name}/logs`

Retrieve logs for a deployment (across all of its workers).

Use `after`/`before`/`order` on the first request to set the time range and sort order; for
the next pages pass the `cursor` from the previous response (it remembers the range and order).

- Operation id: `get_deployment_logs`
- Tag: workflows/deployments

### Parameters

- `name` (string, required, in path)
- `worker_name` (string or null, optional, in query) — Filter logs by worker name
- `workflow_name` (string or null, optional, in query) — Filter logs by workflow name
- `after` (string (date-time) or null, optional, in query) — Only return logs at or after this timestamp
- `before` (string (date-time) or null, optional, in query) — Only return logs before this timestamp
- `order` (enum: 'asc', 'desc', optional, in query) — First-page sort order: 'asc' (oldest first) or 'desc'. Ignored when `cursor` is set.
- `cursor` (string or null, optional, in query) — Pagination cursor from a previous response's `next_cursor`; carries the window and order
- `limit` (integer, optional, in query) — Maximum number of logs to return

### Responses

- `200` — Successful Response (application/json, schema DeploymentLogSearchResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Stream Deployment Logs {#operation-stream_deployment_logs}

`GET /v1/workflows/deployments/{name}/logs/stream`

Stream logs for a deployment (all of its workers) via SSE.

Resume cursor comes from the `Last-Event-ID` header or `last_event_id` query param (header wins)
and takes precedence over `after`; omit all to tail from the deployment start.

- Operation id: `stream_deployment_logs`
- Tag: workflows/deployments

### Parameters

- `name` (string, required, in path)
- `worker_name` (string or null, optional, in query) — Filter logs by worker name
- `workflow_name` (string or null, optional, in query) — Filter logs by workflow name
- `after` (string (date-time) or null, optional, in query) — Start a fresh stream at this timestamp (ignored when resuming via last_event_id)
- `last_event_id` (string or null, optional, in query) — Resume from this cursor (a prior response's SSE id)
- `Last-Event-ID` (string or null, optional, in header) — Resume from this cursor (a prior response's SSE id). Takes precedence over the query parameter.

### Responses

- `200` — Stream of Server-Sent Events (SSE): `log` events carry a DeploymentLogRecord; `error` events carry a StreamError payload. (text/event-stream)
- `404` — Deployment not found
- `503` — Logs backend unavailable
- `422` — Validation Error (application/json, schema HTTPValidationError)
