"""Corpus adapter for docs.mistral.ai, built from the public docs repository.

The adapter reads `mistralai/platform-docs-public` at a pinned commit and emits one
normalized markdown page per live URL (see DECISIONS.md D-001 to D-009).
"""

SITE_ORIGIN = "https://docs.mistral.ai"
DOCS_REPO_URL = "https://github.com/mistralai/platform-docs-public.git"
PINNED_REF = "bee3023d26c331c00fa6c24bc746ef4cf5e97031"
LOCALE = "en"
