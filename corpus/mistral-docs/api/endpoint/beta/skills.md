---
url: https://docs.mistral.ai/api/endpoint/beta/skills
title: Beta Skills API
breadcrumbs: [API, Beta Skills]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Beta Skills API

Reference for the Beta Skills endpoints of the Mistral API, generated from the OpenAPI specification.

## ListSkills {#operation-skills_list}

`GET /v2/skills`

- Operation id: `skills_list`
- Tag: beta/skills

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

- `200` — Success (application/json, schema ListSkillsResponse)

## CreateSkill {#operation-skills_create}

`POST /v2/skills`

- Operation id: `skills_create`
- Tag: beta/skills

### Request body

`application/json` (required), schema `CreateSkillRequest`

- `name` (string, required) — Stable object name.
- `definition` (SkillDefinition, required) — Versioned skill content.
  - `description` (string, optional) — Model-facing trigger and usage description.
  - `body` (string, optional) — Skill body content.
  - `assets` (object, optional) — Additional files available to the skill.
- `notes` (string, optional) — Notes for this version.
- `sharingScope` (enum: 'sharing_scope_unspecified', 'private', 'workspace', optional) — Registry sharing scope.
- `aliases` (array of string, optional) — Aliases pointing to this version.

### Responses

- `200` — Success (application/json, schema Skill)

## GetSkill {#operation-skills_get}

`GET /v2/skills/{skill_id}`

- Operation id: `skills_get`
- Tag: beta/skills

### Parameters

- `skill_id` (string, required, in path)
- `version` (integer (int32), optional, in query)
- `alias` (string, optional, in query)
- `fields` (array of string, optional, in query)

### Responses

- `200` — Success (application/json, schema Skill)

## DeleteSkill {#operation-skills_delete}

`DELETE /v2/skills/{skill_id}`

- Operation id: `skills_delete`
- Tag: beta/skills

### Parameters

- `skill_id` (string, required, in path)

### Responses

- `200` — Success (application/json, schema DeleteSkillResponse)

## UpdateSkill {#operation-skills_update}

`PATCH /v2/skills/{skill_id}`

- Operation id: `skills_update`
- Tag: beta/skills

### Parameters

- `skill_id` (string, required, in path)

### Request body

`application/json` (required)

- `sharingScope` (enum: 'sharing_scope_unspecified', 'private', 'workspace', optional) — Registry sharing scope.

### Responses

- `200` — Success (application/json, schema Skill)

## ListSkillVersions {#operation-skills_list_versions}

`GET /v2/skills/{skill_id}/versions`

- Operation id: `skills_list_versions`
- Tag: beta/skills

### Parameters

- `skill_id` (string, required, in path)

### Responses

- `200` — Success (application/json, schema ListSkillVersionsResponse)

## CreateSkillVersion {#operation-skills_create_version}

`POST /v2/skills/{skill_id}/versions`

- Operation id: `skills_create_version`
- Tag: beta/skills

### Parameters

- `skill_id` (string, required, in path)

### Request body

`application/json` (required)

- `definition` (SkillDefinition, required) — Versioned skill content.
  - `description` (string, optional) — Model-facing trigger and usage description.
  - `body` (string, optional) — Skill body content.
  - `assets` (object, optional) — Additional files available to the skill.
- `notes` (string, optional) — Notes for this version.
- `aliases` (array of string, optional) — Aliases pointing to this version.

### Responses

- `200` — Success (application/json, schema CreateSkillVersionResponse)

## GetSkillVersion {#operation-skills_get_version}

`GET /v2/skills/{skill_id}/versions/{version}`

- Operation id: `skills_get_version`
- Tag: beta/skills

### Parameters

- `skill_id` (string, required, in path)
- `version` (integer (int32), required, in path)
- `fields` (array of string, optional, in query)

### Responses

- `200` — Success (application/json, schema Skill)

## UpdateSkillVersionMetadata {#operation-skills_update_version_metadata}

`PATCH /v2/skills/{skill_id}/versions/{version}`

- Operation id: `skills_update_version_metadata`
- Tag: beta/skills

### Parameters

- `skill_id` (string, required, in path)
- `version` (integer (int32), required, in path)

### Request body

`application/json` (required)

- `notes` (string, optional) — Notes for this version.
- `aliases` (AliasList, optional) — Aliases pointing to this version.
  - `values` (array of string, optional)

### Responses

- `200` — Success (application/json, schema Skill)
