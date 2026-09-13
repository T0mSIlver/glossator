---
url: https://docs.mistral.ai/admin/admin-api/manage-workspaces
title: Manage Workspaces
breadcrumbs: [Admin, Admin API]
kind: doc
locale: en
source_path: src/content/en/docs/admin/admin-api/manage-workspaces/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Manage Workspaces with the Admin API

Manage Workspaces and their members programmatically.

## Before you start {#before-you-start}

All requests use the base URL `https://console.mistral.ai/api/admin` and an Admin API key in the `x-api-key` header. See [Authentication and Admin API keys](https://docs.mistral.ai/admin/admin-api/authentication).

## Workspace roles {#workspace-roles}

Assign Workspace roles with the plural `role_names` field. List every role and its UUID with `GET /api/admin/roles`. See [Manage groups and roles](https://docs.mistral.ai/admin/admin-api/manage-groups-roles#roles) for the full role catalog.

> **Note**
>
> The singular `role` and `role_name` fields are deprecated. Prefer the plural `roles` / `role_names`.

## List Workspaces {#list-workspaces}

Supports the `is_archived`, `page`, `page_size`, and `search` query parameters.

```bash
curl "https://console.mistral.ai/api/admin/workspaces?page=1&page_size=50" \
  -H "x-api-key: $ADMIN_API_KEY"
```

## Create a Workspace {#create-workspace}

`name` and `admin_user_id` are required. Optional: `description`, `icon`, and `add_all_org_members`.

```bash
curl -X POST https://console.mistral.ai/api/admin/workspaces \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{
    "name": "MySpace",
    "description": "Small Workspace",
    "icon": "",
    "add_all_org_members": false,
    "admin_user_id": "<USER_UUID>"
  }'
```

The response includes the Workspace `uuid`.

## Update a Workspace {#update-workspace}

```bash
curl -X PATCH https://console.mistral.ai/api/admin/workspaces/<WORKSPACE_UUID> \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"name": "Renamed Workspace", "description": "Updated description"}'
```

## Delete a Workspace {#delete-workspace}

```bash
curl -X DELETE https://console.mistral.ai/api/admin/workspaces/<WORKSPACE_UUID> \
  -H "x-api-key: $ADMIN_API_KEY"
```

## Manage members {#members}

Add or update members with a `members` array. Each entry takes a `user_uuid` and `role_names`.

```bash
# Add members
curl -X POST https://console.mistral.ai/api/admin/workspaces/<WORKSPACE_UUID>/add-users \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"members": [{"user_uuid": "<USER_UUID>", "role_names": ["user"]}]}'

# Add or update members (idempotent)
curl -X PATCH https://console.mistral.ai/api/admin/workspaces/<WORKSPACE_UUID>/users \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"members": [{"user_uuid": "<USER_UUID>", "role_names": ["workspace_admin"]}]}'
```

### Remove members {#remove-members}

This removes the listed users from the Workspace and deletes their permissions in it.

```bash
curl -X DELETE https://console.mistral.ai/api/admin/workspaces/<WORKSPACE_UUID>/remove-users \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"members": [{"user_uuid": "<USER_UUID_1>"}, {"user_uuid": "<USER_UUID_2>"}]}'
```
