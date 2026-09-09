# Retrieval grid

## What this measures

Every one of 294 questions was run through 2 retrieval configurations, and the ranked hits of each run were kept. The question each row answers is: which index variant, which ranking weights, and reranking or not, put the documentation section that answers a question inside the top few results.

A hit counts as correct in two ways, reported separately:

- **page**: the hit's URL is one of the question's gold URLs. This is what a reader needs to reach the answer at all.
- **section**: the hit's URL *and* anchor match a gold URL and anchor. This is what a citation needs in order to deep-link.

Most markdown headings in this corpus carry no anchor (D-003a), so a question whose gold has no anchor cannot be scored at the section level. 142 of 244 answerable questions carry an anchor on every gold source and are the only ones in the section tables; the rest are page level only, and are not counted as section misses.

Unanswerable questions have no gold, so they are excluded from every recall number and reported on their own below.

Several chunks of one page are one result: the ranked list is collapsed to distinct pages (or sections) at their best rank before it is scored, so recall@k reads as "the answer was among the first k pages" rather than "among the first k chunks".

## Datasets

- Questions: `eval/dev.jsonl`, sha256 `acf3c2e148f1aa40`
- 294 questions: 50 api_reference, 44 capability, 50 cross_page, 50 post_cutoff, 50 single_page, 50 unanswerable
- Reranker prompt: `listwise-rerank/v1`, sha256 `257020c17044`
- Reranker model: `ministral-14b-2512`

## Configurations

| configuration | variant | weight set | rerank | ranking weights |
|---|---|---|---|---|
| `sec1024-shipped+rerank` | sec1024 | shipped | yes | schema defaults |
| `sec1024-vector-heavy+rerank` | sec1024 | vector-heavy | yes | `bm25_content` 0.3, `content_embedding_closeness` 8 |

Every row retrieves 10 hits.

## Results

### Page-level matching

**recall@1**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.705 | 0.800 | 0.568 | 0.380 | 0.900 | 0.860 |
| `sec1024-vector-heavy+rerank` | 0.732 | 0.920 | 0.580 | 0.380 | 0.880 | 0.880 |

**recall@3**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.879 | 0.880 | 0.784 | 0.780 | 0.960 | 0.980 |
| `sec1024-vector-heavy+rerank` | 0.897 | 0.980 | 0.739 | 0.810 | 0.960 | 0.980 |

**recall@5**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.897 | 0.880 | 0.818 | 0.820 | 0.960 | 1.000 |
| `sec1024-vector-heavy+rerank` | 0.916 | 0.980 | 0.773 | 0.850 | 0.960 | 1.000 |

**recall@10**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.908 | 0.880 | 0.852 | 0.840 | 0.960 | 1.000 |
| `sec1024-vector-heavy+rerank` | 0.918 | 0.980 | 0.784 | 0.850 | 0.960 | 1.000 |

**mrr**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.864 | 0.833 | 0.792 | 0.840 | 0.923 | 0.921 |
| `sec1024-vector-heavy+rerank` | 0.892 | 0.950 | 0.794 | 0.860 | 0.913 | 0.931 |

**ndcg@10**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.858 | 0.845 | 0.780 | 0.781 | 0.933 | 0.941 |
| `sec1024-vector-heavy+rerank` | 0.878 | 0.958 | 0.750 | 0.796 | 0.925 | 0.948 |

Question counts per column: overall 244, api_reference 50, capability 44, cross_page 50, post_cutoff 50, single_page 50.

### Section-level matching

**recall@1**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.641 | 0.200 | -- | -- | 0.872 | 0.889 |
| `sec1024-vector-heavy+rerank` | 0.627 | 0.180 | -- | -- | 0.851 | 0.889 |

**recall@3**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.789 | 0.540 | -- | -- | 0.915 | 0.933 |
| `sec1024-vector-heavy+rerank` | 0.796 | 0.520 | -- | -- | 0.915 | 0.978 |

**recall@5**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.831 | 0.600 | -- | -- | 0.957 | 0.956 |
| `sec1024-vector-heavy+rerank` | 0.852 | 0.620 | -- | -- | 0.957 | 1.000 |

