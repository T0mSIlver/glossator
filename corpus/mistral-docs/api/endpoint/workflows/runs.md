---
url: https://docs.mistral.ai/api/endpoint/workflows/runs
title: Workflows Runs API
breadcrumbs: [API, Workflows Runs]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Workflows Runs API

Reference for the Workflows Runs endpoints of the Mistral API, generated from the OpenAPI specification.

## List Runs {#operation-list_runs_v1_workflows_runs_get}

`GET /v1/workflows/runs`

- Operation id: `list_runs_v1_workflows_runs_get`
- Tag: workflows/runs

### Parameters

- `workflow_identifier` (string or null, optional, in query) — Filter by workflow name or id
- `root_execution_id` (string or null, optional, in query) — Filter by root execution id; returns the whole execution tree (the root and all its descendant sub-workflows).
- `search` (string or null, optional, in query) — Search by workflow name, display name, or ID
- `status` (object, optional, in query) — Filter by workflow status
- `deployment_name` (string or null, optional, in query) — Filter by deployment name
- `sort_by` (enum: 'start_time', 'end_time', optional, in query) — Field to sort by
- `order` (enum: 'asc', 'desc', optional, in query) — Sort direction
- `start_time_after` (string (date-time) or null, optional, in query) — Include runs with start_time >= value
- `start_time_before` (string (date-time) or null, optional, in query) — Include runs with start_time <= value
- `end_time_after` (string (date-time) or null, optional, in query) — Include runs with end_time >= value. Running executions (no end_time) are excluded; use the status filter to include them.
- `end_time_before` (string (date-time) or null, optional, in query) — Include runs with end_time <= value. Running executions (no end_time) are excluded; use the status filter to include them.
- `user_id` (string or null, optional, in query) — Filter by user id. Use 'current' to filter by the authenticated user
- `workflow_tags` (array of string or null, optional, in query) — Filter to runs of workflows tagged with all listed tags (AND).
- `include_internal` (boolean, optional, in query) — Include runs of internal/technical workflows (e.g. parallel-execution)
- `page_size` (integer, optional, in query) — Number of items per page
- `next_page_token` (string or null, optional, in query) — Token for the next page of results
- `search_key` (array of string or null, optional, in query) — Filter executions by search key as repeated 'key:value' entries. Each entry matches an exact key and a similar value; multiple entries are AND'd together (max 3).

### Responses

- `200` — Successful Response (application/json, schema WorkflowExecutionListResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Run {#operation-get_run_v1_workflows_runs_run_id_get}

`GET /v1/workflows/runs/{run_id}`

- Operation id: `get_run_v1_workflows_runs__run_id__get`
- Tag: workflows/runs

### Parameters

- `run_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowExecutionResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Run History {#operation-get_run_history_v1_workflows_runs_run_id_history_get}

`GET /v1/workflows/runs/{run_id}/history`

- Operation id: `get_run_history_v1_workflows_runs__run_id__history_get`
- Tag: workflows/runs

### Parameters

- `run_id` (string (uuid), required, in path)
- `decode_payloads` (boolean, optional, in query)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)
