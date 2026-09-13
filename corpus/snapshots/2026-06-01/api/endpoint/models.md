---
url: https://docs.mistral.ai/api/endpoint/models
title: Models API
breadcrumbs: [API, Models]
kind: api
locale: en
source_path: openapi.yaml
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
openapi_md5: 3c3c0d6b147730e71376c46aaca996cc
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Models API

Reference for the Models endpoints of the Mistral API, generated from the OpenAPI specification.

## List Models {#operation-list_models_v1_models_get}

`GET /v1/models`

List all models available to the user.

- Operation id: `list_models_v1_models_get`
- Tag: models

### Parameters

- `provider` (string or null, optional, in query)
- `model` (string or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema ModelList)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Retrieve Model {#operation-retrieve_model_v1_models_model_id_get}

`GET /v1/models/{model_id}`

Retrieve information about a model.

- Operation id: `retrieve_model_v1_models__model_id__get`
- Tag: models

### Parameters

- `model_id` (string, required, in path) — The ID of the model to retrieve.

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete Model {#operation-delete_model_v1_models_model_id_delete}

`DELETE /v1/models/{model_id}`

Delete a fine-tuned model.

- Operation id: `delete_model_v1_models__model_id__delete`
- Tag: models

### Parameters

- `model_id` (string, required, in path) — The ID of the model to delete.

### Responses

- `200` — Successful Response (application/json, schema DeleteModelOut)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update Fine Tuned Model {#operation-jobs_api_routes_fine_tuning_update_fine_tuned_model}

`PATCH /v1/fine_tuning/models/{model_id}`

Update a model name or description.

- Operation id: `jobs_api_routes_fine_tuning_update_fine_tuned_model`
- Tag: models

### Parameters

- `model_id` (string, required, in path) — The ID of the model to update.

### Request body

`application/json` (required), schema `UpdateFTModelIn`

- `name` (string or null, optional)
- `description` (string or null, optional)

### Responses

- `200` — OK (application/json)

## Archive Fine Tuned Model {#operation-jobs_api_routes_fine_tuning_archive_fine_tuned_model}

`POST /v1/fine_tuning/models/{model_id}/archive`

Archive a fine-tuned model.

- Operation id: `jobs_api_routes_fine_tuning_archive_fine_tuned_model`
- Tag: models

### Parameters

- `model_id` (string, required, in path) — The ID of the model to archive.

### Responses

- `200` — OK (application/json, schema ArchiveFTModelOut)

## Unarchive Fine Tuned Model {#operation-jobs_api_routes_fine_tuning_unarchive_fine_tuned_model}

`DELETE /v1/fine_tuning/models/{model_id}/archive`

Un-archive a fine-tuned model.

- Operation id: `jobs_api_routes_fine_tuning_unarchive_fine_tuned_model`
- Tag: models

### Parameters

- `model_id` (string, required, in path) — The ID of the model to unarchive.

### Responses

- `200` — OK (application/json, schema UnarchiveFTModelOut)
