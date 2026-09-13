# What the system still gets wrong

Four classes of question the shipped pipeline fails, each grounded in recorded
runs with question ids, with the cause, the fix, and what the fix costs. The
evidence is the failure attribution of `eval/runs/2026-09-09-2350-failure-analysis-v2`
(five answer runs, 575 answers, 177 failures classified from the records
without a model, D-042) and the Medium 3.5 replay of the same questions
on Mistral's API (D-017c), which says which classes survive a stronger generator. Question ids
resolve in `eval/dev.jsonl`, `eval/dev-noisy.jsonl` and `eval/mined.jsonl`; the
run directory named with each id holds the answer, its context, the judge's
reason and the class.

This is its own page rather than a section of `evaluation.md` because that
page tells the evaluation story dataset by dataset and this one is organised by
what to fix next; each class needs its run beside every number, which is more
than a section carries. `evaluation.md` and the README's "Read next" list
point here.

Sizes, over the 177 classified failures: exact-value shortfalls 55, false
refusals 35, missed refusals 34, retrieval misses 26, answers citing the wrong
section 19, quotes from the right section that failed verification 8. Context
misses are zero in every run.

## 1. The answer stops one fact short of the reference

**What it is.** The model reads the right passage, quotes it verbatim, answers
the question as asked, and the reference answer wants one more thing: the
version the feature needs, the second accepted form, the related limit. The
judge scores it `partial`. This is the largest class (55 of 177) and it is the
shape of most failures on real questions: on the mined set a quarter of all
answers are partial (0.24 with Ministral 14B, 0.26 with Medium 3.5).

**Examples** (`2026-09-09-1253-mined-shipped`, single pass unless noted).

- `mined-009`, "How do I make OCR return tables as separate structured output
  instead of inline markdown?" The answer names `table_format` and its values
  and quotes the sentence that defines them; the reference also wants "OCR 2512
  or newer". Partial under both generators.
- `mined-004`, running OCR on a `.jpg` without converting to PDF. The answer
  gives `image_url` with a base64 data URL; the reference also wants the hosted
  URL form and that `document_url` is for PDF, PPTX and DOCX. Partial under both.
- `mined-023`, whether JSON mode guarantees the schema. Right answer, right
  quote; the reference also wants the "mention JSON in the prompt" caveat.
  Partial under both.
- `mined-001` (search loop), which `purpose` values file upload accepts. The
  three values are listed and quoted from the API reference; the reference
  answer also lists the other body fields.

**Why it fails.** Two causes, and the record separates them. The prompt asks for
an answer, not for the exact value or limit first, and a model answering a
"how do I" question writes the procedure and stops. And the references were
generated from the gold section (D-020a), so they enumerate what the section
says rather than what the question needs; the human labels found the reader
more lenient than the judge on every disagreement, and one reference in forty
wrong (D-021b). The replay on Mistral's API is the test of whether the
generator is the cause; its judged verdicts, and so how many mined partials stay
partial under Medium 3.5, are pending (D-017c).

**What would fix it.** In the prompt: "state the exact value, limit or
parameter before explaining; when the source names a version or a condition
for the feature, name it." On the reference side: a judged pass over the
references against the gold section text, which the failure tool already
implements as `--judge-model` and has not run, to retire references that ask
for more than the question does.

**What it costs.** The prompt rule is one line, measured by the replay path:
the recorded contexts with a new system message, 288 questions, about 1 USD on
Medium 3.5 or 0.10 USD on Ministral 14B, judged on z.ai at no Mistral cost.
The reference pass is 145 judge calls on GLM, no Mistral cost, and a human
sample of the retirements. Expected effect: this class is half of the gap
between 0.80 and 1.0 on the mined set; recovering a third of it is the realistic
target, since some partials are real omissions.

## 2. A question the documentation does not answer, asked in its own words

