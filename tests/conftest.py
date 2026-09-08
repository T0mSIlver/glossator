"""Skip the backend-dependent tests when no search backend is set up.

`test_search_roundtrip` and `test_mcp_tools` both reach the backend through
`search_app.get_index`, which builds the Vespa application definition at call time.
Without `make setup-vespa` that call raises before either test can reach its own skip
guard, turning "nothing is running" into a failure. Probing once here keeps `pytest`
meaningful on a machine with no backend.
"""

from __future__ import annotations

import os

import pytest

BACKEND_TEST_MODULES = ("test_search_roundtrip", "test_mcp_tools")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "exampledocs")


def _backend_error() -> str | None:
    """The reason the backend is unusable, or `None` when it is ready."""
    try:
        from search_app import get_index

        get_index(COLLECTION_NAME)
    except Exception as error:  # noqa: BLE001 - any failure means the backend is not set up
        return f"{type(error).__name__}: {error}"
    return None


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    if not any(item.module.__name__ in BACKEND_TEST_MODULES for item in items if item.module):
        return
    error = _backend_error()
    if error is None:
        return
    skip = pytest.mark.skip(
        reason=f"search backend not configured ({error}); run `make setup-vespa` first"
    )
    for item in items:
        if item.module and item.module.__name__ in BACKEND_TEST_MODULES:
            item.add_marker(skip)
