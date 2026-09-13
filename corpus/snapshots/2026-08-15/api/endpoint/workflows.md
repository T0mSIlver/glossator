---
url: https://docs.mistral.ai/api/endpoint/workflows
title: Workflows API
breadcrumbs: [API, Workflows]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Workflows API

Reference for the Workflows endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Workflows {#operation-get_workflows_v1_workflows_get}

`GET /v1/workflows`

- Operation id: `get_workflows_v1_workflows_get`
- Tag: workflows

### Parameters

- `status` (object, optional, in query) — Filter by workflow status
- `include_shared` (boolean, optional, in query) — Whether to include shared workflows
- `available_in_chat_assistant` (boolean or null, optional, in query) — Whether to only return workflows available in chat assistant
- `deployment_name` (array of string or null, optional, in query) — Filter by deployment name(s)
- `deployment_status` (enum: 'active', 'inactive', optional, in query) — Filter by deployment activity. active=only active, inactive=only inactive, None=no filter
- `archived` (boolean or null, optional, in query) — Filter by archived state. False=exclude archived, True=only archived, None=include all
- `tags` (array of string or null, optional, in query) — Filter to workflows tagged with all listed tags (AND).
- `sort_by` (string or null, optional, in query) — Field to sort by
- `order` (enum: 'asc', 'desc', optional, in query) — Sort direction
- `cursor` (string or null, optional, in query) — The cursor for pagination
- `limit` (integer, optional, in query) — The maximum number of workflows to return
- `active_only` (boolean, optional, in query) — Deprecated: use deployment_status instead
- `search` (string or null, optional, in query) — Fuzzy search query for workflow name, display name, description, or ID

### Responses

- `200` — Successful Response (application/json, schema WorkflowListResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Registrations {#operation-get_workflow_registrations_v1_workflows_registrations_get}

`GET /v1/workflows/registrations`

- Operation id: `get_workflow_registrations_v1_workflows_registrations_get`
- Tag: workflows

### Parameters

- `workflow_id` (string (uuid) or null, optional, in query) — The workflow ID to filter by
- `task_queue` (string or null, optional, in query) — The task queue to filter by
- `active_only` (boolean, optional, in query) — Whether to only return active workflows versions
- `include_shared` (boolean, optional, in query) — Whether to include shared workflow versions
- `workflow_search` (string or null, optional, in query) — The workflow name to filter by
- `archived` (boolean or null, optional, in query) — Filter by archived state. False=exclude archived, True=only archived, None=include all
- `with_workflow` (boolean, optional, in query) — Whether to include the workflow definition
- `available_in_chat_assistant` (boolean or null, optional, in query) — Whether to only return workflows available in chat assistant
- `limit` (integer, optional, in query) — The maximum number of workflows versions to return
- `cursor` (string or null, optional, in query) — The cursor for pagination

### Responses

- `200` — Successful Response (application/json, schema WorkflowRegistrationListResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Execute Workflow {#operation-execute_workflow_v1_workflows_workflow_identifier_execute_post}

`POST /v1/workflows/{workflow_identifier}/execute`

- Operation id: `execute_workflow_v1_workflows__workflow_identifier__execute_post`
- Tag: workflows

### Parameters

- `workflow_identifier` (string, required, in path)

### Request body

`application/json` (required), schema `WorkflowExecutionRequest`

- `execution_id` (string or null, optional) — Allows you to specify a custom execution ID. If not provided, a random ID will be generated.
- `input` (object, optional) — The input to the workflow. This should be a dictionary or a BaseModel that matches the workflow's input schema.
  - one of 3 (anyOf):
    - object
    - object
    - null
- `wait_for_result` (boolean, optional) — If true, wait for the workflow to complete and return the result directly.
- `timeout_seconds` (number or null, optional) — Maximum time to wait for completion when wait_for_result is true.
- `custom_tracing_attributes` (object or null, optional)
- `force_new_trace` (boolean, optional) — If true, ignore the caller's trace context and start a new, independent trace for this execution instead of joining the caller's trace.
- `extensions` (object or null, optional) — Plugin-specific data to propagate into WorkflowContext.extensions at execution time.
- `task_queue` (string or null, optional) — Deprecated. Use deployment_name instead.
- `deployment_name` (string or null, optional) — Name of the deployment to route this execution to

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Execute Workflow Registration {#operation-execute_workflow_registration_v1_workflows_registrations_workflow_registration_id_execute_post}

`POST /v1/workflows/registrations/{workflow_registration_id}/execute`

- Operation id: `execute_workflow_registration_v1_workflows_registrations__workflow_registration_id__execute_post`
- Tag: workflows
- Deprecated: yes

### Parameters

- `workflow_registration_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `WorkflowExecutionRequest`

- `execution_id` (string or null, optional) — Allows you to specify a custom execution ID. If not provided, a random ID will be generated.
- `input` (object, optional) — The input to the workflow. This should be a dictionary or a BaseModel that matches the workflow's input schema.
  - one of 3 (anyOf):
    - object
    - object
    - null
- `wait_for_result` (boolean, optional) — If true, wait for the workflow to complete and return the result directly.
- `timeout_seconds` (number or null, optional) — Maximum time to wait for completion when wait_for_result is true.
- `custom_tracing_attributes` (object or null, optional)
- `force_new_trace` (boolean, optional) — If true, ignore the caller's trace context and start a new, independent trace for this execution instead of joining the caller's trace.
- `extensions` (object or null, optional) — Plugin-specific data to propagate into WorkflowContext.extensions at execution time.
- `task_queue` (string or null, optional) — Deprecated. Use deployment_name instead.
- `deployment_name` (string or null, optional) — Name of the deployment to route this execution to

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow {#operation-get_workflow_v1_workflows_workflow_identifier_get}

`GET /v1/workflows/{workflow_identifier}`

- Operation id: `get_workflow_v1_workflows__workflow_identifier__get`
- Tag: workflows

### Parameters

- `workflow_identifier` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowGetResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update Workflow {#operation-update_workflow_v1_workflows_workflow_identifier_put}

`PUT /v1/workflows/{workflow_identifier}`

- Operation id: `update_workflow_v1_workflows__workflow_identifier__put`
- Tag: workflows

### Parameters

- `workflow_identifier` (string, required, in path)

### Request body

`application/json` (required), schema `WorkflowUpdateRequest`

- `display_name` (string or null, optional) — New display name value
- `description` (string or null, optional) — New description value
- `available_in_chat_assistant` (boolean or null, optional) — Whether to make the workflow available in the chat assistant
- `tags` (array of string or null, optional) — New tags. Replaces the existing tag list.

### Responses

- `200` — Successful Response (application/json, schema WorkflowUpdateResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Registration {#operation-get_workflow_registration_v1_workflows_registrations_workflow_registration_id_get}

`GET /v1/workflows/registrations/{workflow_registration_id}`

- Operation id: `get_workflow_registration_v1_workflows_registrations__workflow_registration_id__get`
- Tag: workflows

### Parameters

- `workflow_registration_id` (string (uuid), required, in path)
- `with_workflow` (boolean, optional, in query) — Whether to include the workflow definition
- `include_shared` (boolean, optional, in query) — Whether to include shared workflow versions

### Responses

- `200` — Successful Response (application/json, schema WorkflowRegistrationGetResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Bulk Archive Workflows {#operation-bulk_archive_workflows_v1_workflows_archive_put}

`PUT /v1/workflows/archive`

- Operation id: `bulk_archive_workflows_v1_workflows_archive_put`
- Tag: workflows

### Request body

`application/json` (required), schema `WorkflowBulkArchiveRequest`

- `workflow_ids` (array of string (uuid), required) — List of workflow IDs to archive

### Responses

- `200` — Successful Response (application/json, schema WorkflowBulkArchiveResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Bulk Unarchive Workflows {#operation-bulk_unarchive_workflows_v1_workflows_unarchive_put}

`PUT /v1/workflows/unarchive`

- Operation id: `bulk_unarchive_workflows_v1_workflows_unarchive_put`
- Tag: workflows

### Request body

`application/json` (required), schema `WorkflowBulkUnarchiveRequest`

- `workflow_ids` (array of string (uuid), required) — List of workflow IDs to unarchive

### Responses

- `200` — Successful Response (application/json, schema WorkflowBulkUnarchiveResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Archive Workflow {#operation-archive_workflow_v1_workflows_workflow_identifier_archive_put}

`PUT /v1/workflows/{workflow_identifier}/archive`

- Operation id: `archive_workflow_v1_workflows__workflow_identifier__archive_put`
- Tag: workflows

### Parameters

- `workflow_identifier` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowArchiveResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Unarchive Workflow {#operation-unarchive_workflow_v1_workflows_workflow_identifier_unarchive_put}

`PUT /v1/workflows/{workflow_identifier}/unarchive`

- Operation id: `unarchive_workflow_v1_workflows__workflow_identifier__unarchive_put`
- Tag: workflows

### Parameters

- `workflow_identifier` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowUnarchiveResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
