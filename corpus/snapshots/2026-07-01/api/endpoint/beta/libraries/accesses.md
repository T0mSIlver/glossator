---
url: https://docs.mistral.ai/api/endpoint/beta/libraries/accesses
title: Beta Libraries Accesses API
breadcrumbs: [API, Beta Libraries Accesses]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
openapi_md5: a48c7e7248a7d23ff0ece7147ffa1a80
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Libraries Accesses API

Reference for the Beta Libraries Accesses endpoints of the Mistral API, generated from the OpenAPI specification.

## List all of the access to this library. {#operation-libraries_share_list_v1}

`GET /v1/libraries/{library_id}/share`

Given a library, list all of the Entity that have access and to what level.

- Operation id: `libraries_share_list_v1`
- Tag: beta/libraries/accesses

### Parameters

- `library_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema ListSharingResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create or update an access level. {#operation-libraries_share_create_v1}

`PUT /v1/libraries/{library_id}/share`

Given a library id, you can create or update the access level of an entity. You have to be owner of the library to share a library. An owner cannot change their own role. A library cannot be shared outside of the organization.

- Operation id: `libraries_share_create_v1`
- Tag: beta/libraries/accesses

### Parameters

- `library_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `SharingRequest`

- `org_id` (string (uuid) or null, optional)
- `level` (enum: 'Viewer', 'Editor', required)
- `share_with_uuid` (string (uuid), required) — The id of the entity (user, workspace or organization) to share with
- `share_with_type` (enum: 'User', 'Workspace', 'Org', required) — The type of entity, used to share a library.

### Responses

- `200` — Successful Response (application/json, schema Sharing)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete an access level. {#operation-libraries_share_delete_v1}

`DELETE /v1/libraries/{library_id}/share`

Given a library id, you can delete the access level of an entity. An owner cannot delete their own access. You have to be the owner of the library to delete an access other than yours. Warning: the response will change from 200 (returning the deleted sharing) to 204 No Content in a future version.

- Operation id: `libraries_share_delete_v1`
- Tag: beta/libraries/accesses

### Parameters

- `library_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `SharingDelete`

- `org_id` (string (uuid) or null, optional)
- `share_with_uuid` (string (uuid), required) — The id of the entity (user, workspace or organization) to share with
- `share_with_type` (enum: 'User', 'Workspace', 'Org', required) — The type of entity, used to share a library.

### Responses

- `200` — Access deleted (deprecated, will be removed in favor of 204). (application/json, schema Sharing)
- `204` — Access deleted. This will become the only response in a future version.
- `422` — Validation Error (application/json, schema HTTPValidationError)
