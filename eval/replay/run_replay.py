#!/usr/bin/env python3
"""Send recorded generation prompts to an OpenAI-compatible chat endpoint.

Standard library only. Reads `prompts.jsonl` (one request per line, as
exported by `glossator.eval.replay export`) and appends one line per completed
request to the output file: the raw response body, the text, usage, latency,
the response-format mode actually used, and any error. Re-running resumes:
ids already in the output are skipped, so a killed run keeps what it paid for.

Structured output: the first request tries `response_format: json_schema`; if
the server rejects it with a 4xx the run falls back to `json_object` for every
later request, and if that is rejected too it sends no response_format at all.
Whichever mode ends up in use is written on every row, so the scoring side
knows what the model was asked for.

    export OPENAI_API_KEY=...
    python run_replay.py --base-url https://host/v1 --model mistral-medium-2604 \\
        --input prompts.jsonl --output results.jsonl --concurrency 4

Send back `results.jsonl` (and nothing else is needed).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

RETRY_STATUSES = {408, 409, 425, 429, 500, 502, 503, 504}
MODES = ["json_schema", "json_object", "none"]


class Endpoint:
    def __init__(
        self, base_url: str, api_key: str, model: str, timeout: float, headers: dict[str, str]
    ):
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.model = model
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            **headers,
        }
        self.mode_index = 0
        self.lock = threading.Lock()

    @property
    def mode(self) -> str:
        return MODES[self.mode_index]

    def _downgrade(self, from_mode: str, reason: str) -> None:
        with self.lock:
            if MODES[self.mode_index] == from_mode and self.mode_index < len(MODES) - 1:
                self.mode_index += 1
                print(
                    f"[replay] response_format {from_mode!r} rejected ({reason[:200]}); "
                    f"using {self.mode!r} from now on",
                    file=sys.stderr,
                )

    def body(self, row: dict, mode: str) -> dict:
        body = {
            "model": self.model,
            "messages": row["messages"],
            "temperature": row["temperature"],
            "max_tokens": row["max_tokens"],
        }
        if mode == "json_schema":
            body["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": row["response_schema"], "schema": row["json_schema"]},
            }
        elif mode == "json_object":
            body["response_format"] = {"type": "json_object"}
        return body

    def post(self, body: dict) -> tuple[int, dict | str]:
        data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(self.url, data=data, headers=self.headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            text = error.read().decode("utf-8", errors="replace")
            try:
                return error.code, json.loads(text)
            except json.JSONDecodeError:
                return error.code, text
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            return 0, f"{type(error).__name__}: {error}"

    def complete(self, row: dict, max_attempts: int, base_delay: float) -> dict:
        started = datetime.now(timezone.utc).isoformat()  # noqa: UP017 (3.9-compatible)
        attempt = 0
        last_error = None
        while attempt < max_attempts:
            attempt += 1
            mode = self.mode
            body = self.body(row, mode)
            t0 = time.monotonic()
            status, payload = self.post(body)
            latency_ms = (time.monotonic() - t0) * 1000
            if status == 200 and isinstance(payload, dict) and payload.get("choices"):
                message = payload["choices"][0].get("message") or {}
                content = message.get("content")
                if isinstance(content, list):  # some servers return content parts
                    content = "".join(
                        part.get("text", "") for part in content if isinstance(part, dict)
                    )
                return {
                    "id": row["id"],
                    "run": row["run"],
                    "question_id": row["question_id"],
                    "source_call_id": row["source_call_id"],
                    "model": self.model,
                    "response_format": mode,
                    "temperature": row["temperature"],
                    "max_tokens": row["max_tokens"],
                    "attempt": attempt,
                    "started_at": started,
                    "latency_ms": latency_ms,
                    "finish_reason": payload["choices"][0].get("finish_reason"),
                    "text": content or "",
                    "usage": payload.get("usage"),
                    "response": payload,
                    "error": None,
                }
            detail = json.dumps(payload) if isinstance(payload, dict) else str(payload)
            last_error = f"HTTP {status}: {detail[:2000]}"
            lowered = last_error.lower()
            rejected_format = (
                status in (400, 422)
                and mode != "none"
                and (
                    "response_format" in lowered or "json_schema" in lowered or "schema" in lowered
                )
            )
            if rejected_format:
                self._downgrade(mode, last_error)
                continue  # same attempt budget, new mode
            if status in RETRY_STATUSES or status == 0:
                time.sleep(base_delay * (2 ** (attempt - 1)))
                continue
            break
        return {
            "id": row["id"],
            "run": row["run"],
            "question_id": row["question_id"],
            "source_call_id": row["source_call_id"],
            "model": self.model,
            "response_format": self.mode,
            "temperature": row["temperature"],
            "max_tokens": row["max_tokens"],
            "attempt": attempt,
            "started_at": started,
            "latency_ms": None,
            "finish_reason": None,
            "text": "",
            "usage": None,
            "response": None,
            "error": last_error,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--base-url",
        required=True,
        help="e.g. https://host/v1 (the script appends /chat/completions)",
    )
    parser.add_argument(
        "--model", required=True, help="model id as the endpoint names it, e.g. mistral-medium-2604"
    )
    parser.add_argument("--input", type=Path, default=Path("prompts.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("results.jsonl"))
    parser.add_argument(
        "--api-key-env",
        default="OPENAI_API_KEY",
        help="environment variable holding the bearer token",
    )
    parser.add_argument(
        "--header", action="append", default=[], help="extra header, Name: value (repeatable)"
    )
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--max-attempts", type=int, default=6)
    parser.add_argument("--retry-base-seconds", type=float, default=2.0)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="stop after this many new requests (for a smoke test)",
    )
    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help="re-send rows whose stored result carries an error",
    )
    args = parser.parse_args()

    api_key = os.environ.get(args.api_key_env, "")
    if not api_key:
        print(f"[replay] {args.api_key_env} is not set", file=sys.stderr)
        return 2
    headers = {}
    for item in args.header:
        name, _, value = item.partition(":")
        headers[name.strip()] = value.strip()

    rows = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    done: dict[str, dict] = {}
    if args.output.exists():
        for line in args.output.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                done[row["id"]] = row
    pending = [
        r for r in rows if r["id"] not in done or (args.retry_errors and done[r["id"]].get("error"))
    ]
    if args.limit is not None:
        pending = pending[: args.limit]
    print(
        f"[replay] {len(rows)} prompts, {len(done)} already in {args.output}, "
        f"{len(pending)} to send",
        file=sys.stderr,
    )
    if not pending:
        return 0

    endpoint = Endpoint(args.base_url, api_key, args.model, args.timeout, headers)
    write_lock = threading.Lock()
    kept: dict[str, dict] = {
        k: v for k, v in done.items() if not (args.retry_errors and v.get("error"))
    }
    if args.retry_errors and len(kept) != len(done):
        args.output.write_text(
            "".join(json.dumps(v, ensure_ascii=False) + "\n" for v in kept.values()),
            encoding="utf-8",
        )

    # The first request runs alone so the response-format probe settles before
    # the pool starts; otherwise several workers could each hit the rejection.
    first, rest = pending[0], pending[1:]
    counts = {"ok": 0, "error": 0}
    tokens = {"prompt": 0, "completion": 0}
    t_start = time.monotonic()

    def handle(result: dict) -> None:
        with write_lock:
            with args.output.open("a", encoding="utf-8") as handle_:
                handle_.write(json.dumps(result, ensure_ascii=False) + "\n")
            if result["error"]:
                counts["error"] += 1
                print(f"[replay] {result['id']}: {result['error'][:160]}", file=sys.stderr)
            else:
                counts["ok"] += 1
                usage = result.get("usage") or {}
                tokens["prompt"] += usage.get("prompt_tokens") or 0
                tokens["completion"] += usage.get("completion_tokens") or 0
            n = counts["ok"] + counts["error"]
            if n % 10 == 0 or n == len(pending):
                elapsed = time.monotonic() - t_start
                print(
                    f"[replay] {n}/{len(pending)} done, {counts['error']} errors, "
                    f"{elapsed:.0f}s, mode={endpoint.mode}",
                    file=sys.stderr,
                )

    handle(endpoint.complete(first, args.max_attempts, args.retry_base_seconds))
    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futures = [
            pool.submit(endpoint.complete, row, args.max_attempts, args.retry_base_seconds)
            for row in rest
        ]
        for future in as_completed(futures):
            handle(future.result())

    print(
        f"[replay] finished: {counts['ok']} ok, {counts['error']} errors, "
        f"{tokens['prompt']} prompt and {tokens['completion']} completion tokens, "
        f"response_format={endpoint.mode}",
        file=sys.stderr,
    )
    return 0 if counts["error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