**recall@10**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.845 | 0.620 | -- | -- | 0.957 | 0.978 |
| `sec1024-vector-heavy+rerank` | 0.852 | 0.620 | -- | -- | 0.957 | 1.000 |

**mrr**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.718 | 0.362 | -- | -- | 0.903 | 0.920 |
| `sec1024-vector-heavy+rerank` | 0.715 | 0.350 | -- | -- | 0.893 | 0.934 |

**ndcg@10**

| configuration | overall | api_reference | capability | cross_page | post_cutoff | single_page |
|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 0.750 | 0.426 | -- | -- | 0.917 | 0.934 |
| `sec1024-vector-heavy+rerank` | 0.749 | 0.417 | -- | -- | 0.909 | 0.951 |

Question counts per column: overall 142, api_reference 50, capability 0, cross_page 0, post_cutoff 47, single_page 45.

## Latency, cost and failures

| configuration | median ms | p90 ms | rerank calls | applied | fell back | budget skipped | rerank USD | errors |
|---|---|---|---|---|---|---|---|---|
| `sec1024-shipped+rerank` | 4358 | 6303 | 294 | 253 | 41 | 0 | 0.20438 | 0 |
| `sec1024-vector-heavy+rerank` | 5479 | 6817 | 294 | 253 | 41 | 0 | 0.20246 | 0 |

Latency is wall-clock for one question through one configuration: the Vespa round trip and, where it ran, the reranker's model call. The query's embedding is not in it -- a question is embedded once per embedding model and the vector is reused across every configuration that shares it, so charging that call to one configuration and not the others would be arbitrary.

## Unanswerable questions

The dataset holds 50 questions with no gold source, so they carry no recall. What they measure is whether the engine returns something confident anyway. Across every configuration, 100 of 100 runs returned a top hit, and 0 were reported as having no lexical footing.

