# Answer samples

Ten seeded questions (seed 0) for consumer `claude-haiku-low`, the arms'
answers side by side with the judge's verdicts.

## mined2-078 (api_reference)

Is there an endpoint that reports how much my organization is using Vibe Code, for a dashboard?

### A0 (judge: not judged)

Based on my search of Mistral's documentation, **I could not find a specific endpoint for reporting Vibe Code usage for dashboards**.

The documentation I reviewed shows:
- **Chat Completion API** (POST `/v1/chat/completions`) - for model interactions
- **Admin functionality** mentioned for billing, SSO, workspaces, and access policies
- But **no documented public API endpoint** for usage reporting or dashboard data

**Recommendations:**

1. **Check Mistral Console** — Log into https://console.mistral.ai and look for a Usage or Billing section in your organization's dashboard (though this would be manual, not an API endpoint)

2. **Contact Mistral Support** — Reach out to Mistral's support team at the "Reach out" link on https://docs.mistral.ai, as they may:
   - Have an undocumented internal API for usage data
   - Offer programmatic access to billing/usage metrics
   - Have plans for such an API

3. **Check for Billing/Usage exports** — Many platforms offer CSV/JSON exports of usage data you could pull into your own dashboard

If you need to build a dashboard now, you might need to use Mistral's web console directly or contact their sales/support team for available programmatic access options.

### A1 (judge: not judged)

