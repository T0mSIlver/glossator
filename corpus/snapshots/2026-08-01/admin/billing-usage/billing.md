---
url: https://docs.mistral.ai/admin/billing-usage/billing
title: Billing
breadcrumbs: [Admin, Billing and usage]
kind: doc
locale: en
source_path: src/content/en/docs/admin/billing-usage/billing/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Billing

Use Billing to manage how your Organization pays for Mistral services. This includes payment methods, billing information, credits, monthly spending limits, usage for the current month, and invoices.

You need the **Admin** or **Billing** Organization role to manage billing.

## Open Billing {#open-billing}

Open [Admin Panel > Subscriptions > Billing](https://admin.mistral.ai/organization/billing).

## Payment methods {#payment-methods}

Use **Payment methods** to add or update the payment method for your Organization. If no payment method is configured, the Billing page shows that no payment method has been added.

## Billing information {#billing-information}

Use **Billing information** to update the billing profile for your Organization. This information appears on future invoices.

## Credits {#credits}

Use **Credits** to review the credit balance available to your Organization. The Billing page shows:

- current credit balance;
- pending pay-as-you-go usage;
- credit history, including grants, purchases, remaining balance, expiration, and status.

You can also redeem a gift code from this section.

## Monthly spending limit {#monthly-spending-limit}

Use **Monthly spending limit (API and Vibe)** to configure a monthly usage cap for API and Vibe consumption at the Organization level.

> **Warning**
>
> If the limit is reached, API access can be suspended until the next month begins or an admin increases the limit. If recent invoice payments fail, access can also be affected until the payments are processed again.

The Organization spending limit applies across the Organization. Workspace spending limits cannot exceed it. For Workspace-specific caps, see [Workspace usage and limits](https://docs.mistral.ai/admin/workspaces/usage-limits).

## Current usage {#current-usage}

The **Usage** section shows current API usage for the ongoing month. It can include:

- current usage;
- monthly limit;
- API usage.

For detailed usage breakdowns by day, model, capability, and Workspace, see [Usage and limits](https://docs.mistral.ai/admin/billing-usage/usage-limits).

## Invoices {#invoices}

The **Invoices** section lists past invoices with their invoice ID, date, amount, payment status, type, and download action.

To learn how to read and download invoices, see [Invoices](https://docs.mistral.ai/admin/billing-usage/invoices).
