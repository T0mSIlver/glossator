---
url: https://docs.mistral.ai/api/endpoint/beta/observability/judges
title: Beta Observability Judges API
breadcrumbs: [API, Beta Observability Judges]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Observability Judges API

Reference for the Beta Observability Judges endpoints of the Mistral API, generated from the OpenAPI specification.

## Get judges with optional filtering and search {#operation-get_judges_v1_observability_judges_get}

`GET /v1/observability/judges`

- Operation id: `get_judges_v1_observability_judges_get`
- Tag: beta/observability/judges

### Parameters

- `type_filter` (array of JudgeOutputType or null, optional, in query) — Filter by judge output types
- `model_filter` (array of string or null, optional, in query) — Filter by model names
- `page_size` (integer, optional, in query)
- `page` (integer, optional, in query)
- `q` (string or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema ListJudgesResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Create a new judge {#operation-create_judge_v1_observability_judges_post}

`POST /v1/observability/judges`

- Operation id: `create_judge_v1_observability_judges_post`
- Tag: beta/observability/judges

### Request body

`application/json` (required), schema `CreateJudgeRequest`

- `name` (string, required)
- `description` (string, required)
- `model_name` (string, required)
- `output` (object, required)
  - one of 2 (oneOf):
    - JudgeClassificationOutput
      - `type` (string, optional)
      - `options` (array of JudgeClassificationOutputOption, required)
    - JudgeRegressionOutput
      - `type` (string, optional)
      - `min` (number, optional)
      - `min_description` (string, required)
      - `max` (number, optional)
      - `max_description` (string, required)
- `instructions` (string, required)
- `tools` (array of string, required)

### Responses

- `201` — Successful Response (application/json, schema Judge)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get judge by id {#operation-get_judge_by_id_v1_observability_judges_judge_id_get}

`GET /v1/observability/judges/{judge_id}`

- Operation id: `get_judge_by_id_v1_observability_judges__judge_id__get`
- Tag: beta/observability/judges

### Parameters

- `judge_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema Judge)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Update a judge {#operation-update_judge_v1_observability_judges_judge_id_put}

`PUT /v1/observability/judges/{judge_id}`

- Operation id: `update_judge_v1_observability_judges__judge_id__put`
- Tag: beta/observability/judges

### Parameters

- `judge_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateJudgeRequest`

- `name` (string, required)
- `description` (string, required)
- `model_name` (string, required)
- `output` (object, required)
  - one of 2 (oneOf):
    - JudgeClassificationOutput
      - `type` (string, optional)
      - `options` (array of JudgeClassificationOutputOption, required)
    - JudgeRegressionOutput
      - `type` (string, optional)
      - `min` (number, optional)
      - `min_description` (string, required)
      - `max` (number, optional)
      - `max_description` (string, required)
- `instructions` (string, required)
- `tools` (array of string, required)

### Responses

- `204` — Successful Response
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Delete a judge {#operation-delete_judge_v1_observability_judges_judge_id_delete}

`DELETE /v1/observability/judges/{judge_id}`

- Operation id: `delete_judge_v1_observability_judges__judge_id__delete`
- Tag: beta/observability/judges

### Parameters

- `judge_id` (string (uuid), required, in path)

### Responses

- `204` — Successful Response
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Run a saved judge on a conversation {#operation-judge_conversation_v1_observability_judges_judge_id_live_judging_post}

`POST /v1/observability/judges/{judge_id}/live-judging`

- Operation id: `judge_conversation_v1_observability_judges__judge_id__live_judging_post`
- Tag: beta/observability/judges

### Parameters

- `judge_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `JudgeConversationRequest`

- `messages` (array of object, required)
- `properties` (object or null, optional)

### Responses

- `200` — Successful Response (application/json, schema JudgeOutput)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)
