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

- `run_replay.py`: standard-library runner for any OpenAI-compatible chat
  endpoint. Resumable, retries 429 and 5xx, falls back from `json_schema` to
  `json_object` to no response format and records which mode each row used.

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
Bring back `results.jsonl`. The import side pairs each row with its source
record by `source_call_id`, parses and verifies citations with the same code
the original run used, judges with GLM 5.3 blind, and writes a run directory
beside the originals.
