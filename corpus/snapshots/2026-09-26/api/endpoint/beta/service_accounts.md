---
url: https://docs.mistral.ai/api/endpoint/beta/service_accounts
title: Beta Service Accounts API
breadcrumbs: [API, Beta Service Accounts]
kind: api
locale: en
source_path: openapi.yaml
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
openapi_md5: 71b15b9981e95fd9c3ab90aa80f2d1b6
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Service Accounts API

Reference for the Beta Service Accounts endpoints of the Mistral API, generated from the OpenAPI specification.

## List Service Accounts {#operation-list_service_accounts_v1_service_accounts_get}

`GET /v1/service-accounts`

List the service accounts in a workspace, or across the organization.

Scoped to a workspace, this requires the Workspace admin (`workspace_admin`) role on
it. Omitting the workspace lists the whole organization and requires the Organization
admin (`organization_admin`) role instead.

- Operation id: `list_service_accounts_v1_service_accounts_get`
- Tag: beta/service_accounts

### Parameters

- `workspace_id` (string (uuid) or null, optional, in query)
- `include_deleted` (boolean, optional, in query)
- `offset` (integer, required, in query)
- `limit` (integer, required, in query)

### Responses

- `200` — Successful Response (application/json, schema ListServiceAccountsResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create Service Account {#operation-create_service_account_v1_service_accounts_post}

`POST /v1/service-accounts`

Create a service account in a workspace. Requires the Workspace admin (`workspace_admin`) role.

- Operation id: `create_service_account_v1_service_accounts_post`
- Tag: beta/service_accounts

### Request body

`application/json` (required), schema `CreateServiceAccountRequest`

- `name` (string, required)
- `workspace_id` (string (uuid), required)
- `description` (string or null, optional)
- `role_ids` (array of string (uuid), optional)

### Responses

- `201` — Successful Response (application/json, schema ServiceAccount)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List Assignable Service Account Roles {#operation-list_assignable_service_account_roles_v1_service_accounts_assignable_roles_get}

`GET /v1/service-accounts/assignable-roles`

List the workspace roles that can be assigned to a service account.

Requires the Workspace admin (`workspace_admin`) role.

- Operation id: `list_assignable_service_account_roles_v1_service_accounts_assignable_roles_get`
- Tag: beta/service_accounts

### Parameters

- `workspace_id` (string (uuid), required, in query)

### Responses

- `200` — Successful Response (application/json, schema ListAssignableServiceAccountRolesResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Service Account {#operation-get_service_account_v1_service_accounts_service_account_id_get}

`GET /v1/service-accounts/{service_account_id}`

Retrieve a service account.

Requires the Workspace admin (`workspace_admin`) role.

- Operation id: `get_service_account_v1_service_accounts__service_account_id__get`
- Tag: beta/service_accounts

### Parameters

- `service_account_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema ServiceAccount)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete Service Account {#operation-delete_service_account_v1_service_accounts_service_account_id_delete}

`DELETE /v1/service-accounts/{service_account_id}`

Delete a service account.

Requires the Workspace admin (`workspace_admin`) role.

- Operation id: `delete_service_account_v1_service_accounts__service_account_id__delete`
- Tag: beta/service_accounts

### Parameters

- `service_account_id` (string (uuid), required, in path)

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update Service Account {#operation-update_service_account_v1_service_accounts_service_account_id_patch}

`PATCH /v1/service-accounts/{service_account_id}`

Update a service account.

Requires the Workspace admin (`workspace_admin`) role.

- Operation id: `update_service_account_v1_service_accounts__service_account_id__patch`
- Tag: beta/service_accounts

### Parameters

- `service_account_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateServiceAccountRequest`

- `description` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema ServiceAccount)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List Service Account Roles {#operation-list_service_account_roles_v1_service_accounts_service_account_id_roles_get}

`GET /v1/service-accounts/{service_account_id}/roles`

List the workspace roles assigned to a service account.

Requires the Workspace admin (`workspace_admin`) role.

- Operation id: `list_service_account_roles_v1_service_accounts__service_account_id__roles_get`
- Tag: beta/service_accounts

### Parameters

- `service_account_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema ListServiceAccountRolesResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Set Service Account Roles {#operation-set_service_account_roles_v1_service_accounts_service_account_id_roles_put}

`PUT /v1/service-accounts/{service_account_id}/roles`

Replace the workspace roles assigned to a service account.

Requires the Workspace admin (`workspace_admin`) role.

- Operation id: `set_service_account_roles_v1_service_accounts__service_account_id__roles_put`
- Tag: beta/service_accounts

### Parameters

- `service_account_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `SetServiceAccountRolesRequest`

- `role_ids` (array of string (uuid), optional)

### Responses

- `200` — Successful Response (application/json, schema ListServiceAccountRolesResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
