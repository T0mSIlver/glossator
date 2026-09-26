---
url: https://docs.mistral.ai/api/endpoint/beta/rag/managed_indexes
title: Beta Rag Managed Indexes API
breadcrumbs: [API, Beta Rag Managed Indexes]
kind: api
locale: en
source_path: openapi.yaml
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
openapi_md5: 71b15b9981e95fd9c3ab90aa80f2d1b6
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Rag Managed Indexes API

Reference for the Beta Rag Managed Indexes endpoints of the Mistral API, generated from the OpenAPI specification.

## List managed indexes {#operation-list_indexes_v1_rag_managed_indexes_get}

`GET /v1/rag/managed_indexes`

Lists all managed search indexes for the current workspace.

- Operation id: `list_indexes_v1_rag_managed_indexes_get`
- Tag: beta/rag/managed_indexes

### Parameters

- `page_size` (integer, optional, in query) — Maximum number of indexes to return
- `page_token` (string or null, optional, in query) — Cursor returned as next_page_token by the previous page

### Responses

- `200` — Successful Response (application/json, schema ListManagedIndexesResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create a managed index {#operation-create_index_v1_rag_managed_indexes_post}

`POST /v1/rag/managed_indexes`

Reserves a managed search index and starts asynchronous backing-table provisioning. Poll the returned Location until status is ready or failed.

- Operation id: `create_index_v1_rag_managed_indexes_post`
- Tag: beta/rag/managed_indexes

### Request body

`application/json` (required), schema `CreateManagedIndexRequest`

- `name` (string, required)
- `schema` (ManagedIndexFields, optional)
  - `document_fields` (object, optional)
  - `chunk_fields` (object, optional)
- `config` (ManagedIndexConfig, required)
  - `embedding` (object, required)
    - one of 2 (oneOf):
      - MistralEmbeddingModel
      - CustomEmbeddingModel

### Responses

- `202` — Index reserved and queued for provisioning (application/json, schema ManagedIndexResponse)
- `409` — An index with the same name already exists
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get a managed index {#operation-get_index_v1_rag_managed_indexes_index_name_get}

`GET /v1/rag/managed_indexes/{index_name}`

Returns the managed search index with the given name.

- Operation id: `get_index_v1_rag_managed_indexes__index_name__get`
- Tag: beta/rag/managed_indexes

### Parameters

- `index_name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema ManagedIndexResponse)
- `404` — Index not found
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update a managed index schema {#operation-update_index_v1_rag_managed_indexes_index_name_put}

`PUT /v1/rag/managed_indexes/{index_name}`

Records a new schema for the managed search index and applies it asynchronously. The index keeps serving its current schema until the new one is on disk; poll it until status is ready. Additive only: the new schema must keep every field the current one has.

- Operation id: `update_index_v1_rag_managed_indexes__index_name__put`
- Tag: beta/rag/managed_indexes

### Parameters

- `index_name` (string, required, in path)

### Request body

`application/json` (required), schema `UpdateManagedIndexRequest`

- `schema` (ManagedIndexFields, required)
  - `document_fields` (object, optional)
  - `chunk_fields` (object, optional)

### Responses

- `202` — Schema recorded and queued (application/json, schema ManagedIndexResponse)
- `404` — Index not found
- `409` — Index is not ready, or another update won the race
- `422` — The change cannot be applied to an existing index

## Delete a managed index {#operation-delete_index_v1_rag_managed_indexes_index_name_delete}

`DELETE /v1/rag/managed_indexes/{index_name}`

Marks the managed search index for deletion and returns it with status deleting. The backing table is dropped asynchronously; poll the index until it returns 404.

- Operation id: `delete_index_v1_rag_managed_indexes__index_name__delete`
- Tag: beta/rag/managed_indexes

### Parameters

- `index_name` (string, required, in path)

### Responses

- `202` — Index marked for deletion (application/json, schema DeleteManagedIndexResponse)
- `404` — Index not found
- `409` — Index is still provisioning
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Ingest documents into a managed index {#operation-ingest_documents_v1_rag_managed_indexes_index_name_documents_post}

`POST /v1/rag/managed_indexes/{index_name}/documents`

Validates and persists documents. Always returns 200; each document is reported as accepted or rejected in the response body.

- Operation id: `ingest_documents_v1_rag_managed_indexes__index_name__documents_post`
- Tag: beta/rag/managed_indexes

### Parameters

- `index_name` (string, required, in path)

### Request body

`application/json` (required), schema `IngestDocumentsRequest`

- `documents` (array of object, required)

### Responses

- `200` — Successful Response (application/json, schema IngestDocumentsResponse)
- `404` — Index not found
- `409` — Index is not ready for ingestion
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete documents from a managed index {#operation-delete_documents_v1_rag_managed_indexes_index_name_documents_delete}

`DELETE /v1/rag/managed_indexes/{index_name}/documents`

Deletes the given documents by id. Returns the ids actually removed and, in `missing`, any requested ids that were not present.

- Operation id: `delete_documents_v1_rag_managed_indexes__index_name__documents_delete`
- Tag: beta/rag/managed_indexes

### Parameters

- `index_name` (string, required, in path)

### Request body

`application/json` (required), schema `DeleteDocumentsRequest`

- `document_ids` (array of string, required)

### Responses

- `200` — Successful Response (application/json, schema DeleteDocumentsResponse)
- `404` — Index not found
- `409` — Index is not ready for ingestion
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Search a managed index {#operation-search_index_v1_rag_managed_indexes_index_name_search_post}

`POST /v1/rag/managed_indexes/{index_name}/search`

Runs an approximate-nearest-neighbor vector search over the index and returns matching chunks, closest-first.

- Operation id: `search_index_v1_rag_managed_indexes__index_name__search_post`
- Tag: beta/rag/managed_indexes

### Parameters

- `index_name` (string, required, in path)

### Request body

`application/json` (required), schema `SearchRequest`

- `retriever` (object, required)
  - one of 3 (oneOf):
    - KeywordRetriever
      - `top_k` (integer, optional)
      - `type` (string, optional)
      - `query` (string, required)
      - `filter` (object or null, optional)
      - `field` (string or null, optional)
    - NearestNeighbourRetriever
      - `top_k` (integer, optional)
      - `type` (string, optional)
      - `query` (string or null, optional)
      - `query_embedding` (array of number or null, optional)
      - `field` (string or null, optional)
      - `filter` (object or null, optional)
    - RRFRetriever
      - `top_k` (integer, optional)
      - `type` (string, optional)
      - `retrievers` (array of object, required)
      - `weights` (array of number or null, optional)
      - `rank_constant` (integer, optional)
      - `filter` (object or null, optional)

### Responses

- `200` — Successful Response (application/json, schema SearchResponse)
- `400` — Invalid search query (application/json)
- `404` — Index not found
- `409` — Index is not ready for search
- `500` — Search execution failed
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Navigate to adjacent chunks {#operation-navigate_index_v1_rag_managed_indexes_index_name_navigate_post}

`POST /v1/rag/managed_indexes/{index_name}/navigate`

Returns the chunks adjacent to a position within a source, in reading order. NEXT fetches chunks at or after the end offset; PREVIOUS fetches chunks before the start offset. A 200 with an empty list means the source exists but no chunk falls in the requested direction; a 404 means the source has no chunks at all.

- Operation id: `navigate_index_v1_rag_managed_indexes__index_name__navigate_post`
- Tag: beta/rag/managed_indexes

### Parameters

- `index_name` (string, required, in path)

### Request body

`application/json` (required), schema `NavigateRequest`

- `source_id` (string, required)
- `start_offset` (integer, required)
- `end_offset` (integer, required)
- `direction` (enum: 'next', 'previous', required)
- `top_k` (integer, optional)
- `content_type` (string, optional)

### Responses

- `200` — Successful Response (application/json, schema NavigationResponse)
- `404` — Index not found, or source/chunk does not exist in the index
- `409` — Index is not ready for search
- `500` — Navigation query failed during execution
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Read chunks within a span {#operation-read_index_v1_rag_managed_indexes_index_name_read_post}

`POST /v1/rag/managed_indexes/{index_name}/read`

Returns the chunks of a source whose span falls within [start_offset, end_offset). Either bound may be omitted to leave that side open. A 200 with an empty list means the source exists but no chunk falls in the range; a 404 means the source has no chunks at all.

- Operation id: `read_index_v1_rag_managed_indexes__index_name__read_post`
- Tag: beta/rag/managed_indexes

### Parameters

- `index_name` (string, required, in path)

### Request body

`application/json` (required), schema `ReadRequest`

- `source_id` (string, required)
- `start_offset` (integer or null, optional)
- `end_offset` (integer or null, optional)
- `top_k` (integer, optional)
- `content_type` (string, optional)

### Responses

- `200` — Successful Response (application/json, schema NavigationResponse)
- `404` — Index not found, or source/chunk does not exist in the index
- `409` — Index is not ready for search
- `500` — Navigation query failed during execution
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Grep for a pattern within a source {#operation-grep_index_v1_rag_managed_indexes_index_name_grep_post}

`POST /v1/rag/managed_indexes/{index_name}/grep`

Lexical substring match within a single source, in reading order. PHRASE mode matches the pattern literally (whitespace-sensitive, case-insensitive); TERM mode requires every whitespace-split token present in any order. A 200 with an empty list means the source exists but no chunk matched; a 404 means the source has no chunks at all.

- Operation id: `grep_index_v1_rag_managed_indexes__index_name__grep_post`
- Tag: beta/rag/managed_indexes

### Parameters

- `index_name` (string, required, in path)

### Request body

`application/json` (required), schema `GrepRequest`

- `source_id` (string, required)
- `pattern` (string, required)
- `mode` (enum: 'phrase', 'term', optional)
- `top_k` (integer, optional)
- `content_type` (string, optional)

### Responses

- `200` — Successful Response (application/json, schema NavigationResponse)
- `404` — Index not found, or source/chunk does not exist in the index
- `409` — Index is not ready for search
- `500` — Navigation query failed during execution
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get a single chunk by id {#operation-get_chunk_index_v1_rag_managed_indexes_index_name_chunks_chunk_id_get}

`GET /v1/rag/managed_indexes/{index_name}/chunks/{chunk_id}`

Returns a single chunk by its canonical id. A 404 means no chunk with that id exists in the index.

- Operation id: `get_chunk_index_v1_rag_managed_indexes__index_name__chunks__chunk_id__get`
- Tag: beta/rag/managed_indexes

### Parameters

- `index_name` (string, required, in path)
- `chunk_id` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema NavigationResponse)
- `404` — Index not found, or source/chunk does not exist in the index
- `409` — Index is not ready for search
- `500` — Navigation query failed during execution
- `422` — Validation Error (application/json, schema HTTPValidationError)
