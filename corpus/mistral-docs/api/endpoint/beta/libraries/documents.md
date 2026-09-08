---
url: https://docs.mistral.ai/api/endpoint/beta/libraries/documents
title: Beta Libraries Documents API
breadcrumbs: [API, Beta Libraries Documents]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Beta Libraries Documents API

Reference for the Beta Libraries Documents endpoints of the Mistral API, generated from the OpenAPI specification.

## List documents in a given library. {#operation-libraries_documents_list_v1}

`GET /v1/libraries/{library_id}/documents`

Given a library, lists the document that have been uploaded to that library.

- Operation id: `libraries_documents_list_v1`
- Tag: beta/libraries/documents

### Parameters

- `library_id` (string (uuid), required, in path)
- `search` (string or null, optional, in query)
- `page_size` (integer, optional, in query)
- `page` (integer, optional, in query)
- `filters_attributes` (string or null, optional, in query) — Deprecated: this parameter will be removed in a future version.
- `sort_by` (string, optional, in query)
- `sort_order` (string, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema ListDocumentsResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Upload a new document. {#operation-libraries_documents_upload_v1}

`POST /v1/libraries/{library_id}/documents`

Given a library, upload a new document to that library. It is queued for processing, it status will change it has been processed. The processing has to be completed in order be discoverable for the library search

- Operation id: `libraries_documents_upload_v1`
- Tag: beta/libraries/documents

### Parameters

- `library_id` (string (uuid), required, in path)

### Request body

`multipart/form-data` (required)

- `file` (File, required) — The File object (not file name) to be uploaded. To upload a file and specify a custom file name you should format your request as such: ```bash file=@path/to/your/file.jsonl;filename=custom_name.jsonl ``` Otherwise, you can just keep the original file name: ```bash file=@path/to/your/file.jsonl ```

### Responses

- `201` — Upload successful, returns the created document information's. (application/json, schema Document)
- `200` — A document with the same hash was found in this library. Returns the existing document. (application/json, schema Document)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Retrieve the metadata of a specific document. {#operation-libraries_documents_get_v1}

`GET /v1/libraries/{library_id}/documents/{document_id}`

Given a library and a document in this library, you can retrieve the metadata of that document.

- Operation id: `libraries_documents_get_v1`
- Tag: beta/libraries/documents

### Parameters

- `library_id` (string (uuid), required, in path)
- `document_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema Document)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update the metadata of a specific document. {#operation-libraries_documents_update_v1}

`PUT /v1/libraries/{library_id}/documents/{document_id}`

Given a library and a document in that library, update the name of that document.

- Operation id: `libraries_documents_update_v1`
- Tag: beta/libraries/documents
- Deprecated: yes

### Parameters

- `library_id` (string (uuid), required, in path)
- `document_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateDocumentRequest`

- `name` (string, optional)
- `attributes` (object or null, optional)
- `expires_at` (string (date-time) or null, optional) — If set, the document will be automatically deleted after this date.

### Responses

- `200` — Successful Response (application/json, schema Document)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete a document. {#operation-libraries_documents_delete_v1}

`DELETE /v1/libraries/{library_id}/documents/{document_id}`

Given a library and a document in that library, delete that document. The document will be deleted from the library and the search index.

- Operation id: `libraries_documents_delete_v1`
- Tag: beta/libraries/documents

### Parameters

- `library_id` (string (uuid), required, in path)
- `document_id` (string (uuid), required, in path)

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update the metadata of a specific document. {#operation-libraries_documents_patch_v1}

`PATCH /v1/libraries/{library_id}/documents/{document_id}`

Given a library and a document in that library, update the name and/or attributes of that document.

- Operation id: `libraries_documents_patch_v1`
- Tag: beta/libraries/documents

### Parameters

- `library_id` (string (uuid), required, in path)
- `document_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateDocumentRequest`

- `name` (string, optional)
- `attributes` (object or null, optional)
- `expires_at` (string (date-time) or null, optional) — If set, the document will be automatically deleted after this date.

### Responses

- `200` — Successful Response (application/json, schema Document)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Retrieve the text content of a specific document. {#operation-libraries_documents_get_text_content_v1}

`GET /v1/libraries/{library_id}/documents/{document_id}/text_content`

Given a library and a document in that library, you can retrieve the text content of that document if it exists. For documents like pdf, docx and pptx the text content results from our processing using Mistral OCR.

- Operation id: `libraries_documents_get_text_content_v1`
- Tag: beta/libraries/documents

### Parameters

- `library_id` (string (uuid), required, in path)
- `document_id` (string (uuid), required, in path)
- `page_start` (integer or null, optional, in query)
- `page_end` (integer or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema DocumentTextContent)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Retrieve the processing status of a specific document. {#operation-libraries_documents_get_status_v1}

`GET /v1/libraries/{library_id}/documents/{document_id}/status`

Given a library and a document in that library, retrieve the processing status of that document.

- Operation id: `libraries_documents_get_status_v1`
- Tag: beta/libraries/documents

### Parameters

- `library_id` (string (uuid), required, in path)
- `document_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema ProcessingStatus)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Retrieve the signed URL of a specific document. {#operation-libraries_documents_get_signed_url_v1}

`GET /v1/libraries/{library_id}/documents/{document_id}/signed-url`

Given a library and a document in that library, retrieve the signed URL of a specific document.The url will expire after 30 minutes and can be accessed by anyone with the link.

- Operation id: `libraries_documents_get_signed_url_v1`
- Tag: beta/libraries/documents

### Parameters

- `library_id` (string (uuid), required, in path)
- `document_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Retrieve the signed URL of text extracted from a given document. {#operation-libraries_documents_get_extracted_text_signed_url_v1}

`GET /v1/libraries/{library_id}/documents/{document_id}/extracted-text-signed-url`

Given a library and a document in that library, retrieve the signed URL of text extracted. For documents that are sent to the OCR this returns the result of the OCR queries.

- Operation id: `libraries_documents_get_extracted_text_signed_url_v1`
- Tag: beta/libraries/documents

### Parameters

- `library_id` (string (uuid), required, in path)
- `document_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Reprocess a document. {#operation-libraries_documents_reprocess_v1}

`POST /v1/libraries/{library_id}/documents/{document_id}/reprocess`

Given a library and a document in that library, reprocess that document, it will be billed again.

- Operation id: `libraries_documents_reprocess_v1`
- Tag: beta/libraries/documents

### Parameters

- `library_id` (string (uuid), required, in path)
- `document_id` (string (uuid), required, in path)

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)
