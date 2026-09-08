"""Corpus adapter for docs.mistral.ai, built from the public docs repository.

The adapter reads `mistralai/platform-docs-public` at a pinned commit and emits one
normalized markdown page per live URL (see DECISIONS.md D-001 to D-009).
"""

SITE_ORIGIN = "https://docs.mistral.ai"
DOCS_REPO_URL = "https://github.com/mistralai/platform-docs-public.git"
PINNED_REF = "2e094f7bbe1395de4a738a3483def3573143d973"
LOCALE = "en"
