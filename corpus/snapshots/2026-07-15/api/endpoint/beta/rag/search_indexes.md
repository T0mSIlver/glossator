---
url: https://docs.mistral.ai/api/endpoint/beta/rag/search_indexes
title: Beta Rag Search Indexes API
breadcrumbs: [API, Beta Rag Search Indexes]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
openapi_md5: c28e3a674c73b4319d99305d173a6656
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

## Get Index Summary {#operation-get_index_summary_v1_rag_indexes_index_index_id_summary_field_language_get}

`GET /v1/rag/indexes/index/{index_id}/summary_field/{language}`

Retrieve the summary field for an index if it exists

- Operation id: `get_index_summary_v1_rag_indexes_index__index_id__summary_field__language__get`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)
- `language` (enum: 'en', 'fr', 'es', 'de', 'it', 'pt_br', 'pl', 'ar', 'nl', required, in path)

### Responses

- `200` — Successful Response (application/json, schema GetSummaryResponseSummary)
- `403` — Unauthorized
- `404` — Index or the summary for the given language not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Set Index Summary {#operation-set_index_summary_v1_rag_indexes_index_index_id_summary_field_language_put}

`PUT /v1/rag/indexes/index/{index_id}/summary_field/{language}`

Update the summary field for an index

- Operation id: `set_index_summary_v1_rag_indexes_index__index_id__summary_field__language__put`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)
- `language` (enum: 'en', 'fr', 'es', 'de', 'it', 'pt_br', 'pl', 'ar', 'nl', required, in path)

### Request body

`application/json` (required), schema `UpdateSummaryRequestSummary`

- `content` (string, required)
- `status` (enum: 'handwritten', 'generated_confirmed', required)
- `translated` (boolean, required)

### Responses

- `200` — Successful Response (application/json)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Generate a summary field for an index {#operation-generate_index_summary_v1_rag_indexes_index_index_id_summary_field_language_post}

`POST /v1/rag/indexes/index/{index_id}/summary_field/{language}`

Streams a summary for the index in chunks of json.

The first chunk contains metadata for the summary, the following contain
chunks of 'content' that should be joined together to form a full summary.

- Operation id: `generate_index_summary_v1_rag_indexes_index__index_id__summary_field__language__post`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)
- `language` (enum: 'en', 'fr', 'es', 'de', 'it', 'pt_br', 'pl', 'ar', 'nl', required, in path)

### Responses

- `200` — Successful Response (application/x-ndjson)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Schema Summary {#operation-get_schema_summary_v1_rag_indexes_index_index_id_schemas_schema_schema_id_summary_field_language_get}

`GET /v1/rag/indexes/index/{index_id}/schemas/schema/{schema_id}/summary_field/{language}`

Retrieve the summary field for a schema if it exists

- Operation id: `get_schema_summary_v1_rag_indexes_index__index_id__schemas_schema__schema_id__summary_field__language__get`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)
- `schema_id` (string (uuid), required, in path)
- `language` (enum: 'en', 'fr', 'es', 'de', 'it', 'pt_br', 'pl', 'ar', 'nl', required, in path)

### Responses

- `200` — Successful Response (application/json, schema GetSummaryResponseSummary)
- `403` — Unauthorized
- `404` — Index, schema or the summary for the given language not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Set Schema Summary {#operation-set_schema_summary_v1_rag_indexes_index_index_id_schemas_schema_schema_id_summary_field_language_put}

`PUT /v1/rag/indexes/index/{index_id}/schemas/schema/{schema_id}/summary_field/{language}`

Update the summary field for an index

- Operation id: `set_schema_summary_v1_rag_indexes_index__index_id__schemas_schema__schema_id__summary_field__language__put`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)
- `schema_id` (string (uuid), required, in path)
- `language` (enum: 'en', 'fr', 'es', 'de', 'it', 'pt_br', 'pl', 'ar', 'nl', required, in path)

### Request body

`application/json` (required), schema `UpdateSummaryRequestSummary`

- `content` (string, required)
- `status` (enum: 'handwritten', 'generated_confirmed', required)
- `translated` (boolean, required)

### Responses

- `200` — Successful Response (application/json)
- `403` — Unauthorized
- `404` — Index not found
- `400` — Invalid request
- `500` — Internal server error
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Generate a summary field for a schema {#operation-generate_schema_summary_post_v1_rag_indexes_index_index_id_schemas_schema_schema_id_summary_field_language_post}

`POST /v1/rag/indexes/index/{index_id}/schemas/schema/{schema_id}/summary_field/{language}`

Streams a summary for the schema in chunks of json.

The first chunk contains metadata for the summary, the following contain
chunks of 'content' that should be joined together to form a full summary.

- Operation id: `generate_schema_summary_post_v1_rag_indexes_index__index_id__schemas_schema__schema_id__summary_field__language__post`
- Tag: beta/rag/search_indexes

### Parameters

- `index_id` (string (uuid), required, in path)
- `schema_id` (string (uuid), required, in path)
- `language` (enum: 'en', 'fr', 'es', 'de', 'it', 'pt_br', 'pl', 'ar', 'nl', required, in path)

### Responses

- `200` — Successful Response (application/x-ndjson)
- `403` — Unauthorized
- `404` — Index or schema not found
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
- `404` — Index or Schema not found
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
