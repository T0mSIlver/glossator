"""One question through one harness process, whichever harness it is."""

from __future__ import annotations

import contextlib
import os
import subprocess
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from glossator.eval.consumer.answers import is_quota_error
from glossator.eval.consumer.claude import (
    claude_command,
    claude_failure,
    parse_claude_events,
    parse_claude_tokens,
    write_claude_mcp_config,
)
from glossator.eval.consumer.codex import (
    codex_command,
    codex_failure,
    parse_codex_events,
    parse_codex_tokens,
)
from glossator.eval.consumer.consumers import ConsumerSpec
from glossator.eval.consumer.models import HarnessTokens, ToolCallRecord
from glossator.eval.consumer.opencode import (
    opencode_command,
    parse_opencode_events,
    parse_opencode_tokens,
    write_opencode_config,
)
from glossator.eval.consumer.tools import TOKEN_ENV_VAR
from glossator.eval.consumer.vibe import (
    parse_vibe_events,
    parse_vibe_session,
    vibe_command,
    write_vibe_home,
)
from glossator.eval.consumer.vibe_arms import VIBE_ARMS


@dataclass(slots=True)
class CollectedAnswer:
    answer_text: str
    tool_calls: list[ToolCallRecord]
    tokens: HarnessTokens
    cost_usd: float
    wall_seconds: float
    transcript: str
    error: str | None


@dataclass(slots=True)
class _HarnessRun:
    """What one headless harness process left behind."""

    lines: list[str]
    stderr: str
    wall_seconds: float
    timed_out: bool
    events_path: Path


