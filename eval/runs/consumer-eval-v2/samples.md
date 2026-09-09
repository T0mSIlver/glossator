# Answer samples

Ten seeded questions (seed 0) for consumer `claude-sonnet-low`, the arms'
answers side by side with the judge's verdicts.

## mined-080 (cross_page)

Which `mistral-vespa` commands do I run to create a migration and deploy it?

### A0 (judge: not judged)

I don't have any knowledge of a Mistral tool called `mistral-vespa`, and it doesn't match anything I'm aware of in Mistral's published tooling (their platform docs cover `mistral-common`, `mistralai` Python/TS SDKs, `mistral-inference`, `mistral-finetune`, and La Plateforme's API/CLI, but no `mistral-vespa` package). "Vespa" is a separate open-source vector search engine (vespa.ai), and I'm not aware of an official Mistral integration package by that name either.

I don't want to fabricate command names or a workflow for a tool I can't verify exists. Could you share:

1. Where you encountered `mistral-vespa` (a repo URL, internal doc, or package registry link)?
2. Or point me to the actual documentation page you're working from?

If you share a link, I can read it directly and give you the exact commands with a citation.

### A1 (judge: not judged)

Two commands:

1. **Create the migration** — generates a timestamped migration stub:
```bash
uv run mistral-vespa generate-migration <name> [--app-dir <path>]
```

2. **Deploy it** — builds the application from all migrations and deploys it (single-node or Kubernetes):
```bash
uv run mistral-vespa migrate [--app-dir <path>] [flags]
```
Example for a local Docker deployment: `uv run mistral-vespa migrate --config-server http://localhost:19071`

`--app-dir` defaults to `./vespa_app` for both commands.

Sources:
[1] [CLI reference > `generate-migration`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate-migration) — "Create a timestamped migration stub."
[2] [CLI reference > `migrate`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#migrate) — "Build the application from migrations and deploy it. Supports both single-node (localhost) and Kubernetes deployments."

### A2: not run

## mined-011 (unanswerable)

Can Document QnA answer questions about an image (.png, .jpg), or does it only take PDFs?

### A0 (judge: not judged)

Yes — Document QnA is not limited to PDFs. It works over Mistral's underlying Document AI/OCR pipeline, which explicitly accepts image inputs (PNG, JPEG/JPG, AVIF, etc.) in addition to PDF, PPTX, DOCX, and other document formats — passed as image URLs or base64-encoded images, just as PDFs can be passed as URLs, base64, or uploaded files.

The Document QnA page's examples happen to only show PDF usage (URL, base64, and uploaded-file variants), but the format support itself comes from the shared OCR/document-processing layer, which is explicit about image support.

Sources:
- [Document QnA | Mistral Docs](https://docs.mistral.ai/capabilities/document_ai/document_qna/)
- [OCR Processor | Mistral Docs](https://docs.mistral.ai/capabilities/document_ai/basic_ocr/)
- [Document Processing | Mistral Docs](https://docs.mistral.ai/studio/document-processing/overview)

### A1 (judge: not judged)

Not exclusively PDFs — but it's not quite the same feature for images either. Breakdown:

- **Document QnA** [1] combines OCR with an LLM for natural-language Q&A over documents. Its documented usage examples pass the file via a `document_url` content block, and the sample shown is specifically PDF (including base64-encoded PDF) [2].
- Separately, Mistral's vision-capable chat models accept images directly as `image_url` content blocks, supporting **PNG (.png), JPEG (.jpg/.jpeg), WEBP (.webp), and single-frame GIF (.gif)** [3]. So you can absolutely send an image and ask questions about it via the same chat completions endpoint — it just goes through the vision/image path (`image_url`) rather than the `document_url` path that the Document QnA guide illustrates.

So in practice: if you want Q&A over a scanned/photographed document or a picture, you can either use `document_url` (docs also support image formats for the underlying OCR step, per the OCR docs) or `image_url` with a vision model — it isn't limited to PDFs, but the Document QnA page's own examples are PDF-focused.

Sources:
- [Document QnA](https://docs.mistral.ai/studio/document-processing/document_qna)
- [Document QnA — Usage](https://docs.mistral.ai/studio/document-processing/document_qna#usage)
- [Vision — supported image formats](https://docs.mistral.ai/studio/conversations/vision#what-types-of-image-files-are-supported)

### A2: not run

## mined-058 (single_page)

Can I use `KeywordRetriever` against the Vespa backend? Passing a keyword query to it raises a pydantic ValidationError.

### A0 (judge: not judged)

I don't have verified documentation on a `KeywordRetriever` class or Vespa backend as part of Mistral's platform — this doesn't match anything I'm aware of in Mistral's official docs (chat/embeddings/agents/fine-tuning APIs, Le Chat, La Plateforme, etc. at docs.mistral.ai).

This sounds like it might come from a third-party RAG/retrieval framework (e.g., Haystack, LlamaIndex, or a custom internal library) that happens to integrate Mistral models, rather than from Mistral itself. Could you share:

1. Which library/package `KeywordRetriever` is from (import path or repo)?
2. A link to the docs page or source where you found it?

Without that I'd be guessing rather than citing a real source, and I don't want to fabricate a Mistral doc link. If you can point me to the repo, I can look at the actual `KeywordRetriever` implementation and pydantic schema to explain why the Vespa backend query validation fails.

### A1 (judge: not judged)

No — that's expected behavior, not a bug you're hitting by mistake.

Per Mistral's docs, `KeywordRetriever` requires a client implementing `KeywordStoreIndex`, but **the built-in Vespa and Postgres backends don't implement `KeywordStoreIndex`**. That's why passing one to `KeywordRetriever` fails Pydantic validation on the `client` field (it expects a `KeywordStoreIndex`, and Vespa's store type doesn't satisfy that interface).

What to do instead:
- For keyword/BM25-style search against Vespa, use `VectorRetriever` — it sends both the query text and its embedding to the backend, so it can do hybrid-style matching against a built-in backend like Vespa.
- If you truly need a standalone lexical/keyword retriever, you must implement a custom `KeywordStoreIndex` yourself; `KeywordRetriever` only works with that custom store.
- If you want to combine vector + keyword retrieval, that pattern (`QueryEngine` with `VectorRetriever` + `KeywordRetriever` + `RRFRanker`) is documented for the case where you have a **separate custom keyword store**, not for Vespa alone.

Source: [Retrievers — Keyword Retriever](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#keyword-retriever)

### A2: not run

## mined-013 (single_page)

Which file formats can Document Annotations be run on?

### A0 (judge: not judged)

Document Annotations can be run on:

- **PDF**
- **Images** (including low-quality or handwritten sources)
- **Scans**
- **DOCX**
- **PPTX**

Source: [Document Annotations – Mistral AI Docs](https://docs.mistral.ai/capabilities/document_ai/annotations/)

### A1 (judge: not judged)

Document Annotations can be run on: PDF, images (even low-quality or handwritten sources), scans, DOCX, and PPTX [1].

[1] [Document Annotations > Accepted Formats](https://docs.mistral.ai/studio/document-processing/annotations#accepted-formats:~:text=You%20can%20use%20our%20API,sources.%20%2D%20scans%2C%20DOCX%2C%20PPTX...) — "You can use our API with the following document formats: OCR with pdf, OCR with image (even from low-quality or handwritten sources), scans, DOCX, PPTX..."

### A2: not run

## dev-097 (unanswerable)

What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit?

### A0 (judge: not judged)

Based on my research of Mistral's official documentation, I could not find published numeric limits for this specific question.

**What the documentation says:**
- `MistralAI-User` is the on-demand crawler used for "user actions in Vibe" — when a user asks a question, it may visit a web page to help answer and cites the source. It's explicitly *not* a bulk/automatic crawler and is not used for training. ([Mistral crawlers](https://docs.mistral.ai/robots))
- The "Open URL" feature in Vibe explicitly **fetches only the single page** at the URL provided — "It doesn't crawl the entire site or follow links." ([Search the web | Mistral Docs](https://docs.mistral.ai/vibe/work/web-search-open-url))
- The "Limits and lifecycle" page for Vibe Code Web covers session duration (24h max, 3h inactivity timeout) and daily session quotas (2/day free, 100/day paid) — it does **not** mention a per-request page-visit cap or a per-minute rate limit for the crawler. ([Limits and lifecycle | Mistral Docs](https://docs.mistral.ai/vibe/code/vibe-code-web/limits-and-lifecycle))

**Conclusion:** Mistral's public documentation does not publish a specific maximum number of pages MistralAI-User may visit per request, nor a documented per-minute rate limit for it. If you need an authoritative number, I'd recommend checking with Mistral support directly, since it isn't in the docs I could access.

Sources:
- [Mistral crawlers](https://docs.mistral.ai/robots)
- [Search the web | Mistral Docs](https://docs.mistral.ai/vibe/work/web-search-open-url)
- [Limits and lifecycle | Mistral Docs](https://docs.mistral.ai/vibe/code/vibe-code-web/limits-and-lifecycle)
- [Vibe | Mistral Docs](https://docs.mistral.ai/vibe)

### A1 (judge: not judged)

Documentation doesn't specify any of this — no per-request page-count cap or per-minute rate limit for `MistralAI-User`.

What the docs say about `MistralAI-User`:
- It's the crawler used for "user actions in Vibe" — when a user asks a question, Vibe "may **visit a web page** to help answer" and cites it, and it "governs which sites these user requests can be made to." No numeric cap on the number of pages per request is mentioned. ([docs.mistral.ai/robots#mistralai-user](https://docs.mistral.ai/robots#mistralai-user))
- The related "Open URL" feature explicitly fetches only a **single page** per URL you paste (no crawling/following links), and you can paste multiple URLs in one chat — but no maximum count is documented. ([docs.mistral.ai/vibe/work/web-search-open-url#limitations](https://docs.mistral.ai/vibe/work/web-search-open-url#limitations), [...#multiple-urls](https://docs.mistral.ai/vibe/work/web-search-open-url#multiple-urls))

Rate limits: I only found general API rate-limit documentation (requests/second, tokens/minute for La Plateforme completions/OCR), which applies to API usage, not to the `MistralAI-User` crawler specifically. There is no documented per-minute rate limit for `MistralAI-User` requests. ([docs.mistral.ai/admin/billing-usage/usage-limits](https://docs.mistral.ai/admin/billing-usage/usage-limits#completion-rate-limits))

If you need an authoritative number for either limit, it isn't published in Mistral's docs — you'd have to ask Mistral directly.

### A2: not run

## dev-247 (api_reference)

For the GET /v1/workflows/deployments/{name} operation, which parameters must I provide and what does the optional workflow_name query parameter do?

### A0 (judge: not judged)

For `GET /v1/workflows/deployments/{name}`:

- **Required:** `name` — the deployment name, passed as a path parameter. This is the only required parameter for this specific endpoint (it returns the deployment's active status and its worker list).
- **`workflow_name` (optional):** This query parameter actually belongs to the sibling *listing* endpoint, `GET /v1/workflows/deployments` (not the single-deployment lookup by name). There, it's used to filter the returned deployments down to those associated with a specific workflow. It's often used alongside `active_only=false`, which additionally includes inactive deployments in the results.

So in short: for the single-deployment endpoint you only need to supply the `name` path parameter; `workflow_name` doesn't apply there — it's for filtering the list of all deployments by which workflow they belong to.

Sources:
- [Deployments | Mistral Docs](https://docs.mistral.ai/studio-api/workflows/managing-workflows-in-production/deployments)
- [Workflows | Mistral Docs](https://docs.mistral.ai/studio-api/workflows/building-workflows/workflows)

### A1 (judge: not judged)

For `GET /v1/workflows/deployments/{name}`:

- **Required:** `name` (string, path) — the deployment name.
- **Optional:** `workflow_name` (string or null, query) — scopes the deployment's serving status to that specific workflow.

Response: `200` returns a `DeploymentDetailResponse`; `422` on validation error.

Source: [Workflows Deployments API > Get Deployment](https://docs.mistral.ai/api/endpoint/workflows/deployments#operation-get_deployment_v1_workflows_deployments_name_get)

### A2: not run

## mined-029 (api_reference)

Is there an endpoint to delete an agent I created with the Agents API?

### A0 (judge: not judged)

Yes. You can delete an agent with:

```
DELETE https://api.mistral.ai/v1/agents/{agent_id}
Authorization: Bearer YOUR_API_KEY
```

Deletion is permanent — the agent's configuration is removed, and if it was shared, it becomes unavailable to everyone else too.

Sources:
- [How do I delete an Agent? – Mistral AI Help Center](https://help.mistral.ai/en/articles/347485-how-do-i-delete-an-agent)
- [Beta Agents Endpoints – Mistral AI Documentation](https://docs.mistral.ai/api/endpoint/beta/agents)

### A1 (judge: not judged)

Yes. The Agents API has:

**`DELETE /v1/agents/{agent_id}`** — deletes an agent entity.
- Path parameter: `agent_id` (string, required)
- Returns `204` on success, `422` on validation error

There's also a related endpoint to delete just an alias without deleting the agent: **`DELETE /v1/agents/{agent_id}/aliases`** (query param `alias`).

Source: [Beta Agents API](https://docs.mistral.ai/api/endpoint/beta/agents#operation-agents_api_v1_agents_delete)

### A2: not run

## mined-021 (single_page)

Which models support custom structured outputs? `chat.parse` with a pydantic response format raises a JSON decode error on the model I picked.

### A0 (judge: not judged)

Per Mistral's docs, **custom structured outputs** (JSON Schema/Pydantic response formats via `response_format={"type": "json_schema", ...}` or `chat.parse`) are only guaranteed on specific models — not all of them support the strict schema-constrained decoding needed for `chat.parse` to reliably return valid JSON.

- Docs: [Custom Structured Output](https://docs.mistral.ai/capabilities/structured-output/custom_structured_output/)
- Docs: [JSON mode](https://docs.mistral.ai/capabilities/structured-output/json_mode/)

As of Mistral's published list, custom structured output (schema-constrained) support is limited to their newer/larger models (e.g. `mistral-large-latest`, `mistral-small-latest`, `pixtral-large-latest`, `codestral-latest`-class models) — smaller/older or vision-only variants often only support the looser `json_object` mode, not schema-enforced output. Because model support changes fairly often, treat that list as indicative rather than exhaustive — check the "Supported models" table on the custom structured output page above for the current, authoritative list before picking a model.

**Why you're likely seeing a JSON decode error:** if the model you picked doesn't support custom structured outputs, the API silently falls back to normal free-form generation (or plain JSON mode without schema enforcement) instead of constrained decoding. The response then isn't guaranteed to be valid JSON matching your Pydantic model, so `chat.parse`'s internal `json.loads`/validation step throws a decode error. The fix is to switch to one of the models listed as supporting `json_schema` in the docs table above — the same code will then produce schema-valid output.

If you tell me which model you're currently using, I can confirm from the docs whether it's on the supported list.

### A1 (judge: not judged)

Custom Structured Outputs are supported by **all currently available Mistral models except `codestral-mamba`** [1]. So if you're pointing `chat.parse` at Codestral Mamba, that's the cause — switch to any other model (e.g. `ministral-8b-latest`, the docs' own example) and it should work.

If you're already on a supported model and still hitting a JSON decode error, likely causes given how `chat.parse` works:
- Your Pydantic schema uses types/constructs that don't map cleanly to JSON Schema (the schema is derived from your Pydantic model and sent as `response_format.json_schema`).
- `max_tokens` is too low and the model's JSON output gets truncated mid-response, which breaks the parser.
- You're trying to parse `.content` (raw string) yourself instead of using `.choices[0].message.parsed`, which is the SDK's already-decoded Pydantic instance [2].

Sources:
1. [Which models support custom Structured Outputs?](https://docs.mistral.ai/studio/conversations/structured-output/custom#which-models-support-custom-structured-outputs) — "All currently available models except for `codestral-mamba` are supported."
2. [Custom Structured Outputs — Start the completion](https://docs.mistral.ai/studio/conversations/structured-output/custom#start-the-completion) — describes `message.parsed` vs `message.content` and the auto-prepended system prompt instruction.

### A2: not run

## mined-082 (single_page)

Does the Postgres backend scope queries from the retrieval context the way Vespa does?

### A0 (judge: not judged)

No — the Postgres backend does not scope queries the way Vespa does.

- **Postgres backend**: `IngestContext` and `RetrievalContext` are accepted on every entrypoint of `PostgresStoreIndex`, but they're only carried through for propagation — the backend derives no actual query scoping from them.
- **Vespa backend**: actively uses the context — it reads `group_id` off the context to scope a streaming-mode query (and will refuse to run the query if `group_id` is missing), and binds `query_params` into the schema's `yql_filter`.

So if you're relying on `RetrievalContext` to isolate/filter results per group or tenant, that behavior is Vespa-specific — switching to Postgres won't give you the same isolation guarantees unless you add your own filtering (e.g., a WHERE clause or row-level security).

Sources:
- [mistralai-search-toolkit-plugins-postgres · PyPI](https://pypi.org/project/mistralai-search-toolkit-plugins-postgres/)
- [mistralai-search-toolkit-plugins-vespa · PyPI](https://pypi.org/project/mistralai-search-toolkit-plugins-vespa/0.0.13/)
- [Search index | Mistral Docs](https://docs.mistral.ai/studio-api/search-toolkit/search-index)

### A1 (judge: not judged)

No — this is called out explicitly as a difference from Vespa.

Both backends accept `IngestContext` and `RetrievalContext` at every entry point, but the Postgres backend only propagates them without deriving query scope from them. It does **not** apply `group_id` or `yql_filter` for tenant isolation the way the Vespa backend does — every query can see the full collection. The docs recommend isolating each tenant in a separate collection/table, or applying filtering before the store, as a workaround. [1]

[1] [Postgres — No context-derived filtering](https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres#notes)

### A2: not run

## dev-277 (post_cutoff)

In Mistral's Work chat, if I want to fetch live data from a connected tool like Gmail, Drive, or Notion, which feature should I use, and how does it differ from using Web Search?

### A0 (judge: not judged)

## Use Connectors, not Web Search

To fetch live data from Gmail, Drive, Notion, etc. in Le Chat/Work, enable a **Connector**, not Web Search — they're built for different data sources:

**Connectors**
- Connectors are secure bridges between Work and your external tools/data sources (Gmail, Google Drive, GitHub, Notion, Linear, Slack, Outlook, SharePoint, Stripe, etc.), letting Work retrieve, analyze, and act on your private data as part of a task.
- Most (Gmail, Notion, Slack, etc.) authenticate via direct OAuth and fetch data **in real time** when you ask — e.g., "list and summarize my emails" pulls live from Gmail.
- Google Drive is the exception: instead of live fetching, it **indexes** your files ahead of time so Le Chat can search them instantly (a "Knowledge Connector" — Team/Enterprise only, requires admin setup).
- To use one: click the **+** icon (or type `/`) in the chat box → **Tools** → enable the connector you need → describe your task naturally.

**Web Search**
- Web Search lets Le Chat query the open internet for current, public information (news, general facts, anything past its training cutoff) and cites sources inline with a globe icon.
- It has no access to your private accounts — it can't see your emails, files, or Notion workspace.

**The key difference:** Web Search answers questions using public internet content; Connectors give the assistant access to *your* private, authenticated data in specific tools like Gmail/Drive/Notion. You enable both the same way (the Tools menu), but pick the one matching whether you need public web info or your own connected-app data.

Sources:
- [Connect tools with Connectors | Mistral Docs](https://docs.mistral.ai/le-chat/knowledge-integrations/connectors)
- [Knowledge Connectors | Mistral Docs](https://docs.mistral.ai/le-chat/knowledge-integrations/connectors/knowledge-connectors)
- [Search the web | Mistral Docs](https://docs.mistral.ai/le-chat/research-analysis/web-search)
- [Choose Chat, Work, or Code | Mistral Docs](https://docs.mistral.ai/vibe/choose-chat-work-code)

### A1 (judge: not judged)

For fetching live data from Gmail, Drive, or Notion, use **Connectors**, not Web Search.

**Connectors** [1] are secure bridges between Work and your external tools/data sources. They let Work retrieve, analyze, and act on data from services like Gmail, Google Drive, GitHub, or Notion as part of a task — e.g., "Check my Gmail for unread messages about the quarterly report and summarize them." You connect each app once (most use a direct OAuth flow), and org admins can disable specific connectors.

**Web search** [2] is a different capability: it lets Work fetch current information from across the public internet to answer a prompt (with sources), not from your private connected apps. There's also a related "Open URL" mode for analyzing a specific page you already have a link to.

In short:
- Need data from your own Gmail/Drive/Notion/Jira/Slack/etc. → **Connectors**
- Need up-to-date info from the public web → **Web Search**

Sources:
- [Connect tools with Connectors](https://docs.mistral.ai/vibe/work/connectors)
- [Search the web > Web search](https://docs.mistral.ai/vibe/work/web-search-open-url#web-search)

### A2: not run
