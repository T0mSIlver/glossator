---
url: https://docs.mistral.ai/studio-api/observability
title: Observability
breadcrumbs: [Studio]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/observability/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Observability

Observability helps you understand what your LLM applications are doing in production, measure response quality at scale, and iterate with confidence.

> **Info**
>
> The entire Observability suite (Explorer, Judges, Campaigns, and Datasets) is available to **Enterprise-tier organizations** only.

## What Observability does {#what-observability-does}

The Observability suite gives you three core capabilities:

- **Visibility**: see what's happening in your production traffic, event by event.
- **Quality signals**: score and classify assistant responses automatically with LLM-powered [Judges](https://docs.mistral.ai/studio-api/observability/judges).
- **Iteration loops**: use [Campaigns](https://docs.mistral.ai/studio-api/observability/campaigns) to annotate traffic at scale and build quality-tagged [Datasets](https://docs.mistral.ai/studio-api/observability/datasets).

## The four components {#the-four-components}

These capabilities are built around four components that work together.

**Explorer**

Explorer lets you **search**, **filter**, and **inspect every chat completion event** flowing through your workspace.

You can **explore individual conversations** (including messages, tool calls, and metadata) and **export filtered slices** to [Datasets](https://docs.mistral.ai/studio-api/observability/datasets) for deeper analysis.

When to use it?

 *You want to understand what's happening in production, investigate a quality issue, or find representative examples for later analysis.*

[Go to Explorer →](https://docs.mistral.ai/studio-api/observability/explorer)

**Judges**

Judges are Agents that **grade chat completion events** based on criteria you define.

Two types of Judges are available:
- **Classification:** Outputs discrete labels (e.g., pass/fail, safe/unsafe, topic categories).
- **Regression:** Outputs a numeric score within a defined range (e.g., a 1–5 helpfulness rating).

When to use it?

 *You need to programmatically evaluate model outputs across large volumes of traffic.*

> **Note**
>
> Judges are not run directly: **attach them to** [Campaigns](https://docs.mistral.ai/studio-api/observability/campaigns) to score live traffic.

[Go to Judges →](https://docs.mistral.ai/studio-api/observability/judges)

**Campaigns**

Campaigns uses [Judges](https://docs.mistral.ai/studio-api/observability/judges) to **evaluate your production traffic** at scale.

Annotations are saved to [Explorer](https://docs.mistral.ai/studio-api/observability/explorer), allowing you to **filter and export conversations** by quality label later.

When to use it?

 *You want to score a batch of production traffic to find problems or build quality-tagged datasets.*

[Go to Campaigns →](https://docs.mistral.ai/studio-api/observability/campaigns)

**Datasets**

Datasets are **collections of conversation records** (including messages, properties, and metadata).

Build them from [Explorer](https://docs.mistral.ai/studio-api/observability/explorer) searches, [Campaign](https://docs.mistral.ai/studio-api/observability/campaigns) results, or import your own data via JSONL files.

When to use it?

 *Use Datasets to curate, edit, and reuse conversation records for analysis or Judge evaluation.*

> **Tip**
>
> Datasets are **fully editable**: add expected outputs, fix messages, and remove noise directly in [Studio](https://console.mistral.ai/observability/datasets).

[Go to Datasets →](https://docs.mistral.ai/studio-api/observability/datasets)

## How they connect {#how-they-connect}

The typical flow moves from left to right:

![A flow diagram showing the Observability workflow: Explorer → Judge → Campaign → Explorer (filter by annotations) → Dataset. Arrows indicate data flow.](https://docs.mistral.ai/img/observability_basic_flow.svg)

> **Tip**
>
> You don't need to follow this exact sequence. Adjust the workflow based on your specific needs.

## Next steps {#next-steps}

**End-to-end guide**
- [Observability quickstart](https://docs.mistral.ai/studio-api/observability/quickstart) — Learn how to set up a Judge and get a quality signal from real traffic.

**Component deep dives**
- [Explorer](https://docs.mistral.ai/studio-api/observability/explorer) — Search, filter, inspect, and export production events.
- [Judges](https://docs.mistral.ai/studio-api/observability/judges) — Design and configure automated scoring criteria.
- [Campaigns](https://docs.mistral.ai/studio-api/observability/campaigns) — Run batch annotations on live production traffic.
- [Datasets](https://docs.mistral.ai/studio-api/observability/datasets) — Build and manage curated collections of conversation records.
