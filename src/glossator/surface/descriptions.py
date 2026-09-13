"""The text a host shows the model: the server instructions and one description per tool."""

from glossator.surface.names import HISTORY, READ_PAGE, SEARCH
from glossator.surface.search import MAX_HITS


def instructions(page_count: int, enabled: frozenset[str]) -> str:
    """The rules for a host that reads nothing but this string (D-037a)."""
    scope = (
        f"{page_count} pages of Mistral's documentation"
        if page_count
        else "Mistral's documentation"
    )
    steps = [f"{SEARCH} finds the sections that state a fact"]
    if READ_PAGE in enabled:
        steps.append(f"{READ_PAGE} reads the page a hit is on")
    if HISTORY in enabled:
        steps.append(f"{HISTORY} shows when a fact, section or path changed")
    return (
        f"Searches {scope} (docs.mistral.ai guides, API reference, model cards) at a "
        "pinned commit. Use it for any question about Mistral models, the API, SDKs, "
        "pricing, limits, Studio, Work, Vibe or La Plateforme.\n\n"
        f"{'; '.join(steps)}.\n\n"
        "Cite the cite: link printed beside the text you used, as a Markdown link, next to "
        "each claim it supports. Never write a docs.mistral.ai URL from memory. When the "
        "documentation "
        "does not answer the question, say so instead of answering from memory. If a "
        "search returns the pages you already read, the corpus has nothing more on it. "
        "An unknown page URL means the page does not exist at this commit; do not retry it."
    )


def _search_description() -> str:
    return f"""Search Mistral's documentation for the sections that state something.
    Each hit prints its section key, its heading path, a snippet and the link to cite.

    USE WHEN: the question is about a Mistral model, parameter, limit, price,
    error or product feature.

    DO NOT USE: to read a page you already hold a hit on ({READ_PAGE}).

    Args:
        q: What you want to find, in one sentence. Empty with under: list its pages.
        max_hits: Hits to return, 1-{MAX_HITS}.
        under: A page URL. Keeps hits to the pages under it; lists them when q is empty.
    """


def _read_page_description() -> str:
    return f"""Read one Mistral documentation page in reading order, or one section of it.

    USE WHEN: a search hit names the section and you need the surrounding text,
    a table, or a code block before answering.

    DO NOT USE: to find where something is said ({SEARCH}).

    Args:
        page_url: The page URL exactly as a hit printed it.
        section: A section key exactly as a hit or a next: line printed it, to
            read that section instead of the whole page.
        lang: The code samples to print: python, typescript or curl. When a page
            shows a sample in several languages, the others are omitted and named.
    """


def _history_description() -> str:
    return f"""Track Mistral documentation across stored snapshots.

    USE WHEN: something appeared, changed, moved or disappeared, or you need
    the changes below a page or path.

    DO NOT USE: to read the current documentation ({SEARCH}, {READ_PAGE}).

    Args:
        text: Exact phrase for its first and last stored appearance; add
            page_url or under to look on one page or path.
        page_url: Page to track. Add section for one key printed by a hit or read.
        section: Optional key on page_url. A fragment on page_url also supplies it.
        under: Page or path: its sections and, per page beneath it, what changed
            between stored dates.
        since: Optional date for under; snaps to the next stored date.
    """


DESCRIPTIONS = {
    SEARCH: _search_description(),
    READ_PAGE: _read_page_description(),
    HISTORY: _history_description(),
}

__all__ = ["DESCRIPTIONS", "instructions"]
