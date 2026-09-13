---
url: https://docs.mistral.ai/studio/observability/traces/send-traces
title: Send traces
breadcrumbs: [Studio, Observability, Distributed tracing]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/traces/send-traces/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
hidden: true
---

# Send traces

This page covers how to instrument each supported data source so it sends [OpenTelemetry](https://opentelemetry.io/) traces to Mistral. After traces are flowing, you can explore them in the [Trace Explorer](https://console.mistral.ai/observability/traces).

Sending traces requires only a valid Mistral API key: no feature flag or special role is needed.

## Coverage by integration {#coverage}

| Integration | Enablement | LLM calls | Tool calls | Agent spans |
|-------------|-----------|-----------|------------|-------------|
| Mistral SDK (Python) | Opt-in (`configure_telemetry`) | Yes | Manual, via `get_telemetry_tracer` | Yes |
| Mistral SDK (TypeScript) | Opt-in (`configureTelemetry`) | Yes | Manual, via `getTelemetryTracer` | Yes |
| Workflows | Automatic (`OTEL_ENABLED=true` on the service) | Yes | Yes | N/A |
| Vibe Code CLI | Opt-in (`enable_otel = true`) | Yes | Yes | Yes |
| Vibe Work | Admin toggle in Studio | Yes | Yes | Yes |
| Vibe Code Web | Admin toggle in Studio | Yes | Yes | Yes |

> **Note**
>
> Every source above redacts spans client-side before export by default. See [Data redaction](https://docs.mistral.ai/studio/observability/traces/data-redaction) to review the policy or change what is masked.

Studio Playground doesn't send traces.

## Enable tracing {#enable-tracing}

**Mistral SDK (Python)**

**Requirements:** Mistral Python SDK with the `telemetry` extra. The code examples require `mistralai[telemetry] >= 2.4.13`.

Observability is in Private Preview and the SDK integration changes quickly, so we recommend using the latest SDK version.

```bash
uv add "mistralai[telemetry]"
```

For more details, see the [SDK's observability README](https://github.com/mistralai/client-python#telemetry--observability) and [examples](https://github.com/mistralai/client-python/tree/main/examples/mistral/observability).

```python
from mistralai.client import Mistral
from mistralai.extra.observability import configure_telemetry

client = Mistral(api_key="your-api-key")
configure_telemetry(client)
```

After this call, the SDK traces all LLM calls, embeddings, agent operations, FIM completions, and OCR requests automatically.

**Add tool spans manually:**

Tool calls within your application aren't traced automatically. Use `get_telemetry_tracer` to add them:

```python
from mistralai.client import Mistral
from mistralai.extra.observability import configure_telemetry, get_telemetry_tracer

client = Mistral(api_key="your-api-key")
configure_telemetry(client)
tracer = get_telemetry_tracer(client, "my-agent")

with tracer.start_as_current_span("invoke_agent"):
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": "Search for recent news."}],
    )

    with tracer.start_as_current_span("execute_tool web_search") as tool_span:
        tool_span.set_attribute("gen_ai.tool.name", "web_search")
        tool_span.set_attribute("gen_ai.tool.call.arguments", "recent news")
        # run your tool here
```

**Mistral SDK (TypeScript)**

**Requirements:** Mistral TypeScript SDK. The code examples require `@mistralai/mistralai >= 2.3.0`.

Observability is in Private Preview and the SDK integration changes quickly, so we recommend using the latest SDK version.

```typescript
import { Mistral } from "@mistralai/mistralai";
import { configureTelemetry } from "@mistralai/mistralai/extra/observability";

const client = new Mistral({ apiKey: "your-api-key" });
await configureTelemetry(client, "dedicated");
```

After this call, the SDK traces all LLM calls, embeddings, agent operations, FIM completions, OCR, moderation, and deep research requests automatically.

**Workflows**

Set `OTEL_ENABLED=true` on the Workflows service. This is an infrastructure-level setting. Once set, every workflow execution generates traces automatically with no per-workflow configuration needed.

Workflow traces include every step: LLM calls, tool invocations, branching decisions, and retry attempts.

**Vibe Code CLI**

Enable tracing in your Vibe Code CLI configuration:

```bash
# Single session
VIBE_ENABLE_OTEL=true vibe

# Permanent setting in ~/.vibe/config.toml
enable_otel = true
```

> **Caution**
>
> Traces include tool call arguments and results, which can contain sensitive data. These are redacted client-side by default; see [Data redaction](https://docs.mistral.ai/studio/observability/traces/data-redaction) to review or adjust the policy.

**Vibe Work and Vibe Code Web**

A Workspace Admin or Org Admin enables conversation tracing for Vibe Work and Vibe Code Web per workspace. In Studio, go to `Workspace > Settings > Observability` and turn on the **Conversation Tracing** toggle.

> **Caution**
>
> Traces include tool call arguments and results, which can contain sensitive data. These are redacted client-side by default; see [Data redaction](https://docs.mistral.ai/studio/observability/traces/data-redaction) to review or adjust the policy.

**Custom (OTEL)**

Any application instrumented with OpenTelemetry can send traces directly to Mistral's telemetry collector.

**Endpoint:** `https://api.mistral.ai/telemetry/v1/traces`

**Protocol:** OTLP/HTTP (JSON)

**Auth:** `Authorization: Bearer <MISTRAL_API_KEY>`

No feature flag is needed: any valid Mistral API key works. Follow the [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai) when naming spans and attributes.

## Verify traces are arriving {#verify}

After enabling instrumentation, make one or more requests through your application, then open the [Trace Explorer](https://console.mistral.ai/observability/traces) in Studio. Traces typically appear within a few seconds.

If you don't see any traces, check that:

1. Your API key belongs to an Enterprise workspace with Observability enabled.
2. You called `configure_telemetry(client)` (or the TypeScript equivalent) before making any API calls.
3. Your workspace role is Org Admin, Workspace Admin, or Observability Viewer.

## FAQ {#faq}

### Do I need to change my application code? {#do-i-need-to-change-my-application-code}

For the Mistral SDK, two lines are enough: install the telemetry extra and call `configure_telemetry(client)`. All subsequent SDK calls are traced automatically.

### Are traces stored securely? {#are-traces-stored-securely}

Traces are stored in Mistral's infrastructure and are only accessible to users with the appropriate role in your workspace. Data is retained for 30 days.

### Can I send traces from a non-Mistral LLM framework? {#can-i-send-traces-from-a-non-mistral-llm-framework}

Yes. Any application that follows the OpenTelemetry GenAI semantic conventions can send traces to `https://api.mistral.ai/telemetry/v1/traces` using OTLP/HTTP and a valid Mistral API key.
