"""Why an answer failed: retrieval, context, generation, refusal, or the question.

An answer evaluation says how often the pipeline is wrong. It does not say which
part of the pipeline was wrong, and that is the number that decides where the next
effort goes: a retrieval miss and a generation failure on the same question call
for opposite work, and on a small generator (Ministral 3 14B, D-017a) the
temptation is to blame the model for both.

This reads the records an answer evaluation already wrote (D-023) and assigns each
failed answer to one class, in a fixed order, from evidence that is in the record:
the chunk ids every retrieval round returned, the chunk ids the assembled context
carried, the citations and their verification, and the refusal flag. It makes no
model call, so it can be re-run on any past run for free and its numbers are
recomputable from `records.jsonl` alone.

The one thing the records do not carry is the page behind a retrieved chunk id.
Chunk ids are ``uuid5(NAMESPACE_DNS, "<page url>:char:<start>-<end>")`` -- the
toolkit's ``compute_id`` over the extractor's ``source_id``, which is the page URL
(``glossator.ingest.extractor``) -- and the chunker is deterministic and offline,
so the whole map is rebuilt from the vendored corpus in about a second without
Vespa, an index, or a network call. `metrics.json` records how many of the run's
recorded chunk ids the map resolved, so a corpus that has moved on since a run
shows up as an unresolved count rather than as a silently wrong class.
"""
