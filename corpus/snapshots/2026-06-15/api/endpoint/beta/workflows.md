---
url: https://docs.mistral.ai/api/endpoint/beta/workflows
title: Beta Workflows API
breadcrumbs: [API, Beta Workflows]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
openapi_md5: bdb780fc2046eadc8ab1125990abd435
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Workflows API

Reference for the Beta Workflows endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Workflow Registrations {#operation-get_workflow_registrations_v1_workflows_registrations_get}

`GET /v1/workflows/registrations`

- Operation id: `get_workflow_registrations_v1_workflows_registrations_get`
- Tag: beta/workflows

### Parameters

- `workflow_id` (string (uuid) or null, optional, in query) — The workflow ID to filter by
- `task_queue` (string or null, optional, in query) — The task queue to filter by
- `active_only` (boolean, optional, in query) — Whether to only return active workflows versions
- `include_shared` (boolean, optional, in query) — Whether to include shared workflow versions
- `workflow_search` (string or null, optional, in query) — The workflow name to filter by
- `archived` (boolean or null, optional, in query) — Filter by archived state. False=exclude archived, True=only archived, None=include all
- `with_workflow` (boolean, optional, in query) — Whether to include the workflow definition
- `available_in_chat_assistant` (boolean or null, optional, in query) — Whether to only return workflows compatible with chat assistant
- `limit` (integer, optional, in query) — The maximum number of workflows versions to return
- `cursor` (string (uuid) or null, optional, in query) — The cursor for pagination

### Responses

- `200` — Successful Response (application/json, schema WorkflowRegistrationListResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Execute Workflow {#operation-execute_workflow_v1_workflows_workflow_identifier_execute_post}

`POST /v1/workflows/{workflow_identifier}/execute`

- Operation id: `execute_workflow_v1_workflows__workflow_identifier__execute_post`
- Tag: beta/workflows

### Parameters

- `workflow_identifier` (string, required, in path)

### Request body

`application/json` (required), schema `WorkflowExecutionRequest`

- `execution_id` (string or null, optional) — Allows you to specify a custom execution ID. If not provided, a random ID will be generated.
- `input` (object or null, optional) — The input to the workflow. This should be a dictionary that matches the workflow's input schema.
- `encoded_input` (object or null, optional) — Encoded input to the workflow, used when payload encoding is enabled.
  - `b64payload` (string, required) — The encoded payload
  - `encoding_options` (array of EncodedPayloadOptions, optional) — The encoding of the payload
  - `empty` (boolean, optional) — Whether the payload is empty
- `wait_for_result` (boolean, optional) — If true, wait for the workflow to complete and return the result directly.
- `timeout_seconds` (number or null, optional) — Maximum time to wait for completion when wait_for_result is true.
- `custom_tracing_attributes` (object or null, optional)
- `task_queue` (string or null, optional) — Deprecated. Use deployment_name instead.
- `deployment_name` (string or null, optional) — Name of the deployment to route this execution to

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Execute Workflow Registration {#operation-execute_workflow_registration_v1_workflows_registrations_workflow_registration_id_execute_post}

`POST /v1/workflows/registrations/{workflow_registration_id}/execute`

- Operation id: `execute_workflow_registration_v1_workflows_registrations__workflow_registration_id__execute_post`
- Tag: beta/workflows
- Deprecated: yes

### Parameters

- `workflow_registration_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `WorkflowExecutionRequest`

- `execution_id` (string or null, optional) — Allows you to specify a custom execution ID. If not provided, a random ID will be generated.
- `input` (object or null, optional) — The input to the workflow. This should be a dictionary that matches the workflow's input schema.
- `encoded_input` (object or null, optional) — Encoded input to the workflow, used when payload encoding is enabled.
  - `b64payload` (string, required) — The encoded payload
  - `encoding_options` (array of EncodedPayloadOptions, optional) — The encoding of the payload
  - `empty` (boolean, optional) — Whether the payload is empty
- `wait_for_result` (boolean, optional) — If true, wait for the workflow to complete and return the result directly.
- `timeout_seconds` (number or null, optional) — Maximum time to wait for completion when wait_for_result is true.
- `custom_tracing_attributes` (object or null, optional)
- `task_queue` (string or null, optional) — Deprecated. Use deployment_name instead.
- `deployment_name` (string or null, optional) — Name of the deployment to route this execution to

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow {#operation-get_workflow_v1_workflows_workflow_identifier_get}

`GET /v1/workflows/{workflow_identifier}`

- Operation id: `get_workflow_v1_workflows__workflow_identifier__get`
- Tag: beta/workflows

### Parameters

- `workflow_identifier` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowGetResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update Workflow {#operation-update_workflow_v1_workflows_workflow_identifier_put}

`PUT /v1/workflows/{workflow_identifier}`

- Operation id: `update_workflow_v1_workflows__workflow_identifier__put`
- Tag: beta/workflows

### Parameters

- `workflow_identifier` (string, required, in path)

### Request body

`application/json` (required), schema `WorkflowUpdateRequest`

- `display_name` (string or null, optional) — New display name value
- `description` (string or null, optional) — New description value
- `available_in_chat_assistant` (boolean or null, optional) — Whether to make the workflow available in the chat assistant

### Responses

- `200` — Successful Response (application/json, schema WorkflowUpdateResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workflow Registration {#operation-get_workflow_registration_v1_workflows_registrations_workflow_registration_id_get}

`GET /v1/workflows/registrations/{workflow_registration_id}`

- Operation id: `get_workflow_registration_v1_workflows_registrations__workflow_registration_id__get`
- Tag: beta/workflows

### Parameters

- `workflow_registration_id` (string (uuid), required, in path)
- `with_workflow` (boolean, optional, in query) — Whether to include the workflow definition
- `include_shared` (boolean, optional, in query) — Whether to include shared workflow versions

### Responses

- `200` — Successful Response (application/json, schema WorkflowRegistrationGetResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Archive Workflow {#operation-archive_workflow_v1_workflows_workflow_identifier_archive_put}

`PUT /v1/workflows/{workflow_identifier}/archive`

- Operation id: `archive_workflow_v1_workflows__workflow_identifier__archive_put`
- Tag: beta/workflows

### Parameters

- `workflow_identifier` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowArchiveResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Unarchive Workflow {#operation-unarchive_workflow_v1_workflows_workflow_identifier_unarchive_put}

`PUT /v1/workflows/{workflow_identifier}/unarchive`

- Operation id: `unarchive_workflow_v1_workflows__workflow_identifier__unarchive_put`
- Tag: beta/workflows

### Parameters

- `workflow_identifier` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema WorkflowUnarchiveResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
