---
url: https://docs.mistral.ai/admin/workspaces/usage-limits
title: Workspace usage and limits
breadcrumbs: [Admin, Configure Workspaces]
kind: doc
locale: en
source_path: src/content/en/docs/admin/workspaces/usage-limits/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Manage Workspace usage and limits

Each Workspace tracks its own API and Vibe consumption. Use Workspace-level usage and limits to understand which teams, products, or environments drive spend, then set caps that match their budget or risk profile.

## Monitor Workspace usage {#monitor-usage}

Workspace usage is available from the Workspace detail view in the Admin Panel.

1. Open [Admin Panel > Administration > Workspaces](https://admin.mistral.ai/organization/workspaces).
2. Select the Workspace.
3. Open the **Usage** tab.

The usage view can show:

- month-to-date spend;
- token consumption;
- usage by model;
- usage by capability, such as OCR.

Studio also shows usage for the active Workspace directly in the console.

## Set a monthly spending limit {#spending-limits}

A monthly spending limit caps API and Vibe consumption for one Workspace. By default, Workspaces have no monthly cap.

1. Open [Admin Panel > Administration > Workspaces](https://admin.mistral.ai/organization/workspaces).
2. Select the Workspace.
3. Open the **Settings** tab.
4. Enter a value in **Monthly spending limit**.
5. Save your changes.

To remove a cap, clear the field and save. This resets the limit to **Never**.

> **Note**
>
> The Workspace spending limit uses your Organization's billing currency. It cannot be higher than the Organization spending limit.

> **Warning**
>
> If a Workspace reaches its monthly spending limit, API access for that Workspace is suspended until the next month begins or an admin increases the limit. If recent invoice payments fail, access can also be affected until the payments are processed again.

## Understand rate limits {#rate-limits}

Rate limits apply at the Workspace level and are shared across all API keys in that Workspace. If multiple applications use keys from the same Workspace, their combined traffic counts against the same limits.

Rate limits include:

- **Requests per second (RPS)**: maximum concurrent API requests.
- **Tokens per minute**: throughput limit for token processing.
- **Tokens per month**: overall consumption cap.

View your current rate limits at [Admin Panel > API > Limits](https://admin.mistral.ai/plateforme/limits). For more details, see [Usage and limits](https://docs.mistral.ai/admin/billing-usage/usage-limits).

## Cost-control patterns {#cost-control-patterns}

Use Workspace-level usage and limits to model operational boundaries:

- **Environment isolation**: create separate Workspaces for development, staging, and production, each with its own cap.
- **Team budgets**: create one Workspace per team and set a cap that matches that team's monthly allocation.
- **Project billing**: create a dedicated Workspace for each customer project to attribute and cap costs per engagement.

When a Workspace reaches its limit, only that Workspace is affected. Other Workspaces in the Organization continue operating normally.