| question | configuration | top hit | footing |
|---|---|---|---|
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/admin/scim#operation-users_api_admin_scim_sync_get_scim_sync_run | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/users | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/admin/billing#operation-users_api_admin_usage_get_usage | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/conversations/chat-completion#chat-completion | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/work/web-search-open-url#limitations | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec1024-shipped+rerank` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task#step-1 | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/identity-access/service-accounts#manage | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#open-backoffice | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/conversations/chat-completion/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/identity-access/user-management#invite-members | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/code/cli/offline-models#hardware | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec1024-shipped+rerank` | https://docs.mistral.ai/inference/prompting#system-prompt | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/billing-usage/invoices#payment-schedule | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/document-processing/document_qna | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec1024-shipped+rerank` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/batch-processing | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/code/cli/hooks#declare | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/billing-usage/billing#monthly-spending-limit | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/rate_limiting#case-2-rate-limit-across-activities-key-provided | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec1024-shipped+rerank` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-if-my-file-size-is-larger-than-500mb-and-i-get-the-error-message-413-request-entity-too-large | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/workflows/building-workflows/activities/basics#timeouts | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/work/switch-organization-workspace#scoped | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows#timeout | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec1024-shipped+rerank` | https://docs.mistral.ai/inference/priority-tier#quotas-and-limits | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec1024-shipped+rerank` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-happens-if-i-try-to-create-a-job-that-already-exists | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec1024-shipped+rerank` | https://docs.mistral.ai/inference/deployment/local-deployment/vllm#offline-mode-inference | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/identity-access/user-management#api-keys | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/judges | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec1024-shipped+rerank` | https://docs.mistral.ai/getting-started/quickstarts/admin/configure-sso#step-2 | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec1024-shipped+rerank` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec1024-shipped+rerank` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/concurrency#configuration-options-offset | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/observability/evaluations/datasets#how-large-can-my-dataset-be | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec1024-shipped+rerank` | https://docs.mistral.ai/studio/observability/evaluations/judges#basic-llm-judge | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec1024-shipped+rerank` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/analyze-data#step-3 | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/spans#operation-get_span_fields_v1_observability_spans_fields_get | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec1024-shipped+rerank` | https://docs.mistral.ai/admin/workspaces/usage-limits#rate-limits | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec1024-shipped+rerank` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec1024-shipped+rerank` | https://docs.mistral.ai/models | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec1024-shipped+rerank` | https://docs.mistral.ai/api/endpoint/files#operation-files_api_routes_upload_file | not checked |
| Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/set-up-organization/sign-in-method/saml-sso#start-in-admin | not checked |
| What is the maximum retention period for a SCIM sync run's result before it is deleted, and can completed runs be purged early via the API? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#what-zdr-does-not-cover | not checked |
| Is there a maximum number of Organizations that can be linked to a single Enterprise Account, and what happens if that limit is exceeded? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#organizations | not checked |
| What is the maximum historical retention period for usage data retrievable via the Get Usage endpoint? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/admin/billing#operation-users_api_admin_usage_get_usage | not checked |
| What is the maximum number of messages allowed in a single chat completion request? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/chat | not checked |
| Does the Mistral GCP deployment support server-side prompt caching, and is there a cache hit discount on rawPredict calls? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/conversations/advanced/prompt-caching | not checked |
| What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Does `mistral-vespa generate` validate that the output directory is empty before writing, or does it have a flag to force overwriting existing files? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/search/search-toolkit/search-index/vespa/cli#generate | not checked |
| Is there a keyboard shortcut to switch directly to Work mode from Chat or Code without opening the sidebar? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task#step-1 | not checked |
| Is there a maximum number of credentials (API keys or workload identity credentials) that can be attached to a single service account? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/identity-access/service-accounts#manage | not checked |
| Is there a limit on the number of handoff targets an agent can have, and what happens if a handoff references a nonexistent agent? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities | not checked |
| What is the maximum number of API keys a single Mistral AI account can generate? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/set-up-organization/enterprise-accounts#when-you-need-an-enterprise-account | not checked |
| Is there a recommended maximum length or word limit for the role statement when providing a purpose in a prompt? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/inference/prompting#purpose | not checked |
| Is there a limit on how many agents a single account or workspace can create? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow | not checked |
| How long does an invitation remain valid before it expires, and can the expiration period be customized? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/identity-access/user-management#invite-members | not checked |
| What is the maximum number of selected event ids returned in a single ListCampaignSelectedEventsResponse, and does the endpoint support pagination? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns | not checked |
| What is the minimum GPU VRAM requirement to fine-tune the Ministral 3 14B Instruct weights locally? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/code/cli/offline-models#hardware | not checked |
| Is there a maximum character or token length enforced for system prompts in Mistral models, and what happens if it is exceeded? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/inference/prompting#system-prompt | not checked |
| What is the per-token price charged when pay-as-you-go usage kicks in after the included monthly allowance is exhausted? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/billing-usage/invoices#payment-schedule | not checked |
| Is there a maximum number of campaigns that can be stored or returned per request, and is there a pagination limit for the campaigns list? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/campaigns | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Ministral 3 8B? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/document-processing/document_qna | not checked |
| What is the maximum rate at which MistralAI-User requests can be sent to a single site during user actions in Vibe? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Can I apply document_annotation_format when passing an image (ImageURLChunk) instead of a PDF document, and does the annotation then apply per image? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/batch-processing | not checked |
| Is there a limit on how many hooks can be declared, or a defined execution order when multiple hooks match the same tool call? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/code/cli/hooks#declare | not checked |
| Does the platform offer a grace period or retry policy for failed invoice payments before account suspension? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/billing-usage/usage-limits#organization-spending-limit | not checked |
| Is there a rate limit on how many observability datasets can be deleted per minute via the API? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/datasets#operation-delete_dataset_v1_observability_datasets_dataset_id_delete | not checked |
| What is the maximum total byte size allowed for a request body before a 400 error is returned? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#whats-the-size-limit-of-the-validation-data | not checked |
| Is there a timeout limit for code interpreter executions, and what happens if the executed code exceeds it? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#explanation-of-the-output | not checked |
| Is there a limit on how many agents can be created per workspace or per API key? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/workspaces/your-first-workspace | not checked |
| When deleting a judge that is currently referenced by active evaluations, does the API return a 409 Conflict, or does the deletion succeed and leave the evaluations without a judge? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/observability/evaluations#how-do-i-use-an-llm-as-a-judge | not checked |
| Is there a way to configure a timeout so that pending approval prompts auto-reject if left unanswered, and can that timeout duration be customized? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/work/safety-and-approvals#approvals | not checked |
| What are the specific numeric rate limits per model included in the custom Priority Tier limits? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/inference/priority-tier#quotas-and-limits | not checked |
| What is the maximum number of fine-tuning jobs that can run concurrently per project on the fine-tuning API? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-happens-if-i-try-to-create-a-job-that-already-exists | not checked |
| Is there an air-gapped license validation mode, and how often does an offline installation re-check entitlements before degrading? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/code/cli/install-setup#prerequisites | not checked |
| Is there a way to automatically revoke API keys and deactivate active sessions for a member the moment they are removed from the Organization? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/admin/identity-access/user-management#remove-members | not checked |
| Is there a limit on the number of characters or options allowed in the instructions or JudgeClassificationOutput options fields? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/judges | not checked |
| Is there a limit on the number of users that can auto-join per day through email-domain authentication, or a maximum organization size it enforces? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/getting-started/quickstarts/admin/configure-sso#step-2 | not checked |
| What are the valid ranges or allowed values for the learning_rate hyperparameter when creating a classifier fine-tuning job? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning#what-is-the-recommended-learning-rate | not checked |
| Is there a documented rate limit or maximum number of page visits MistralAI-User will make per user request in Vibe? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/robots#mistralai-user | not checked |
| Is there a documented maximum number of concurrent token-stream tasks a single workflow can run, and what happens if that limit is exceeded? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/concurrency#configuration-options-offset | not checked |
| What is the maximum disk size available in the sandbox's default image, and can it be increased? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/conversations/vision#how-many-tokens-correspond-to-an-image-andor-what-is-the-maximum-resolution | not checked |
| What is the maximum number of live-judging requests per minute that can be made against a single chat completion event via this endpoint? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/chat_completion_events#operation-judge_chat_completion_event_v1_observability_chat_completion_events_event_id_live_judging_post | not checked |
| Is there a limit on how many fine-tuned custom models I can have active at the same time on my Mistral AI account? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/work/scheduled-tasks#limits | not checked |
| Does Mistral AI's documentation specify any recommended or maximum token budget for an LLM judge prompt when evaluating large evaluation sets? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/studio/observability/evaluations/judges#basic-llm-judge | not checked |
| Is there a way to export or share the todos list from the Work panel once a task is complete? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/work/safety-and-approvals#todos-panel | not checked |
| What is the maximum number of span field definitions that the Get span fields endpoint can return in a single response, and is there pagination support? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/observability/spans | not checked |
| Is there an API to programmatically list or delete reusable Prompts, and what are the rate limits for Prompt execution? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/beta/prompts#operation-prompts_delete | not checked |
| Does Mistral Document AI on Azure impose a maximum page count per document for processing, and if so, what is the limit? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/vibe/work/libraries#limits | not checked |
| What is the maximum number of documents that can be submitted in a single Document QnA request with Magistral Small 1.0? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/models | not checked |
| What is the maximum file size allowed for a FileField upload, and is there a limit on the number of files when multiple=True? | `sec1024-vector-heavy+rerank` | https://docs.mistral.ai/api/endpoint/files#operation-files_api_routes_upload_file | not checked |

## Figures

Regenerated from `metrics.json` by `make eval-report run=<dir>`.

- `figures/recall-at-k-page.svg`, `figures/recall-at-k-section.svg`: recall against k, one line per configuration
- `figures/best-two-by-type-page.svg`, `figures/best-two-by-type-section.svg`: recall@5 per question type, for the two leading configurations

## Conclusion

At the page level, over the 244 questions that matching can score, `sec1024-vector-heavy+rerank` leads on recall@5 with 0.916, +0.018 over `sec1024-shipped+rerank` (0.897).

At the section level, over the 142 questions that matching can score, `sec1024-vector-heavy+rerank` leads on recall@5 with 0.852, +0.021 over `sec1024-shipped+rerank` (0.831).

The reranker made 588 calls for $0.4068, about $0.000692 a call, and its ranking was applied 506 of those times; the other 82 returned a ranking the reordering could not use and fell back to retrieval order, which the per-question records name.

This feeds D-012a: the shipped ranking weights are a starting point and the winning row above is what replaces them, and D-015: whether one listwise call buys enough ordering to be worth its latency in the serving path.
