---
url: https://docs.mistral.ai/api/endpoint/workflows/deployments
title: Workflows Deployments API
breadcrumbs: [API, Workflows Deployments]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
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
- `order_by` (enum: 'updated_at', 'created_at', optional, in query) — Field to sort by. When omitted, active and managed deployments are grouped first, then sorted by created_at. When set, results are sorted purely by the specified field with no grouping.
- `order` (enum: 'asc', 'desc', optional, in query) — Sort direction. Applied to order_by when set, or within each activity group when omitted.
- `limit` (integer or null, optional, in query) — Maximum number of deployments to return
- `cursor` (string or null, optional, in query) — Cursor from a previous response for pagination
- `workspace_id` (string (uuid) or null, optional, in query) — Workspace ID to scope the request to. Defaults to the caller's context.

### Responses

- `200` — Successful Response (application/json, schema DeploymentListResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create Deployment {#operation-create_deployment_v1_workflows_deployments_post}

`POST /v1/workflows/deployments`

- Operation id: `create_deployment_v1_workflows_deployments_post`
- Tag: workflows/deployments

### Request body

`application/json` (required), schema `CreateDeploymentRequest`

- `name` (string, required)
- `spec` (DeploymentWorkerSpecInput, required)
  - `github_url` (string, required)
  - `revision` (string or null, optional)
  - `entrypoint` (string or null, optional)
  - `working_dir` (string or null, optional)
- `resources` (object or null, optional)
  - `replicas` (integer or null, optional)
  - `cpu_request` (string or null, optional)
  - `cpu_limit` (string or null, optional)
  - `memory_request` (string or null, optional)
  - `memory_limit` (string or null, optional)
- `hardened` (boolean, optional)

### Responses

- `202` — Successful Response (application/json, schema ManagedDeploymentResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Deployment {#operation-get_deployment_v1_workflows_deployments_name_get}

`GET /v1/workflows/deployments/{name}`

- Operation id: `get_deployment_v1_workflows_deployments__name__get`
- Tag: workflows/deployments

### Parameters

- `name` (string, required, in path)
- `workflow_name` (string or null, optional, in query) — Scope serving status to this workflow

### Responses

- `200` — Successful Response (application/json, schema DeploymentDetailResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete Deployment {#operation-delete_deployment_v1_workflows_deployments_name_delete}

`DELETE /v1/workflows/deployments/{name}`

- Operation id: `delete_deployment_v1_workflows_deployments__name__delete`
- Tag: workflows/deployments

### Parameters

- `name` (string, required, in path)

### Responses

- `202` — Successful Response (application/json, schema ManagedDeploymentResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update Deployment {#operation-update_deployment_v1_workflows_deployments_name_patch}

`PATCH /v1/workflows/deployments/{name}`

- Operation id: `update_deployment_v1_workflows_deployments__name__patch`
- Tag: workflows/deployments

### Parameters

- `name` (string, required, in path)

### Request body

`application/json` (required), schema `UpdateDeploymentRequest`

- `spec` (object or null, optional)
  - `github_url` (string or null, optional)
  - `revision` (string or null, optional)
  - `entrypoint` (string or null, optional)
  - `working_dir` (string or null, optional)
- `resources` (object or null, optional)
  - `replicas` (integer or null, optional)
  - `cpu_request` (string or null, optional)
  - `cpu_limit` (string or null, optional)
  - `memory_request` (string or null, optional)
  - `memory_limit` (string or null, optional)

### Responses

- `202` — Successful Response (application/json, schema ManagedDeploymentResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Stop Deployment {#operation-stop_deployment_v1_workflows_deployments_name_stop_post}

`POST /v1/workflows/deployments/{name}/stop`

- Operation id: `stop_deployment_v1_workflows_deployments__name__stop_post`
- Tag: workflows/deployments

### Parameters

- `name` (string, required, in path)

### Responses

- `202` — Successful Response (application/json, schema ManagedDeploymentResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Start Deployment {#operation-start_deployment_v1_workflows_deployments_name_start_post}

`POST /v1/workflows/deployments/{name}/start`

- Operation id: `start_deployment_v1_workflows_deployments__name__start_post`
- Tag: workflows/deployments

### Parameters

- `name` (string, required, in path)

### Responses

- `202` — Successful Response (application/json, schema ManagedDeploymentResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Restart Deployment {#operation-restart_deployment_v1_workflows_deployments_name_restart_post}

`POST /v1/workflows/deployments/{name}/restart`

- Operation id: `restart_deployment_v1_workflows_deployments__name__restart_post`
- Tag: workflows/deployments

### Parameters

- `name` (string, required, in path)

### Responses

- `202` — Successful Response (application/json, schema ManagedDeploymentResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List Deployment Workers {#operation-list_deployment_workers_v1_workflows_deployments_name_workers_get}

`GET /v1/workflows/deployments/{name}/workers`

- Operation id: `list_deployment_workers_v1_workflows_deployments__name__workers_get`
- Tag: workflows/deployments

### Parameters

- `name` (string, required, in path)
- `worker_status` (enum: 'active', 'inactive', optional, in query) — Filter by worker activity. active=only active, inactive=only inactive, None=no filter
- `limit` (integer, optional, in query) — Maximum number of workers to return
- `cursor` (string or null, optional, in query) — Cursor from a previous response's `next_cursor`. Resend `worker_status` unchanged alongside it.

### Responses

- `200` — Successful Response (application/json, schema DeploymentWorkerListResponse)
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
