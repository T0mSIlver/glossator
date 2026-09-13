"""The README's fixed prose: the classification rules and what they cannot see."""

from __future__ import annotations

from glossator.eval.failures.models import CLASS_TITLES, DefectSignal, FailureClass, SubLabel

RULES = f"""Every answer whose primary judge verdict is `partial` or `wrong`, or whose
refusal went the wrong way (it refused a question the dataset says is answerable,
or answered one the dataset marks unanswerable), is a failure and gets exactly one
class. The tests run in this order, and each one is only reached when the one
before it passed, so a class always means "everything upstream of it worked".

1. **{CLASS_TITLES[FailureClass.RETRIEVAL_MISS]}** -- no chunk of a gold page appears in
   `trace.events[].result_ids` for any round: not the seed retrieval, not any of the
   search loop's tool calls. Chunk ids are resolved to pages through the corpus, not
   through the run: a chunk id is `uuid5(NAMESPACE_DNS, "<page url>:char:<start>-<end>")`,
   so re-chunking the vendored corpus with the run's own chunker rebuilds the whole map
   offline. Sub-labels: `{SubLabel.RERANKER_DROP.value}` when a recorded reranker call
   shows the gold page among the candidates it was offered and it did not come back;
   `{SubLabel.SEARCH_MISS.value}` when the gold page was not among those candidates;
   `{SubLabel.CANDIDATES_NOT_RECORDED.value}` when the run has no recorded reranker call
   for that question, which is every run made before reranker calls reached the call
   ledger (D-023b), so search and reranker cannot be told apart there.
2. **{CLASS_TITLES[FailureClass.CONTEXT_MISS]}** -- a gold chunk came back from retrieval
   but no source in `trace.sources` came from a gold page, so the model never saw it.
   Sub-labels: `{SubLabel.DROPPED_FROM_CONTEXT.value}` when the gold chunk is in
   `trace.dropped_chunk_ids`, `{SubLabel.OUTRANKED_IN_ASSEMBLY.value}` otherwise.
3. **{CLASS_TITLES[FailureClass.GENERATION]}** -- a gold chunk was in the assembled
   context, the model answered rather than refusing, and the answer is still partial or
   wrong. Sub-labels say what the citations did with it:
   `{SubLabel.NO_CITATION_TO_GOLD.value}` (the answer cited something else),
   `{SubLabel.UNVERIFIED_QUOTE_FROM_GOLD.value}` (it cited the gold section but the quote
   failed verification), `{SubLabel.VERIFIED_QUOTE_FROM_GOLD.value}` (it quoted the gold
   section verbatim and answered wrong anyway, which is the strongest evidence of a model
   limit rather than a pipeline one).
4. **{CLASS_TITLES[FailureClass.REFUSAL]}** -- reported separately, because D-035b showed
   false refusals dominate under noise. `{SubLabel.FALSE_REFUSAL.value}`: the answer set
   `insufficient_evidence` on an answerable question *with a gold chunk in the context*.
   `{SubLabel.MISSED_REFUSAL.value}`: it answered a question the dataset marks
   unanswerable. A refusal that follows a retrieval or context miss is classed as that
   miss instead, because refusing when the evidence never arrived is the pipeline working,
   and an unanswerable question has no gold to retrieve, so tests 1 to 3 never apply to
   one.
5. **question or reference defect** -- *flagged, not decided*, and not a class: it is a
   column on the rows above and overlaps them. Two deterministic signals raise it, and
   neither is evidence on its own: `{DefectSignal.JUDGE_NAMES_THE_REFERENCE.value}`, the
   judge's one-sentence reason mentions the reference answer; and
   `{DefectSignal.HUMAN_IS_MORE_LENIENT.value}`, a hand label for that answer scores it
   higher than the judge did (D-021b found every primary-judge disagreement went the
   strict way). The first signal is reported with the rate at which answers that *passed*
   carry the same wording, because `answer-judge/v2` shows the judge the reference and
   tells it to grade against it, so naming it is the norm rather than a symptom. Deciding
   whether a reference is actually wrong needs a judge that reads the gold section text,
   which is what `--judge-model provider:model` runs and what this run did not do."""

BLIND_SPOTS = f"""\
- **A wrong gold link in the dataset looks like a retrieval miss.** The gold URL is
  taken as ground truth. If the dataset points at the wrong page, retrieval can have
  found the page that really answers the question and still be counted as having missed.
  This is the single largest source of error in the retrieval-miss column and the reason
  the defect flag exists.
- **A correct answer from a page that is not gold looks like a failure.** D-033 saw this
  on capability questions, where a model card carries the same fact as the `/models`
  matrix. The one relaxation the answer evaluation already applies is applied here too --
  the card of a model the question names counts as the gold page -- and nothing beyond it.
- **`{SubLabel.CANDIDATES_NOT_RECORDED.value}` hides the reranker.** Where a run has no
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
  `gold_section_in_context` column on each row says which of the two happened."""
