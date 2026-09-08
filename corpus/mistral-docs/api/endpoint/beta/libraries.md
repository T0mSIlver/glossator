---
url: https://docs.mistral.ai/api/endpoint/beta/libraries
title: Beta Libraries API
breadcrumbs: [API, Beta Libraries]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Beta Libraries API

Reference for the Beta Libraries endpoints of the Mistral API, generated from the OpenAPI specification.

## List all libraries you have access to. {#operation-libraries_list_v1}

`GET /v1/libraries`

List all libraries that you have created or have been shared with you.

- Operation id: `libraries_list_v1`
- Tag: beta/libraries

### Parameters

- `page_size` (integer, optional, in query)
- `page_token` (string or null, optional, in query) — Continuation token from a previous response's next_page_token. Preferred over `page`.
- `page` (integer, optional, in query) — Deprecated: use page_token. Offset paging re-scans earlier pages and is being phased out.
- `search` (string or null, optional, in query) — Case-insensitive search on the library name.
- `filter_owned_by_me` (boolean or null, optional, in query) — Deprecated: this parameter will be removed in a future version.

### Responses

- `200` — Successful Response (application/json, schema ListLibrariesResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create a new Library. {#operation-libraries_create_v1}

`POST /v1/libraries`

Create a new Library, you will be marked as the owner and only you will have the possibility to share it with others. When first created this will only be accessible by you.

- Operation id: `libraries_create_v1`
- Tag: beta/libraries

### Request body

`application/json` (required), schema `CreateLibraryRequest`

- `name` (string, required)
- `description` (string or null, optional)
- `chunk_size` (integer or null, optional) — The size of the chunks (in characters) to split document text into. Must be between 256 and 32768.
- `owner_type` (enum: 'User', 'Workspace', optional) — Determines who owns the created library. 'User' creates a private library accessible only to its owner. 'Workspace' creates a library shared with the workspace. Defaults to 'Workspace' for API key sessions. Only API keys with the 'Private and shared connectors' connector access scope can create private, user-owned libraries.

### Responses

- `201` — Successful Response (application/json, schema Library)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Detailed information about a specific Library. {#operation-libraries_get_v1}

`GET /v1/libraries/{library_id}`

Given a library id, details information about that Library.

- Operation id: `libraries_get_v1`
- Tag: beta/libraries

### Parameters

- `library_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema Library)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update a library. {#operation-libraries_update_v1}

`PUT /v1/libraries/{library_id}`

Given a library id, you can update the name and description.

- Operation id: `libraries_update_v1`
- Tag: beta/libraries
- Deprecated: yes

### Parameters

- `library_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateLibraryRequest`

- `name` (string, optional)
- `description` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema Library)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete a library and all of it's document. {#operation-libraries_delete_v1}

`DELETE /v1/libraries/{library_id}`

Given a library id, deletes it together with all documents that have been uploaded to that library. Warning: the response will change from 200 (returning the deleted library) to 204 No Content in a future version.

- Operation id: `libraries_delete_v1`
- Tag: beta/libraries

### Parameters

- `library_id` (string (uuid), required, in path)

### Responses

- `200` — Library deleted (deprecated, will be removed in favor of 204). (application/json, schema Library)
- `204` — Library deleted. This will become the only response in a future version.
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update a library. {#operation-libraries_patch_v1}

`PATCH /v1/libraries/{library_id}`

Given a library id, you can update the name and description.

- Operation id: `libraries_patch_v1`
- Tag: beta/libraries

### Parameters

- `library_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateLibraryRequest`

- `name` (string, optional)
- `description` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema Library)
- `422` — Validation Error (application/json, schema HTTPValidationError)
