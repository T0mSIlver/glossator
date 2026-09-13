---
url: https://docs.mistral.ai/admin/admin-api/manage-users
title: Manage users
breadcrumbs: [Admin, Admin API]
kind: doc
locale: en
source_path: src/content/en/docs/admin/admin-api/manage-users/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Manage users with the Admin API

Manage the members of your Organization programmatically. For an end-to-end onboarding flow, see [User provisioning](https://docs.mistral.ai/admin/admin-api/user-provisioning).

## Before you start {#before-you-start}

All requests use the base URL `https://api.mistral.ai/v1/admin` and an Admin API key in the `x-api-key` header. See [Authentication and Admin API keys](https://docs.mistral.ai/admin/admin-api/authentication).

## Organization roles {#organization-roles}

Assign Organization roles with the plural `role_names` field. Accepted names: `member`, `billing_manager`, `organization_admin`. You can also pass role UUIDs in `roles`. List them with `GET /v1/admin/roles`.

> **Note**
>
> The singular `role` and `role_name` fields are deprecated. Prefer the plural `roles` / `role_names`, which support assigning multiple roles.

## List users {#list-users}

Supports the `page`, `page_size`, and `email` query parameters.

```bash
curl "https://api.mistral.ai/v1/admin/users?page=1&page_size=50" \
  -H "x-api-key: $ADMIN_API_KEY"
```

### Get a single user {#get-user}

```bash
curl https://api.mistral.ai/v1/admin/users/<USER_UUID> \
  -H "x-api-key: $ADMIN_API_KEY"
```

## Create users {#create-users}

Send an array of users. Each entry requires `email`, `first_name`, and `last_name`. Set roles with `role_names` and product access with `subscription_types` (`CHAT`, `MISTRAL_CODE`).

```bash
curl -X POST https://api.mistral.ai/v1/admin/users \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '[
    {"email": "ada@example.com", "first_name": "Ada", "last_name": "Lovelace", "role_names": ["organization_admin"]},
    {"email": "alan@example.com", "first_name": "Alan", "last_name": "Turing", "role_names": ["member"], "subscription_types": ["CHAT", "MISTRAL_CODE"]}
  ]'
```

The response maps each email to its created user ID. Created users sign in by entering their email and completing the account recovery flow.

## Update a user {#update-user}

Change a user's roles or product subscriptions.

```bash
curl -X PATCH https://api.mistral.ai/v1/admin/users/<USER_UUID> \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"role_names": ["member"], "subscription_types": ["CHAT"]}'
```

## Delete a user {#delete-user}

```bash
curl -X DELETE https://api.mistral.ai/v1/admin/users/<USER_UUID> \
  -H "x-api-key: $ADMIN_API_KEY"
```

## Invitations {#invitations}

Invite users by email instead of creating them directly. `email` is required and accepts one address, or several separated by commas or new lines. Optional fields include `role_names`, `subscription_types`, `workspace_uuids`, and `email_language`.

```bash
# Create an invitation
curl -X POST https://api.mistral.ai/v1/admin/users-invite \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"email": "grace@example.com", "role_names": ["member"], "workspace_uuids": ["<WORKSPACE_UUID>"]}'

# List invitations
curl https://api.mistral.ai/v1/admin/users-invite \
  -H "x-api-key: $ADMIN_API_KEY"

# Delete an invitation
curl -X DELETE https://api.mistral.ai/v1/admin/users-invite/<INVITATION_UUID> \
  -H "x-api-key: $ADMIN_API_KEY"
```
