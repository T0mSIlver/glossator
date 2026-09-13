---
url: https://docs.mistral.ai/api/endpoint/beta/observability/datasets
title: Beta Observability Datasets API
breadcrumbs: [API, Beta Observability Datasets]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
openapi_md5: a48c7e7248a7d23ff0ece7147ffa1a80
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Observability Datasets API

Reference for the Beta Observability Datasets endpoints of the Mistral API, generated from the OpenAPI specification.

## List existing datasets {#operation-get_datasets_v1_observability_datasets_get}

`GET /v1/observability/datasets`

- Operation id: `get_datasets_v1_observability_datasets_get`
- Tag: beta/observability/datasets

### Parameters

- `page_size` (integer, optional, in query)
- `page` (integer, optional, in query)
- `q` (string or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema ListDatasetsResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Create a new empty dataset {#operation-create_dataset_v1_observability_datasets_post}

`POST /v1/observability/datasets`

- Operation id: `create_dataset_v1_observability_datasets_post`
- Tag: beta/observability/datasets

### Request body

`application/json` (required), schema `CreateDatasetRequest`

- `name` (string, required)
- `description` (string, required)

### Responses

- `201` — Successful Response (application/json, schema Dataset)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get dataset by id {#operation-get_dataset_by_id_v1_observability_datasets_dataset_id_get}

`GET /v1/observability/datasets/{dataset_id}`

- Operation id: `get_dataset_by_id_v1_observability_datasets__dataset_id__get`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema DatasetPreview)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Delete a dataset {#operation-delete_dataset_v1_observability_datasets_dataset_id_delete}

`DELETE /v1/observability/datasets/{dataset_id}`

- Operation id: `delete_dataset_v1_observability_datasets__dataset_id__delete`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)

### Responses

- `204` — Successful Response
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Patch dataset {#operation-update_dataset_v1_observability_datasets_dataset_id_patch}

`PATCH /v1/observability/datasets/{dataset_id}`

- Operation id: `update_dataset_v1_observability_datasets__dataset_id__patch`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateDatasetRequest`

- `name` (string or null, optional)
- `description` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema DatasetPreview)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## List existing records in the dataset {#operation-get_dataset_records_v1_observability_datasets_dataset_id_records_get}

`GET /v1/observability/datasets/{dataset_id}/records`

- Operation id: `get_dataset_records_v1_observability_datasets__dataset_id__records_get`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)
- `page_size` (integer, optional, in query)
- `page` (integer, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema ListDatasetRecordsResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Add a conversation to the dataset {#operation-create_dataset_record_v1_observability_datasets_dataset_id_records_post}

`POST /v1/observability/datasets/{dataset_id}/records`

- Operation id: `create_dataset_record_v1_observability_datasets__dataset_id__records_post`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `CreateDatasetRecordRequest`

- `payload` (ConversationPayload, required)
  - `messages` (array of object, required)
- `properties` (object, required)

### Responses

- `201` — Successful Response (application/json, schema DatasetRecord)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Populate the dataset with a campaign {#operation-post_dataset_records_from_campaign_v1_observability_datasets_dataset_id_imports_from_campaign_post}

`POST /v1/observability/datasets/{dataset_id}/imports/from-campaign`

- Operation id: `post_dataset_records_from_campaign_v1_observability_datasets__dataset_id__imports_from_campaign_post`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `ImportDatasetFromCampaignRequest`

- `campaign_id` (string (uuid), required)

### Responses

- `202` — Successful Response (application/json, schema DatasetImportTask)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Populate the dataset with samples from the explorer {#operation-post_dataset_records_from_explorer_v1_observability_datasets_dataset_id_imports_from_explorer_post}

`POST /v1/observability/datasets/{dataset_id}/imports/from-explorer`

- Operation id: `post_dataset_records_from_explorer_v1_observability_datasets__dataset_id__imports_from_explorer_post`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `ImportDatasetFromExplorerRequest`

- `completion_event_ids` (array of string, required)

### Responses

- `202` — Successful Response (application/json, schema DatasetImportTask)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Populate the dataset with samples from an uploaded file {#operation-post_dataset_records_from_file_v1_observability_datasets_dataset_id_imports_from_file_post}

`POST /v1/observability/datasets/{dataset_id}/imports/from-file`

- Operation id: `post_dataset_records_from_file_v1_observability_datasets__dataset_id__imports_from_file_post`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `ImportDatasetFromFileRequest`

- `file_id` (string, required)

### Responses

- `202` — Successful Response (application/json, schema DatasetImportTask)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Populate the dataset with samples from the playground {#operation-post_dataset_records_from_playground_v1_observability_datasets_dataset_id_imports_from_playground_post}

`POST /v1/observability/datasets/{dataset_id}/imports/from-playground`

- Operation id: `post_dataset_records_from_playground_v1_observability_datasets__dataset_id__imports_from_playground_post`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `ImportDatasetFromPlaygroundRequest`

- `conversation_ids` (array of string, required)

### Responses

- `202` — Successful Response (application/json, schema DatasetImportTask)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Populate the dataset with samples from another dataset {#operation-post_dataset_records_from_dataset_v1_observability_datasets_dataset_id_imports_from_dataset_post}

`POST /v1/observability/datasets/{dataset_id}/imports/from-dataset`

- Operation id: `post_dataset_records_from_dataset_v1_observability_datasets__dataset_id__imports_from_dataset_post`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `ImportDatasetFromDatasetRequest`

- `dataset_record_ids` (array of string (uuid), required)

### Responses

- `202` — Successful Response (application/json, schema DatasetImportTask)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Export to the Files API and retrieve presigned URL to download the resulting JSONL file {#operation-export_dataset_to_jsonl_v1_observability_datasets_dataset_id_exports_to_jsonl_get}

`GET /v1/observability/datasets/{dataset_id}/exports/to-jsonl`

- Operation id: `export_dataset_to_jsonl_v1_observability_datasets__dataset_id__exports_to_jsonl_get`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema ExportDatasetResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get status of a dataset import task {#operation-get_dataset_import_task_v1_observability_datasets_dataset_id_tasks_task_id_get}

`GET /v1/observability/datasets/{dataset_id}/tasks/{task_id}`

- Operation id: `get_dataset_import_task_v1_observability_datasets__dataset_id__tasks__task_id__get`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)
- `task_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema DatasetImportTask)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## List import tasks for the given dataset {#operation-get_dataset_import_tasks_v1_observability_datasets_dataset_id_tasks_get}

`GET /v1/observability/datasets/{dataset_id}/tasks`

- Operation id: `get_dataset_import_tasks_v1_observability_datasets__dataset_id__tasks_get`
- Tag: beta/observability/datasets

### Parameters

- `dataset_id` (string (uuid), required, in path)
- `page_size` (integer, optional, in query)
- `page` (integer, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema ListDatasetImportTasksResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)
