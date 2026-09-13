---
url: https://docs.mistral.ai/api/endpoint/beta/rag/search_indexes
title: Beta Rag Search Indexes API
breadcrumbs: [API, Beta Rag Search Indexes]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
openapi_md5: a48c7e7248a7d23ff0ece7147ffa1a80
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Rag Search Indexes API

Reference for the Beta Rag Search Indexes endpoints of the Mistral API, generated from the OpenAPI specification.

## Register (or re-register) a search index {#operation-register_search_index_v1_rag_indexes_put}

`PUT /v1/rag/indexes`

- Operation id: `register_search_index_v1_rag_indexes_put`
- Tag: beta/rag/search_indexes

### Request body

`application/json` (required), schema `RegisterSearchIndexRequestIndex`

- `name` (string, required)
- `status` (enum: 'online', 'offline', optional)
- `index` (object, required)

### Responses

- `200` — Successful Response (application/json, schema RegisterSearchIndexResponseIndex)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Index Summaries {#operation-get_index_summaries_v1_rag_indexes_summary_get}

`GET /v1/rag/indexes/summary`

Fetch summary view of all indexes available to a user

- Operation id: `get_index_summaries_v1_rag_indexes_summary_get`
- Tag: beta/rag/search_indexes

### Responses

- `200` — Successful Response (application/json)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error

## Unregister Search Index {#operation-unregister_search_index_v1_rag_indexes_index_index_id_delete}

`DELETE /v1/rag/indexes/index/{index_id}`

Delete all information about an index

- Operation id: `unregister_search_index_v1_rag_indexes_index__index_id__delete`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update Index Metrics {#operation-update_index_metrics_v1_rag_indexes_index_index_id_metrics_put}

`PUT /v1/rag/indexes/index/{index_id}/metrics`

Update the metrics for a given index

- Operation id: `update_index_metrics_v1_rag_indexes_index__index_id__metrics_put`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)

### Request body

`application/json` (required)

- one of 2 (anyOf):
  - UpdateIndexMetricsRequestIndexMetricsOnline
    - `status` (string, required)
    - `document_count` (integer, required)
    - `schema_metrics` (array of UpdateIndexMetricsRequestSchemaMetrics, required)
  - UpdateIndexMetricsRequestIndexMetricsOffline
    - `status` (string, required)
    - `clear_metrics` (boolean, optional)

### Responses

- `200` — Successful Response (application/json)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `422` — Unknown schema update
- `500` — Internal server error

## Get Index Details {#operation-get_index_details_v1_rag_indexes_index_index_id_detail_get}

`GET /v1/rag/indexes/index/{index_id}/detail`

Get a detailed view of the stored data for a single index

- Operation id: `get_index_details_v1_rag_indexes_index__index_id__detail_get`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema GetSearchIndexDetailResponseIndex)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Set Index Summary {#operation-set_index_summary_v1_rag_indexes_index_index_id_summary_field_put}

`PUT /v1/rag/indexes/index/{index_id}/summary_field`

Update the summary field for an index

- Operation id: `set_index_summary_v1_rag_indexes_index__index_id__summary_field_put`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateIndexSummaryRequestSummary`

- `summary` (string, required)

### Responses

- `200` — Successful Response (application/json)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Index Schema Detail {#operation-get_index_schema_detail_v1_rag_indexes_index_index_id_schemas_schema_schema_id_detail_get}

`GET /v1/rag/indexes/index/{index_id}/schemas/schema/{schema_id}/detail`

Get a detailed view of the stored information for a schema

- Operation id: `get_index_schema_detail_v1_rag_indexes_index__index_id__schemas_schema__schema_id__detail_get`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)
- `schema_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema GetSearchIndexSchemaDetailResponseSchemaModel)
- `403` — Unauthorized
- `404` — Schema not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Set Schema Summary {#operation-set_schema_summary_v1_rag_indexes_index_index_id_schemas_schema_schema_id_summary_field_put}

`PUT /v1/rag/indexes/index/{index_id}/schemas/schema/{schema_id}/summary_field`

Update the summary field for an index

- Operation id: `set_schema_summary_v1_rag_indexes_index__index_id__schemas_schema__schema_id__summary_field_put`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)
- `schema_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateSchemaSummaryRequestSummary`

- `summary` (string, required)

### Responses

- `200` — Successful Response (application/json)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Index Schema File {#operation-get_index_schema_file_v1_rag_indexes_index_index_id_schemas_schema_schema_id_file_get}

`GET /v1/rag/indexes/index/{index_id}/schemas/schema/{schema_id}/file`

- Operation id: `get_index_schema_file_v1_rag_indexes_index__index_id__schemas_schema__schema_id__file_get`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)
- `schema_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema GetSearchIndexSchemaSDFileResponseSDFile)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Document Lookup {#operation-document_lookup_v1_rag_indexes_index_index_id_schemas_schema_schema_id_retrievables_retrievable_document_id_get}

`GET /v1/rag/indexes/index/{index_id}/schemas/schema/{schema_id}/retrievables/retrievable/{document_id}`

Fetch stored information about a retrievable element stored in an index

- Operation id: `document_lookup_v1_rag_indexes_index__index_id__schemas_schema__schema_id__retrievables_retrievable__document_id__get`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)
- `schema_id` (string (uuid), required, in path)
- `document_id` (string, required, in path) — the native ID in the underlying index

### Responses

- `200` — Successful Response (application/json, schema VespaGetRetrievableResponseRetrievable)
- `403` — Unauthorized
- `404` — Index or schema not found
- `400` — Invalid request
- `412` — The server is missing information required to perform a document lookup
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Document Fetch {#operation-document_fetch_v1_rag_indexes_index_index_id_schemas_schema_schema_id_retrievables_get}

`GET /v1/rag/indexes/index/{index_id}/schemas/schema/{schema_id}/retrievables`

Fetch a few stored retrievable elements from the index/schema

- Operation id: `document_fetch_v1_rag_indexes_index__index_id__schemas_schema__schema_id__retrievables_get`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)
- `schema_id` (string (uuid), required, in path)
- `group_id` (string or null, optional, in query) — Only retrieve from this group

### Responses

- `200` — Successful Response (application/json)
- `403` — Unauthorized
- `404` — Index or schema not found
- `400` — Invalid request
- `412` — The server is missing information required to perform a lookup
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)
