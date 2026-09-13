"""The history forms: which one a call names, and the snapshot query it runs.

The MCP tool and ``GET /history`` take the same five arguments (D-048, D-051),
so both resolve them here and a rule changes in one place.
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from glossator import changelog as changelog_service
from glossator import history as history_service
from glossator.surface.errors import bad_param, unknown_page
from glossator.surface.names import HISTORY

HistoryKind = Literal["text", "page_url", "under"]

_FORMS_HINT = (
    f'{HISTORY}(text="phrase", page_url="url" or under="path"), '
    f'{HISTORY}(page_url="url", section="key") or {HISTORY}(under="path", since="date").'
)


@dataclass(frozen=True, slots=True)
class HistoryForm:
    """One valid history call. ``value`` is the argument that names the form;
    ``page_url`` and ``under`` also scope a phrase search."""

    kind: HistoryKind
    value: str
    page_url: str | None
    section: str | None
    under: str | None
    since: str | None


def resolve_history_form(
    text: str | None,
    page_url: str | None,
    section: str | None,
    under: str | None,
    since: str | None,
) -> HistoryForm:
    """The form the arguments name, or E_BAD_PARAM naming the forms that exist."""
    if section is not None and page_url is None:
        raise bad_param("section requires page_url.", f'{HISTORY}(page_url="url", section="key").')
    if since is not None and under is None:
        raise bad_param("since requires under.", f'{HISTORY}(under="path", since="date").')
    kind: HistoryKind
    if text is not None:
        if page_url is not None and under is not None:
            raise bad_param("text takes page_url or under, not both.", _FORMS_HINT)
        if section is not None or since is not None:
            raise bad_param("text takes page_url or under, not section or since.", _FORMS_HINT)
        kind, value = "text", text
    elif page_url is not None and under is not None:
        raise bad_param("page_url and under are two forms; pass one.", _FORMS_HINT)
    elif page_url is not None:
        kind, value = "page_url", page_url
    elif under is not None:
        kind, value = "under", under
    else:
        raise bad_param("history takes text, page_url or under.", _FORMS_HINT)
    if not value.strip():
        raise bad_param(f"{kind} is empty.", f"send text in {kind}.")
    return HistoryForm(kind, value, page_url, section, under, since)


async def query_history(form: HistoryForm, manifest: Path) -> dict[str, Any]:
    """The history service's result for one form. The services read snapshot
    files, so they run off the event loop."""
    try:
        if form.kind == "text":
            return await asyncio.to_thread(
                history_service.phrase_history,
                form.value,
                manifest,
                page_url=form.page_url,
                under=form.under,
            )
        if form.kind == "page_url":
            return await asyncio.to_thread(
                history_service.section_history, form.value, form.section, manifest
            )
        return await asyncio.to_thread(
            changelog_service.history_under, form.value, form.since, manifest
        )
    # UnknownPageError is a ValueError, so it is caught first.
    except history_service.UnknownPageError as exc:
        raise unknown_page(str(exc)) from exc
    except (OSError, ValueError) as exc:
        raise bad_param(str(exc), "pass one documented history form.") from exc


__all__ = ["HistoryForm", "HistoryKind", "query_history", "resolve_history_form"]
