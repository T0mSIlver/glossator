---
url: https://docs.mistral.ai/admin/admin-api/manage-groups-roles
title: Manage groups and roles
breadcrumbs: [Admin, Admin API]
kind: doc
locale: en
source_path: src/content/en/docs/admin/admin-api/manage-groups-roles/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Manage groups and roles with the Admin API

Create and manage user groups, assign them to Workspaces, and look up roles. For the concept, see [Groups](https://docs.mistral.ai/admin/identity-access/groups).

## Before you start {#before-you-start}

All requests use the base URL `https://console.mistral.ai/api/admin` and an Admin API key in the `x-api-key` header. See [Authentication and Admin API keys](https://docs.mistral.ai/admin/admin-api/authentication).

## Manage groups {#manage-groups}

List groups (`page`, `page_size`, `search`), or create one. `name` is required; `description` and `target_type` (`W` for Workspace, `O` for Organization) are optional.

```bash
# List groups
curl https://console.mistral.ai/api/admin/user-groups \
  -H "x-api-key: $ADMIN_API_KEY"

# Create a group
curl -X POST https://console.mistral.ai/api/admin/user-groups \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"name": "Interns", "description": "User group for interns"}'
```

The response includes the group `uuid`. Get, update, or delete a group by its UUID:

```bash
curl https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID> \
  -H "x-api-key: $ADMIN_API_KEY"

curl -X PATCH https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID> \
  -H "Content-Type: application/json" -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"description": "Updated description"}'

curl -X DELETE https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID> \
  -H "x-api-key: $ADMIN_API_KEY"
```

## Manage members {#members}

List members, or add and remove them with a `user_uuids` array.

```bash
# List members
curl https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID>/members \
  -H "x-api-key: $ADMIN_API_KEY"

# Add members
curl -X POST https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID>/members \
  -H "Content-Type: application/json" -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"user_uuids": ["<USER_UUID_1>", "<USER_UUID_2>"]}'

# Remove members
curl -X DELETE https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID>/members \
  -H "Content-Type: application/json" -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"user_uuids": ["<USER_UUID_1>"]}'
```

## Assign a group to a workspace {#workspace-assignments}

The quickest way to provision every member of a group into a Workspace is `provision-workspace`, which accepts a friendly `workspace_role_name`:

```bash
curl -X POST https://console.mistral.ai/api/admin/user-groups/provision-workspace \
  -H "Content-Type: application/json" -H "x-api-key: $ADMIN_API_KEY" \
  -d '{
    "user_group_uuid": "<GROUP_UUID>",
    "workspace_uuid": "<WORKSPACE_UUID>",
    "workspace_role_name": "user"
  }'
```

To manage assignments as resources, use the group's `workspaces` sub-collection, with `role_names` (see [Roles](https://docs.mistral.ai/admin/admin-api/manage-groups-roles#roles)):

```bash
# List a group's Workspace assignments
curl https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID>/workspaces \
  -H "x-api-key: $ADMIN_API_KEY"

# Assign the group to a Workspace
curl -X POST https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID>/workspaces \
  -H "Content-Type: application/json" -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"workspace_uuid": "<WORKSPACE_UUID>", "role_names": ["user"]}'

# Update the roles on an assignment
curl -X PATCH https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID>/workspaces/<WORKSPACE_UUID> \
  -H "Content-Type: application/json" -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"role_names": ["workspace_admin"]}'

# Remove the group from a workspace
curl -X DELETE https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID>/workspaces/<WORKSPACE_UUID> \
  -H "x-api-key: $ADMIN_API_KEY"
```

### Set a group's Organization role {#group-org-role}

```bash
curl -X PATCH https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID>/organization-role \
  -H "Content-Type: application/json" -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"organization_role": "member"}'
```

## Roles {#roles}

List every role and its UUID. RBAC must be enabled for the Organization.

```bash
curl https://console.mistral.ai/api/admin/roles \
  -H "x-api-key: $ADMIN_API_KEY"
```

The response groups roles into `organization_roles` and `workspace_roles`.

**Organization roles**

| `role_name` | Access |
|-------------|--------|
| `member` | Product usage; manages their own profile |
| `billing_manager` | Subscriptions, invoices, and payment methods; cannot change Organization settings |
| `organization_admin` | Full control of the Organization |

**Workspace roles**

| `role_name` | Access |
|-------------|--------|
| `user` | le Chat and its features; no Studio |
| `dev` | Studio and all primitives (agents, fine-tuning, etc.); no le Chat |
| `mistral_code_user` | Mistral Code (requires a seat) |
| `billing` | Usage and cost reports only |
| `workspace_contributor` | All product features (`user`, `dev`, `mistral_code_user`); no management or observability |
| `workspace_admin` | Workspace contributor plus Workspace administration; no observability |
| `observability_viewer` | Observability product |

> **Note**
>
> `GET /api/admin/roles` is the authoritative list of roles and their UUIDs.
