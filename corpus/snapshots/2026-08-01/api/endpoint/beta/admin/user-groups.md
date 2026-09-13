---
url: https://docs.mistral.ai/api/endpoint/beta/admin/user-groups
title: Beta Admin User Groups API
breadcrumbs: [API, Beta Admin User Groups]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
openapi_md5: 1ae55facb05ef4d5bf803842b3033337
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Admin User Groups API

Reference for the Beta Admin User Groups endpoints of the Mistral API, generated from the OpenAPI specification.

## Get User Groups {#operation-users_api_admin_user_groups_get_user_groups}

`GET /v1/admin/user-groups`

Get all user groups across the organization.

- Operation id: `users_api_admin_user_groups_get_user_groups`
- Tag: beta/admin/user-groups

### Parameters

- `page` (integer, optional, in query) — Page number to return.
- `page_size` (integer, optional, in query) — Maximum number of results per page.
- `search` (string or null, optional, in query) — Search term used to filter user groups by name.

### Responses

- `200` — OK (application/json, schema AdminUserGroupsOut)

## Create User Group {#operation-users_api_admin_user_groups_create_user_group}

`POST /v1/admin/user-groups`

Create a new user group.

- Operation id: `users_api_admin_user_groups_create_user_group`
- Tag: beta/admin/user-groups

### Request body

`application/json` (required), schema `AdminUserGroupIn`

- `name` (string, required) — Name of the user group.
- `description` (string or null, optional) — Optional description of the user group.
- `target_type` (enum: 'W', 'O', optional) — Type of resources this group can access.

### Responses

- `200` — OK (application/json, schema AdminUserGroupOut)

## Provision Group To Workspace {#operation-users_api_admin_user_groups_provision_group_to_workspace}

`POST /v1/admin/user-groups/provision-workspace`

Provision all users from a user group to a workspace with a specific role.

- Operation id: `users_api_admin_user_groups_provision_group_to_workspace`
- Tag: beta/admin/user-groups

### Request body

`application/json` (required), schema `AdminProvisionGroupToWorkspaceIn`

- `user_group_uuid` (string (uuid), required) — User group ID to provision.
- `workspace_uuid` (string (uuid), required) — Workspace ID where the group is provisioned.
- `workspace_role` (object, optional) — Workspace role value to assign to the group. Mutually exclusive with 'workspace_role_name'.
  - one of 3 (anyOf):
    - WorkspaceRole
    - StaticWorkspaceRoles
    - null
- `workspace_role_name` (enum: 'billing', 'user', 'contributor', 'dev', 'dev_contributor', 'mistral_code_user', 'cloud_user', 'workspace_contributor', 'workspace_admin', 'observability_viewer', 'workflow_executor', optional) — Workspace role name to assign to the group. Mutually exclusive with 'workspace_role'.

### Responses

- `204` — No Content

## Get User Group {#operation-users_api_admin_user_groups_get_user_group}

`GET /v1/admin/user-groups/{group_uuid}`

Get a specific user group.

- Operation id: `users_api_admin_user_groups_get_user_group`
- Tag: beta/admin/user-groups

### Parameters

- `group_uuid` (string (uuid), required, in path) — User group ID.

### Responses

- `200` — OK (application/json, schema AdminUserGroupOut)

## Delete User Group {#operation-users_api_admin_user_groups_delete_user_group}

`DELETE /v1/admin/user-groups/{group_uuid}`

Delete a user group.

- Operation id: `users_api_admin_user_groups_delete_user_group`
- Tag: beta/admin/user-groups

### Parameters

- `group_uuid` (string (uuid), required, in path) — User group ID.

### Responses

- `204` — No Content

## Update User Group {#operation-users_api_admin_user_groups_update_user_group}

`PATCH /v1/admin/user-groups/{group_uuid}`

Update a user group.

- Operation id: `users_api_admin_user_groups_update_user_group`
- Tag: beta/admin/user-groups

### Parameters

- `group_uuid` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `AdminUpdateUserGroupIn`

- `name` (string or null, optional) — Updated name of the user group.
- `description` (string or null, optional) — Updated description of the user group.
- `target_type` (enum: 'W', 'O', optional) — Updated permission target type for this group.

### Responses

- `200` — OK (application/json, schema AdminUserGroupOut)

## Get User Group Members {#operation-users_api_admin_user_groups_get_user_group_members}

`GET /v1/admin/user-groups/{group_uuid}/members`

Get members of a user group.

- Operation id: `users_api_admin_user_groups_get_user_group_members`
- Tag: beta/admin/user-groups

### Parameters

- `group_uuid` (string (uuid), required, in path) — User group ID.
- `page` (integer, optional, in query) — Page number to return.
- `page_size` (integer, optional, in query) — Maximum number of results per page.

### Responses

- `200` — OK (application/json, schema AdminUserGroupMembersOut)

## Assign Users To Group {#operation-users_api_admin_user_groups_assign_users_to_group}

`POST /v1/admin/user-groups/{group_uuid}/members`

Assign users to a user group.

- Operation id: `users_api_admin_user_groups_assign_users_to_group`
- Tag: beta/admin/user-groups

### Parameters

