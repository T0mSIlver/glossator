---
url: https://docs.mistral.ai/admin/billing-usage/usage-limits
title: Usage and limits
breadcrumbs: [Admin, Billing and usage]
kind: doc
locale: en
source_path: src/content/en/docs/admin/billing-usage/usage-limits/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Usage and limits

Use **Usage and limits** to understand how your Organization consumes Mistral services and which limits apply. This page covers the global usage dashboard, Organization spending limits, Workspace spending limits, and API rate limits.

## Open usage and limits {#open-usage-and-limits}

Use these Admin Panel pages depending on what you need to check or change:

| Task | Admin Panel page |
| --- | --- |
| Review usage and cost breakdowns | [Admin Panel > API > Usage](https://admin.mistral.ai/organization/usage) |
| Review API rate limits | [Admin Panel > API > Limits](https://admin.mistral.ai/plateforme/limits) |
| Set the Organization spending limit | [Admin Panel > Subscriptions > Billing](https://admin.mistral.ai/organization/billing) |
| Set a Workspace spending limit | [Admin Panel > Administration > Workspaces](https://admin.mistral.ai/organization/workspaces) |

## Usage dashboard {#usage-dashboard}

The usage dashboard shows Organization usage for a selected billing period. Use it to understand spend, identify heavy usage areas, and decide whether to adjust Workspace caps or API limits.

The dashboard can show:

- total cost;
- cost per day;
- completion usage;
- Vibe usage beyond quota;
- OCR usage;
- Agents and Connectors usage;
- Libraries API usage;
- Audio usage;
- Document Library storage.

### Usage breakdowns {#usage-breakdowns}

Use breakdowns to find where usage comes from. Depending on the service, the dashboard can break usage down by:

- model;
- input and output tokens;
- API or capability;
- Workspace;
- storage and Libraries.

For programmatic usage reporting, see [Usage metrics with the Admin API](https://docs.mistral.ai/admin/admin-api/usage-metrics).

## Organization spending limit {#organization-spending-limit}

The Organization monthly spending limit caps API and Vibe consumption across the Organization. It uses the Organization billing currency.

> **Warning**
>
> If the Organization reaches its monthly spending limit, API access can be suspended until the next month begins or an admin increases the limit. If recent invoice payments fail, access can also be affected until the payments are processed again.

Workspace spending limits cannot exceed the Organization spending limit. To manage payments, credits, billing information, and invoices, see [Billing](https://docs.mistral.ai/admin/billing-usage/billing).

## Workspace spending limits {#workspace-spending-limits}

A Workspace spending limit caps API and Vibe consumption for one Workspace. Use Workspace caps to model team budgets, project budgets, or environment boundaries.

To configure a Workspace cap:

1. Open [Admin Panel > Administration > Workspaces](https://admin.mistral.ai/organization/workspaces).
2. Select the Workspace.
3. Open the **Settings** tab.
4. Set **Monthly spending limit**.
5. Save your changes.

For a full Workspace-focused guide, see [Workspace usage and limits](https://docs.mistral.ai/admin/workspaces/usage-limits).

## API rate limits {#api-rate-limits}

API rate limits define how much traffic your Organization can send. They are shown in [Admin Panel > API > Limits](https://admin.mistral.ai/plateforme/limits).

### Completion rate limits {#completion-rate-limits}

Completion rate limits are listed per model and include:

- **Tokens per minute**: the token throughput limit for the model.
- **Requests per second**: the request throughput limit for the model.

### Audio rate limits {#audio-rate-limits}

Audio limits apply to audio API consumption and can include:

- audio seconds per minute;
- audio seconds per month.

### Document OCR rate limits {#ocr-rate-limits}

Document OCR limits apply to OCR API consumption and can include pages per minute.

### Document limits {#document-limits}

Document limits control document upload and download behavior. They can include:

- maximum file size for document uploads;
- whether users can download documents from Libraries.

## API plan and usage tiers {#api-plan-and-tiers}

Your API plan affects the limits available to your Organization.

- **Free mode** lets you create API keys and use the free tier within the limits shown on the Limits page.
- **Scale** is the pay-as-you-go API plan. It gives access to paid API usage and higher limits.

For current API pricing and model availability, see [API and model pricing](https://mistral.ai/pricing/#api). To review your plan, see [Subscriptions](https://docs.mistral.ai/admin/billing-usage/subscriptions).

## Request higher limits {#request-higher-limits}

If you need higher limits, contact [support](https://help.mistral.ai) with:

- the models or APIs you plan to use;
- the target requests per second;
- the expected tokens per minute and tokens per month;
- a short description of your use case.
