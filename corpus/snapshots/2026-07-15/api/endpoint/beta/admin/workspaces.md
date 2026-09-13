---
url: https://docs.mistral.ai/api/endpoint/beta/admin/workspaces
title: Beta Admin Workspaces API
breadcrumbs: [API, Beta Admin Workspaces]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
openapi_md5: c28e3a674c73b4319d99305d173a6656
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Admin Workspaces API

Reference for the Beta Admin Workspaces endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Workspaces {#operation-users_api_admin_workspaces_get_workspaces}

`GET /api/admin/workspaces`

List Workspaces in the Organization.

- Operation id: `users_api_admin_workspaces_get_workspaces`
- Tag: beta/admin/workspaces

### Parameters

- `is_archived` (boolean, optional, in query) — Whether to include archived Workspaces.
- `page` (integer, optional, in query) — Page number to return.
- `page_size` (integer, optional, in query) — Maximum number of results per page.
- `search` (string or null, optional, in query) — Search term to filter Workspaces by name.

### Responses

- `200` — OK (application/json, schema WorkspacesOut)

## Create Workspace {#operation-users_api_admin_workspaces_create_workspace}

`POST /api/admin/workspaces`

Create a Workspace.

- Operation id: `users_api_admin_workspaces_create_workspace`
- Tag: beta/admin/workspaces

### Request body

`application/json` (required), schema `AdminWorkspaceIn`

- `name` (string, required) — Workspace name.
- `description` (string, optional) — Workspace description.
- `icon` (string, optional) — Workspace icon.
- `add_all_org_members` (boolean, optional) — Whether to add all Organization members to the Workspace.
- `admin_user_id` (string (uuid), required) — User ID to grant the Workspace Admin role to.

### Responses

- `200` — OK (application/json, schema WorkspaceEnrichedOUT)

## Delete Workspaces {#operation-users_api_admin_workspaces_delete_workspaces}

`DELETE /api/admin/workspaces/{workspace_uuid}`

Archive a Workspace.

- Operation id: `users_api_admin_workspaces_delete_workspaces`
- Tag: beta/admin/workspaces

### Parameters

- `workspace_uuid` (string (uuid), required, in path) — Workspace ID.

### Responses

- `204` — No Content

## Update Workspaces {#operation-users_api_admin_workspaces_update_workspaces}

`PATCH /api/admin/workspaces/{workspace_uuid}`

Update a Workspace.

- Operation id: `users_api_admin_workspaces_update_workspaces`
- Tag: beta/admin/workspaces

### Parameters

- `workspace_uuid` (string (uuid), required, in path) — Workspace ID.

### Request body

`application/json` (required), schema `UpdateWorkspaceIN`

- `name` (string or null, optional) — Updated Workspace name.
- `description` (string or null, optional) — Updated Workspace description.
- `icon` (string or null, optional) — Updated Workspace icon.

### Responses

- `200` — OK (application/json, schema WorkspaceOUT)

## Add Users Workspaces {#operation-users_api_admin_workspaces_add_users_workspaces}

`POST /api/admin/workspaces/{workspace_uuid}/add-users`

Add members to a Workspace.

- Operation id: `users_api_admin_workspaces_add_users_workspaces`
- Tag: beta/admin/workspaces

### Parameters

- `workspace_uuid` (string (uuid), required, in path) — Workspace ID.

### Request body

`application/json` (required), schema `WorkspaceMemberIN`

- `members` (array of WorkspaceMemberSingleIN or null, optional) — Workspace members to add or update.
  - `role_names` (array of enum: 'billing', 'user', 'contributor', 'dev', 'dev_contributor', 'mistral_code_user', 'cloud_user', 'workspace_contributor', 'workspace_admin', 'observability_viewer' or null, optional) — Simplified role names to assign. Mutually exclusive with 'roles'.
  - `roles` (object, optional) — Role values to assign. Mutually exclusive with 'role_names'.
  - `role_name` (enum: 'billing', 'user', 'contributor', 'dev', 'dev_contributor', 'mistral_code_user', 'cloud_user', 'workspace_contributor', 'workspace_admin', 'observability_viewer', optional) — Deprecated single role name, kept for backward compatibility. Mutually exclusive with 'role'.
  - `role` (object, optional) — Deprecated legacy single role value, kept for backward compatibility. Mutually exclusive with 'role_name'.
  - `user_uuid` (string (uuid), required) — User ID of the Workspace member.

### Responses

- `200` — OK (application/json, schema AddUsersToWorkspaceOUT)

## Add Or Update Users Workspaces {#operation-users_api_admin_workspaces_add_or_update_users_workspaces}

`PATCH /api/admin/workspaces/{workspace_uuid}/users`

Add or update Workspace members.

- Operation id: `users_api_admin_workspaces_add_or_update_users_workspaces`
- Tag: beta/admin/workspaces

### Parameters

- `workspace_uuid` (string (uuid), required, in path) — Workspace ID.

### Request body

`application/json` (required), schema `WorkspaceMemberIN`

- `members` (array of WorkspaceMemberSingleIN or null, optional) — Workspace members to add or update.
  - `role_names` (array of enum: 'billing', 'user', 'contributor', 'dev', 'dev_contributor', 'mistral_code_user', 'cloud_user', 'workspace_contributor', 'workspace_admin', 'observability_viewer' or null, optional) — Simplified role names to assign. Mutually exclusive with 'roles'.
  - `roles` (object, optional) — Role values to assign. Mutually exclusive with 'role_names'.
  - `role_name` (enum: 'billing', 'user', 'contributor', 'dev', 'dev_contributor', 'mistral_code_user', 'cloud_user', 'workspace_contributor', 'workspace_admin', 'observability_viewer', optional) — Deprecated single role name, kept for backward compatibility. Mutually exclusive with 'role'.
  - `role` (object, optional) — Deprecated legacy single role value, kept for backward compatibility. Mutually exclusive with 'role_name'.
  - `user_uuid` (string (uuid), required) — User ID of the Workspace member.

### Responses

- `200` — OK (application/json, schema AddOrUpdateUsersToWorkspaceOUT)

## Remove Users Workspaces {#operation-users_api_admin_workspaces_remove_users_workspaces}

`DELETE /api/admin/workspaces/{workspace_uuid}/remove-users`

Remove members from a Workspace.

- Operation id: `users_api_admin_workspaces_remove_users_workspaces`
- Tag: beta/admin/workspaces

### Parameters

- `workspace_uuid` (string (uuid), required, in path) — Workspace ID.

### Request body

`application/json` (required), schema `RemoveWorkspaceMembersIN`

- `members` (array of BaseWorkspaceMemberIN, required) — Workspace members to remove.
  - `user_uuid` (string (uuid), required) — User ID of the Workspace member.

### Responses

- `200` — OK (application/json, schema RemoveWorkspaceMembersOUT)