def _run_harness(
    command: Sequence[str],
    cell_dir: Path,
    *,
    timeout_s: float,
    cwd: Path | None = None,
    stdin_path: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> _HarnessRun:
    """One harness process, its event stream and stderr kept in the cell.

    Nothing is ever read from the terminal: stdin is either the prompt file or
    ``/dev/null``, so a harness that would otherwise wait for input exits.
    """
    cell_dir.mkdir(parents=True, exist_ok=True)
    events_path = cell_dir / "events.jsonl"
    stderr_path = cell_dir / "stderr.txt"
    started = time.perf_counter()
    timed_out = False
    with contextlib.ExitStack() as stack:
        events_file = stack.enter_context(events_path.open("w"))
        stderr_file = stack.enter_context(stderr_path.open("w"))
        stdin: Any = subprocess.DEVNULL
        if stdin_path is not None:
            stdin = stack.enter_context(stdin_path.open("rb"))
        try:
            subprocess.run(
                list(command),
                cwd=str(cwd) if cwd is not None else None,
                stdin=stdin,
                stdout=events_file,
                stderr=stderr_file,
                timeout=timeout_s,
                check=False,
                env=dict(env) if env is not None else None,
            )
        except subprocess.TimeoutExpired:
            timed_out = True
    return _HarnessRun(
        lines=events_path.read_text().splitlines() if events_path.is_file() else [],
        stderr=stderr_path.read_text() if stderr_path.is_file() else "",
        wall_seconds=time.perf_counter() - started,
        timed_out=timed_out,
        events_path=events_path,
    )


def _harness_environment(token: str, token_env: str = TOKEN_ENV_VAR) -> dict[str, str]:
    """The consumer's environment: this process's, plus the server token for a
    harness that reads it from a named variable."""
    environment = dict(os.environ)
    if token:
        environment[token_env] = token
    return environment


def _collected(
    run: _HarnessRun,
    answer: str,
    calls: Sequence[ToolCallRecord],
    tokens: HarnessTokens,
    cost: float,
    *,
    timeout_s: float,
    failure: str | None = None,
) -> CollectedAnswer:
    """One cell's answer, with the failure a silent harness leaves in stderr."""
    error = failure
    if run.timed_out:
        error = f"harness timeout after {timeout_s:.0f}s"
    elif not answer and not calls:
        if is_quota_error(run.stderr) or (failure and is_quota_error(failure)):
            detail = (run.stderr.strip() or (failure or ""))[-300:]
            error = f"provider quota exhausted: {detail}"
        elif error is None:
            error = "harness produced no answer text and no tool calls"
    return CollectedAnswer(
        answer_text=answer,
        tool_calls=list(calls),
        tokens=tokens,
        cost_usd=cost,
        wall_seconds=run.wall_seconds,
        transcript=str(run.events_path),
        error=error,
    )


def collect_opencode(
    spec: ConsumerSpec,
    prompt: str,
    cell_dir: Path,
    *,
    mcp_url: str | None,
    token: str,
    timeout_s: float,
) -> CollectedAnswer:
    """One question through headless opencode. Prompt travels as an argv item
    read from the prompt file (no shell), stdin stays /dev/null."""
    cell_dir.mkdir(parents=True, exist_ok=True)
    (cell_dir / "prompt.txt").write_text(prompt + "\n")
    if mcp_url is not None:
        write_opencode_config(cell_dir, mcp_url, token)
    run = _run_harness(opencode_command(spec, prompt, cell_dir), cell_dir, timeout_s=timeout_s)
    answer, calls = parse_opencode_events(run.lines)
    tokens, cost = parse_opencode_tokens(run.lines)
    return _collected(run, answer, calls, tokens, cost, timeout_s=timeout_s)


def collect_claude(
    spec: ConsumerSpec,
    prompt: str,
    cell_dir: Path,
    *,
    mcp_url: str | None,
    token: str,
    timeout_s: float,
) -> CollectedAnswer:
    """One question through headless claude, from the cell's own directory.

    The MCP server is declared in the cell's ``mcp.json`` and nowhere else, so
    the arm decides what the consumer can call.
    """
    cell_dir.mkdir(parents=True, exist_ok=True)
    (cell_dir / "prompt.txt").write_text(prompt + "\n")
    config_path = write_claude_mcp_config(cell_dir, mcp_url, token)
    run = _run_harness(
        claude_command(spec, prompt, config_path),
        cell_dir,
        timeout_s=timeout_s,
        cwd=cell_dir,
        env=_harness_environment(token),
    )
    answer, calls = parse_claude_events(run.lines)
    tokens, cost = parse_claude_tokens(run.lines)
    return _collected(
        run, answer, calls, tokens, cost, timeout_s=timeout_s, failure=claude_failure(run.lines)
    )


def collect_codex(
    spec: ConsumerSpec,
    prompt: str,
    cell_dir: Path,
    *,
    mcp_url: str | None,
    token: str,
    timeout_s: float,
) -> CollectedAnswer:
    """One question through headless codex, prompt piped in on stdin."""
    cell_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = cell_dir / "prompt.md"
    prompt_path.write_text(prompt + "\n")
    answer_path = cell_dir / "answer.md"
    run = _run_harness(
        codex_command(spec, answer_path, mcp_url),
        cell_dir,
        timeout_s=timeout_s,
        cwd=cell_dir,
        stdin_path=prompt_path,
        env=_harness_environment(token),
    )
    answer, calls = parse_codex_events(run.lines)
    tokens, cost = parse_codex_tokens(run.lines)
    if not answer and answer_path.is_file():
        answer = answer_path.read_text().strip()
    return _collected(
        run, answer, calls, tokens, cost, timeout_s=timeout_s, failure=codex_failure(run.lines)
    )


@dataclass(frozen=True, slots=True)
class VibeSetting:
    """Where the vibe arms' directories and the sandbox shell live."""

    environments_root: Path
    sandbox_shell: Path
    fd_path: Path | None


def collect_vibe(
    spec: ConsumerSpec,
    prompt: str,
    cell_dir: Path,
    *,
    arm: str,
    setting: VibeSetting,
    mcp_url: str | None,
    token: str,
    timeout_s: float,
) -> CollectedAnswer:
    """One question through headless Vibe, in the cell's own Vibe home.

    The arm's directory is the working directory and, for the shell, the only
    directory that exists: ``$SHELL`` is the sandbox wrapper, which reads the
    directory from ``GLOSSATOR_ARM_ENV``.
    """
    vibe_arm = VIBE_ARMS[arm]
    cell_dir.mkdir(parents=True, exist_ok=True)
    (cell_dir / "prompt.txt").write_text(prompt + "\n")
    home = cell_dir / "vibe-home"
    write_vibe_home(home, spec, vibe_arm, mcp_url=mcp_url, token_env=TOKEN_ENV_VAR)
    workdir = vibe_arm.workdir(setting.environments_root).resolve()
    environment = _harness_environment(token)
    environment.update(
        {
            "VIBE_HOME": str(home.resolve()),
            "SHELL": str(setting.sandbox_shell.resolve()),
            "GLOSSATOR_ARM_ENV": str(workdir),
        }
    )
    if setting.fd_path is not None:
        environment["GLOSSATOR_ARM_FD"] = str(setting.fd_path)
    run = _run_harness(
        vibe_command(prompt, workdir),
        cell_dir,
        timeout_s=timeout_s,
        cwd=workdir,
        env=environment,
    )
    answer, calls = parse_vibe_events(run.lines)
    tokens, cost, session_failure = parse_vibe_session(home)
    failure = None
    if not answer and not calls:
        failure = session_failure or (run.stderr.strip()[-300:] or None)
    return _collected(run, answer, calls, tokens, cost, timeout_s=timeout_s, failure=failure)


COLLECTORS = {
    "opencode": collect_opencode,
    "claude": collect_claude,
    "codex": collect_codex,
}
