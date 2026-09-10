# Search-loop cap grid: loop-grid

**What this measures.** The search loop stops after `round_cap` rounds, answers
at most `searches_per_round` searches per round, and shows the model
`tool_result_chars`-character previews of what its tools found (D-035c). None of
the three values had ever been varied; this grid moves one at a time away from
the shipped point (round_cap 4, searches_per_round
4, tool_result_chars
600), so each row isolates one knob.

**Read the numbers as relative.** Every configuration ran its chat calls on the local server `http://192.168.1.183:8080` -- a quantized Ministral 3 served by llama.cpp -- with embeddings on the Mistral API. They are comparisons between
configurations of the same server, not absolute quality figures; every shipped
figure keeps coming from the Mistral API (D-035c). A difference of a few points
on 30 questions is a signal to follow up, not a
conclusion.

## Configuration

- Dataset: `eval/dev-fresh60.jsonl`, sha256 `c663126d79ebf3c0c8cc6000a73be2fd9281c0ae672ae4d42532f1fae8fa7fc0`
- Generation model: `llamacpp/ministral3-14b`; judge: `None`; index variant: `sec1024`
- Structured output sent as `json_schema`
- Each row is a normal answer-eval run of `search_loop` only, in the directory named in `config.json`.

## Results

| configuration | correctness (judge) | groundedness (judge) | cited URL matches gold | quotes verified | rounds used | round cap hit | tool calls | prompt tokens per answer | median seconds per answer |
|---|---|---|---|---|---|---|---|---|---|
| `shipped` | 0.85 | 0.84 | 0.72 | 0.86 | 2.6 | 0.13 | 2.1 | 11299.0 | 65.3 |
| `round-cap-6` | 0.77 | 0.74 | 0.88 | 0.83 | 2.9 | 0.07 | 2.4 | 14206.9 | 51.6 |
| `round-cap-8` | 0.82 | 0.70 | 0.76 | 0.80 | 2.8 | 0.00 | 2.6 | 14235.4 | 39.9 |
| `searches-per-round-6` | 0.75 | 0.80 | 0.72 | 0.84 | 2.1 | 0.03 | 1.5 | 9195.1 | 35.1 |
| `tool-result-chars-1500` | 0.87 | 0.71 | 0.64 | 0.75 | 2.0 | 0.00 | 1.3 | 10394.7 | 33.3 |
| `tool-result-chars-full` | 0.77 | 0.80 | 0.64 | 0.85 | 2.0 | 0.00 | 1.3 | 10113.1 | 32.2 |

The judge was skipped for this grid (`--skip-judge`), so the judged columns (correctness, groundedness) are empty; every row holds its answers, traces, tokens and latencies, and a later `rejudge` fills the judged columns without re-running generation.

## Figures

- `figures/correctness-by-round_cap.svg`
- `figures/tokens-by-round_cap.svg`
- `figures/correctness-by-searches_per_round.svg`
- `figures/tokens-by-searches_per_round.svg`
- `figures/correctness-by-tool_result_chars.svg`
- `figures/tokens-by-tool_result_chars.svg`

Each figure shows one axis; the shipped point is the bar every other bar on that
axis is compared against.


## Notes on this run

- Generation-only grid on the local Ministral 3 server with reasoning off; judged columns are filled by rejudge later.

## Files

- `config.json` -- the grid definition: every row's axis, value, overrides and run directory.
- `metrics.json` -- the table above, as numbers.
- Each row's evidence (answers, citations, calls, per-question records) is in its
  own run directory, named in `config.json`.

## What it feeds

D-035c: whether the loop's caps should move, and in which direction, decided on
relative numbers from a local server before any API credits are spent.