**What it is.** The question is unanswerable, the corpus holds facts next to it,
and the model assembles an answer from the neighbours. 34 of 177 failures, all
on unanswerable questions; on the mined set, where the unanswerables come from
real users (no status page, no hosted reranker, no local token counting), the
refusal rate is 0.61 to 0.67 against 0.90 on generated unanswerables (D-038a).

**Examples** (`2026-09-09-1253-mined-shipped`, single pass).

- `mined-084`, "Does Mistral host a reranker model I can call as an endpoint?"
  The answer says yes and cites the Search Toolkit's `CrossEncoderReRanker`
  page, which describes a component the reader must host. Wrong under both
  generators.
- `mined-011`, whether Document QnA takes images. The answer says yes, citing
  six verified sources about the OCR processor and vision models; the
  documentation never shows Document QnA with an image. Wrong under both.
- `mined-016`, where to check for an OCR incident. No status page exists in the
  corpus; the search loop kept searching and returned nothing.
- `dev-188` (`2026-09-09-0312-dev60-rerank`), pagination limit on campaigns.
  The answer asserts a limit the page does not state. The reader's notes
  flagged the reference itself on this one (D-021b).

**Why it fails.** Every quote verifies, because the sentences are real; what is
false is the bridge between them, and the verifier checks spans, not claims
(D-027a saw this first on "128 tools"). Similarity floors cannot catch it:
these questions are made of the corpus's vocabulary and their best hit scores
like an answerable one (D-030b). The refusal rule fires on "no verified
citation", which is the wrong signal here, and D-042 showed that loosening it
the other way flips 43 correct refusals into wrong answers.

**What would fix it.** A claim check rather than a span check: after the
answer, one call that reads the answer's leading claim against the cited
passages and asks whether the passages state it or only something adjacent,
the question the judge's groundedness prompt already asks. A `no` sets
`insufficient_evidence`. The agent surface has a cheaper form of the same
fix: the instructions tell the consumer to say when a page does not state the
thing (D-044), and a consumer with its own reasoning reformulates rather than
bridges (D-035b).

**What it costs.** One extra model call per answer on the `answer` path,
about 1,500 prompt tokens: 0.003 USD and 2 to 3 s on Medium 3.5, measured
against the mined unanswerables and the 43 correct refusals the rule already
gets right, since the check must not undo them. Not on the agent path.

## 3. The question is not in the documentation's words

**What it is.** The right page exists and retrieval does not find it: 26 of
177 failures, half of them on the noisy set, where a vague wording or a wrong
product term costs the single pass 19 points of correctness (D-035b). On real
questions it is the user's own framing that misses: a symptom, a type error, a
word the docs do not use.

**Examples.**

- `mined-006` (`mined-shipped`, single pass), "OCR only gives me an
  `![img-0.jpeg](img-0.jpeg)` placeholder for figures, how do I get a
  description of each image?" The answer is the annotations page; nothing of
  it was retrieved.
- `mined-017` (same run), where API and model changes are announced. Retrieval
  returned the platform overview and two Vibe pages; the changelog and
  model-lifecycle pages never appeared.
- `mined-007` and `mined-046` (search loop), an unexpected keyword argument
  and a TypeScript type that rejects `/v1/ocr`: the API reference pages for
  OCR and batch were not retrieved in any round.
- `dev-027-vague` (`2026-09-09-1228-noisy-single`), the retry-failed-records
  question rewritten without its nouns: the batch-processing page came back
  instead and the answer refused.

**Why it fails.** Hybrid retrieval scores the question's words against the
page's words. Vector similarity carries a paraphrase but not a symptom, and
the lexical half sees nothing when the term is wrong. On clean questions
retrieval misses are 1 to 3%; on vague and wrong-term questions 12% (D-042).
An always-on rewrite recovers a fifth of the loss and costs 5 points on clean
questions, because a question already in the documentation's words can only
lose specificity (D-035b).

