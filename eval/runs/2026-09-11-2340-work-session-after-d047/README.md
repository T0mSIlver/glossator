# The tricky question, asked in Work eleven minutes after D-047 went live

One question in Mistral Work at 23:40 on 2026-09-11, six minutes after the
D-047 server came up: "What are the main features in the new mistral search
toolkit to evaluate a retrieval pipeline? Search the docs". The same question
as the 20:36 session (D-047, first fact). The reduced conversation is in
`transcript.md`.

## Calls

| calls | count | notes |
|---|---|---|
| `mistral_docs_search` with words | 16 | twelve keyword strings, `evaluation` alone twice; five returned the landing page's sections already read |
| `mistral_docs_search` listing, `under` set | 2 | the toolkit subtree (27 pages) and `/studio/search` (29 pages): positive proof twice that no evaluation page exists |
| `mistral_docs_read_page` | 8 | seven whole pages, one guessed URL `…/search-toolkit/evaluation`, refused with `E_UNKNOWN_PAGE` and not retried |

26 calls against 19 at 20:36. No read used a section key; every page read was
small enough to arrive whole.

## The answer

Better than at 20:36 in three ways: it opens with "the dedicated evaluation
module documentation is not yet fully published"; it names no metric the tools
did not print (no MRR, no NDCG); and it accepted the unknown-page error and the
two listings as proof instead of guessing again. The model's last thought says
it will answer from "what is explicitly stated", "the Observability SDK
features that likely integrate", and "standard IR evaluation metrics that would
be relevant", and the answer does exactly that: precision, recall, F1, hit rate
and MRR "by comparing retrieved results against ground truth" are presented
as toolkit capabilities, and "Search Toolkit integrates with Mistral's
Observability Evaluation SDK" is stated as fact. No page says either. This is
the over-reach of D-038 in a hedged form, not a hallucinated section.

The answer links two pages, the toolkit landing page and the Observability
evaluations page, as bare page URLs. The tool results carried eight `cite:`
lines with text fragments; none was copied. Haiku at low effort, on the same
question and the same server family earlier the same evening, refused cleanly
in five searches (`2026-09-11-2130-consumer-haiku`).
