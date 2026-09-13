---
url: https://docs.mistral.ai/admin/admin-api/user-provisioning
title: User provisioning
breadcrumbs: [Admin, Admin API]
kind: doc
locale: en
source_path: src/content/en/docs/admin/admin-api/user-provisioning/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# User provisioning with the Admin API

This guide walks through provisioning users with the Admin API: create users in bulk, organize them into a user group, and grant the group access to a Workspace. It then covers updating users and removing them from a Workspace.

## Before you start {#before-you-start}

You need an Admin API key created in the Backoffice. Every request uses the base URL `https://console.mistral.ai/api/admin` and the `x-api-key` header. See [Admin API authentication](https://docs.mistral.ai/admin/admin-api/authentication).

## Create users in bulk {#create-users}

Send an array of users to create them in a single request. Each entry takes a role, an email, and a name.

```bash
curl -X POST https://console.mistral.ai/api/admin/users \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '[
    {"role": "A", "email": "ada@example.com", "first_name": "Ada", "last_name": "Lovelace"},
    {"role": "M", "email": "alan@example.com", "first_name": "Alan", "last_name": "Turing"}
  ]'
```

The response maps each email to the created user ID. Created users sign in by entering their email and completing the account recovery flow.

> **Note**
>
> Role values such as `A` (Admin) and `M` (Member) are accepted. The singular `role` field is deprecated. Prefer `roles` / `role_names`. List the available roles and their UUIDs with `GET /api/admin/roles`. See [Roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions).

## Invite users by email {#invite-users}

Instead of creating users directly, you can email invitations. Recipients accept the invite to join the Organization. Pass a comma-separated list to invite several people at once.

```bash
curl -X POST https://console.mistral.ai/api/admin/users-invite \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"email": "grace@example.com,katherine@example.com", "role": "M"}'
```

List or delete pending invitations:

```bash
# List invitations
curl https://console.mistral.ai/api/admin/users-invite \
  -H "x-api-key: $ADMIN_API_KEY"

# Delete an invitation by its UUID
curl -X DELETE https://console.mistral.ai/api/admin/users-invite/<INVITATION_UUID> \
  -H "x-api-key: $ADMIN_API_KEY"
```

## Group users {#group-users}

A user group lets you manage and assign users together. Create the group:

```bash
curl -X POST https://console.mistral.ai/api/admin/user-groups \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"name": "Interns", "description": "User group for interns"}'
```

The response includes the group `uuid`. Add members by their user IDs:

```bash
curl -X POST https://console.mistral.ai/api/admin/user-groups/<GROUP_UUID>/members \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"user_uuids": ["<USER_UUID_1>", "<USER_UUID_2>"]}'
```

See [User groups](https://docs.mistral.ai/admin/identity-access/groups) for the concept.

## Assign a group to a workspace {#assign-workspace}

Create a workspace, optionally making one user its admin:

```bash
curl -X POST https://console.mistral.ai/api/admin/workspaces \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{
    "name": "MySpace",
    "description": "Small workspace",
    "icon": "",
    "add_all_org_members": false,
    "admin_user_id": "<USER_UUID>"
  }'
```

The response includes the Workspace `uuid`. Provision every member of the group into the Workspace with a given role:

```bash
curl -X POST https://console.mistral.ai/api/admin/user-groups/provision-workspace \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{
    "user_group_uuid": "<GROUP_UUID>",
    "workspace_uuid": "<WORKSPACE_UUID>",
    "workspace_role": "M"
  }'
```

## Manage the user lifecycle {#lifecycle}

Update a user's role or subscriptions:

```bash
curl -X PATCH https://console.mistral.ai/api/admin/users/<USER_UUID> \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"role": "M", "subscription_types": ["CHAT", "MISTRAL_CODE"]}'
```

Remove users from a Workspace. This deletes all of their permissions in that workspace:

```bash
curl -X DELETE https://console.mistral.ai/api/admin/workspaces/<WORKSPACE_UUID>/remove-users \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"members": [{"user_uuid": "<USER_UUID_1>"}, {"user_uuid": "<USER_UUID_2>"}]}'
```

## Next steps {#next-steps}

- [Usage metrics](https://docs.mistral.ai/admin/admin-api/usage-metrics)

- [User groups](https://docs.mistral.ai/admin/identity-access/groups)
