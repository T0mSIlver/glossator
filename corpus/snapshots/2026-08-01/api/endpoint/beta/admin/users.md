---
url: https://docs.mistral.ai/api/endpoint/beta/admin/users
title: Beta Admin Users API
breadcrumbs: [API, Beta Admin Users]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
openapi_md5: 1ae55facb05ef4d5bf803842b3033337
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Admin Users API

Reference for the Beta Admin Users endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Users {#operation-users_api_admin_users_get_users}

`GET /v1/admin/users`

List Organization members and pending invitations.

- Operation id: `users_api_admin_users_get_users`
- Tag: beta/admin/users

### Parameters

- `page` (integer, optional, in query) — Page number to return.
- `page_size` (integer, optional, in query) — Maximum number of results per page.
- `email` (string or null, optional, in query) — Email address to filter users and invitations.

### Responses

- `200` — OK (application/json, schema OrganizationAdminUsersOUT)

## Create Users {#operation-users_api_admin_users_create_users}

`POST /v1/admin/users`

Create Organization members.

- Operation id: `users_api_admin_users_create_users`
- Tag: beta/admin/users

### Request body

`application/json` (required)

- `role_names` (array of enum: 'member', 'billing_manager', 'organization_admin' or null, optional) — Simplified role names to assign. Mutually exclusive with 'roles'.
- `roles` (object, optional) — Role values to assign. Mutually exclusive with 'role_names'.
  - one of 3 (anyOf):
    - array of UserRole
    - array of StaticOrganizationRoles
    - null
- `role_name` (enum: 'member', 'billing_manager', 'organization_admin', optional) — Deprecated single role name, kept for backward compatibility. Mutually exclusive with 'role'.
- `role` (object, optional) — Deprecated legacy single role value, kept for backward compatibility. Mutually exclusive with 'role_name'.
  - one of 3 (anyOf):
    - UserRole
    - StaticOrganizationRoles
    - null
- `email` (string, required) — Email address of the user to create.
- `first_name` (string, required) — First name of the user to create.
- `last_name` (string, required) — Last name of the user to create.
- `subscription_types` (array of PlanType or null, optional) — Product seats to assign to the user.

### Responses

- `200` — OK (application/json, schema OrganizationUsersCreateOUT)

## Get Invite {#operation-users_api_admin_users_get_invite}

`GET /v1/admin/users-invite`

List pending Organization invitations.

- Operation id: `users_api_admin_users_get_invite`
- Tag: beta/admin/users

### Responses

- `200` — OK (application/json)

## Invite Users {#operation-users_api_admin_users_invite_users}

`POST /v1/admin/users-invite`

Invite users to the Organization.

- Operation id: `users_api_admin_users_invite_users`
- Tag: beta/admin/users

### Request body

`application/json` (required), schema `OrganizationInviteIN`

- `role_names` (array of enum: 'member', 'billing_manager', 'organization_admin' or null, optional) — Simplified role names to assign. Mutually exclusive with 'roles'.
- `roles` (object, optional) — Role values to assign. Mutually exclusive with 'role_names'.
  - one of 3 (anyOf):
    - array of UserRole
    - array of StaticOrganizationRoles
    - null
- `role_name` (enum: 'member', 'billing_manager', 'organization_admin', optional) — Deprecated single role name, kept for backward compatibility. Mutually exclusive with 'role'.
- `role` (object, optional) — Deprecated legacy single role value, kept for backward compatibility. Mutually exclusive with 'role_name'.
  - one of 3 (anyOf):
    - UserRole
    - StaticOrganizationRoles
    - null
- `email` (string, required) — Email address, comma-separated emails, or newline-separated emails to invite.
- `subscription_type` (enum: 'API', 'CHAT', 'ON_PREMISE', 'LICENSE', 'MISTRAL_CODE', optional) — Deprecated single product seat to assign.
- `subscription_types` (array of PlanType or null, optional) — Product seats to assign to invited users.
- `subscription_seat_automatic_granting` (boolean, optional) — Whether to grant subscription seats automatically.
- `email_language` (enum: 'en', 'fr', 'es', 'de', 'it', 'pt_br', 'pl', 'ar', 'nl', optional) — Language used for invitation emails.
- `workspace_uuids` (array of string (uuid) or null, optional) — Workspace IDs the invited users should join.

### Responses

- `200` — OK (application/json, schema OrganizationInvitesCreateOUT)

## Delete Invite {#operation-users_api_admin_users_delete_invite}

`DELETE /v1/admin/users-invite/{invite_uuid}`

- Operation id: `users_api_admin_users_delete_invite`
- Tag: beta/admin/users

### Parameters

- `invite_uuid` (string (uuid), required, in path) — Organization invitation ID.

### Responses

- `200` — OK (application/json, schema DeleteOUT)

## Get User {#operation-users_api_admin_users_get_user}

`GET /v1/admin/users/{user_id}`

Get details for an Organization member.

- Operation id: `users_api_admin_users_get_user`
- Tag: beta/admin/users

### Parameters

- `user_id` (string (uuid), required, in path) — User ID.

### Responses

- `200` — OK (application/json, schema AdminUserOUT)

## Delete User {#operation-users_api_admin_users_delete_user}

`DELETE /v1/admin/users/{user_id}`

Remove a member from the Organization.

- Operation id: `users_api_admin_users_delete_user`
- Tag: beta/admin/users

### Parameters

- `user_id` (string (uuid), required, in path) — User ID.

### Responses

- `200` — OK (application/json, schema DeleteOUT)

## Update User {#operation-users_api_admin_users_update_user}

`PATCH /v1/admin/users/{user_id}`

Update an Organization member's roles and product seats.

- Operation id: `users_api_admin_users_update_user`
- Tag: beta/admin/users

### Parameters

- `user_id` (string (uuid), required, in path) — User ID.

### Request body

`application/json` (required), schema `AdminOrganizationMemberUpdate`

- `role_names` (array of enum: 'member', 'billing_manager', 'organization_admin' or null, optional) — Simplified role names to assign. Mutually exclusive with 'roles'.
- `roles` (object, optional) — Role values to assign. Mutually exclusive with 'role_names'.
  - one of 3 (anyOf):
    - array of UserRole
    - array of StaticOrganizationRoles
    - null
- `role_name` (enum: 'member', 'billing_manager', 'organization_admin', optional) — Deprecated single role name, kept for backward compatibility. Mutually exclusive with 'role'.
- `role` (object, optional) — Deprecated legacy single role value, kept for backward compatibility. Mutually exclusive with 'role_name'.
  - one of 3 (anyOf):
    - UserRole
    - StaticOrganizationRoles
    - null
- `subscription_types` (array of enum: 'CHAT', 'MISTRAL_CODE' or null, optional) — Product seats to assign to the member.

### Responses

- `200` — OK (application/json, schema AdminOrganizationMemberOUT)

## Get Roles {#operation-users_api_admin_roles_get_roles}

`GET /v1/admin/roles`

List Organization and Workspace roles.

- Operation id: `users_api_admin_roles_get_roles`
- Tag: beta/admin/users

### Responses

- `200` — OK (application/json, schema RolesOut)
