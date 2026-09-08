---
url: https://docs.mistral.ai/api/endpoint/beta/rag/search_indexes
title: Beta Rag Search Indexes API
breadcrumbs: [API, Beta Rag Search Indexes]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Rag Search Indexes API

Reference for the Beta Rag Search Indexes endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Deployment Summaries {#operation-get_deployment_summaries_v1_rag_deployments_get}

`GET /v1/rag/deployments`

Fetch all indexes available to a user

- Operation id: `get_deployment_summaries_v1_rag_deployments_get`
- Tag: beta/rag/search_indexes

### Responses

- `200` — Successful Response (application/json, schema GetDeploymentSummariesResponse)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error

## Register (or re-register) a search index {#operation-register_deployment_v1_rag_deployments_put}

`PUT /v1/rag/deployments`

- Operation id: `register_deployment_v1_rag_deployments_put`
- Tag: beta/rag/search_indexes

### Request body

`application/json` (required), schema `RegisterDeploymentRequestDeployment`

- `name` (string, required)
- `status` (enum: 'online', 'offline', optional)
- `deployment` (object, required)

### Responses

- `200` — Successful Response (application/json, schema RegisterSearchIndexResponseIndex)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Unregister Deployment {#operation-unregister_deployment_v1_rag_deployments_deployment_id_delete}

`DELETE /v1/rag/deployments/{deployment_id}`

Delete all information about a deployment

- Operation id: `unregister_deployment_v1_rag_deployments__deployment_id__delete`
- Tag: beta/rag/search_indexes

### Parameters

- `deployment_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update Index Metrics {#operation-update_index_metrics_v1_rag_deployments_deployment_id_metrics_put}

`PUT /v1/rag/deployments/{deployment_id}/metrics`

Update the metrics for a given index

- Operation id: `update_index_metrics_v1_rag_deployments__deployment_id__metrics_put`
- Tag: beta/rag/search_indexes

### Parameters

- `deployment_id` (string (uuid), required, in path)

### Request body

`application/json` (required)

- one of (anyOf):
  - UpdateMetricsRequestDeploymentMetricsOnline
    - `status` (string, required)
    - `document_count` (integer, required)
    - `index_metrics` (array of UpdateMetricsRequestIndexMetrics, required)
  - UpdateMetricsRequestDeploymentMetricsOffline
    - `status` (string, required)
    - `clear_metrics` (boolean, optional)

### Responses

- `200` — Successful Response (application/json)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `422` — Attempted to update unknown index
- `500` — Internal server error
