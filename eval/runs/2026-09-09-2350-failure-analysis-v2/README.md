# Failure analysis: which part of the pipeline was wrong

**What this measures.** Not how often the pipeline fails --- the answer evaluations
already say that --- but *which part* failed each time. Every answer these runs
recorded that the judge scored `partial` or `wrong`, or that refused in the wrong
direction, is assigned one class: the retrieval never found the page, the context
never carried it, the model had it and still answered wrong, or the refusal went the
wrong way. A wrong answer with the right passage in front of the model and a wrong
answer whose page was never retrieved call for opposite work, and the generator here
is a small model (Ministral 3 14B, D-017a), which makes the split worth having before
anything is blamed on it.

No model was called to produce this run's classes. Every class is decided from the
records the answer evaluations already wrote, so it can be recomputed from
`records.jsonl` at any time.

## Configuration

- Runs analysed: 5 --- `2026-09-09-1253-mined-shipped`, `2026-09-09-1211-fresh60-shipped`, `2026-09-09-0312-dev60-rerank`, `2026-09-09-1228-noisy-single`, `2026-09-09-1230-clean-single`
- Corpus: `corpus/mistral-docs`; chunk map rebuilt offline: `sec1024` 4440 chunks
- Human labels: `eval/labels/dev60-rerank-human.jsonl`
- Reference-defect judge: `not run` (reference-defect/v1, hashes {"system": "2dff9e4c2ae22e87", "user": "77564d9ba6798f8b"})

Directories named but not analysed:

- None: every directory named on the command line held answers.

## How each class is decided

Every answer whose primary judge verdict is `partial` or `wrong`, or whose
refusal went the wrong way (it refused a question the dataset says is answerable,
or answered one the dataset marks unanswerable), is a failure and gets exactly one
class. The tests run in this order, and each one is only reached when the one
before it passed, so a class always means "everything upstream of it worked".

1. **retrieval miss** -- no chunk of a gold page appears in
   `trace.events[].result_ids` for any round: not the seed retrieval, not any of the
   search loop's tool calls. Chunk ids are resolved to pages through the corpus, not
   through the run: a chunk id is `uuid5(NAMESPACE_DNS, "<page url>:char:<start>-<end>")`,
   so re-chunking the vendored corpus with the run's own chunker rebuilds the whole map
   offline. Sub-labels: `reranker_drop` when a recorded reranker call
   shows the gold page among the candidates it was offered and it did not come back;
   `search_miss` when the gold page was not among those candidates;
   `candidates_not_recorded` when the run has no recorded reranker call
   for that question, which is every run made before reranker calls reached the call
   ledger (D-023b), so search and reranker cannot be told apart there.
2. **context miss** -- a gold chunk came back from retrieval
   but no source in `trace.sources` came from a gold page, so the model never saw it.
   Sub-labels: `dropped_from_context` when the gold chunk is in
   `trace.dropped_chunk_ids`, `outranked_in_assembly` otherwise.
3. **generation failure** -- a gold chunk was in the assembled
   context, the model answered rather than refusing, and the answer is still partial or
   wrong. Sub-labels say what the citations did with it:
   `no_citation_to_gold` (the answer cited something else),
   `unverified_quote_from_gold` (it cited the gold section but the quote
   failed verification), `verified_quote_from_gold` (it quoted the gold
   section verbatim and answered wrong anyway, which is the strongest evidence of a model
   limit rather than a pipeline one).
4. **refusal failure** -- reported separately, because D-035b showed
   false refusals dominate under noise. `false_refusal`: the answer set
   `insufficient_evidence` on an answerable question *with a gold chunk in the context*.
   `missed_refusal`: it answered a question the dataset marks
   unanswerable. A refusal that follows a retrieval or context miss is classed as that
   miss instead, because refusing when the evidence never arrived is the pipeline working,
   and an unanswerable question has no gold to retrieve, so tests 1 to 3 never apply to
   one.
5. **question or reference defect** -- *flagged, not decided*, and not a class: it is a
   column on the rows above and overlaps them. Two deterministic signals raise it, and
   neither is evidence on its own: `judge_names_the_reference`, the
   judge's one-sentence reason mentions the reference answer; and
   `human_is_more_lenient`, a hand label for that answer scores it
   higher than the judge did (D-021b found every primary-judge disagreement went the
   strict way). The first signal is reported with the rate at which answers that *passed*
   carry the same wording, because `answer-judge/v2` shows the judge the reference and
   tells it to grade against it, so naming it is the norm rather than a symptom. Deciding
   whether a reference is actually wrong needs a judge that reads the gold section text,
   which is what `--judge-model provider:model` runs and what this run did not do.

## Known blind spots

- **A wrong gold link in the dataset looks like a retrieval miss.** The gold URL is
  taken as ground truth. If the dataset points at the wrong page, retrieval can have
  found the page that really answers the question and still be counted as having missed.
  This is the single largest source of error in the retrieval-miss column and the reason
  the defect flag exists.
- **A correct answer from a page that is not gold looks like a failure.** D-033 saw this
  on capability questions, where a model card carries the same fact as the `/models`
  matrix. The one relaxation the answer evaluation already applies is applied here too --
  the card of a model the question names counts as the gold page -- and nothing beyond it.
