"""glossator: grounded question answering over Mistral's documentation."""

from importlib.metadata import PackageNotFoundError, version


def package_version() -> str:
    """Return the installed version or a source-tree fallback."""
    try:
        return version("glossator")
    except PackageNotFoundError:
        return "0.0.0+unknown"
