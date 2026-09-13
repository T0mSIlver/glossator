---
url: https://docs.mistral.ai/api/endpoint/beta/workflows/runs
title: Beta Workflows Runs API
breadcrumbs: [API, Beta Workflows Runs]
kind: api
locale: en
source_path: openapi.yaml
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
openapi_md5: 3c3c0d6b147730e71376c46aaca996cc
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Workflows Runs API

Reference for the Beta Workflows Runs endpoints of the Mistral API, generated from the OpenAPI specification.

## List Runs {#operation-list_runs_v1_workflows_runs_get}

`GET /v1/workflows/runs`

- Operation id: `list_runs_v1_workflows_runs_get`
- Tag: beta/workflows/runs

### Parameters

- `workflow_identifier` (string or null, optional, in query) — Filter by workflow name or id
- `search` (string or null, optional, in query) — Search by workflow name, display name or id
- `status` (object, optional, in query) — Filter by workflow status
- `page_size` (integer, optional, in query) — Number of items per page
- `next_page_token` (string or null, optional, in query) — Token for the next page of results

### Responses

- `200` — Successful Response (application/json, schema WorkflowExecutionListResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Run {#operation-get_run_v1_workflows_runs_run_id_get}

`GET /v1/workflows/runs/{run_id}`

- Operation id: `get_run_v1_workflows_runs__run_id__get`
- Tag: beta/workflows/runs

### Parameters

- `run_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowExecutionResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Run History {#operation-get_run_history_v1_workflows_runs_run_id_history_get}

`GET /v1/workflows/runs/{run_id}/history`

- Operation id: `get_run_history_v1_workflows_runs__run_id__history_get`
- Tag: beta/workflows/runs

### Parameters

- `run_id` (string (uuid), required, in path)
- `decode_payloads` (boolean, optional, in query)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)
