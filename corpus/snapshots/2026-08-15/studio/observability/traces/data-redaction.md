---
url: https://docs.mistral.ai/studio/observability/traces/data-redaction
title: Data redaction
breadcrumbs: [Studio, Observability, Distributed tracing]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/traces/data-redaction/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
hidden: true
---

# Data redaction

Spans capture the input and output of each operation, including prompts, responses, and tool call arguments and results. This data can contain secrets or personally identifiable information (PII). To limit what leaves your environment, Mistral applies **client-side redaction**: spans are scrubbed on the machine that produces them, before they are exported to our platform.

Redaction is **on by default** across Mistral products and SDKs. It is best-effort and based on regular expressions, so it removes the patterns it recognizes while keeping the structure of your spans intact. The one exception is when you run your own OpenTelemetry pipeline, where you opt in explicitly (see below).

> **Caution**
>
> Redaction is a safety net, not a guarantee. The default policy targets common secret and PII patterns, but it can miss free-form PII or secrets that do not match a known pattern. Do not rely on it as the only control for highly sensitive data.

## How redaction works {#how-it-works}

Redaction runs at the OpenTelemetry exporter level, so it applies to every span regardless of how the span was created. Each span attribute is inspected and rewritten according to the active policy before the span is sent. The original, unredacted span never leaves the process.

Because it runs on the client, redaction adds no extra round trip and keeps sensitive data off the network entirely.

## Redaction policies {#policies}

Every surface exposes the same three modes. The SDKs additionally let you supply your own policy.

| Mode               | What it does                                                                                                                                                                    | Trade-off                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `default` (on)     | Content-oriented. Scans string values and redacts matched secrets and PII (API tokens, emails, card-like sequences, IPv4 addresses) while keeping attribute keys and structure. | Preserves most observability value. Best-effort, so it may miss patterns outside the known set. |
| `strict`           | Key-oriented. Redacts whole values for sensitive keys and all non-primitive values, then scans the remaining values for secret patterns.                                        | Very conservative. Erases most prompt and response content.                                     |
| `none`             | No redaction. Spans are exported as captured.                                                                                                                                   | Full fidelity. Use only in trusted environments.                                                |
| Custom (SDKs only) | Supply your own policy or a per-attribute callback that decides how each value is masked.                                                                                       | Full control. You own the logic.                                                                |

## Redaction by source {#by-source}

| Source                   | Default | Configurable                                                         |
| ------------------------ | ------- | -------------------------------------------------------------------- |
| Mistral SDK (Python)     | On      | Fully (including a custom callback policy)                           |
| Mistral SDK (TypeScript) | On      | Fully (including a custom callback policy)                           |
| Workflows                | On      | Yes on workers you run; hosted workers only in dedicated deployments |
| Vibe Code CLI            | On      | Yes                                                                  |
| Vibe Work                | On      | Only in dedicated deployments                                        |
| Vibe Code Web            | On      | Only in dedicated deployments                                        |
| Custom (OTEL)            | Off     | Fully (including a custom callback policy)                           |

## Configure redaction {#configure}

**Mistral SDK (Python)**

Redaction is on by default in dedicated mode. Pass the `redaction` argument to change it:

```python
from mistralai.extra.observability import (
    configure_telemetry,
    AttributeRedactionPolicy,
)

configure_telemetry(client)                                        # default policy
configure_telemetry(client, redaction=AttributeRedactionPolicy())  # strict, key-oriented
configure_telemetry(client, redaction=False)                       # disabled
configure_telemetry(                                               # custom per-attribute callback
    client,
    redaction=lambda key, value: None if "email" in key else value,
)
```

> **Note**
>
> If you point the SDK at your own OpenTelemetry setup instead of letting it manage tracing, the SDK no longer owns the exporter and the `redaction` argument has no effect. Redact in your own pipeline instead (see the **Custom (OTEL)** tab).

For more detail, see the [redaction section of the SDK README](https://github.com/mistralai/client-python#redaction) and the [observability examples](https://github.com/mistralai/client-python/tree/main/examples/mistral/observability).

**Mistral SDK (TypeScript)**

Redaction is on by default in dedicated mode. Pass the `redaction` option to change it:

```typescript
import {
  configureTelemetry,
  AttributeRedactionPolicy,
} from "@mistralai/mistralai/extra/observability";

await configureTelemetry(client); // default policy
await configureTelemetry(client, "dedicated", { redaction: new AttributeRedactionPolicy() }); // strict
await configureTelemetry(client, "dedicated", { redaction: false }); // disabled
await configureTelemetry(client, "dedicated", {
  // custom callback
  redaction: (key, value) => (key.includes("email") ? undefined : value),
});
```

> **Note**
>
> If you point the SDK at your own OpenTelemetry setup instead of letting it manage tracing, the SDK no longer owns the exporter and the `redaction` option has no effect. Redact in your own pipeline instead (see the **Custom (OTEL)** tab).

For more detail, see the [redaction section of the SDK README](https://github.com/mistralai/client-ts#redaction) and the [observability examples](https://github.com/mistralai/client-ts/tree/main/examples/src/observability).

**Workflows**

Set the `OTEL_REDACTION` environment variable on the Workflows service. This is an infrastructure-level setting:

```bash
OTEL_REDACTION=default  # default | strict | none
```

Redaction applies to every span before OTLP export, independently of the `OTEL_ENABLED` master switch.

On workers you run yourself, set this variable directly. On Mistral-hosted workers the default policy is applied for you and is not configurable, except in dedicated deployments where the level is set for the whole deployment.

**Vibe Code CLI**

Set the redaction mode in your Vibe Code CLI configuration:

```bash
# Single session
VIBE_OTEL_REDACTION=strict vibe

# Permanent setting in ~/.vibe/config.toml
otel_redaction = "default"  # default | strict | none
```

**Vibe Work and Vibe Code Web**

Vibe Work and Vibe Code Web traces are redacted with the default policy before they leave Mistral's infrastructure. In Mistral's hosted service this is managed for you and is not configurable. In a dedicated deployment, the redaction level is set for the whole deployment.

**Custom (OTEL)**

If you own the OpenTelemetry pipeline, redaction is not applied automatically. Wrap your span exporter with `RedactingSpanExporter` from the Mistral SDK to redact spans before they are exported:

```python
from mistralai.extra.observability import RedactingSpanExporter, default_redaction_policy
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

processor = BatchSpanProcessor(
    RedactingSpanExporter(OTLPSpanExporter(), default_redaction_policy())
)
```

The TypeScript SDK exposes the same `RedactingSpanExporter` from `@mistralai/mistralai/extra/observability`.

## FAQ {#faq}

### Is redaction on by default? {#is-redaction-on-by-default}

Yes, everywhere Mistral controls the export pipeline: the SDKs in dedicated mode, Workflows,
Vibe Code CLI, Vibe Code Web, and Vibe Work. If you run your own OpenTelemetry pipeline, wrap your exporter
with `RedactingSpanExporter` to enable it.

### Does redaction guarantee no sensitive data is exported? {#does-redaction-guarantee-no-sensitive-data-is-exported}

No. Redaction is best-effort and pattern-based. It removes what it recognizes while preserving
observability value, but it can miss free-form PII or secrets that do not match a known pattern.
Use `strict` mode or a custom policy for stronger guarantees, and apply additional controls to
highly sensitive data.

### Does redaction affect performance? {#does-redaction-affect-performance}

It runs at the exporter level, outside the request hot path, so the impact on your application
is negligible.
