---
url: https://docs.mistral.ai/admin/security-access/organization
title: Organizations and Workspaces
breadcrumbs: [Admin, Security & Access]
kind: doc
locale: en
source_path: src/content/en/docs/admin/security-access/organization/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Organizations and Workspaces

Your Mistral AI account is structured around two levels: **Organizations** and **Workspaces**. Organizations handle billing, user management, and security. Workspaces give you isolated environments for projects, teams, or API usage.

## Organizations {#organizations}

An Organization is the top-level entity for your company or team. When you create an account, a default Organization is created automatically. If your company email matches an existing Organization with [Email Domain Authentication](https://docs.mistral.ai/admin/security-access/email-domain-auth) enabled, you may be prompted to join it.

At the Organization level, administrators can manage:

- **Billing** for all Workspaces
- **Subscriptions** (Vibe and Studio)
- **Members** and role assignments
- **Security** settings (SSO, domain authentication)
- **Privacy** and data handling preferences
- **Audit logs** (Enterprise)

Every Organization has a unique **Organization ID** that you can reference in API calls or when contacting support.

## Workspaces {#workspaces}

A Workspace is an isolated environment within your Organization. Each Workspace has its own API keys, member access list, and usage tracking.

Workspaces are useful for:

- **Separating environments**: keep development, staging, and production isolated
- **Scoping API keys**: keys created in a Workspace only access that Workspace's resources
- **Tracking costs**: monitor usage and spending per team or project
- **Sharing resources**: datasets and batch jobs are shared among Workspace members
- **Scoping Vibe Work usage**: chat history, [Projects](https://docs.mistral.ai/vibe/work/projects), [Skills](https://docs.mistral.ai/vibe/work/skills), [Scheduled tasks](https://docs.mistral.ai/vibe/work/scheduled-tasks), and Connector authentications are tied to the active Workspace. [Libraries](https://docs.mistral.ai/vibe/work/libraries) are also workspace-scoped by default; admins can additionally allow Org-level sharing so a Library is visible across all Workspaces. See [Switch Organization or Workspace](https://docs.mistral.ai/vibe/work/switch-organization-workspace) for the user view.

> **Tip**
>
> You can create unlimited Workspaces regardless of your plan. On Team and Enterprise plans, you can add multiple members to each Workspace. On other plans, Workspaces are single-user.

## Workspace roles {#workspace-roles}

Workspace roles are **independent** from Organization roles. A user with the Member role at the Organization level can be an Admin within a specific Workspace.

| Role | Permissions |
|------|-------------|
| **Admin** | Full control over the Workspace: manage settings, add and remove members, create and delete API keys |
| **Member** | Use Workspace resources (API keys, models, datasets). Can't change Workspace settings |

## Create an Organization {#create-organization}

You can create a new Organization at any time:

1. Click on your organization name in the top-left corner of Studio.
2. Click **Create** in the Organizations section.
3. Enter a name and accept the terms of service.

## Create a Workspace {#create-workspace}

Only Organization Admins can create Workspaces.

1. Open [Workspaces](https://admin.mistral.ai).
2. Click **New workspace**.
3. Configure the Workspace:
   - **Name** (required): a clear label for the Workspace.
   - **Description** (optional): context about the Workspace's purpose.
   - **Members** (optional): add Organization members now, or later.
4. Click **Create**.

You can also create Workspaces from Studio by clicking your organization name and selecting **+ Add** in the Workspaces section.

## Manage Workspace members {#manage-members}

To add or manage members in a Workspace, users must already be members of your Organization.

1. Open the Workspace settings.
2. Click the **Members** tab.
3. Click **Add Members** and select users from your Organization.
4. Assign a Workspace role (Admin or Member).

Changes apply immediately. You can update roles or remove members at any time.

## Workspace settings {#workspace-settings}

Workspace Admins can customize:

- **Name** and **description**
- **Icon** (optional emoji)
- **Permissions**: control whether members can create API keys
- **Spending limits**: set a monthly spending cap for the Workspace
- **Vibe Work tools**: enable or disable specific tools and Connectors for this Workspace
- **Vibe Work chat retention**: how long chats are kept before being deleted

## Archive a Workspace {#archiving}

If you no longer need a Workspace, you can archive it from the Workspace settings.

> **Warning**
>
> Archiving a Workspace is permanent and can't be undone. All API keys in the Workspace stop working immediately.
