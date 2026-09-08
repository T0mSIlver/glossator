---
url: https://docs.mistral.ai/admin/admin-api/overview
title: Overview
breadcrumbs: [Admin, Admin API]
kind: doc
locale: en
source_path: src/content/en/docs/admin/admin-api/overview/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Admin API overview

The Admin API is an Enterprise-only feature that lets Organization administrators and solutions engineers automate account management. Use it to provision users, manage Workspaces and groups, rotate API keys, set spend and rate limits, and retrieve usage and audit logs.

> **Info**
>
> The Admin API is in **Preview** and available on Enterprise plans. Endpoints and fields can change as we refine the API.

## Concepts {#concepts}

Most Admin docs describe one Organization. Some Enterprise customers also have an **Enterprise Account**, which groups several Organizations when they need stronger isolation between groups of users than Workspaces provide.

The **Backoffice** ([backoffice.mistral.ai](https://backoffice.mistral.ai)) manages Enterprise Accounts, their Organizations, their members, and each Organization's **Admin API keys**. For the product model, see [Enterprise Accounts and Backoffice](https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts).

> **Warning**
>
> The Backoffice is not the Admin Panel. The Admin Panel (`admin.mistral.ai`) administers a single Organization. The Backoffice (`backoffice.mistral.ai`) manages an Enterprise Account and the Organizations under it.

A **user group** bundles users so you can manage them together. For example, create a group, add members, then assign the group to a Workspace with a given role. See [Groups](https://docs.mistral.ai/admin/identity-access/groups).

## Authentication {#authentication}

The Admin API uses a dedicated **Admin API key**, created in the Backoffice and passed in the `x-api-key` header. A user's standard API key never grants admin access. See [Authentication and Admin API keys](https://docs.mistral.ai/admin/admin-api/authentication) for details.

## Capabilities {#capabilities}

Use the Admin API to manage:

- **Users and invitations**: see [User management](https://docs.mistral.ai/admin/identity-access/user-management)
- **Groups**: see [Groups](https://docs.mistral.ai/admin/identity-access/groups)
- **Workspaces**: see [Your first Workspace](https://docs.mistral.ai/admin/workspaces/your-first-workspace)
- **API keys**: see [API keys](https://docs.mistral.ai/admin/identity-access/api-keys)
- **Spend and rate limits**: see [Usage and limits](https://docs.mistral.ai/admin/billing-usage/usage-limits)
- **Usage**: see [Usage metrics with the Admin API](https://docs.mistral.ai/admin/admin-api/usage-metrics)
- **Audit logs**: see [Audit logs](https://docs.mistral.ai/admin/monitor-comply/audit-logs/overview)

## Roles and permissions {#roles}

Several endpoints accept role fields by UUID (`roles`) or by name (`role_names`). Workspace assignment endpoints accept `workspace_role` (UUID) or `workspace_role_name` (name). When RBAC is enabled, list the available roles and their UUIDs with `GET /v1/admin/roles`.

> **Note**
>
> Singular role fields (`role`, `role_name`) are deprecated. Use the plural equivalents (`roles`, `role_names`), which support assigning multiple roles to a user.

For the full role model, see [Roles and permissions](https://docs.mistral.ai/admin/identity-access/roles-permissions).

## In this section {#in-this-section}

- [Authentication and Admin API keys](https://docs.mistral.ai/admin/admin-api/authentication)

- [Manage users](https://docs.mistral.ai/admin/admin-api/manage-users)

- [Manage Workspaces](https://docs.mistral.ai/admin/admin-api/manage-workspaces)

- [Manage groups and roles](https://docs.mistral.ai/admin/admin-api/manage-groups-roles)

- [User provisioning](https://docs.mistral.ai/admin/admin-api/user-provisioning)

- [Usage metrics](https://docs.mistral.ai/admin/admin-api/usage-metrics)

- [API reference](https://docs.mistral.ai/admin/admin-api/api-reference)