- **`candidates_not_recorded` hides the reranker.** Where a run has no
  recorded reranker call, a search that never found the page and a reranker that dropped
  it look the same.
- **Judged correctness is a floor.** The primary judge is stricter than a reader (D-021b:
  it never called an answer correct that the reader rejected, and called five partial or
  wrong that the reader accepted), so the failure counts here are an upper bound on what
  a reader would call a failure.
- **One class per answer.** An answer can fail for two reasons at once; it is counted
  under the first one in the order, which is the upstream one.
- **The context test is page-level.** A failure is a generation failure once *any* chunk
  of a gold page reaches the context, even when the exact gold section did not. The
  `gold_section_in_context` column on each row says which of the two happened.

## Results

Across 5 runs, 177 of 575 answers
failed (31%). 6397 of
6397 recorded chunk ids resolved to a page through the corpus;
an unresolved id is a chunk the current corpus no longer produces, and is counted on the
row it came from as `unresolved_chunks`.

| run | answers | failures | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| 2026-09-09-1253-mined-shipped | 170 | 64 (38%) | 7 (4%) | 0 (0%) | 43 (25%) | 14 (8%) |
| 2026-09-09-1211-fresh60-shipped | 60 | 18 (30%) | 2 (3%) | 0 (0%) | 8 (13%) | 8 (13%) |
| 2026-09-09-0312-dev60-rerank | 120 | 21 (18%) | 1 (1%) | 0 (0%) | 8 (7%) | 12 (10%) |
| 2026-09-09-1228-noisy-single | 105 | 44 (42%) | 13 (12%) | 0 (0%) | 12 (11%) | 19 (18%) |
| 2026-09-09-1230-clean-single | 120 | 30 (25%) | 3 (2%) | 0 (0%) | 11 (9%) | 16 (13%) |

126 of 177 failures carry the reference-defect flag: `judge_names_the_reference` 125, `human_is_more_lenient` 4 (a row can carry both). For comparison, 367 of the 398 answers that passed carry the same `judge_names_the_reference` wording (92%), so that signal on its own separates nothing; `human_is_more_lenient` is the discriminating one. The reference-defect judge did not run: no `--judge-model` was given, so every reference-defect entry below is a flag raised by a deterministic signal and nothing more. Running it is one call per flagged failure and decides those flags.

### `2026-09-09-1253-mined-shipped`

Dataset `eval/mined.jsonl`, generator `ministral-14b-2512`, index `sec1024`,
reranker True. 170 of 170 answers carry a primary
verdict (0 do not), 7 ended in an error. 2485 of 2485 recorded chunk ids resolved to a page through the corpus.

**By strategy**

| strategy | answers | failures | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| search_loop | 85 | 34 (40%) | 5 (6%) | 0 (0%) | 22 (26%) | 7 (8%) |
| single_pass | 85 | 30 (35%) | 2 (2%) | 0 (0%) | 21 (25%) | 7 (8%) |

**By question type**

| question type | answers | failures | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| api_reference | 22 | 7 (32%) | 2 (9%) | 0 (0%) | 5 (23%) | 0 (0%) |
| capability | 2 | 2 (100%) | 0 (0%) | 0 (0%) | 1 (50%) | 1 (50%) |
| cross_page | 8 | 4 (50%) | 1 (12%) | 0 (0%) | 2 (25%) | 1 (12%) |
| single_page | 120 | 40 (33%) | 4 (3%) | 0 (0%) | 35 (29%) | 1 (1%) |
| unanswerable | 18 | 11 (61%) | 0 (0%) | 0 (0%) | 0 (0%) | 11 (61%) |

**Sub-labels**

| class | sub-label | failures |
|---|---|---|
| retrieval miss | `candidates_not_recorded` | 7 |
| generation failure | `no_citation_to_gold` | 15 |
| generation failure | `unverified_quote_from_gold` | 4 |
| generation failure | `verified_quote_from_gold` | 24 |
| refusal failure | `false_refusal` | 3 |
| refusal failure | `missed_refusal` | 11 |

47 of 64 failures carry the reference-defect flag: `judge_names_the_reference` 47, `human_is_more_lenient` 0 (a row can carry both). For comparison, 92 of the 106 answers that passed carry the same `judge_names_the_reference` wording (87%), so that signal on its own separates nothing; `human_is_more_lenient` is the discriminating one.

**Examples**

**retrieval miss**

- `mined-003` (cross_page, search_loop, judged wrong, `candidates_not_recorded`) --- "What file formats and what maximum size can I upload for OCR? A .zip upload comes back as 422 `Invalid file format.`"
  - what happened: no chunk of https://docs.mistral.ai/studio/document-processing/basic_ocr, https://docs.mistral.ai/resources/known-limitations in any round; the answer saw nothing
  - the judge: The system produced no answer at all, leaving the question unanswered.
- `mined-006` (single_page, single_pass, judged wrong, `candidates_not_recorded`) --- "OCR only gives me an `![img-0.jpeg](img-0.jpeg)` placeholder for figures — how do I get a description of each image in the document?"
  - what happened: no chunk of https://docs.mistral.ai/studio/document-processing/annotations in any round; the answer saw nothing
  - the judge: The system produced no text, so the question is unanswered.
