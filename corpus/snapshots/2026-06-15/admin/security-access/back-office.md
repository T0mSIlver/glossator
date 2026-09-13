---
url: https://docs.mistral.ai/admin/security-access/back-office
title: Admin Panel
breadcrumbs: [Admin, Security & Access]
kind: doc
locale: en
source_path: src/content/en/docs/admin/security-access/back-office/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Admin Panel

The [Admin Panel](https://admin.mistral.ai) is where you manage your organization's settings, users, billing, and security. It's the central hub for everything administrative across Vibe and Studio.

## Accessing the Admin Panel {#access}

You can reach the Admin Panel in two ways:

- **Direct URL**: go to [Admin Panel](https://admin.mistral.ai).
- **From Studio or Vibe**: expand the main menu and select **Admin**.

You don't need to log in separately. Sessions are shared across Vibe, Studio, and the Admin Panel, so switching between products is instant.

## Admin Panel vs. Studio {#admin-vs-studio}

The Admin Panel and Studio serve different purposes:

- [Admin Panel](https://admin.mistral.ai): for setup and administration. Manage billing, subscriptions, SSO, user invitations, audit logs, and organization settings.
- [Studio](https://console.mistral.ai): for building and using tools. Create API keys, manage Workspace members, and run batch jobs.

## Access by role {#roles}

What you see in the Admin Panel depends on your organization role:

| Role | What you can do |
|------|-----------------|
| **Admin** | Full control: organization settings, member management, security configuration, billing, privacy, audit logs |
| **Billing** | Subscriptions, invoices, payment methods, and usage information. Can't invite users or change organization settings |
| **Member** | Profile settings and preferences. Read-only view of organization information |

## What you can manage {#what-you-can-manage}

From the Admin Panel, administrators can:

- **Organization**: rename, configure settings, view the Organization ID
- **Members**: invite users, assign seats and roles, remove members
- **Workspaces**: create isolated environments with independent API keys and usage tracking
- **Access**: configure SSO and Email Domain Authentication
- **Billing**: manage payment methods, subscriptions, and invoices
- **Usage limits**: set spending caps per Workspace
- **Audit logs**: monitor activity across the organization (Enterprise)
- **Privacy**: configure data handling and training opt-out settings