**What would fix it.** Rewrite only when the first retrieval is weak: a low
top score or no lexical footing, both already in the trace, triggers one
rewrite into the documentation's vocabulary and a second retrieval. On the
agent path the consumer does this itself, and the loop's lead doubled on
noisy questions for exactly that reason.

**What it costs.** One call of about 300 tokens, 0.0006 USD at Medium prices
and 0.7 s, on the minority of questions that trigger it. Measured on
`eval/dev-noisy.jsonl` against `2026-09-09-1228-noisy-single`, and on the clean
set to confirm the 5-point loss is gone.

## 4. The answer is right and the refusal rule throws it away

**What it is.** The model answers correctly, its quote fails verification, the
answer has no verified citation, and the rule "no verified citation means
insufficient evidence" turns it into a refusal. 35 of 177 failures, a third of
them capability questions and a quarter API-reference questions. Under Medium
3.5 on Mistral's API it is 4 of 50 answerable tuned questions against 3 with
Ministral 14B, and 2 of 50 fresh questions against 4: Medium writes one long
quote where the 14B wrote several short ones (145 characters on the tuned set)
and one failed quote is then the whole citation list (D-017c).

**Examples.**

- `dev-047` (`2026-09-09-0312-dev60-rerank`), required fields of
  `POST /v1/admin/api-keys`. The answer is judged correct; the quote joins two
  parameter rows of the API reference, the verifier finds no such span, the
  answer is recorded as a refusal.
- `dev-066` (`2026-09-09-1230-clean-single`), which models support
  `moderations`. Both models named; the quote is a reformatted table row.
- `dev-064` (`2026-09-10-1615-medium35-replay-dev60-rerank`), which models
  support BBox extraction: the three OCR models are right, the quote splices
  the capability matrix with commas and fails.
- `mined-040` (`mined-shipped`), where to see each model's capabilities: the
  answer links the matrix page and quotes a Markdown link's text without its
  syntax.
- `mined-015` (`mined-shipped`), context limit behind a 321,774-token PDF: the
  page holds the limits in another section and the answer refused.

**Why it fails.** The verifier requires a contiguous span of the Markdown
source, with whitespace and emphasis normalised, which is what makes a quote
checkable and what the sentence-highlight link needs. Table rows, list items
and link text are exactly the places where a model quotes the page as a reader
sees it: `[Mistral account](url)` becomes `Mistral account`, two cells become
one clause, a long span gets an ellipsis. The prompt says "at least ten
characters, character for character" and nothing about an upper bound, so a
model that follows instructions well writes the longest faithful quote it can.
The rule then does what D-042 decided it should: without a verified quote,
refuse.

**What would fix it.** Bound the quote in the prompt: one span per claim, one
sentence or one table cell, no ellipsis, copied from the source's Markdown
including link syntax. The verifier stays as it is, since the spans it rejects
are also the spans a browser cannot highlight (D-036b). A second lever, for
capability questions specifically, is to accept a quote that matches a single
table cell, which the source-span rebuild already locates.

**What it costs.** A prompt change, measured by replay like class 1, on the
same 288 questions, about 1 USD on Medium. The expected effect is direct: on
the tuned set it is the whole 9-point gap in refusal-correct between the two
generators, and on capability questions it is the difference between citing
the matrix and refusing.

## What is not on this list

- **Reranker drops** cannot be separated from search misses in the runs before
  D-023b, when reranker calls did not reach the ledger. Later runs record
  them, and the failure tool labels them apart.
- **Search-loop empty answers** on the mined set (`mined-007`, `mined-046`,
  `mined-083` above) are the loop returning nothing after its rounds; the loop
  is the documented thorough mode, not the default, and D-035e found its caps
  are not the lever.
- **French questions** were a class until the question was rendered in English
  for retrieval (D-008b); the residual gap is 2 points.
- **Capability questions at rank 1** (0.51 reranked, D-034) are a retrieval
  precision problem the gold's strictness overstates: a model card is also a
  correct source, and the relaxation is recorded in `gold_relaxed_matches`.
