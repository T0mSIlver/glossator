---
url: https://docs.mistral.ai/studio/observability/traces
title: Distributed tracing
breadcrumbs: [Studio, Observability]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/traces/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
hidden: true
---

# Distributed tracing

Every request in your AI application is captured as a **trace**: a tree of **spans** representing every step in the execution chain. Each span carries its input, output, latency, token counts, and status.

Traces are collected using [OpenTelemetry](https://opentelemetry.io/) and are supported across Mistral products and the Mistral SDK.

> **Info**
>
> **Data retention:** traces are kept for **30 days**.

## In this section

- [Send traces](https://docs.mistral.ai/studio/observability/traces/send-traces): instrument your application and start collecting trace data.
- [Explore traces](https://docs.mistral.ai/studio/observability/traces/explorer): search, filter, and inspect traces in Studio.
- [Data redaction](https://docs.mistral.ai/studio/observability/traces/data-redaction): review and configure what is masked before spans are exported.
