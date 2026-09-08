---
url: https://docs.mistral.ai/api/endpoint/beta/observability/datasets/records
title: Beta Observability Datasets Records API
breadcrumbs: [API, Beta Observability Datasets Records]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Beta Observability Datasets Records API

Reference for the Beta Observability Datasets Records endpoints of the Mistral API, generated from the OpenAPI specification.

## Get the content of a given dataset record {#operation-get_dataset_record_v1_observability_dataset_records_dataset_record_id_get}

`GET /v1/observability/dataset-records/{dataset_record_id}`

- Operation id: `get_dataset_record_v1_observability_dataset_records__dataset_record_id__get`
- Tag: beta/observability/datasets/records

### Parameters

- `dataset_record_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema DatasetRecord)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Delete a record from a dataset {#operation-delete_dataset_record_v1_observability_dataset_records_dataset_record_id_delete}

`DELETE /v1/observability/dataset-records/{dataset_record_id}`

- Operation id: `delete_dataset_record_v1_observability_dataset_records__dataset_record_id__delete`
- Tag: beta/observability/datasets/records

### Parameters

- `dataset_record_id` (string (uuid), required, in path)

### Responses

- `204` — Successful Response
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Delete multiple records from datasets {#operation-delete_dataset_records_v1_observability_dataset_records_bulk_delete_post}

`POST /v1/observability/dataset-records/bulk-delete`

- Operation id: `delete_dataset_records_v1_observability_dataset_records_bulk_delete_post`
- Tag: beta/observability/datasets/records

### Request body

`application/json` (required), schema `DeleteDatasetRecordsRequest`

- `dataset_record_ids` (array of string (uuid), required)

### Responses

- `204` — Successful Response
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Run Judge on a dataset record based on the given options {#operation-judge_dataset_record_v1_observability_dataset_records_dataset_record_id_live_judging_post}

`POST /v1/observability/dataset-records/{dataset_record_id}/live-judging`

- Operation id: `judge_dataset_record_v1_observability_dataset_records__dataset_record_id__live_judging_post`
- Tag: beta/observability/datasets/records

### Parameters

- `dataset_record_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `JudgeDatasetRecordRequest`

- `judge_definition` (CreateJudgeRequest, required)
  - `name` (string, required)
  - `description` (string, required)
  - `model_name` (string, required)
  - `output` (object, required)
    - one of (oneOf):
      - JudgeClassificationOutput
      - JudgeRegressionOutput
  - `instructions` (string, required)
  - `tools` (array of string, required)

### Responses

- `200` — Successful Response (application/json, schema JudgeOutput)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Update a dataset record payload {#operation-update_dataset_record_payload_v1_observability_dataset_records_dataset_record_id_payload_put}

`PUT /v1/observability/dataset-records/{dataset_record_id}/payload`

- Operation id: `update_dataset_record_payload_v1_observability_dataset_records__dataset_record_id__payload_put`
- Tag: beta/observability/datasets/records

### Parameters

- `dataset_record_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateDatasetRecordPayloadRequest`

- `payload` (DatasetRecordPayload, required) — Caller-authored input object stored on a dataset record.

### Responses

- `204` — Successful Response
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Update dataset record properties {#operation-update_dataset_record_properties_v1_observability_dataset_records_dataset_record_id_properties_put}

`PUT /v1/observability/dataset-records/{dataset_record_id}/properties`

- Operation id: `update_dataset_record_properties_v1_observability_dataset_records__dataset_record_id__properties_put`
- Tag: beta/observability/datasets/records

### Parameters

- `dataset_record_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateDatasetRecordPropertiesRequest`

- `properties` (object, required)

### Responses

- `204` — Successful Response
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)
