# A Work session that searched thirteen times for a page that does not exist

One question asked in Mistral Work on 2026-09-11 at 14:10, with the deployed
three-tool server attached as a Connector: "What are the main features in the
new Mistral search toolkit? Search the docs." The full conversation is in
`transcript.md`.

## What happened

| calls | outcome |
|---|---|
| 13 `mistral_docs_search` | 8 returned the same five sections of the Search Toolkit landing page |
| 2 `mistral_docs_read_page` | the landing page and the quickstart, both complete |
| 2 `mistral_docs_read_page` on a guessed URL | `…/search-toolkit/evaluation`, `E_UNKNOWN_PAGE` both times |

The landing page says the toolkit "provides components for ingestion,
retrieval, and evaluation". Ingestion and retrieval each have a page tree;
evaluation has no page, in the pinned corpus and on the live site (404 on
`/search-toolkit/evaluation`). The model reasoned that a named component must
have a page and kept searching: `evaluation search toolkit`, `evaluation
metrics`, `evaluation`, `retrieval evaluation`, `site:docs.mistral.ai/studio/
search/search-toolkit`, `search-toolkit/evaluation`, `retrieval evaluation
metrics hit rate`, and guessed the URL twice.

The model was right that the component exists: the installed package ships
`mistralai.search.toolkit.evals` (`RetrieverEvaluator`, `MetricsCalculator`,
`EvaluationDataset`, `RetrievalMetrics`), which no documentation page mentions.
`docs/upstream.md` row 16 records the defect.

## Where the answer went wrong

The model's own draft, visible in the transcript, said "Evaluation: mentioned
as a core component but details not fully documented in the pages I accessed".
The answer it sent replaced that with an "Evaluation" section built from the
semantic cache's `CacheMetrics` hit-rate counter, cited to the cache page. Two
smaller stretches in the same answer: "S3, GCS, Azure" file loading inferred
from the names of optional extras, and "paragraph-aware" chunking inferred
from a class name. The refusal rule held for twelve calls and broke at the
write-up, which is the over-reach cell D-038 and D-038b measure.

## What changed because of it

- The server instructions gained two stop rules: a search that returns the
  pages already read means the corpus has nothing more, and an unknown page
  URL means the page does not exist at this commit (D-044a).
- `eval/mined-v2.jsonl` row `mined2-084` asks the question this session could
  not answer, typed `unanswerable`, with the reference answer stating what the
  documentation does and does not say.
- `docs/upstream.md` row 16.
