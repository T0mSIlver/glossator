---
url: https://docs.mistral.ai/admin/overview
title: Admin overview
breadcrumbs: [Admin]
kind: doc
locale: en
source_path: src/content/en/docs/admin/overview/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Admin overview

The [Admin Panel](https://admin.mistral.ai) is the control surface for your Organization. It brings together the main tools you need to set up your Organization, manage access, track usage, and automate administration.

## Open Admin {#open-admin}

You can open Admin in two ways:

- Go directly to [Admin Panel](https://admin.mistral.ai).
- From Vibe or Studio, open the main menu and select `Admin`.

> **Info**
>
> You don't need to sign in again. Sessions are shared across Vibe, Studio, and the Admin Panel.

> **Note**
>
> You need an Organization admin or Workspace admin role to access Admin. The pages and actions you can use depend on your role.

## How Admin fits together {#how-admin-fits-together}

While teams use **Vibe** to work with Mistral models and coding tools, and **Studio** to build applications with Mistral APIs and services, **Admin** is where you manage the resources behind that work. It defines who can access Mistral products, how teams and Workspaces are organized, how usage is tracked, and which policies apply.

At its core, the Admin model is built around three concepts:

- **Organization**: your company's top-level account.
- **Workspaces**: separate areas used to organize teams, products, environments, or budgets.
- **Members**: the people who belong to that Organization.

Members belong to an Organization and gain access to one or more Workspaces through roles, groups, and provisioning rules.

> **Info**
>
> The **Admin API** controls the same model programmatically. If you're on an Enterprise or Team plan, you can use it to [automate administration](https://docs.mistral.ai/admin/admin-api/overview), including Organization management, member lifecycle operations, Workspace administration, and access workflows.

### Organization-level settings {#organization-level-settings}

Organization-level settings apply across the whole Organization, such as access, billing, and compliance settings:

- [Verify your domain](https://docs.mistral.ai/admin/set-up-organization/verify-domain) before you configure sign-in methods.
- [Configure SAML SSO](https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso) if your Organization uses single sign-on.
- [Manage subscriptions](https://docs.mistral.ai/admin/billing-usage/subscriptions) and [billing](https://docs.mistral.ai/admin/billing-usage/billing).
- [Review audit logs](https://docs.mistral.ai/admin/monitor-comply/audit-logs/overview) and [privacy controls](https://docs.mistral.ai/admin/monitor-comply/privacy-data-controls).

### Members, roles, and groups {#members-roles-and-groups}

Members are the people in your Organization. Roles define what a member can view or change, and seats control access to paid products. For setup steps, see [Manage identity and access (RBAC)](https://docs.mistral.ai/admin/identity-access/user-management).

> **Tip**
>
> Use _role-based access control_ (_RBAC_) to grant only the permissions that each person needs. Groups help you manage access for multiple members at once. _System for Cross-domain Identity Management_ (_SCIM_) support will automate onboarding and offboarding when it becomes generally available.

### Workspaces {#workspaces}

Workspaces separate teams, products, environments, or business units inside the same Organization. Each Workspace can have its own members, usage, and limits.

Use Workspaces when teams need separate budgets, usage tracking, access boundaries, or product areas. For setup details, see [Create your first Workspace](https://docs.mistral.ai/admin/workspaces/your-first-workspace).

## Get started {#get-started}

If you're setting up Admin for the first time, configure your Organization first. These settings apply to every member and Workspace. If you already know what you need, choose a section below:

- [Set up your Organization](https://docs.mistral.ai/admin/set-up-organization/create-organization) — Configure the Admin Panel, Organization settings, and sign-in methods.

- [Manage access](https://docs.mistral.ai/admin/identity-access/roles-permissions) — Invite members, assign roles, create groups, and prepare SCIM.

- [Create Workspaces](https://docs.mistral.ai/admin/workspaces/your-first-workspace) — Separate teams, environments, feature access, API keys, and usage.

- [Review usage and limits](https://docs.mistral.ai/admin/billing-usage/usage-limits) — Track usage, spending limits, invoices, and API rate limits.

- [Automate administration](https://docs.mistral.ai/admin/admin-api/overview) — Use the Admin API for provisioning, Workspaces, groups, keys, and usage metrics.

- [Monitor and comply](https://docs.mistral.ai/admin/monitor-comply/audit-logs/overview) — Review audit logs and privacy controls.