- `mined-007` (api_reference, search_loop, judged wrong, `candidates_not_recorded`) --- "Which annotation parameters does the OCR endpoint take? `bbox_annotation_format` is rejected as an unexpected keyword argument."
  - what happened: no chunk of https://docs.mistral.ai/api/endpoint/ocr in any round; the answer saw nothing
  - the judge: The system produced no answer, leaving the question about OCR annotation parameters unanswered.

**context miss** -- none in this run.

**generation failure**

- `mined-006` (single_page, search_loop, judged partial, `no_citation_to_gold`) --- "OCR only gives me an `![img-0.jpeg](img-0.jpeg)` placeholder for figures — how do I get a description of each image in the document?"
  - what happened: cited https://docs.mistral.ai/studio/document-processing/annotations instead of the gold section
  - the judge: Correctly identifies bbox_annotation_format as the way to get per-image descriptions, but omits the reference's contrast that document_annotation_format annotates the whole document instead.
- `mined-015` (cross_page, search_loop, judged partial, `unverified_quote_from_gold`) --- "A one-page 308 kB PDF sent as base64 to Document QnA reports 321,774 prompt tokens and 400s — what is the context limit and why is the document so expensive?"
  - what happened: rejected (quote is not in the cited source) quote from the gold section: "Mistral Small 4 | Max context length | 256k tokens"
  - the judge: It states 256k for Mistral Small 4, matching the reference, but omits the 128k limit for Medium 3.1, the 400 error behavior, and never explains why the document is token-expensive (input+output counted, base64/OCR [...]
- `mined-001` (api_reference, search_loop, judged partial, `verified_quote_from_gold`) --- "The docs show `client.files.upload(..., purpose="ocr")` but my type checker says only `fine-tune` and `batch` are valid — which values does the file upload [...]"
  - what happened: verified quote from the gold section: "purpose (enum: 'fine-tune', 'batch', 'ocr', optional)"
  - the judge: Correctly lists the three valid purpose values and confirms ocr is valid, but omits that the request body also accepts optional expiry and visibility plus the required file parameter.

**refusal failure**

- `mined-015` (cross_page, single_pass, judged wrong, `false_refusal`) --- "A one-page 308 kB PDF sent as base64 to Document QnA reports 321,774 prompt tokens and 400s — what is the context limit and why is the document so expensive?"
  - what happened: refused an answerable question with another section of the gold page in the context: "The sources do not specify the **context limit** for Document QnA or explain why a 308 kB PDF incurs 321,774 prompt [...]"
  - the judge: The documentation does state context limits (256k tokens on Medium 3.5, Small 4 and Large 3; 128k on Medium 3.1), so declining to answer contradicts the reference answer.
- `mined-011` (unanswerable, search_loop, judged wrong, `missed_refusal`) --- "Can Document QnA answer questions about an image (.png, .jpg), or does it only take PDFs?"
  - what happened: answered a question the dataset marks unanswerable, citing 5 verified source(s): "Yes, **Document QnA** can answer questions about images (such as `.png` or `.jpg`), not just PDFs. The supported image [...]"
  - the judge: The reference states the docs only ever show PDFs for Document QnA and never say images can be used; the answer asserts images are supported by Document QnA, an unsupported invention.
- `mined-019` (single_page, single_pass, judged wrong, `false_refusal`) --- "Does forcing `tool_choice` guarantee that the model calls a tool, and which tool it picks?"
  - what happened: refused an answerable question with the gold section in the context: "{ "answer_markdown": "Forcing `tool_choice` with the value `""
  - the judge: The answer is truncated mid-sentence and conveys no substantive content about tool_choice forcing.

### `2026-09-09-1211-fresh60-shipped`

Dataset `eval/dev-fresh60.jsonl`, generator `ministral-14b-2512`, index `sec1024`,
reranker True. 60 of 60 answers carry a primary
verdict (0 do not), 0 ended in an error. 480 of 480 recorded chunk ids resolved to a page through the corpus.

**By strategy**

| strategy | answers | failures | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| single_pass | 60 | 18 (30%) | 2 (3%) | 0 (0%) | 8 (13%) | 8 (13%) |

**By question type**

| question type | answers | failures | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| api_reference | 10 | 3 (30%) | 0 (0%) | 0 (0%) | 1 (10%) | 2 (20%) |
| capability | 10 | 5 (50%) | 2 (20%) | 0 (0%) | 1 (10%) | 2 (20%) |
| cross_page | 10 | 5 (50%) | 0 (0%) | 0 (0%) | 5 (50%) | 0 (0%) |
| post_cutoff | 10 | 2 (20%) | 0 (0%) | 0 (0%) | 1 (10%) | 1 (10%) |
| single_page | 10 | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) |
| unanswerable | 10 | 3 (30%) | 0 (0%) | 0 (0%) | 0 (0%) | 3 (30%) |

**Sub-labels**

| class | sub-label | failures |
|---|---|---|
| retrieval miss | `candidates_not_recorded` | 2 |
| generation failure | `unverified_quote_from_gold` | 2 |
| generation failure | `verified_quote_from_gold` | 6 |
| refusal failure | `false_refusal` | 5 |
| refusal failure | `missed_refusal` | 3 |

15 of 18 failures carry the reference-defect flag: `judge_names_the_reference` 15, `human_is_more_lenient` 0 (a row can carry both). For comparison, 38 of the 42 answers that passed carry the same `judge_names_the_reference` wording (90%), so that signal on its own separates nothing; `human_is_more_lenient` is the discriminating one.

**Examples**

**retrieval miss**

- `dev-007` (capability, single_pass, judged wrong, `candidates_not_recorded`) --- "which models support Built-In Tools"
  - what happened: no chunk of https://docs.mistral.ai/models in any round; the answer saw https://docs.mistral.ai/studio/agents/agent-tools, https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents, https://docs.mistral.ai/studio/connectors/conversations
  - the judge: The question asks which models support Built-In Tools and the reference lists 8 specific models; the answer instead lists only two alias model names and admits it cannot determine the full list.
- `dev-159` (capability, single_pass, judged partial, `candidates_not_recorded`) --- "Which Mistral models support Predicted Outputs?"
  - what happened: no chunk of https://docs.mistral.ai/models in any round; the answer saw https://docs.mistral.ai/studio/conversations/advanced/predicted-outputs, https://docs.mistral.ai/studio/conversations/structured-output/custom
  - the judge: The answer lists only codestral-latest and mistral-large-2411, omitting the other models the reference names (Mistral Medium, Small, Pixtral Large, GLM, other Codestral versions).

**context miss** -- none in this run.

**generation failure**

- `dev-149` (api_reference, single_pass, judged partial, `unverified_quote_from_gold`) --- "In Mistral AI's Files API, what parameter does the `GET /v1/files/{file_id}/content` (Download File) operation require, and what does it return on success?"
  - what happened: rejected (quote is not in the cited source) quote from the gold section: "Download a file - Operation id: `files_api_routes_download_file` - Tag: files `GET /v1/files/{file_id}/content`"
  - the judge: Correctly identifies the required file_id path parameter and that binary/stream content is returned, but omits the 200 status code and the explicit application/octet-stream content type of the response.
- `dev-033` (cross_page, single_pass, judged partial, `verified_quote_from_gold`) --- "How can I build a single agent that both calls my custom function for fetching the European Central Bank interest rate and generates images, and how do I [...]"
  - what happened: verified quote from the gold section: "for i, chunk in enumerate(response.outputs[-1].content):"
  - the judge: The image-retrieval part matches the reference (ToolFileChunk with file_id downloaded via files endpoint), but the question asks for a single agent with both a function tool and the image_generation tool, and this [...]
- `dev-252` (capability, single_pass, judged partial, `unverified_quote_from_gold`) --- "Which Mistral models support batching?"
  - what happened: rejected (quote is not in the cited source) quote from the gold section: "Codestral (25-01) | yes"
  - the judge: It agrees that all models in the capability matrix support batching, but adds a long specific model list and a Codestral-Mamba caveat that are not in the reference answer, plus irrelevant job-creation code.

**refusal failure**

- `dev-061` (capability, single_pass, judged correct, `false_refusal`) --- "Does Mistral Medium 3 (`mistral-medium-2505`) support Built-In Tools?"
  - what happened: refused an answerable question with the gold section in the context: "Yes, Mistral Medium 3 (`mistral-medium-2505`) supports **Built-In Tools** according to the official documentation. This [...]"
  - the judge: The answer correctly states mistral-medium-2505 supports Built-In Tools, matching the reference.
- `dev-097` (unanswerable, single_pass, judged correct, `missed_refusal`) --- "What is the maximum number of web pages MistralAI-User may visit for a single user request in Vibe, and is there a per-minute rate limit?"
  - what happened: answered a question the dataset marks unanswerable, citing 4 verified source(s): "The MistralAI-User agent in Vibe is **not explicitly documented** to have a defined maximum number of web pages it may [...]"
  - the judge: Correctly states no documented page limit or page-visit rate limit for MistralAI-User, matching the reference answer; extra detail about Open URL fetching only one page is consistent and non-contradictory.
- `dev-072` (capability, single_pass, judged correct, `false_refusal`) --- "Does Mistral Small 3.1 (`mistral-small-2503`) support Built-In Tools?"
  - what happened: refused an answerable question with the gold section in the context: "Yes, Mistral Small 3.1 (`mistral-small-2503`) supports **Built-In Tools** as listed in its [features documentation] and [...]"
  - the judge: Agrees with the reference that mistral-small-2503 supports Built-In Tools.

### `2026-09-09-0312-dev60-rerank`

Dataset `eval/dev.jsonl`, generator `ministral-14b-2512`, index `sec1024`,
reranker True. 120 of 120 answers carry a primary
verdict (0 do not), 0 ended in an error. 1632 of 1632 recorded chunk ids resolved to a page through the corpus.

**By strategy**

| strategy | answers | failures | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| search_loop | 60 | 9 (15%) | 0 (0%) | 0 (0%) | 3 (5%) | 6 (10%) |
| single_pass | 60 | 12 (20%) | 1 (2%) | 0 (0%) | 5 (8%) | 6 (10%) |

**By question type**

| question type | answers | failures | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| api_reference | 20 | 4 (20%) | 1 (5%) | 0 (0%) | 2 (10%) | 1 (5%) |
| capability | 20 | 4 (20%) | 0 (0%) | 0 (0%) | 3 (15%) | 1 (5%) |
| cross_page | 20 | 4 (20%) | 0 (0%) | 0 (0%) | 3 (15%) | 1 (5%) |
| post_cutoff | 20 | 1 (5%) | 0 (0%) | 0 (0%) | 0 (0%) | 1 (5%) |
| single_page | 20 | 2 (10%) | 0 (0%) | 0 (0%) | 0 (0%) | 2 (10%) |
| unanswerable | 20 | 6 (30%) | 0 (0%) | 0 (0%) | 0 (0%) | 6 (30%) |

**Sub-labels**

| class | sub-label | failures |
|---|---|---|
| retrieval miss | `candidates_not_recorded` | 1 |
| generation failure | `no_citation_to_gold` | 2 |
| generation failure | `unverified_quote_from_gold` | 1 |
| generation failure | `verified_quote_from_gold` | 5 |
| refusal failure | `false_refusal` | 6 |
| refusal failure | `missed_refusal` | 6 |

15 of 21 failures carry the reference-defect flag: `judge_names_the_reference` 14, `human_is_more_lenient` 4 (a row can carry both). For comparison, 95 of the 99 answers that passed carry the same `judge_names_the_reference` wording (96%), so that signal on its own separates nothing; `human_is_more_lenient` is the discriminating one.

**Examples**

**retrieval miss**

- `dev-052` (api_reference, single_pass, judged wrong, `candidates_not_recorded`) --- "For the GET /v1/workflows/events/stream operation, are any query parameters required, and what does a 422 response mean?"
  - what happened: no chunk of https://docs.mistral.ai/api/endpoint/events in any round; the answer saw https://docs.mistral.ai/api/endpoint/workflows/executions, https://docs.mistral.ai/studio/workflows/interacting-with-workflows/queries, https://docs.mistral.ai/api/endpoint/workflows/deployments
  - the judge: The answer describes a different endpoint (stream workflow execution logs with a required execution_id path parameter) rather than GET /v1/workflows/events/stream, whose parameters are all optional; it also omits the [...]

**context miss** -- none in this run.

**generation failure**

- `dev-031` (cross_page, single_pass, judged partial, `no_citation_to_gold`) --- "Our organization wants to programmatically automate workspace and API key provisioning, and we also need to cap costs per workspace. Which capability can we [...]"
  - what happened: cited https://docs.mistral.ai/admin/admin-api/usage-metrics instead of the gold section
  - the judge: Correctly names the Admin API for automation but omits the reference's answer that API requests return 429 Too Many Requests once the monthly spending limit is reached.
- `dev-138` (cross_page, single_pass, judged partial, `unverified_quote_from_gold`) --- "I'm ingesting chunks that carry embeddings into a Search Toolkit index configured with MISTRAL_EMBED_DIM_1024. Which chunk field holds the vector, how does [...]"
  - what happened: rejected (quote is not in the cited source) quote from the gold section: "| Schema preset | Embedder constant | |---------------|-------------------| | `MISTRAL_EMBED_DIM_1024` | [...]"
  - the judge: The embedding field and MODEL_1024_EMBEDDING constant are correct, but the answer invents a document_id field for parent resolution instead of parent_ref via hashed source_id.
- `dev-052` (api_reference, search_loop, judged partial, `verified_quote_from_gold`) --- "For the GET /v1/workflows/events/stream operation, are any query parameters required, and what does a 422 response mean?"
  - what happened: verified quote from the gold section: "- `422` — Validation Error (application/json, schema HTTPValidationError)"
  - the judge: Correct that no parameters are required and 422 is a validation error with HTTPValidationError schema, but adds unsupported speculation that workflow_exec_id is 'highly recommended'.

**refusal failure**

- `dev-047` (api_reference, single_pass, judged correct, `false_refusal`) --- "Which fields in the request body are required when calling POST /v1/admin/api-keys to create a Workspace API key?"
  - what happened: refused an answerable question with the gold section in the context: "To create a Workspace API key by calling `POST /v1/admin/api-keys`, the following fields in the request body are [...]"
  - the judge: Matches the reference: workspace_uuid and user_id required, name and expiration optional.
- `dev-011` (unanswerable, search_loop, judged correct, `missed_refusal`) --- "Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted?"
  - what happened: answered a question the dataset marks unanswerable, citing 1 verified source(s): "There is no explicit mention of a timeout or expiration period for the open SSO configuration modal in the provided [...]"
  - the judge: Correctly states the documentation mentions no timeout/expiration for the SSO configuration modal, matching the reference answer.
- `dev-121` (single_page, single_pass, judged correct, `false_refusal`) --- "Which Mistral security advisory was published in May 2026, and what does it concern?"
  - what happened: refused an answerable question with the gold section in the context: "The Mistral security advisory published in May 2026 is **MAI-2026-002**. It concerns a **TanStack supply chain attack** [...]"
  - the judge: Identifies MAI-2026-002 and the TanStack supply chain attack on Mistral SDK packages, matching the reference; extra detail is not contradicted by it.

### `2026-09-09-1228-noisy-single`

Dataset `eval/dev-noisy.jsonl`, generator `ministral-14b-2512`, index `sec1024`,
reranker True. 105 of 105 answers carry a primary
verdict (0 do not), 0 ended in an error. 840 of 840 recorded chunk ids resolved to a page through the corpus.

**By strategy**

| strategy | answers | failures | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| single_pass | 105 | 44 (42%) | 13 (12%) | 0 (0%) | 12 (11%) | 19 (18%) |

**By question type**

| question type | answers | failures | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| api_reference | 18 | 8 (44%) | 4 (22%) | 0 (0%) | 2 (11%) | 2 (11%) |
| capability | 17 | 7 (41%) | 3 (18%) | 0 (0%) | 1 (6%) | 3 (18%) |
| cross_page | 17 | 12 (71%) | 3 (18%) | 0 (0%) | 6 (35%) | 3 (18%) |
| post_cutoff | 19 | 6 (32%) | 0 (0%) | 0 (0%) | 3 (16%) | 3 (16%) |
| single_page | 17 | 4 (24%) | 3 (18%) | 0 (0%) | 0 (0%) | 1 (6%) |
| unanswerable | 17 | 7 (41%) | 0 (0%) | 0 (0%) | 0 (0%) | 7 (41%) |

**Sub-labels**

| class | sub-label | failures |
|---|---|---|
| retrieval miss | `candidates_not_recorded` | 13 |
| generation failure | `no_citation_to_gold` | 2 |
| generation failure | `verified_quote_from_gold` | 10 |
| refusal failure | `false_refusal` | 12 |
| refusal failure | `missed_refusal` | 7 |

28 of 44 failures carry the reference-defect flag: `judge_names_the_reference` 28, `human_is_more_lenient` 0 (a row can carry both). For comparison, 59 of the 61 answers that passed carry the same `judge_names_the_reference` wording (97%), so that signal on its own separates nothing; `human_is_more_lenient` is the discriminating one.

**Examples**

**retrieval miss**

- `dev-019-vague` (single_page, single_pass, judged wrong, `candidates_not_recorded`) --- "Where do I look to find how much money my team's shared area has used so far this month and how much of the AI word-counting stuff it burned, and what kinds of [...]"
  - what happened: no chunk of https://docs.mistral.ai/admin/workspaces/usage-limits in any round; the answer saw https://docs.mistral.ai/admin/billing-usage/usage-limits, https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning, https://docs.mistral.ai/resources/deprecated/finetuning/classifier_factory
  - the judge: The documentation does answer this (Workspaces > Usage tab), so declining to answer is incorrect.
- `dev-027-vague` (single_page, single_pass, judged wrong, `candidates_not_recorded`) --- "If I try again the items that didn't work in a big job I sent at once, what happens to the scoring checks for that job and the stuff it shows me on the web [...]"
  - what happened: no chunk of https://docs.mistral.ai/studio/observability/evaluations/retry-failed-records in any round; the answer saw https://docs.mistral.ai/studio/batch-processing, https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning, https://docs.mistral.ai/studio/observability/evaluations/goals
  - the judge: The documentation does answer this question (failed records are retried, evaluator scores recomputed, run updated in place), so declining to answer is incorrect.
- `dev-041-vague` (cross_page, single_pass, judged wrong, `candidates_not_recorded`) --- "When adding text pieces that have short locator descriptions and then turning them into vectors, how do the vector field and the fixed ID on each piece affect [...]"
  - what happened: no chunk of https://docs.mistral.ai/studio/search/search-toolkit/concepts/document-model, https://docs.mistral.ai/studio/search/search-toolkit/concepts/embedding-model in any round; the answer saw https://docs.mistral.ai/studio/search/search-toolkit/ingestion, https://docs.mistral.ai/studio/knowledge-rag/rag_quickstart, https://docs.mistral.ai/studio/knowledge-rag/embeddings/text_embeddings
  - the judge: It answers a generic RAG-from-scratch question, ignoring that the chunk id is deterministically hashed from source_id plus locator (enabling overwrite on re-ingest) and omitting the preset/embedder pairing (e.g. [...]

**context miss** -- none in this run.

**generation failure**

- `dev-064-wrong_term` (capability, single_pass, judged wrong, `no_citation_to_gold`) --- "Which Mistral models support Bounding Box Detection?"
  - what happened: cited https://docs.mistral.ai/models/ocr-4-0, https://docs.mistral.ai/models/ocr-4-1, https://docs.mistral.ai/studio/document-processing/basic_ocr instead of the gold section
  - the judge: The answer omits OCR 2 (mistral-ocr-2505), which the reference lists as supporting bbox-extraction, and asserts that bounding box detection is not supported in pre-OCR 4.0 models, directly contradicting the reference.
- `dev-003-wrong_term` (cross_page, single_pass, judged partial, `verified_quote_from_gold`) --- "I'm building an ML inference workflow where a model load is expensive but each prediction call is a quick, exception-safe computation. How should I combine [...]"
  - what happened: verified quote from the gold section: "Reach for sticky sessions when several activities in a row need to hit the same expensive resource — a loaded ML model"
  - the judge: The approach and the ignored settings (sticky_to_worker, rate_limit, heartbeat_timeout) match the reference, but it never uses run_activities_locally() for the predict calls, which is the reference's key mechanism for [...]
- `dev-276-chatty` (post_cutoff, single_pass, judged partial, `no_citation_to_gold`) --- "I'm building an internal knowledge tool for my team and I'm wiring up the Mistral Python SDK to manage our documents. At some point users need to remove one [...]"
  - what happened: cited https://docs.mistral.ai/api/endpoint/beta/libraries/documents instead of the gold section
  - the judge: The answer correctly identifies the two required identifiers (library_id and document_id) and the REST endpoint, but omits the actual Python SDK call client.beta.libraries.documents.delete(...) that the reference answer [...]

**refusal failure**

- `dev-009-wrong_term` (post_cutoff, single_pass, judged wrong, `false_refusal`) --- "When using HTMLExtractor from the mistralai-search-toolkit, what is the default value of the error_handling parameter, and which options are allowed for it?"
  - what happened: refused an answerable question with the gold section in the context: "The `HTMLExtractor` from the `mistralai-search-toolkit` does not explicitly mention an `error_handling` parameter in [...]"
  - the judge: The reference answer states decode_errors defaults to 'strict' with allowed values 'strict', 'ignore', 'replace'; the answer under test declines to answer and claims the parameter is absent, contradicting the reference.
- `dev-011-wrong_term` (unanswerable, single_pass, judged wrong, `missed_refusal`) --- "Is there a timeout or expiration period for the open OAuth configuration modal after which the setup must be restarted?"
  - what happened: answered a question the dataset marks unanswerable, citing 1 verified source(s): "Yes, there is a timeout for the open OAuth configuration modal. The auth URL provided during the OAuth flow has a [...]"
  - the judge: The question asks about the SSO/OAuth configuration modal timeout, which the documentation does not cover; the answer invents a timeout by conflating it with the unrelated workflow Connector OAuth auth URL window.
- `dev-032-vague` (cross_page, single_pass, judged wrong, `false_refusal`) --- "If I want to save money and time on a back-and-forth chat where most of my text stays the same each time, how do the thing where the system remembers repeated [...]"
  - what happened: refused an answerable question with the gold section in the context: "The Mistral API offers two mechanisms to optimize repeated interactions in chat workflows: **prompt caching** and [...]"
  - the judge: The answer substitutes RAG for predicted outputs and fails to state the key facts: cached tokens billed at 10% of input price and verification via usage.prompt_tokens_details.cached_tokens, while predicted outputs don't [...]

### `2026-09-09-1230-clean-single`

Dataset `eval/dev.jsonl`, generator `ministral-14b-2512`, index `sec1024`,
reranker True. 120 of 120 answers carry a primary
verdict (0 do not), 0 ended in an error. 960 of 960 recorded chunk ids resolved to a page through the corpus.

**By strategy**

| strategy | answers | failures | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| single_pass | 120 | 30 (25%) | 3 (2%) | 0 (0%) | 11 (9%) | 16 (13%) |

**By question type**

| question type | answers | failures | retrieval miss | context miss | generation failure | refusal failure |
|---|---|---|---|---|---|---|
| api_reference | 20 | 5 (25%) | 1 (5%) | 0 (0%) | 1 (5%) | 3 (15%) |
| capability | 20 | 5 (25%) | 0 (0%) | 0 (0%) | 1 (5%) | 4 (20%) |
| cross_page | 20 | 8 (40%) | 1 (5%) | 0 (0%) | 7 (35%) | 0 (0%) |
| post_cutoff | 20 | 3 (15%) | 1 (5%) | 0 (0%) | 1 (5%) | 1 (5%) |
| single_page | 20 | 2 (10%) | 0 (0%) | 0 (0%) | 1 (5%) | 1 (5%) |
| unanswerable | 20 | 7 (35%) | 0 (0%) | 0 (0%) | 0 (0%) | 7 (35%) |

**Sub-labels**

| class | sub-label | failures |
|---|---|---|
| retrieval miss | `candidates_not_recorded` | 3 |
| generation failure | `unverified_quote_from_gold` | 1 |
| generation failure | `verified_quote_from_gold` | 10 |
| refusal failure | `false_refusal` | 9 |
| refusal failure | `missed_refusal` | 7 |

21 of 30 failures carry the reference-defect flag: `judge_names_the_reference` 21, `human_is_more_lenient` 0 (a row can carry both). For comparison, 83 of the 90 answers that passed carry the same `judge_names_the_reference` wording (92%), so that signal on its own separates nothing; `human_is_more_lenient` is the discriminating one.

**Examples**

**retrieval miss**

- `dev-052` (api_reference, single_pass, judged wrong, `candidates_not_recorded`) --- "For the GET /v1/workflows/events/stream operation, are any query parameters required, and what does a 422 response mean?"
  - what happened: no chunk of https://docs.mistral.ai/api/endpoint/events in any round; the answer saw https://docs.mistral.ai/api/endpoint/workflows/executions, https://docs.mistral.ai/studio/workflows/interacting-with-workflows/queries, https://docs.mistral.ai/api/endpoint/beta/observability/traces
  - the judge: The answer invents parameters (execution_id path param, run_id, after, last_event_id) from a different endpoint and omits the actual optional params (scope, activity_id, start_seq); only the 'no required query params' [...]
- `dev-221` (cross_page, single_pass, judged wrong, `candidates_not_recorded`) --- "I'm building a multi-turn code-editing assistant that regenerates large code files with minor changes each turn, using codestral-latest. How can I reduce [...]"
  - what happened: no chunk of https://docs.mistral.ai/studio/conversations/advanced/predicted-outputs, https://docs.mistral.ai/studio/conversations/advanced/prompt-caching in any round; the answer saw https://docs.mistral.ai/studio/conversations/chat-completion, https://docs.mistral.ai/studio/conversations/reasoning, https://docs.mistral.ai/resources/deprecated/finetuning/text_vision_finetuning
  - the judge: The documentation does cover latency optimizations (prompt caching with prompt_cache_key and predicted outputs for codestral-latest), so declining to answer contradicts the reference answer.
- `dev-276` (post_cutoff, single_pass, judged partial, `candidates_not_recorded`) --- "How do I delete a single document from a Library using the Mistral Python SDK, and what are the required identifiers?"
  - what happened: no chunk of https://docs.mistral.ai/studio/search/libraries in any round; the answer saw https://docs.mistral.ai/api/endpoint/beta/libraries/documents, https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference, https://docs.mistral.ai/api/endpoint/beta/libraries
  - the judge: Identifiers (library_id, document_id) match the reference, but the SDK call shown (client.libraries.documents.delete_v1) omits the beta namespace and differs from client.beta.libraries.documents.delete, and the [...]

**context miss** -- none in this run.

**generation failure**

- `dev-162` (capability, single_pass, judged partial, `unverified_quote_from_gold`) --- "Does the model `codestral-embed-2505` support the `embeddings` feature?"
  - what happened: rejected (quote is not in the cited source) quote from the gold section: "Codestral Embed (`codestral-embed-2505`) | yes"
  - the judge: Correctly confirms embeddings support but omits the batching capability stated in the reference answer, and cites a model name (codestral-embed) that differs from codestral-embed-2505.
- `dev-037` (cross_page, single_pass, judged partial, `verified_quote_from_gold`) --- "I'm building a workflow that handles PII and expected business-rule failures. How should I encrypt just the sensitive fields, and what structured fields can [...]"
  - what happened: verified quote from the gold section: "Encrypt all payloads (workflow inputs, activity I/O, signal data) before they leave your worker."
  - the judge: The WorkflowsException guidance (code, status, message) matches the reference, but the encryption half answers a different scheme: it describes encrypting ALL payloads rather than the partial mode with [...]
- `dev-039` (cross_page, single_pass, judged partial, `verified_quote_from_gold`) --- "I want teammates across my organization to work with a step-by-step reasoning assistant for multi-factor decisions. Can I attach Think mode to an Agent, share [...]"
  - what happened: verified quote from the gold section: "An Agent is a **specialized assistant** you configure once and reuse across conversations. Give it instructions, tools, [...]"
  - the judge: Correctly says Think mode cannot be attached to an Agent and must be toggled per conversation, but omits the reference's limit that only one Agent can be active at a time and overreaches with unsupported Work/Skills [...]

**refusal failure**

- `dev-019` (single_page, single_pass, judged partial, `false_refusal`) --- "Where can I see a Workspace's month-to-date spend and token consumption, and what usage breakdowns are available?"
  - what happened: refused an answerable question with the gold section in the context: "To see a Workspace's **month-to-date spend** and **token consumption**, follow these steps: 1. Open the **Admin Panel** [...]"
  - the judge: The Workspace Usage tab steps and breakdowns match the reference, but the answer adds Organization-level dashboard details beyond the reference's scope without citations.
- `dev-011` (unanswerable, single_pass, judged partial, `missed_refusal`) --- "Is there a timeout or expiration period for the open SSO configuration modal after which the setup must be restarted?"
  - what happened: answered a question the dataset marks unanswerable, citing 1 verified source(s): "The Mistral documentation does not specify a timeout or expiration period for the open SSO configuration modal during [...]"
  - the judge: Correctly states no timeout is documented, but adds an unsupported speculation that closing the modal may require restarting setup.
- `dev-061` (capability, single_pass, judged correct, `false_refusal`) --- "Does Mistral Medium 3 (`mistral-medium-2505`) support Built-In Tools?"
  - what happened: refused an answerable question with the gold section in the context: "Yes, Mistral Medium 3 (`mistral-medium-2505`) supports **Built-In Tools** according to the official documentation. This [...]"
  - the judge: Correctly states that mistral-medium-2505 supports Built-In Tools, matching the reference answer.

## Figures

`figures/` is regenerated from `metrics.json` by `make eval-report run=eval/runs/2026-09-09-2350-failure-analysis-v2`.

- `failure-classes.svg`: what each run's failures are made of, one stacked bar per run

## Files

- `config.json` --- the runs analysed, the corpus, the labels, and the judge setting.
- `records.jsonl` --- one row per failed answer: its class, its sub-label, the evidence
  that decided the class, and every intermediate fact the decision used
  (`gold_retrieved`, `gold_in_context`, `gold_section_in_context`, `gold_chunk_dropped`,
  the retrieved pages, the defect signals). Every number in this README is a count over
  these rows.
- `metrics.json` --- every number in the tables above.

## What it feeds

D-016 (which checks the answer evaluation reports), D-034 and D-035 (whether the next
effort belongs in retrieval or in the answer layer) and D-021b (the reference-defect rate
the judge study reports beside its own numbers).