- `group_uuid` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `AdminAssignUsersToGroupIn`

- `user_uuids` (array of string (uuid), required) — User IDs to add to the group.

### Responses

- `204` — No Content

## Remove Users From Group {#operation-users_api_admin_user_groups_remove_users_from_group}

`DELETE /v1/admin/user-groups/{group_uuid}/members`

Remove users from a user group.

- Operation id: `users_api_admin_user_groups_remove_users_from_group`
- Tag: beta/admin/user-groups

### Parameters

- `group_uuid` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `AdminAssignUsersToGroupIn`

- `user_uuids` (array of string (uuid), required) — User IDs to add to the group.

### Responses

- `204` — No Content

## Get Group Workspace Assignments {#operation-users_admin_user_groups_get_group_workspace_assignments}

`GET /v1/admin/user-groups/{group_uuid}/workspaces`

List workspace assignments for a user group.

- Operation id: `users_admin_user_groups_get_group_workspace_assignments`
- Tag: beta/admin/user-groups

### Parameters

- `group_uuid` (string (uuid), required, in path) — User group ID.
- `page` (integer, optional, in query) — Page number to return.
- `page_size` (integer, optional, in query) — Maximum number of results per page.

### Responses

- `200` — OK (application/json, schema GroupWorkspaceAssignmentsOut)

## Assign Group To Workspace {#operation-users_api_admin_user_groups_assign_group_to_workspace}

`POST /v1/admin/user-groups/{group_uuid}/workspaces`

Assign a user group to a workspace.

- Operation id: `users_api_admin_user_groups_assign_group_to_workspace`
- Tag: beta/admin/user-groups

### Parameters

- `group_uuid` (string (uuid), required, in path) — User group ID.

### Request body

`application/json` (required), schema `AssignGroupToWorkspaceIn`

- `role_names` (array of enum: 'billing', 'user', 'contributor', 'dev', 'dev_contributor', 'mistral_code_user', 'cloud_user', 'workspace_contributor', 'workspace_admin', 'observability_viewer', 'workflow_executor' or null, optional) — Simplified role names to assign. Mutually exclusive with 'roles'.
- `roles` (array of object or null, optional) — Role values to assign. Mutually exclusive with 'role_names'.
  - one of 2 (anyOf):
    - WorkspaceRole
    - StaticWorkspaceRoles
- `role` (object, optional) — Deprecated single role value. Use 'role_names' instead.
  - one of 3 (anyOf):
    - WorkspaceRole
    - StaticWorkspaceRoles
    - null
- `workspace_uuid` (string (uuid), required)

### Responses

- `201` — Created

## Remove Group From Workspace {#operation-users_admin_user_groups_remove_group_from_workspace}

`DELETE /v1/admin/user-groups/{group_uuid}/workspaces/{workspace_uuid}`

Remove a user group from a workspace.

- Operation id: `users_admin_user_groups_remove_group_from_workspace`
- Tag: beta/admin/user-groups

### Parameters

- `group_uuid` (string (uuid), required, in path) — User group ID.
- `workspace_uuid` (string (uuid), required, in path) — Workspace ID.

### Responses

- `204` — No Content

## Update Group Workspace Assignment {#operation-users_admin_user_groups_update_group_workspace_assignment}

`PATCH /v1/admin/user-groups/{group_uuid}/workspaces/{workspace_uuid}`

Update the workspace role assignment for a user group.

- Operation id: `users_admin_user_groups_update_group_workspace_assignment`
- Tag: beta/admin/user-groups

### Parameters

- `group_uuid` (string (uuid), required, in path) — User group ID.
- `workspace_uuid` (string (uuid), required, in path) — Workspace ID.

### Request body

`application/json` (required), schema `UpdateGroupWorkspaceAssignmentIn`

- `role_names` (array of enum: 'billing', 'user', 'contributor', 'dev', 'dev_contributor', 'mistral_code_user', 'cloud_user', 'workspace_contributor', 'workspace_admin', 'observability_viewer', 'workflow_executor' or null, optional) — Simplified role names to assign. Mutually exclusive with 'roles'.
- `roles` (array of object or null, optional) — Role values to assign. Mutually exclusive with 'role_names'.
  - one of 2 (anyOf):
    - WorkspaceRole
    - StaticWorkspaceRoles
- `role` (object, optional) — Deprecated single role value. Use 'role_names' instead.
  - one of 3 (anyOf):
    - WorkspaceRole
    - StaticWorkspaceRoles
    - null

### Responses

- `204` — No Content

## Update User Group Organization Role {#operation-users_admin_user_groups_update_user_group_organization_role}

`PATCH /v1/admin/user-groups/{group_uuid}/organization-role`

Update the organization role for a user group.

- Operation id: `users_admin_user_groups_update_user_group_organization_role`
- Tag: beta/admin/user-groups

### Parameters

- `group_uuid` (string (uuid), required, in path) — User group ID.

### Request body

`application/json` (required), schema `UpdateUserGroupOrganizationRoleIn`

- `organization_role` (object, required) — Organization role to assign to the group.
  - one of 2 (anyOf):
    - UserRole
    - StaticOrganizationRoles

### Responses

- `204` — No Content