Yes, there is an endpoint for organization Vibe Code usage. You can use the **[`GET /v1/admin/analytics/vibe/code/usage/by_organization`](https://docs.mistral.ai/api/endpoint/beta/admin/vibe-code-analytics#operation-get_organization_stats_v1_admin_analytics_vibe_code_usage_by_organization)** endpoint.

**Parameters:**
- `start_time` (Unix timestamp in seconds, required)
- `end_time` (Unix timestamp in seconds, required)

**Response:** Returns `VibeOrganizationStatsOUT` schema with usage data for your organization.

There's also a **[Usage dashboard](https://docs.mistral.ai/admin/billing-usage/usage-limits#usage-dashboard)** in the admin panel that visualizes Vibe usage alongside other metrics, or you can use the **[Admin API usage metrics](https://docs.mistral.ai/admin/admin-api/usage-metrics#vibe-code-analytics)** for programmatic access to build your own dashboard.

You'll need an Admin API key to call this endpoint. Is there a specific metric (like active users, modified lines of code, or suggestion outcomes) you need for your dashboard?

### A2: not run

## mined2-011 (cross_page)

The models endpoint returns `mistral-medium-2508` with the alias `mistral-medium-latest` — how do I tell which version an alias currently points at, and when it will change?

### A0 (judge: not judged)

Based on Mistral's documentation, here's how to determine which version an alias points to and when it changes:

## Determining the Current Version

To check which exact version an alias currently points to, you can:

1. **Call the `/models` endpoint** — it returns the actual version identifier. As you noted, `mistral-medium-latest` currently returns `mistral-medium-2508`.
2. **Review the model name format** — Mistral uses `model-name-major-minor` (e.g., `mistral-medium-2508`). The date-like suffix indicates the version.

## When Aliases Change

According to Mistral's Model Lifecycle Policy:

> **"Aliases automatically switch to newer models once they reach General Availability."**

This means:
- The `-latest` alias points to the most recent **General Availability (GA)** version
- When a newer model reaches GA status, the alias automatically updates to point to it
- The `-major` alias references the newest minor version within a specific major release
- The `-minor` alias pins to a fixed version

Mistral doesn't publish a specific schedule for when `-latest` will update. Instead, alias updates happen **immediately** when a new model reaches GA status. To avoid unexpected behavioral or pricing changes from automatic alias updates, **pin to a specific version** (e.g., `mistral-medium-2508`) instead of using `-latest`.

Sources:
- [Mistral Model Lifecycle Policy](https://docs.mistral.ai/inference/model-lifecycle)

### A1 (judge: not judged)

Based on the [Model lifecycle policy documentation](https://docs.mistral.ai/inference/model-lifecycle#naming-convention):

**What an alias currently points to:**
- `mistral-medium-latest` always points to the **latest General Availability version across all generations**
- This is defined semantically — the alias is dynamic and automatically resolves to whatever is currently the latest GA release

The documentation doesn't describe a programmatic API to query the resolved alias; instead, you determine it by checking which version is currently marked as the latest GA model on [Mistral's models page](https://docs.mistral.ai/capabilities/function_calling/) or in your API responses.

**When it will change:**
Aliases **automatically switch when a new model reaches General Availability**. The documentation warns:

> Aliases automatically switch to newer models once they reach General Availability. As a result, using an alias may expose you to silent updates in model behavior and pricing.

**To avoid unexpected changes:**
Pin your deployment to a specific version instead, such as `mistral-medium-2508` (the full `major-minor` identifier). This gives you precise control and prevents automatic updates. GA models receive no silent updates, so you'll only change versions when you deliberately redeploy with a new model ID.

### A2: not run

## mined2-070 (api_reference)

Can I set instructions on a conversation when the agent already carries its own instructions?

### A0 (judge: not judged)

I don't have direct access to browse Mistral's current documentation, so I can't cite the specific pages or provide a precise answer about how instructions layering works on their platform.

To get an accurate answer, I'd recommend:

1. **Checking Mistral's API documentation** — specifically their agents and conversation endpoints documentation
2. **Looking for their instructions/system prompt documentation** — which should cover precedence rules when both agent-level and conversation-level instructions exist

If you have access to Mistral's docs or can share the relevant pages, I can help you interpret them. Alternatively, if you're working with Mistral's API in code, I can help review your implementation.

Do you have a link to the documentation section you're looking at, or would you like help testing this behavior with an actual API call?

### A1 (judge: not judged)

Based on the Mistral documentation, when you set custom instructions on a conversation where an agent already has its own instructions, here's how it works:

**For Skills/Agents in Work**: When a Skill is active for a task, **its instructions take precedence over your custom instructions**. This design lets you apply task-specific procedures without conflicting with your general preferences. [https://docs.mistral.ai/vibe/work/custom-instructions#interaction-with-other-features](https://docs.mistral.ai/vibe/work/custom-instructions#interaction-with-other-features)

So the hierarchy is:
1. **Agent/Skill instructions** (highest priority when active)
2. **Custom instructions** (your general preferences)

This means if you set conversation instructions while an agent is active, the agent's built-in instructions will take precedence. Custom instructions act as a fallback or general context rather than overriding the agent's specific behavior.

For **Projects**, both custom instructions and project context apply together, but this is different from the override behavior with Skills/Agents.

If you need the conversation instructions to take effect, you might need to either:
- Modify the agent's instructions directly (if you own the agent)
- Use a lower-priority context source than the agent provides
- Apply the instructions outside of an active agent context

Would you like more details about any specific aspect of this?

### A2: not run

## mined2-015 (unanswerable)

The OCR API parameters mention document and image chunking but not how the chunking works — is there a page that explains it?

### A0 (judge: not judged)

Yes, Mistral has dedicated documentation on chunking. The key resource is:

**[Document Chunking - Mistral AI Cookbook](https://docs.mistral.ai/resources/cookbooks/mistral-ocr-documentchunking-readme)**

This page explains how to handle large documents that exceed Mistral OCR's size and page limits by splitting them into smaller chunks. It provides:

- A utility script that handles chunking based on `--max_size_mb` (maximum size allowed by the API) and `--max_pages` (maximum number of pages allowed)
- Configuration for API endpoint, API key, and model name
- Integration guidance for existing document processing pipelines

Additionally, Mistral OCR 4 includes **semantic chunking** capabilities where extracted blocks are classified by type (heading, paragraph, table, figure, list, caption, header, footer, etc.). This is particularly useful for RAG pipelines, as preserving document hierarchy improves retrieval quality.

For the OCR API parameters themselves, see the [OCR endpoint documentation](https://docs.mistral.ai/api/endpoint/ocr).

Sources:
- [Document Chunking - Mistral AI Cookbook](https://docs.mistral.ai/resources/cookbooks/mistral-ocr-documentchunking-readme)
- [OCR endpoint - Mistral AI Documentation](https://docs.mistral.ai/api/endpoint/ocr)

### A1 (judge: not judged)

Based on my search of Mistral's documentation, **the OCR API does not have explicit "document chunking" or "image chunking" parameters**. 

The OCR API endpoint ([https://docs.mistral.ai/api/endpoint/ocr#operation-ocr_v1_ocr_post](https://docs.mistral.ai/api/endpoint/ocr#operation-ocr_v1_ocr_post)) offers control over document/image processing through parameters like:

- `pages` — specify which pages to process (e.g., "0-5" or "0,2-4")
- `image_limit` — cap the number of images extracted
- `image_min_size` — filter images by minimum dimensions
- `include_blocks` — get paragraph-level bounding boxes

However, there's no documentation page that explains "chunking" as a concept within the OCR API itself.

**What you might be looking for:** The chunking concept appears in downstream processing. When using OCR output in the Mistral Search Toolkit, the documentation mentions using [`MarkdownTextSplitter`](https://docs.mistral.ai/studio/search/search-toolkit/quickstart#pdf-ingestion) for structure-aware chunking of extracted text—but that's a post-OCR step, not part of the API parameters.

If the OCR API reference mentions chunking in a specific context, could you share which page or parameter section you're referring to? That would help me locate more targeted documentation.

### A2: not run

## dev-097 (unanswerable)

What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit?

### A0 (judge: not judged)

I was unable to find specific documentation about the maximum number of web pages MistralAI-User may visit for a single user request in Vibe or a per-minute rate limit in Mistral's publicly available documentation.

The pages I checked (Vibe Code Limits and Lifecycle, Usage and Limits, and Vibe Code Overview) contain information about session limits, daily quotas, and inactivity timeouts, but do not specify web page processing limits or per-minute rate limits for Vibe.

**To get this information, I recommend:**

1. **Check the Admin Panel** — Visit https://admin.mistral.ai/plateforme/limits for account-specific limits
2. **API Reference** — Review the full API Reference section in Mistral's documentation at https://docs.mistral.ai
3. **Contact Mistral Support** — Reach out through https://help.mistral.ai for technical specifications not covered in public docs
4. **Check your subscription terms** — Visit https://mistral.ai/pricing/ for tier-specific limitations

Sources:
- [Limits and lifecycle | Mistral Docs](https://docs.mistral.ai/vibe/code/vibe-code-web/limits-and-lifecycle)
- [Usage and limits | Mistral Docs](https://docs.mistral.ai/admin/billing-usage/usage-limits)
- [Vibe Code | Mistral Docs](https://docs.mistral.ai/vibe/code/overview)

### A1 (judge: not judged)

Based on Mistral's documentation, **there is no publicly documented maximum number of web pages for a single user request in Vibe**, nor is there a per-minute rate limit specified.

The documentation on [Search the web](https://docs.mistral.ai/vibe/work/web-search-open-url#multiple-urls) states:

> "You can paste **several URLs in a single chat**. Work keeps the content from each page in context, so you can ask follow-up questions that reference or compare them."

However, this description uses the term "several" without defining a specific numerical limit. The documentation does not provide:
- A maximum number of pages per request
- A per-minute rate limit for web page access

If you need specific limits for your use case, I'd recommend checking your Workspace's rate limits in the [admin console](https://admin.mistral.ai/plateforme/limits/) or contacting Mistral support for official guidance on thresholds that may apply to your plan.

### A2: not run

## dev-247 (api_reference)

For the GET /v1/workflows/deployments/{name} operation, which parameters must I provide and what does the optional workflow_name query parameter do?

### A0 (judge: not judged)

Based on the Mistral API documentation, here's what you need to know about the **GET /v1/workflows/deployments/{name}** operation:

## Required Parameters

- **`name`** (path parameter) — The deployment identifier (required). This must be alphanumeric characters, hyphens, or underscores, max 128 characters.

## Optional Query Parameters

- **`workflow_name`** — Filters the results to show only deployments associated with a specific workflow. This allows you to filter by workflow when inspecting a deployment.

## Additional Context

The endpoint can be called using the Python client as:
```python
deployment = client.workflows.deployments.get_deployment(name="invoice-service")
```

When listing deployments (a related operation), you can pass `active_only=False` to include inactive deployments alongside the `workflow_name` filter.

---

**Sources:**
- [Deployments | Mistral Docs](https://docs.mistral.ai/studio-api/workflows/managing-workflows-in-production/deployments)

### A1 (judge: not judged)

Based on the [Mistral API documentation](https://docs.mistral.ai/api/endpoint/workflows/deployments#operation-get_deployment_v1_workflows_deployments_name_get):

**Required parameter:**
- `name` (string, in path) — The deployment name

**Optional parameter:**
- `workflow_name` (string or null, in query) — **Scopes the serving status to this workflow**

The `workflow_name` query parameter allows you to filter the serving status information returned in the deployment details to a specific workflow. This is useful when a deployment serves multiple workflows and you want to see status information specific to one of them.

### A2: not run

## mined2-027 (unanswerable)

The API intermittently returns 411 `A valid Content-Length header is required` — is that documented, and should I retry it?

### A0 (judge: not judged)

Based on my search, **the 411 error doesn't appear to be specifically documented in Mistral's official error documentation**, though you should check their [Error glossary](https://docs.mistral.ai/resources/error-glossary) directly.

## What the 411 error means

The HTTP 411 "Length Required" is a standard HTTP client error indicating the server requires a `Content-Length` header in your request. This typically indicates a client-side issue, not a server problem.

## Should you retry it?

**No, you should not retry 411 errors automatically.** According to Mistral's [retry guidance](https://theneuralbase.com/mistral-api/learn/advanced/retry-configuration/), the SDK only retries transient errors (429, 5xx status codes). The 411 is a 4xx client error, which means retrying without fixing the underlying issue won't help.

## What to do

1. **Ensure your HTTP client sets `Content-Length`** — most modern HTTP libraries (httpx, requests, fetch) handle this automatically. If you're using a custom client or low-level HTTP library, manually set the header.

2. **Check if it's intermittent** — if it's truly intermittent and not consistently reproducible, it could indicate:
   - A client library issue with request construction
   - An issue with your network/proxy stripping headers
   - A rare server-side issue (though less likely for a 4xx error)

3. **Log the full request** — check your actual request headers when the 411 occurs to verify `Content-Length` is present.

If the problem persists after verifying your headers, contact [Mistral support](https://docs.mistral.ai) with details about your client library and request configuration.

### A1 (judge: not judged)

**The 411 error is not documented in Mistral's [error glossary](https://docs.mistral.ai/resources/error-glossary).** The glossary covers 400, 401, 403, 404, 422, 429, 500, 502, 503, and 504, but makes no mention of 411 Content-Length errors.

Since 411 is a standard HTTP client error (not specific to Mistral), a few possibilities:

1. **SDK/client issue**: If you're using an HTTP client library, it may be dropping the `Content-Length` header on some requests. Make sure your client is consistently sending it for POST/PUT requests.

2. **Intermittent proxy/gateway issue**: An intermediary (load balancer, proxy) could be stripping the header. This would explain why it's intermittent.

3. **Request body encoding**: If you're chunking or streaming the request body, `Content-Length` becomes difficult. Mistral may be stricter about this in some cases.

**Regarding retries**: The [retry strategy documentation](https://docs.mistral.ai/resources/error-glossary#retry-strategy) explicitly lists which errors warrant retries: **429, 500, 502, 503, 504**. Since 411 isn't listed and it's a client-side error (not transient), **retrying won't fix it** — you need to fix the request format first.

**Recommendation**: Add logging to inspect the exact request headers being sent, or try sending requests with explicit `Content-Length` calculation in your client setup. If it persists, reach out to support@mistral.ai with a request sample.

### A2: not run

## mined2-024 (cross_page)

The Azure SDK has no OCR support and my calls to `https://<project>.cognitiveservices.azure.com/v1/ocr` return 404 — is Mistral OCR available on Azure?

### A0 (judge: not judged)

Yes, **Mistral OCR is available on Azure**, but not through the traditional Azure Cognitive Services endpoint you're calling.

## The Issue

The endpoint `https://<project>.cognitiveservices.azure.com/v1/ocr` is for Azure Cognitive Services' built-in OCR, not Mistral's. That's why you're getting a 404.

## Using Mistral OCR on Azure

Mistral OCR is available through **Azure AI Foundry** as a serverless deployment with the model identifier `mistral-document-ai-2505`. You need to:

1. **Access it via Azure AI Foundry**, not the standard Cognitive Services endpoint
2. Use the appropriate Azure AI Foundry API endpoint with your credentials
3. Call it with documents (PDFs, images, or base64-encoded content)

The key advantage over traditional OCR is that Mistral Document AI combines vision + language understanding to preserve document structure (tables, headings, figures) and supports 25+ languages with structured output.

## Getting Started

Refer to the official Azure AI Foundry documentation and the Mistral model catalog entry to configure your endpoint and credentials. The model integrates directly into Azure with data residency—documents stay within your Azure region.

Sources:
- [Mistral OCR on Azure AI Foundry - Microsoft Community Hub](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/unlocking-document-intelligence-mistral-ocr-now-available-in-azure-ai-foundry/4401836)
- [Mistral OCR 25.03 - Azure AI Catalog](https://ai.azure.com/catalog/models/mistral-ocr-2503)
- [Azure AI OCR (Mistral) - liteLLM Documentation](https://docs.litellm.ai/docs/providers/azure_ocr)
- [Mistral Document AI on Azure - TypeScript Guide](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/unlock-structured-ocr-in-typescript-with-mistral-document-ai-on-ai-foundry/4466039)

### A1 (judge: not judged)

Yes, **Mistral OCR is available on Azure**. According to [the Azure deployment documentation](https://docs.mistral.ai/inference/deployment/cloud-deployments/azure), **Document AI (with OCR 4)** is one of the models available for deployment on Azure AI.

The issue with your 404 error is likely that you're trying to call the wrong endpoint. The 404 suggests Azure's Cognitive Services OCR endpoint, which is different from Mistral's OCR.

To use Mistral OCR on Azure, you need to:

1. Deploy the **Document AI** model on [Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/deploy-models-mistral)
2. Query it through the deployed endpoint URL (which will be in the form `https://your-endpoint.inference.ai.azure.com/v1/...`)
3. Use the Mistral SDK or direct API calls to the `/v1/ocr` endpoint of your deployed Mistral Document AI instance

The examples in the documentation show chat completion queries, but the same endpoint structure applies to OCR — you'll call your deployed Azure Mistral endpoint's OCR endpoint rather than Azure Cognitive Services' OCR service.

Refer to the [Mistral OCR processor documentation](https://docs.mistral.ai/studio/document-processing/basic_ocr) for the API format, then adapt it to use your Azure deployment URL instead of `api.mistral.ai`.

### A2: not run

## mined2-083 (single_page)

Which self-deployment options does Mistral document, so I can pick one for my own GPUs?

### A0 (judge: not judged)

## Mistral's Self-Deployment Options

Mistral documents several frameworks for self-deploying their open-weight models on your own GPUs:

1. **vLLM** — An open-source LLM inference and serving engine optimized for Mistral models with GPU support and Docker deployment options
2. **TensorRT-LLM** — NVIDIA's inference engine
3. **TGI (Text Generation Inference)** — Hugging Face's inference framework
4. **SkyPilot** — Cloud resource orchestration tool for deployment across different cloud providers
5. **Cerebrium** — Serverless inference platform
6. **Cloudflare Workers AI** — For edge deployment

## Hardware Considerations

GPU requirements depend on your model choice:
- **Devstral 2 (123B)**: Needs minimum 4 H100-class GPUs
- **Devstral Small 2 (24B)**: Runs on single GPU (DGX Spark, GeForce RTX)
- **Lower-end GPUs**: RTX 4090 or 24GB VRAM cards support 4-bit precision with 32k context; H100/A100 support FP8 with 128k context

The vLLM guide supports GPU parallelization via `--tensor-parallel-size` and precision optimization with `--dtype` and `--max-model-len`.

Sources:
- [Deployment Overview](https://docs.mistral.ai/models/deployment)
- [vLLM Deployment Guide](https://docs.mistral.ai/deployment/self-deployment/vllm)
- [SkyPilot Deployment Guide](https://docs.mistral.ai/deployment/self-deployment/skypilot)
- [Cloudflare Workers AI](https://docs.mistral.ai/deployment/self-deployment/cloudflare)

### A1 (judge: not judged)

Mistral documents these self-deployment options for running models on your own infrastructure:

**Inference Engines** (for serving models):
1. **[vLLM](https://vllm.readthedocs.io/)** — Mistral's recommended choice; a Python-only serving framework that exposes an OpenAI-compatible API
2. **[TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)** — NVIDIA's optimized inference engine
3. **[TGI](https://huggingface.co/docs/text-generation-inference/index)** — Hugging Face's Text Generation Inference

**Infrastructure Management Tools** (to facilitate deployment):
- **[SkyPilot](https://skypilot.readthedocs.io)** — Manages infrastructure provisioning
- **[Cerebrium](https://www.cerebrium.ai)** — Deployment and infrastructure platform

For full-stack enterprise deployments with team management features, Mistral recommends [contacting their team directly](https://mistral.ai/contact).

See: [Self-Deployment](https://docs.mistral.ai/inference/deployment/local-deployment)

### A2: not run

## dev-277 (post_cutoff)

In Mistral's Work chat, if I want to fetch live data from a connected tool like Gmail, Drive, or Notion, which feature should I use, and how does it differ from using Web Search?

### A0 (judge: not judged)

Based on Mistral's documentation, here's the answer:

## Feature: **Connectors**

In Mistral's Work chat, you should use **Connectors** to fetch live data from connected tools like Gmail, Drive, or Notion. Connectors are secure bridges that integrate Work with external services, enabling real-time access to your private data.

## Key Differences from Web Search

| Aspect | Connectors | Web Search |
|--------|-----------|-----------|
| **Data Source** | Your private, authenticated accounts (Gmail, Drive, Notion, etc.) | Public internet content |
| **Authentication** | OAuth-based; requires account connection | No authentication needed |
| **Real-time Access** | Pulls live data directly from your services | Searches indexed web pages |
| **Actions** | Can read AND write/modify data (with approval) | Read-only |
| **Privacy** | Data never stored on Mistral servers or used for training | Public content only |

## How It Works

You describe your task in natural language, and Work:
1. Determines which Connector(s) to use
2. Handles authentication if needed
3. Retrieves real-time data from your connected services
4. Requests approval before sensitive actions (sending emails, modifying files, etc.)

## Available Connectors

Work supports 11 Featured Connectors across communication (Gmail, Outlook, Slack), productivity (Google Drive, Notion, Linear, Google Calendar), development (GitHub), and business (Atlassian, Box, SharePoint, Stripe).

---

**Sources:**
- [Connectors in Mistral Docs](https://docs.mistral.ai/vibe/work/connectors)
- [Connect tools with Connectors | Mistral Docs](https://docs.mistral.ai/vibe/work/connectors)
- [Get started with Work | Mistral Docs](https://docs.mistral.ai/vibe/work/get-started)

### A1 (judge: not judged)

To fetch live data from connected tools like Gmail, Drive, or Notion in Work chat, use **[Connectors](https://docs.mistral.ai/vibe/work/connectors)**.

**How Connectors work:**
[Connectors are secure bridges](https://docs.mistral.ai/vibe/work/connectors) between Work and your external tools and data sources. They let Work retrieve, analyze, and act on data from services like Gmail, Google Drive, GitHub, or Notion. You simply ask naturally—e.g., *"Check my Gmail for unread messages about the quarterly report and summarize them"*—and Work decides which Connector to call, handles authentication if needed, and requests approval before sensitive actions.

**How it differs from Web Search:**
The documentation provides a clear comparison:

| You want to... | Use |
|---|---|
| **Pull live data from a connected tool (Gmail, Drive, Notion...)** | **Connectors** |
| **Get a quick, up-to-date answer with sources** | **Web search** |

[Web search](https://docs.mistral.ai/vibe/work/web-search-open-url) fetches current information from across the *public* internet and weaves findings into your response with inline links. **Connectors** instead integrate with your *personal* or *organizational* tools—they access your internal data directly via OAuth authentication, not the public web.

**To use Connectors:**
1. Go to the `Connectors` page and click `Connect` on the tool you need (Gmail, Google Drive, Notion, etc.)
2. Authenticate via OAuth
3. In a Work chat, click the `+` icon or type `/`, select `Tools`, and enable the Connector
4. Describe your task naturally—Work will call the appropriate Connector functions and ask for approval before taking actions like sending emails or creating events

Data fetched through Connectors is never stored on Mistral's servers and is never used for model training.

### A2: not run
