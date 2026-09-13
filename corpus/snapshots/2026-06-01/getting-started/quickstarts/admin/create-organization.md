---
url: https://docs.mistral.ai/getting-started/quickstarts/admin/create-organization
title: Create your organization
breadcrumbs: [Getting started, Quickstarts, Admin]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/admin/create-organization/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Create your organization

Set up a Mistral organization from a new account through [Admin](https://admin.mistral.ai).

- Activate billing so API keys work
- Create your first workspace
- Invite team members and assign roles

Once complete, your team has working API keys and access to the platform.

**Time to complete:** ~15 minutes

## Prerequisites {#prerequisites}

- A Mistral AI account. [Create account](https://console.mistral.ai)
- A credit card or cloud billing account (AWS or Azure Marketplace).
- The email address of at least one colleague to invite.

## Step 1: Create your organization {#step-1}

Log in to [Studio](https://console.mistral.ai). New accounts are prompted to name their organization and redirected to Admin automatically.

Already have an account without an organization? Open [Admin](https://admin.mistral.ai) and follow the setup prompt.

## Step 2: Activate billing {#step-2}

Team members can't generate working API keys until billing is active.

Open [Subscriptions › Billing](https://admin.mistral.ai/organization/billing), click **Add payment method**, and connect your card or cloud marketplace account. Optionally set a **Monthly spending limit** before saving.

Billing takes 2–3 minutes to take effect. If team members report inactive API keys right after, ask them to wait and retry.

## Step 3: Create a workspace {#step-3}

Your default workspace is created automatically: skip this step if one workspace is enough.

Open [Manage › Workspaces](https://admin.mistral.ai/organization/workspaces), click **Create workspace**, and give it a name (for example, "Engineering" or "Production").

## Step 4: Invite team members {#step-4}

Open [Administration › Members](https://admin.mistral.ai/organization/members), click **Invite member**, enter the email address, and assign a role:

| Role | Permissions |
| --- | --- |
| **Admin** | Full control: organization settings, users, security, billing |
| **Billing** | Subscriptions, invoices, and payment methods only |
| **Member** | Uses models and creates API keys within their workspace |

## Step 5: Security and monitoring {#step-5}

As your team grows, control who can access what.

**Configure SSO:**
Enforce enterprise authentication with SAML-based SSO. Navigate to **Administration › Settings** in the Admin panel to configure your identity provider and define an **Allowed email domain** to block invites to personal or external addresses.

**Monitor audit logs:**
Open [Administration › Audit logs](https://admin.mistral.ai/audit-logs) to track critical events. This gives you a record of when API keys were created, who was invited, and when billing settings changed.

## Verify {#verify}

The invited team member receives an email within a few minutes. Once they accept, their status in [Administration › Members](https://admin.mistral.ai/organization/members) changes from **Pending** to **Active**.

## What's next {#whats-next}

- [Configure SSO](https://docs.mistral.ai/getting-started/quickstarts/admin/configure-sso)

- [Manage workspaces](https://docs.mistral.ai/getting-started/quickstarts/admin/manage-workspaces)
