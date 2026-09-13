"""Replay recorded generation prompts on another model, off the pipeline.

Every answer evaluation writes the request it sent to the generator, verbatim,
into `calls.jsonl` (D-023). Those requests are the whole generation step: the
assembled context is in the user message and nothing else reached the model. So
the generator can be swapped without Vespa, embeddings or a reranker in the loop:
export the prompts, run them anywhere an OpenAI-compatible endpoint answers, and
bring the completions back. Retrieval and context are then byte-identical
between the two generators, and any difference is the generator's alone, which
is the column the failure analysis says to move (D-042).

`export` writes one line per question: the messages, sampling and schema as
they were sent, plus the ids that let `import` pair each completion with the
record it replays. Only the first attempt of each question is exported; later
attempts in the ledger are transport retries with the same messages.
"""
