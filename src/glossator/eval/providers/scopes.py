"""Tags a caller puts on every call made inside a block, read back when a call is recorded."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

_candidate_id: ContextVar[str | None] = ContextVar("candidate_id", default=None)
_call_kind: ContextVar[str | None] = ContextVar("call_kind", default=None)


@contextmanager
def candidate_scope(candidate_id: str) -> Iterator[None]:
    """Tag every call made inside the block with the candidate it belongs to.

    A run makes several calls per candidate (generation, filter, page checks);
    without the tag the only way from a call row back to its candidate is
    matching prompt text.
    """
    token = _candidate_id.set(candidate_id)
    try:
        yield
    finally:
        _candidate_id.reset(token)


@contextmanager
def call_scope(kind: str) -> Iterator[None]:
    """Tag calls made inside the block with the job they do.

    What a run spends on generating questions versus on checking them is one of
    the numbers the run README reports, and the schema name alone does not say
    it: two checks can share a schema.
    """
    token = _call_kind.set(kind)
    try:
        yield
    finally:
        _call_kind.reset(token)


def current_candidate_id() -> str | None:
    return _candidate_id.get()


def current_call_kind() -> str | None:
    return _call_kind.get()
