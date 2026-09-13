# Replaying recorded generation prompts on another model

The answer evaluations record every request they sent to the generator
(`calls.jsonl`, D-023). The user message of a `single_pass:grounded_answer`
call holds the assembled context, so the generation step can be re-run on
another model with nothing else in the loop: no Vespa, no embeddings, no
reranker. Retrieval and context stay byte-identical; the difference is the
generator's alone (D-042).

## Files

- `medium-3-5/prompts.jsonl`: 288 requests, one per single-pass question of
  the four reporting runs, sampling normalised to the shipped values
  (temperature 0.2, 1,600 completion tokens). Regenerate with:

  ```
  uv run python -m glossator.eval.replay export \
      eval/runs/2026-09-09-0312-dev60-rerank \
      eval/runs/2026-09-09-1211-fresh60-shipped \
      eval/runs/2026-09-09-1253-mined-shipped \
      eval/runs/2026-09-09-2305-mined-v2-shipped \
      --output eval/replay/medium-3-5/prompts.jsonl --temperature 0.2 --max-tokens 1600
  ```

- `medium-3-5/results.jsonl`: the 288 completions from Medium 3.5 behind an
  OpenAI-compatible gateway, the first measurement (D-017b).

- `medium-3-5-api/results.jsonl`: the same 288 prompts completed on Mistral's
  API (`https://api.mistral.ai/v1`, `mistral-medium-2604`) on 13 September 2026.
  This directory holds the reported Medium 3.5 number (D-017c); its run
  directories are `eval/runs/2026-09-13-1148-medium35-api-replay-*`.

- `run_replay.py`: standard-library runner for any OpenAI-compatible chat
  endpoint. Resumable, retries 429 and 5xx, falls back from `json_schema` to
  `json_object` to no response format and records which mode each row used.
  It is kept outside the repository's ruff and mypy gates on purpose: it
  imports nothing but the standard library so it can be copied alone to a
  machine without this project installed.

## Running it elsewhere

Copy `run_replay.py` and `medium-3-5/prompts.jsonl` to the machine with access:

```
export OPENAI_API_KEY=<token>
python run_replay.py --base-url https://<host>/v1 --model <medium id> \
    --input prompts.jsonl --output results.jsonl --concurrency 4 --limit 3   # smoke test
python run_replay.py --base-url https://<host>/v1 --model <medium id> \
    --input prompts.jsonl --output results.jsonl --concurrency 4              # the rest
```

`--api-key-env` names another variable; `--header "Name: value"` adds one.
Bring back `results.jsonl`, committed on the branch as
`eval/replay/medium-3-5/results.jsonl`.

## Scoring the completions

```
uv run python -m glossator.eval.replay import eval/replay/medium-3-5/results.jsonl     --prompts eval/replay/medium-3-5/prompts.jsonl     --name medium35-replay --model mistral-medium-2604     --judge-models zai:glm-5.3,zai:glm-5.3-flash
```

writes one run directory per source run (`<date>-medium35-replay-dev60-rerank`
and so on). Each replayed answer is parsed, its quotes verified against the
sources rebuilt from the recorded context, its markers stripped where nothing
verified, and the record keeps the source run's retrieval trace untouched; the
call ledger holds every completion verbatim. Without `--judge-models` the run
is written unjudged and `answer_eval rejudge` scores it later.

`check` proves the rebuild: it re-verifies each source run's own citations
against the rebuilt sources and reports how many answers reproduce the recorded
verdicts and chunk ids. On the four reporting runs it is 286 of 286.
