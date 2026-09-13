---
url: https://docs.mistral.ai/admin/user-management-finops/tier
title: Rate limits and usage tiers
breadcrumbs: [Admin, User Management & Fin Ops]
kind: doc
locale: en
source_path: src/content/en/docs/admin/user-management-finops/tier/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Rate limits and usage tiers

When you use the Mistral API, your requests are subject to rate limits. These limits help us ensure fair usage, balance load, and prevent abuse.

Rate limits are set at the **Organization level**, meaning they apply across all Workspaces within your organization.

> **Info**
>
> Visit [Limits](https://admin.mistral.ai/plateforme/limits) to see the current rate limits and usage tier for your Workspace.

## How rate limits work {#how-rate-limits-work}

We enforce three types of limits:

- **Requests per second (RPS)**: the maximum number of concurrent API requests.
- **Tokens per minute**: throughput limit for token processing (input and output tokens combined).
- **Tokens per month**: overall consumption cap.

## Plans and tiers {#plans-and-tiers}

Rate limit tiers depend on your **Studio plan**:

> **Free mode (default)**
>
> Free mode is enabled by default with limited rate limits, intended for **evaluation and prototyping**. To increase your limits, upgrade to a **Scale** plan.

> **Scale plan (pay-as-you-go)**
>
> The Scale plan gives you access to Tier 1 and above. Upgrade in [Subscriptions](https://admin.mistral.ai/organization/billing).

## Usage tiers {#usage-tiers}

Once on the **Scale** plan, tier upgrades happen **automatically** based on your cumulative billed amount:

| Cumulative billing | Tier | Upgrade |
|--------------------|------|---------|
| $0 / €0 (Free mode) | Free | Limited rate limits for evaluation and prototyping |
| $0 / €0 (Scale plan) | Tier 1 | Automatic on plan upgrade |
| > $20 / €20 | Tier 2 | Automatic |
| > $100 / €100 | Tier 3 | Automatic |
| > $500 / €500 | Tier 4 | Automatic |
| > $2,000 / €2,000 | Higher limits | Contact [support](https://help.mistral.ai) |

Cumulative billing is the total sum of all your invoices, not a monthly amount.

## Request higher limits {#increasing-limits}

To request limits beyond Tier 4, you must first **reach Tier 4** and **meet the required billing threshold** (> $2,000 / €2,000). Then, contact [support](https://help.mistral.ai) with:

- Your target requests per second
- The specific model you plan to use
- An estimate of tokens required per minute and per month
