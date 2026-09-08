# Answer-layer smoke, 2026-09-09

**What this measures.** Whether the answer layer works end to end against the live
index and a live model: retrieval, context assembly, grounded generation, quote
verification, tracing, and cost accounting, for all three strategies on the same five
questions. It is a smoke run, not an evaluation — there is no gold answer set and no
judge here, so nothing in it says which strategy answers better. What it does say is
whether each strategy runs, what it costs, and how many of the citations the model
writes survive the quote check.

**The model is `ministral-8b-2512` (Ministral 3 8B), not Mistral Medium 3.5.**
Throughout the run window (2026-09-08 22:00 UTC to 2026-09-09 00:15 UTC) this API key
returned HTTP 429 with `x-ratelimit-limit-req-minute: 0` for every
`mistral-medium-*`, `magistral-*` and `mistral-small-*` id, while `ministral-3b/8b/14b`,
`codestral` and `mistral-embed` answered normally. A limit of zero is a configured
quota, not a burst, so the wrapper's backoff cannot get through it. The run was made on
the largest model that would answer. **Repeat it on `mistral-medium-2604` before any of
these numbers are used to compare strategies**: an 8B model follows the grounded prompt
noticeably less well than Medium 3.5 will, so the verification rates below are a floor,
not an estimate.

Re-run:

```bash
uv run python .agent-runs/smoke.py            # Mistral Medium 3.5, the default
```

## Configuration

`sec1024` (full-dimension section chunks, the serving variant), `top_k=8`,
context budget 6000 tokens, temperature 0.2, round cap 4, page cap 4.
Everything else is in `config.json`, including the prompt hashes.

## Questions

1. How do I create a conversational workflow?
2. What models support function calling?
3. How do I configure a reranker in the Search Toolkit?
4. What is the maximum number of tool calls in one response? (possibly unanswerable)
5. Comment fonctionne le mode JSON avec l'API chat ? (French)

## Results

27 model calls, 89,582 prompt tokens, 10,679 completion tokens, **$0.0150**, no errors.

| strategy | prompt tok | completion tok | USD | total s | verified | rejected | quote rate | distinct sources | insufficient |
|---|---|---|---|---|---|---|---|---|---|
| `single_pass` | 10,429 | 3,145 | 0.0020 | 33.7 | 15 | 4 | 0.79 | 11 | 0 |
| `search_loop` | 30,681 | 4,228 | 0.0052 | 48.8 | 8 | 4 | 0.67 | 7 | 0 |
| `outline` | 48,472 | 3,306 | 0.0078 | 33.4 | 13 | 6 | 0.68 | 7 | 1 |

"Quote rate" is verified citations over all citations the model wrote — the
deterministic citation-correctness number from D-016. "Distinct sources" counts how
many different numbered sources were cited across the five answers, because a model
that cites `[1]` five times looks well-cited and is not.

`outline` costs the most per question because the page outline itself is ~5.8k prompt
tokens on every question, before any documentation is read.

## What it shows

- All three strategies run, on English and French, and produce verified citations.
- The verifier does its job: 14 of 50 citations were rejected as quotes that are not
  in the source they name, and those answers keep their markers while the trace
  records the rejection.
- Only `outline` flagged the possibly-unanswerable question 4 as insufficient
  evidence. `single_pass` and `search_loop` both answered "128", citing the real
  sentence "Maximum number of tools per request: **128**" — a verified quote about a
  different quantity. A quote check cannot catch that; an LLM judge (D-016) has to.
- `search_loop` usually stops after the seed search, so it lands close to
  `single_pass` on easy questions while costing 2.6x as much.

## Files

- `config.json` — every parameter, including prompt hashes.
- `calls.jsonl` — one line per model call: request messages, tools, raw response,
  parsed result, usage, latency, cost, error.
- `records.jsonl` — one line per (question, strategy): the answer, its verified and
  rejected citations, the full trace, usage, latency, cost.
- `metrics.json` — the table above.

## Conclusion

The answer layer is ready to be evaluated; it is not yet evaluated. The next step is
the answer eval (D-016): a gold set, the deterministic checks (cited URL vs gold, quote
verification rate, refusal on unanswerable) and a judge for groundedness and
correctness, run as a grid over the three strategies on Mistral Medium 3.5.
