---
url: https://docs.mistral.ai/api/endpoint/beta/prompts
title: Beta Prompts API
breadcrumbs: [API, Beta Prompts]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Prompts API

Reference for the Beta Prompts endpoints of the Mistral API, generated from the OpenAPI specification.

## ListPrompts {#operation-prompts_list}

`GET /v2/prompts`

- Operation id: `prompts_list`
- Tag: beta/prompts

### Parameters

- `pageSize` (integer (int32), optional, in query)
- `pageToken` (string, optional, in query)
- `alias` (string, optional, in query)
- `fields` (array of string, optional, in query)
- `sort.field` (enum: 'list_sort_field_unspecified', 'list_sort_field_created_at', 'list_sort_field_last_modified_at', 'list_sort_field_name', 'list_sort_field_title', optional, in query) — Defaults to created_at when omitted.
- `sort.direction` (enum: 'list_sort_direction_unspecified', 'list_sort_direction_asc', 'list_sort_direction_desc', optional, in query) — Defaults to descending for timestamp fields and ascending for text fields.
- `sort_by` (string, optional, in query) — REST-friendly alias for sort.field. Supported values: created_at, last_modified_at, name, title.
- `sort_direction` (string, optional, in query) — REST-friendly alias for sort.direction. Supported values: asc, desc.

### Responses

- `200` — Success (application/json, schema ListPromptsResponse)

## CreatePrompt {#operation-prompts_create}

`POST /v2/prompts`

- Operation id: `prompts_create`
- Tag: beta/prompts

### Request body

`application/json` (required), schema `CreatePromptRequest`

- `name` (string, required) — Stable object name.
- `definition` (PromptDefinition, required) — Versioned prompt content.
  - `content` (string, required) — Prompt template content.
  - `variables` (array of PromptVariable, optional) — Variables used by the prompt.
    - `name` (string, optional) — Stable object name.
- `title` (string, optional) — Display title.
- `description` (string, optional) — Display description.
- `notes` (string, optional) — Notes for this version.
- `sharingScope` (enum: 'sharing_scope_unspecified', 'private', 'workspace', optional) — Registry sharing scope.
- `aliases` (array of string, optional) — Aliases pointing to this version.

### Responses

- `200` — Success (application/json, schema Prompt)

## GetPrompt {#operation-prompts_get}

`GET /v2/prompts/{prompt_id}`

- Operation id: `prompts_get`
- Tag: beta/prompts

### Parameters

- `prompt_id` (string, required, in path)
- `version` (integer (int32), optional, in query)
- `alias` (string, optional, in query)
- `fields` (array of string, optional, in query)

### Responses

- `200` — Success (application/json, schema Prompt)

## DeletePrompt {#operation-prompts_delete}

`DELETE /v2/prompts/{prompt_id}`

- Operation id: `prompts_delete`
- Tag: beta/prompts

### Parameters

- `prompt_id` (string, required, in path)

### Responses

- `200` — Success (application/json, schema DeletePromptResponse)

## UpdatePrompt {#operation-prompts_update}

`PATCH /v2/prompts/{prompt_id}`

- Operation id: `prompts_update`
- Tag: beta/prompts

### Parameters

- `prompt_id` (string, required, in path)

### Request body

`application/json` (required)

- `title` (string, optional) — Display title.
- `description` (string, optional) — Display description.
- `sharingScope` (enum: 'sharing_scope_unspecified', 'private', 'workspace', optional) — Registry sharing scope.

### Responses

- `200` — Success (application/json, schema Prompt)

## ListPromptVersions {#operation-prompts_list_versions}

`GET /v2/prompts/{prompt_id}/versions`

- Operation id: `prompts_list_versions`
- Tag: beta/prompts

### Parameters

- `prompt_id` (string, required, in path)

### Responses

- `200` — Success (application/json, schema ListPromptVersionsResponse)

## CreatePromptVersion {#operation-prompts_create_version}

`POST /v2/prompts/{prompt_id}/versions`

- Operation id: `prompts_create_version`
- Tag: beta/prompts

### Parameters

- `prompt_id` (string, required, in path)

### Request body

`application/json` (required)

- `definition` (PromptDefinition, required) — Versioned prompt content.
  - `content` (string, required) — Prompt template content.
  - `variables` (array of PromptVariable, optional) — Variables used by the prompt.
    - `name` (string, optional) — Stable object name.
- `notes` (string, optional) — Notes for this version.
- `aliases` (array of string, optional) — Aliases pointing to this version.

### Responses

- `200` — Success (application/json, schema CreatePromptVersionResponse)

## GetPromptVersion {#operation-prompts_get_version}

`GET /v2/prompts/{prompt_id}/versions/{version}`

- Operation id: `prompts_get_version`
- Tag: beta/prompts

### Parameters

- `prompt_id` (string, required, in path)
- `version` (integer (int32), required, in path)
- `fields` (array of string, optional, in query)

### Responses

- `200` — Success (application/json, schema Prompt)

## UpdatePromptVersionMetadata {#operation-prompts_update_version_metadata}

`PATCH /v2/prompts/{prompt_id}/versions/{version}`

- Operation id: `prompts_update_version_metadata`
- Tag: beta/prompts

### Parameters

- `prompt_id` (string, required, in path)
- `version` (integer (int32), required, in path)

### Request body

`application/json` (required)

- `notes` (string, optional) — Notes for this version.
- `aliases` (AliasList, optional) — Aliases pointing to this version.
  - `values` (array of string, optional)

### Responses

- `200` — Success (application/json, schema Prompt)
