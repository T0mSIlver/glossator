---
url: https://docs.mistral.ai/admin/user-management-finops/billing
title: Billing
breadcrumbs: [Admin, User Management & Fin Ops]
kind: doc
locale: en
source_path: src/content/en/docs/admin/user-management-finops/billing/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Billing

View and manage payment methods, invoices, and billing information for your Organization.

Requires the **Admin** or **Billing** role.

## Set up billing {#setup}

1. Open [Subscriptions › Billing](https://admin.mistral.ai/organization/billing).
2. Add a payment method (credit card or Google Pay).
3. Enter billing details: individual or company name, address, and VAT number if applicable.

You need billing set up to:

- Activate API keys beyond the free tier.
- Subscribe to Pro, Team, or Enterprise plans.

## Invoices {#invoices}

View and download invoices from the billing section of the Admin Panel. Invoices include:

- Subscription charges
- API usage charges (pay-as-you-go)
- Seat allocations

## Payment schedule {#payment-schedule}

- **Vibe subscriptions** (Pro, Team, Enterprise): billed at the start of each billing period (monthly or annual). These are fixed-price plans for Vibe access.
- **API usage** (Scale plan): billed based on consumption (tokens processed). There is no upfront cost; you pay only for what you use.
- **Plan upgrades**: when upgrading a Vibe subscription, payment is due immediately for the new plan.

## Billing scope {#billing-scope}

Billing is managed at the Organization level. All Workspace API usage within your Organization is consolidated into a single bill. Use [usage limits](https://docs.mistral.ai/admin/user-management-finops/usage-limits) to set spending caps per Workspace.
