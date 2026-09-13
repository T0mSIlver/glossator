---
url: https://docs.mistral.ai/admin/user-management-finops/usage-limits
title: Usage limits
breadcrumbs: [Admin, User Management & Fin Ops]
kind: doc
locale: en
source_path: src/content/en/docs/admin/user-management-finops/usage-limits/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Usage limits

Set spending caps and usage thresholds to control costs across your Organization's Workspaces.

## Workspace spending limits {#workspace-limits}

Set a monthly spending cap per Workspace to prevent unexpected charges. When a Workspace reaches its limit, API requests are rejected until the next billing period or until you increase the limit.

To configure a spending limit:

1. Open [Workspace settings](https://admin.mistral.ai).
2. Set the **monthly spending limit**.
3. Save your changes.

## Rate limits {#rate-limits}

Rate limits are applied at the Workspace level and vary by [usage tier](https://docs.mistral.ai/admin/user-management-finops/tier). They include:

- **Requests per second (RPS)**: maximum concurrent API requests.
- **Tokens per minute**: throughput limit for token processing.
- **Tokens per month**: overall consumption cap.

View your current rate limits at [Limits](https://admin.mistral.ai/plateforme/limits).

## Monitor usage {#monitoring}

Track API consumption, token usage, and costs per Workspace from the Admin Panel. From the Workspace settings, click the **Usage** tab to see:

- An overview of your spending
- A detailed breakdown by API and services
- Input and output token costs per model

Use this data alongside spending limits to govern costs across teams and projects.
