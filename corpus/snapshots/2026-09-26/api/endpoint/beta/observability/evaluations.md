---
url: https://docs.mistral.ai/api/endpoint/beta/observability/evaluations
title: Beta Observability Evaluations API
breadcrumbs: [API, Beta Observability Evaluations]
kind: api
locale: en
source_path: openapi.yaml
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
openapi_md5: 71b15b9981e95fd9c3ab90aa80f2d1b6
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Observability Evaluations API

Reference for the Beta Observability Evaluations endpoints of the Mistral API, generated from the OpenAPI specification.

## List worker pipeline configurations {#operation-list_pipeline_configs_v1_observability_pipeline_configs_get}

`GET /v1/observability/pipeline-configs`

- Operation id: `list_pipeline_configs_v1_observability_pipeline_configs_get`
- Tag: beta/observability/evaluations

### Parameters

- `pipeline_kind` (enum: 'detection', 'moderation', 'judge', 'export', optional, in query)
- `enabled` (boolean or null, optional, in query)
- `page_size` (integer, optional, in query)
- `page` (integer, optional, in query)
- `q` (string or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema PipelineConfigsResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Create a worker pipeline configuration {#operation-create_pipeline_config_v1_observability_pipeline_configs_post}

`POST /v1/observability/pipeline-configs`

- Operation id: `create_pipeline_config_v1_observability_pipeline_configs_post`
- Tag: beta/observability/evaluations

### Request body

`application/json` (required), schema `CreatePipelineConfigRequest`

- `name` (string, required)
- `pipeline_kind` (enum: 'detection', 'moderation', 'judge', 'export', required)
- `description` (string or null, optional)
- `selectors` (array of PipelineConfigSelector, required)
  - `source_kind` (enum: 'span', 'log', 'metric', required)
  - `filter` (string or null, optional)
- `definitions` (array of PipelineConfigDefinition, required)
  - one of 4 (anyOf):
    - DetectionDefinition
    - ModerationDefinition
    - JudgeDefinition
    - ExportDefinition
- `enabled` (boolean, optional)

### Responses

- `201` — Successful Response (application/json, schema PipelineConfig)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get a worker pipeline configuration {#operation-get_pipeline_config_v1_observability_pipeline_configs_pipeline_config_id_get}

`GET /v1/observability/pipeline-configs/{pipeline_config_id}`

- Operation id: `get_pipeline_config_v1_observability_pipeline_configs__pipeline_config_id__get`
- Tag: beta/observability/evaluations

### Parameters

- `pipeline_config_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema PipelineConfig)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Replace a worker pipeline configuration {#operation-update_pipeline_config_v1_observability_pipeline_configs_pipeline_config_id_put}

`PUT /v1/observability/pipeline-configs/{pipeline_config_id}`

- Operation id: `update_pipeline_config_v1_observability_pipeline_configs__pipeline_config_id__put`
- Tag: beta/observability/evaluations

### Parameters

- `pipeline_config_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdatePipelineConfigRequest`

- `name` (string, required)
- `pipeline_kind` (enum: 'detection', 'moderation', 'judge', 'export', required)
- `description` (string or null, optional)
- `selectors` (array of PipelineConfigSelector, required)
  - `source_kind` (enum: 'span', 'log', 'metric', required)
  - `filter` (string or null, optional)
- `definitions` (array of PipelineConfigDefinition, required)
  - one of 4 (anyOf):
    - DetectionDefinition
    - ModerationDefinition
    - JudgeDefinition
    - ExportDefinition
- `enabled` (boolean, required)

### Responses

- `200` — Successful Response (application/json, schema PipelineConfig)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Delete a worker pipeline configuration {#operation-delete_pipeline_config_v1_observability_pipeline_configs_pipeline_config_id_delete}

`DELETE /v1/observability/pipeline-configs/{pipeline_config_id}`

- Operation id: `delete_pipeline_config_v1_observability_pipeline_configs__pipeline_config_id__delete`
- Tag: beta/observability/evaluations

### Parameters

- `pipeline_config_id` (string (uuid), required, in path)

### Responses

- `204` — Successful Response
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)
