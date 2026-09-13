---
url: https://docs.mistral.ai/admin/identity-access/roles-permissions
title: Roles and permissions (RBAC)
breadcrumbs: [Admin, Access and permissions]
kind: doc
locale: en
source_path: src/content/en/docs/admin/identity-access/roles-permissions/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Roles and permissions (RBAC)

Mistral uses role-based access control (RBAC) to govern what members can do. Roles are predefined and apply at two scopes: the **Organization** and each **Workspace**.

## How roles work {#how-roles-work}

- **Two scopes.** Organization roles control account-wide administration; Workspace roles control access within a single Workspace. They are independent. A user can be a **Member** of the Organization and a **Workspace admin** of one Workspace.
- **Multiple roles.** A user can hold several roles in the same Organization or Workspace. Permissions are **additive**: the user gets the union of everything their roles grant.
- **Default Workspace role.** New Workspace members get **Workspace contributor** by default, regardless of their Organization role. Even an Organization admin or billing manager starts as a Workspace contributor until you change it.
- **Where to assign.** Assign roles in the [Admin Panel](https://admin.mistral.ai) (a multi-select per member), or programmatically with the Admin API using `role_names`. See [Manage users](https://docs.mistral.ai/admin/admin-api/manage-users) and [Manage groups and roles](https://docs.mistral.ai/admin/admin-api/manage-groups-roles).

## Organization roles {#organization-roles}

Use the `role_names` field in the Admin API to assign Organization roles by name.

| UI label | API Role name | What it grants |
| --- | --- | --- |
| Member | `member` | Product usage. Manages their own profile and preferences. |
| Billing | `billing_manager` | Subscriptions, invoices, payment methods, and usage reports. Cannot change Organization settings or invite members. |
| Admin | `organization_admin` | Full control of the Organization: settings, members, security, billing, and audit logs. |

## Workspace roles {#workspace-roles}

Use the `role_names` field in the Admin API to assign Workspace roles by name.

| UI label | API Role name | What it grants |
| --- | --- | --- |
| User | `user` | Access to Vibe and its features. No Studio access. |
| Developer | `dev` | Access to Studio and all its primitives (agents, fine-tuning, etc.). No Vibe access. |
| Mistral Vibe Code User | `mistral_code_user` | Access to Mistral Code (requires a seat). |
| Workspace Contributor | `workspace_contributor` | All product features (`user`, `dev`, and `mistral_code_user` combined). No management, administration, or observability. |
| Admin | `workspace_admin` | Everything a Workspace Contributor has, plus Workspace administration. |
| Observability Viewer | `observability_viewer` | Access to the Observability suite. |

> **Note**
>
> `GET /v1/admin/roles` returns the authoritative list of roles and their UUIDs. Assign roles by name with `role_names`, or by UUID with `roles`.

> **Note**
>
> Roles apply to non-human principals too. A [service account](https://docs.mistral.ai/admin/identity-access/service-accounts) holds the `workflow_executor` Workspace role so its worker can register and run workflows, and can additionally be granted the **Developer** role from the Admin Console.

## Assign roles {#assign-roles}

**In the Admin Panel**

1. Open [Admin Panel > Administration > Members](https://admin.mistral.ai/organization/members).
2. Select a member.
3. Choose one or more roles from the role selector. Changes apply immediately.

**With the Admin API**

Set Organization roles when creating or updating a user, and Workspace roles when adding members to a Workspace. You can also assign roles to an entire [user group](https://docs.mistral.ai/admin/identity-access/groups).

```bash
# Organization role
curl -X PATCH https://api.mistral.ai/v1/admin/users/<USER_UUID> \
  -H "Content-Type: application/json" -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"role_names": ["member"]}'

# Workspace role
curl -X PATCH https://api.mistral.ai/v1/admin/workspaces/<WORKSPACE_UUID>/users \
  -H "Content-Type: application/json" -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"members": [{"user_uuid": "<USER_UUID>", "role_names": ["workspace_admin"]}]}'
```
