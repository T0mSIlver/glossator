# Answer samples

Ten seeded questions (seed 0) for consumer `vibe-medium35-high`, the arms'
answers side by side with the judge's verdicts.

## mined-077 (unanswerable)

Can I ask the Vespa backend to leave content or metadata out of search results to make responses smaller?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: wrong)

Based on the Mistral documentation as of commit `2e094f7` (7 September 2026):

**No**, the Vespa backend does not support selectively omitting content or metadata from search results to reduce response size.

The documentation for Mistral's platform does not cover Vespa backend configuration or response customization. It primarily focuses on Mistral's API, models, and agent tools, with no mention of Vespa-specific features like filtering search results.

[Vespa](https://docs.mistral.ai/)

### VA (judge: wrong)

Yes.  
Set `include_metadata=False` or `include_content=False` on `QueryEngine.search()` (or on a retriever’s `retrieve()` call) to omit metadata or content from the returned chunks, reducing response size. This works for the Vespa backend because it implements the standard `VectorStoreIndex` protocol used by the retrieval layer.

[Query engine](https://docs.mistral.ai/studio/search/search-toolkit/retrieval#query-engine)
[Custom retrievers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#custom-retrievers)

### VB (judge: wrong)

Yes. Use `include_metadata=False` or `include_content=False` when calling `QueryEngine.search()` or a retriever to exclude those fields from the results and reduce response size.

[Query engine](https://docs.mistral.ai/studio/search/search-toolkit/retrieval#query-engine)
[Retrievers](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#custom-retrievers)

### VC (judge: wrong)

Yes. You can define a **custom document summary** in your schema migrations, which lets you select exactly which fields (content, metadata, etc.) are included in Vespa search results, so you can omit the ones you don’t need and make responses smaller. Use the migration helper `add_schema_custom_document_summary(...)` to add a custom summary to a schema.

[Migration helpers](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migrations#migration-helpers)
[Fields](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/anatomy#fields)

### VD (judge: wrong)

Yes. You can use **custom document summaries** to control which fields (content or metadata) are returned in Vespa search results, thereby making responses smaller.

Specifically:
- Each field has a `summary` parameter that controls how it is rendered in results, and you can pass a custom `SummaryDefinition` to exclude fields from the output [Field types](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migration-helpers#field-types)
- You can also attach a custom document summary to a schema with `add_schema_custom_document_summary()` to precisely select which fields to include or exclude in the result set [add_schema_custom_document_summary](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migration-helpers#evolving-schemas)

## mined-011 (unanswerable)

Can Document QnA answer questions about an image (.png, .jpg), or does it only take PDFs?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: wrong)

Document QnA only takes PDFs.

[Document QnA](https://docs.mistral.ai/studio/agents/document-qna)

### VA (judge: partial)

No, the documentation only shows Document QnA being used with PDFs.

The [Document QnA usage examples](https://docs.mistral.ai/studio/document-processing/document_qna#usage) all demonstrate QnA with a PDF URL, a Base64-encoded PDF, or an uploaded PDF file. While the underlying OCR processor does support image formats, Document QnA itself is presented exclusively with PDFs in its documentation.

### VB (judge: wrong)

Yes, Document QnA can answer questions about PNG and JPG images, not only PDFs. Document QnA combines OCR with LLM capabilities 
[Document AI QnA](https://docs.mistral.ai/studio/document-processing/document_qna)
and, being under the OCR umbrella, uses the same file handling
[QnA with an Uploaded PDF](https://docs.mistral.ai/studio/document-processing/document_qna).
The underlying OCR processor supports PNG, JPEG/JPG, AVIF, TIFF, GIF, HEIC/HEIF, BMP, and WebP images, as well as PDF and other document formats
[What document types are supported?](https://docs.mistral.ai/studio/document-processing/basic_ocr#what-document-types-are-supported).

### VC (judge: wrong)

Yes. Document QnA (under the Document AI OCR umbrella) supports both PDFs and images, including **.png** and **.jpg/.jpeg**.

[What document types are supported?](https://docs.mistral.ai/studio/document-processing/basic_ocr#what-document-types-are-supported)

### VD (judge: wrong)

No. Document QnA only takes PDFs (and other document formats like Word, PowerPoint, ODT, EPUB, RTF), not image files such as `.png` or `.jpg`.

[Document QnA > Document AI QnA > Usage](https://docs.mistral.ai/studio/document-processing/document_qna#usage)

## mined-058 (single_page)

Can I use `KeywordRetriever` against the Vespa backend? Passing a keyword query to it raises a pydantic ValidationError.

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: partial)

**No.** `KeywordRetriever` is not supported with the Vespa backend. Vespa is a vector database that only supports vector similarity search, whereas `KeywordRetriever` performs keyword/lexical search and requires a backend that supports keyword queries (e.g., Elasticsearch or Typesense). The Pydantic validation error occurs because Vespa is not a permitted backend for `KeywordRetriever`.

[Vespa](https://docs.mistral.ai/studio/agents/vector-stores#vespa)
[KeywordRetriever](https://docs.mistral.ai/studio/agents/retrievers#keywordretriever)

### VA (judge: correct)

No. The built-in Vespa backend does **not** implement `KeywordStoreIndex`, so `KeywordRetriever` cannot be used with it and will raise a validation error if you try to pass a Vespa client to it.

Use `KeywordRetriever` only with a custom keyword store. For hybrid search with Vespa, use `VectorRetriever` instead; it sends both the query text and embedding to the backend.

[Keyword Retriever](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#keyword-retriever)
[Search Toolkit components](https://docs.mistral.ai/studio/search/search-toolkit#components)

### VB (judge: correct)

No. The built-in Vespa backend does not implement `KeywordStoreIndex`, so `KeywordRetriever` requires a custom keyword store and will raise a validation error if you pass Vespa. Use `VectorRetriever` for hybrid search with Vespa, as it sends both the query text and embedding to the backend.

[Keyword Retriever](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#keyword-retriever)

### VC (judge: correct)

No. The built-in Vespa backend does **not** implement `KeywordStoreIndex`, which `KeywordRetriever` requires, so you cannot use `KeywordRetriever` against Vespa. The ValidationError occurs because the required interface is missing. Use `VectorRetriever` with Vespa for hybrid search instead.

[Keyword Retriever](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#keyword-retriever)

### VD (judge: partial)

No. The built-in Vespa backend does **not** implement `KeywordStoreIndex`, so you cannot use `KeywordRetriever` with it. Use `VectorRetriever` for hybrid search with Vespa; it sends both the query text and embedding to the backend.

[Keyword Retriever](https://docs.mistral.ai/studio/search/search-toolkit/retrieval/retrievers#keyword-retriever)

## mined-079 (single_page)

What changed in Search Toolkit 0.0.13, and does the old schema call still work?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: wrong)

In Search Toolkit **0.0.13**, the tool call schema replaced the `schema` field with an `arguments` field; the old schema call **does not work**.

[Tool call schema](https://docs.mistral.ai/platform/tools/search-toolkit#tool-call-schema)
[Changelog](https://docs.mistral.ai/platform/tools/search-toolkit#changelog)

### VA (judge: partial)

In **Search Toolkit 0.0.13**:

- **Breaking changes**: `create_schema()` and `create_default_schema()` now take `embedding_model` (an [`EmbeddingModel`](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model) or [`MistralEmbeddingPreset`](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model#presets)) instead of `embedding_dimensions: int`. [`embedding_dimensions`](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migration-helpers#creating-schemas) is **deprecated**: it emits a `DeprecationWarning` and silently builds a `CustomEmbeddingModel(name="unknown")` under the hood. Passing both `embedding_model` and `embedding_dimensions` raises `ValueError`.
- **Improvements**: Added a [Postgres search backend](https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres), a new [`EmbeddingModel`](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model) abstraction, more flexible extractors (custom OCR delegates, text-first PDF), and `exclude_ids` support across the retrieval layer.
- **Bugfixes**: Updated `markdownify` dependency to 1.x and adapted the HTML extractor.

**Does the old schema call still work?**  
Yes, but only via the deprecated `embedding_dimensions` argument: it still runs (with a `DeprecationWarning`) and builds a generic embedding model, as long as you do **not** also pass `embedding_model`.  
[Creating schemas](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migration-helpers#creating-schemas) [0.0.13](https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-13)

### VB (judge: correct)

Search Toolkit **0.0.13** introduced a **breaking change**: `create_schema()` and `create_default_schema()` now require an `embedding_model` (an `EmbeddingModel` or `MistralEmbeddingPreset`) instead of the former `embedding_dimensions: int`; the old `embedding_dimensions` parameter is deprecated, emits a `DeprecationWarning`, and silently builds a `CustomEmbeddingModel(name="unknown")` with the supplied dimension. Passing both parameters raises `ValueError`. Other major changes include: a new **Postgres search backend**, the new `EmbeddingModel` abstraction, and threading of `exclude_ids` through the retrieval layer.
[0.0.13](https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-13)

Yes, the old schema call **still works**: if you pass `embedding_dimensions`, it is accepted, deprecated, and converted to a `CustomEmbeddingModel(name="unknown")` with that dimension count; however, you cannot pass both `embedding_model` and `embedding_dimensions`.
[Creating schemas](https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/migration-helpers#creating-schemas)

### VC (judge: correct)

In Search Toolkit 0.0.13:

- **Breaking changes**: `create_schema()` and `create_default_schema()` now require an `embedding_model` parameter (of type [`EmbeddingModel`](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model) or [`MistralEmbeddingPreset`](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model#presets)) instead of `embedding_dimensions: int`. The old `embedding_dimensions` parameter is **deprecated**: it emits a `DeprecationWarning` and silently builds a `CustomEmbeddingModel(name="unknown")`, so the old schema call still works but is not recommended. Passing both parameters raises a `ValueError`.
  Also, `VespaSchemaDefinition.embedding_dimensions` is replaced by `embedding_model`, and `VespaSearchIndex` now exposes an `embedding_model` property.

[0.0.13](https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-13)

### VD (judge: correct)

In Search Toolkit 0.0.13:

- **Breaking changes**: `create_schema()` and `create_default_schema()` now require an `embedding_model` (an [`EmbeddingModel`](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model) or [`MistralEmbeddingPreset`](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model#presets)) instead of the old `embedding_dimensions: int`. The old `embedding_dimensions` parameter is **deprecated**: it emits a `DeprecationWarning` and silently builds a `CustomEmbeddingModel(name="unknown")`; if you pass both `embedding_dimensions` and `embedding_model`, a `ValueError` is raised. 
- **Other major additions**: A new [Postgres search backend](https://docs.mistral.ai/studio/search/search-toolkit/search-index/postgres), a full [`EmbeddingModel` abstraction](https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model), and various extractor and retrieval improvements.
  [0.0.13](https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-13)

**Does the old schema call still work?**  
Yes—passing `embedding_dimensions` still works but is deprecated (with a warning) and is not recommended for new code.  
[0.0.13](https://docs.mistral.ai/studio/search/search-toolkit/changelog#0-0-13)

## mined-014 (single_page)

Are there limits on document annotations — how many pages can one annotation request cover?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: wrong)

10 pages

[Document processing](https://docs.mistral.ai/studio/agents/introduction#document-processing)

### VA (judge: wrong)

The limit is **8 pages per annotation request**.

The documentation states: "When using Document Annotations, each annotation accepts a maximum of 8 image bounding boxes."

[FAQ](https://docs.mistral.ai/studio/document-processing/annotations#faq)

### VB (judge: wrong)

**1,000 pages**

One annotation request can cover up to 1,000 pages per document.

[Are there any limits regarding the Document AI API?](https://docs.mistral.ai/studio/document-processing/annotations#are-there-any-limits-regarding-the-document-ai-api)

### VC (judge: wrong)

1,000 pages per document.

[Are there any limits regarding the Document AI API?](https://docs.mistral.ai/studio/document-processing/annotations#are-there-any-limits-regarding-the-document-ai-api)

### VD (judge: wrong)

1,000 pages.

Uploaded document files for the Document Intelligence API (which includes annotations) must be no longer than 1,000 pages.

[Are there any limits regarding the Document AI API?](https://docs.mistral.ai/studio/document-processing/annotations#are-there-any-limits-regarding-the-document-ai-api)

## dev-035 (cross_page)

An administrator wants to investigate who deleted conversations by querying audit logs programmatically. Which activity and event type would they look for, what query parameters can narrow results to a specific human user, and how many entries are returned by default per request?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: wrong)

The **activity** is `conversation`, the **event type** is `delete`.

[Activity and event types](https://docs.mistral.ai/platform/audit-logs#activity-and-event-types)

To narrow results to a specific human user, use the query parameters `user_id` (to specify the user) and `actor_type=human`.

[Filtering audit logs](https://docs.mistral.ai/platform/audit-logs#filtering-audit-logs)

By default, **100 entries** are returned per request.

[Pagination](https://docs.mistral.ai/platform/audit-logs#pagination)

### VA (judge: correct)

To investigate who deleted conversations, an administrator would look for:

- **Event type**: `le_chat.conversation.deleted`
- **Target type**: `LE_CHAT_CONVERSATION`

[Event types](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#event-types)  
[Target types](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#target-types)

To narrow results to a specific human user, they can use the query parameter:

- **`actor_user_uuid`**: Filter by the UUID of the user who performed the action
- Optionally combine with **`actor_type=HUMAN`** to explicitly filter for human actors

[Filters](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#filters)  
[Actor types](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#actor-types)

By default, **20 entries** are returned per request.

[Filters](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#filters)

### VB (judge: correct)

To investigate who deleted conversations via the audit logs API:

- **Activity/event type**: `le_chat.conversation.deleted` [What gets logged](https://docs.mistral.ai/admin/monitor-comply/audit-logs/overview#what-is-logged) [le Chat events](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#le-chat-events)

- **Filter to a specific human user**: use the `actor_user_uuid` query parameter to specify the user's UUID. You can also use `actor_type=HUMAN` to restrict results to human actors only. [Filters](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#filters) [Parameters](https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs#operation-users_api_admin_audit_logs_get_audit_logs)

- **Default entries per request**: **20** [Filters](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#filters)

### VC (judge: correct)

- **Activity and event type:** `le_chat.conversation.deleted` (for single deletions) or `le_chat.conversation_batch.deleted` (for batch deletions) under the le Chat activity.
  [le Chat events](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#le-chat-events)

- **Query parameters for a specific human user:**
  - `actor_type=HUMAN` to restrict to human actors.
  - `actor_user_uuid=<user_uuid>` to filter by the UUID of the human user.
  [Filters](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#filters)
  [Actor types](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#actor-types)

- **Default entries per request:** 20.
  [Filters](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#filters)

### VD (judge: correct)

- **Event type**: `le_chat.conversation.deleted` identifies deletion of a le Chat conversation in audit logs.
  [le Chat events](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#le-chat-events)

- **Query parameter for a specific human user**: `actor_user_uuid` filters logs by the UUID of the user who performed the action; to restrict to human actors, also use `actor_type=HUMAN`.
  [Filters](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#filters) and [Get Audit Logs > Parameters](https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs#operation-users_api_admin_audit_logs_get_audit_logs/parameters)

- **Default entries per request**: 20.
  [Filters](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#filters)

## dev-247 (api_reference)

For the GET /v1/workflows/deployments/{name} operation, which parameters must I provide and what does the optional workflow_name query parameter do?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: partial)

For the GET /v1/workflows/deployments/{name} operation:

**Required parameter:**
- `name` (path parameter) – must be provided in the URL path.

**Optional `workflow_name` query parameter:**
- Specifies the workflow name to disambiguate deployments with the same name across different workflows.

[Get a deployment](https://docs.mistral.ai/api/workflows#Get_v1_workflows_deployments_{name})

### VA (judge: correct)

**name** (path, required) [Parameters](https://docs.mistral.ai/api/endpoint/workflows/deployments#operation-get_deployment_v1_workflows_deployments_name_get_parameters).

**workflow_name** query parameter scopes serving status to this workflow [workflow_name](https://docs.mistral.ai/api/endpoint/workflows/deployments#operation-get_deployment_v1_workflows_deployments_name_get_parameters_workflow_name).

### VB (judge: correct)

For `GET /v1/workflows/deployments/{name}` you **must** provide the path parameter:

- `name` (string, required, in path)

The optional query parameter `workflow_name` (string or null) **scopes the serving status to this workflow**.

[Get Deployment](https://docs.mistral.ai/api/endpoint/workflows/deployments#operation-get_deployment_v1_workflows_deployments_name_get)

### VC (judge: correct)

For **GET /v1/workflows/deployments/{name}**, you must provide:

- **`name`** (string, required, in path)

The optional **`workflow_name`** query parameter scopes serving status to this workflow.

[Parameters](https://docs.mistral.ai/api/endpoint/workflows/deployments#operation-get_deployment_v1_workflows_deployments_name_get/parameters)

### VD (judge: correct)

- **Required parameter:** `name` (in path) — the deployment identifier.
- **Optional `workflow_name` query parameter:** scopes serving status to this workflow.

[Parameters](https://docs.mistral.ai/api/endpoint/workflows/deployments#operation-get_deployment_v1_workflows_deployments_name_get)

## mined-025 (api_reference)

What are the allowed values of `reasoning_effort` on the chat completions endpoint?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: wrong)

The allowed values of `reasoning_effort` on the chat completions endpoint are **"none"** and **"minimal"**.

[Chat Completions - request body](https://docs.mistral.ai/api#tag/Chat-Completions/operation/post_chat_completions)

### VA (judge: wrong)

<vibe_stop_event>Turn limit of 40 reached</vibe_stop_event>

### VB (judge: partial)

The allowed values are: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`.

[Chat Completion](https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post)

### VC (judge: partial)

The allowed values for `reasoning_effort` on the chat completions endpoint are:

`none`, `minimal`, `low`, `medium`, `high`, `xhigh`

[Request body](https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post:~:text=The%20presence_penalty%20determines)

### VD (judge: partial)

The allowed values are: `"none"`, `"minimal"`, `"low"`, `"medium"`, `"high"`, `"xhigh"`.

[Request body](https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post/request-body)

## mined-024 (single_page)

Which models take `reasoning_effort`, and what does each value do?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: wrong)

The **`mistral-tiny`**, **`mistral-small`**, **`mistral-medium`**, and **`codestral-latest`** models take the `reasoning_effort` parameter.

- **`none`**: no reasoning traces (default for all models).
- **`minimal`**: short reasoning traces (default for `mistral-medium`).
- **`standard`**: medium reasoning traces (default for `mistral-small` and `codestral-latest`).

[Models](https://docs.mistral.ai/models/models#models) [Reasoning effort](https://docs.mistral.ai/models/models#reasoning-effort)

### VA (judge: wrong)

<vibe_stop_event>Turn limit of 40 reached</vibe_stop_event>

### VB (judge: partial)

- **Models**: `mistral-small-latest`, `mistral-medium-3-5`
  [Model list](https://docs.mistral.ai/studio/conversations/reasoning#before-you-start)

- **Values and behavior**
  - `none`: the model thinks minimally and the thinking chunk is omitted from the response.
  - `minimal`: accepted value (enum), not described in the documentation.
  - `low`: accepted value (enum), not described in the documentation.
  - `medium`: accepted value (enum), not described in the documentation.
  - `high`: the response includes a full thinking chunk before the final answer, at the cost of increased token usage.
  - `xhigh`: accepted value (enum), not described in the documentation.
  [Values](https://docs.mistral.ai/studio/conversations/reasoning#before-you-start)
  [Enum definition](https://docs.mistral.ai/api/endpoint/chat#operation-chat_completion_v1_chat_completions_post)

### VC (judge: correct)

- **Models**: `mistral-small-latest`, `mistral-medium-3-5`
  [Before you start > Model](https://docs.mistral.ai/studio/conversations/reasoning#before-you-start)

- **Values**:
  - `reasoning_effort = "high"`: response includes a full thinking chunk before the final answer, increasing token usage.
  - `reasoning_effort = "none"`: model thinks minimally and the thinking chunk is omitted.
  [Before you start > Model](https://docs.mistral.ai/studio/conversations/reasoning#before-you-start)

### VD (judge: partial)

The models that take `reasoning_effort` are **`mistral-small-latest`** and **`mistral-medium-3-5`**.

[Model](https://docs.mistral.ai/studio/conversations/reasoning#before-you-start)

The parameter controls reasoning in the output as follows:

- **`reasoning_effort = "high"`**: The response includes a full thinking chunk (`ThinkChunk`) before the final answer, at the cost of increased token usage.
- **`reasoning_effort = "none"`**: The model thinks minimally and the thinking chunk is omitted; `message.content` is a plain string.

[The reasoning_effort parameter controls how reasoning is surfaced in the output](https://docs.mistral.ai/studio/conversations/reasoning#before-you-start)
[When `reasoning_effort` is set to "high", the response `message.content` is a list of chunks... When `reasoning_effort` is "none", `message.content` is a plain str](https://docs.mistral.ai/studio/conversations/reasoning#handling-thinking-chunks)

## mined-013 (single_page)

Which file formats can Document Annotations be run on?

### A0: not run

### A1: not run

### A2: not run

### V0 (judge: wrong)

Document Annotations can be run on **PDF, DOCX, PPTX, XLSX, TXT, MD, HTML, JSON, and CSV** file formats.

[Supported file formats for Document Annotations](https://docs.mistral.ai/studio/document-annotations#supported-file-formats)

### VA (judge: correct)

PDF, images (PNG, JPEG/JPG, AVIF, etc.), scans, DOCX, PPTX.

[Accepted Formats](https://docs.mistral.ai/studio/document-processing/annotations#accepted-formats)

### VB (judge: partial)

The supported file formats for Document Annotations are:
**PDF, image (including scans), DOCX, PPTX.**

[Accepted Formats](https://docs.mistral.ai/studio/document-processing/annotations#accepted-formats)

### VC (judge: correct)

PDF, images, scans, DOCX, PPTX.

[Accepted Formats](https://docs.mistral.ai/studio/document-processing/annotations#accepted-formats)

### VD (judge: correct)

PDF, images, scans, DOCX, PPTX.

[Accepted Formats](https://docs.mistral.ai/studio/document-processing/annotations#accepted-formats)
