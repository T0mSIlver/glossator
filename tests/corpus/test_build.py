"""A whole build, from a fixture checkout to written pages and a manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from glossator.corpus.mistral_docs.build import (
    BuildError,
    BuildSummary,
    build_corpus,
    format_summary,
)
from glossator.corpus.mistral_docs.frontmatter import split as split_frontmatter
from glossator.corpus.mistral_docs.source import DocsCheckout

REDIRECT_TS = """
const rawRedirects: RedirectRule[] = [
  { source: "/legacy/overview", destination: "/studio/overview", permanent: true },
  { source: "/gone/:path*", destination: "/studio/vanished", permanent: true },
];
"""

OVERVIEW_MDX = """---
title: Studio Overview
---

import { SectionTab } from '@/components/layout/section-tab';
import { Tabs, TabItem } from '@/components/common/multi-codeblock';
import Shared from './_shared/_page.mdx';

# Studio Overview

Studio is where you build. See [conversations](./conversations) and [models](/models).

:::tip
Read the [quickstart](../getting-started/quickstart) first.
:::

<SectionTab as="h1" sectionId="before-you-start">Before you start</SectionTab>

<Shared />

<Tabs>
  <TabItem value="python" label="python">

```python
# not a heading
client.chat(model="<MODEL>")
```

  </TabItem>
  <TabItem value="typescript" label="typescript">

```typescript
const client = new Mistral();
```

  </TabItem>
</Tabs>
"""

CONVERSATIONS_MDX = """---
title: Conversations
---

import { SectionTab } from '@/components/layout/section-tab';

# Conversations

<SectionTab as="h2" sectionId="messages">Messages</SectionTab>

A conversation is a list of messages.

<SectionTab as="h2">No anchor here</SectionTab>
"""

LEGACY_MDX = """---
title: Legacy Overview
---

# Legacy Overview

This page redirects onto the studio overview.
"""

SHARED_PARTIAL = """Shared guidance that lives in a partial.
"""

MODEL_TS = """
import { StaticModel } from '../schema';
export default {
  name: 'Testral Small',
  describe: (l) => ({
    description: l.text(`A small model for tests.`, { context: 'Full description' }),
    shortDescription: l.text(`Small.`, { context: 'Short description' }),
  }),
  slug: 'testral-small-26-01',
  releaseDate: '2026-01-15',
  frontier: false,
  class: 'Generalist',
  type: 'Open',
  status: 'GA',
  weights: [],
  contextLength: '128k',
  ratings: { speed: 4.0, performance: 3.0, input: 3.0, output: 3.0 },
  pricing: {
    type: 'custom',
    free: false,
    input: [{ type: 'flat', price: 0.1, denominator: '/M Tokens' }],
    output: [],
  },
  identifiers: { apiNames: ['testral-small', 'testral-small-latest'] },
  capabilities: {
    input: ['text'],
    output: ['text'],
    features: ['chat-completions', 'function-calling'],
  },
  metadata: {},
  legacy: false,
} as const satisfies StaticModel;
"""

SCHEMA_TS = """
export const AVAILABLE_MODALITIES = {
  text: { name: 'Text', description: 'Text' },
} as const;

export const AVAILABLE_FEATURES = {
  'chat-completions': {
    name: 'Chat Completions',
    link: '/studio/conversations/chat-completion',
    endpoints: ['chat-completions'],
  },
  'function-calling': {
    name: 'Function Calling',
    link: '/studio/conversations/function-calling',
    endpoints: ['chat-completions'],
  },
} as const satisfies Features;
"""

SPEC: dict[str, Any] = {
    "openapi": "3.1.0",
    "info": {"title": "Test", "version": "1"},
    "paths": {
        "/v1/chat/completions": {
            "post": {
                "operationId": "chat_completion",
                "summary": "Chat Completion",
                "description": "Create a completion.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/ChatRequest"}}
                    },
                },
                "responses": {"200": {"description": "OK"}},
            }
        },
        "/v1/models": {
            "get": {
                "operationId": "list_models",
                "summary": "List Models",
                "responses": {"200": {"description": "OK"}},
            }
        },
    },
    "components": {
        "schemas": {
            "ChatRequest": {
                "type": "object",
                "required": ["model"],
                "properties": {"model": {"type": "string", "description": "Model id."}},
            }
        }
    },
}

SIDEBAR = [
    {
        "sidebarLabel": "Chat",
        "slug": "endpoint/chat",
        "tags": [
            {
                "name": "chat",
                "operations": [
                    {
                        "elementId": "operation-chat_completion",
                        "method": "post",
                        "path": "/v1/chat/completions",
                        "operationId": "chat_completion",
                        "summary": "Chat Completion",
                    },
                    {
                        "elementId": "operation-list_models",
                        "method": "get",
                        "path": "/v1/models",
                        "operationId": "list_models",
                        "summary": "List Models",
                    },
                ],
            }
        ],
    }
]

SEARCH_DOCS = [
    {
        "url": "/en/studio/overview",
        "title": "Studio Overview",
        "type": "docs",
        "breadcrumbs": [
            {"url": "/en/studio", "title": "Studio"},
            {"url": "/en/studio/overview", "title": "Studio Overview"},
        ],
    },
    {
        "url": "/en/studio/conversations",
        "title": "Conversations",
        "type": "docs",
        "breadcrumbs": [
            {"url": "/en/studio", "title": "Studio"},
            {"url": "/en/studio/conversations", "title": "Conversations"},
        ],
    },
]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def checkout(tmp_path: Path) -> DocsCheckout:
    """A miniature docs repository: three pages, a partial, a spec and a model."""
    root = tmp_path / "repo"
    docs = root / "src" / "content" / "en" / "docs"
    _write(root / "redirect.ts", REDIRECT_TS)
    _write(root / "LICENSE", "Apache License 2.0 (fixture)\n")
    _write(docs / "studio" / "_category_.json", '{"label": "Studio"}')
    _write(docs / "studio" / "overview" / "page.mdx", OVERVIEW_MDX)
    _write(docs / "studio" / "overview" / "_shared" / "_page.mdx", SHARED_PARTIAL)
    _write(docs / "studio" / "conversations" / "page.mdx", CONVERSATIONS_MDX)
    _write(docs / "legacy" / "overview" / "page.mdx", LEGACY_MDX)
    _write(root / "src" / "content" / "en" / "api" / "sidebar-metadata.json", json.dumps(SIDEBAR))
    _write(root / "src" / "schema" / "models" / "schema.ts", SCHEMA_TS)
    _write(root / "src" / "schema" / "models" / "models" / "index.ts", "export const models = [];")
    _write(root / "src" / "schema" / "models" / "models" / "testral-small-26-01.ts", MODEL_TS)
    return DocsCheckout(path=root, ref="fixture", commit="c0ffee")


@pytest.fixture
def spec_file(tmp_path: Path) -> Path:
    path = tmp_path / "openapi.yaml"
    path.write_text(yaml.safe_dump(SPEC), encoding="utf-8")
    return path


@pytest.fixture
def search_docs(tmp_path: Path) -> Path:
    path = tmp_path / "search-docs-en.json"
    path.write_text(json.dumps(SEARCH_DOCS), encoding="utf-8")
    return path


def _build(tmp_path: Path, checkout: DocsCheckout, spec_file: Path, **kwargs: Any) -> BuildSummary:
    return build_corpus(
        checkout,
        out_dir=tmp_path / "out",
        cache_dir=tmp_path / "cache",
        openapi_offline=spec_file,
        **kwargs,
    )


def test_every_source_becomes_a_page(
    tmp_path: Path, checkout: DocsCheckout, spec_file: Path
) -> None:
    summary = _build(tmp_path, checkout, spec_file)
    out = tmp_path / "out"
    written = sorted(str(path.relative_to(out)) for path in out.rglob("*.md"))
    assert written == [
        "api/endpoint/chat.md",
        "models.md",
        "models/testral-small-26-01.md",
        "studio/conversations.md",
        "studio/overview.md",
    ]
    assert summary.pages_by_kind == {"doc": 2, "api": 1, "model": 2}
    assert summary.api_operations == 2
    assert summary.anchors_by_kind["api"] == 2


def test_the_manifest_describes_what_was_written(
    tmp_path: Path, checkout: DocsCheckout, spec_file: Path
) -> None:
    _build(tmp_path, checkout, spec_file)
    out = tmp_path / "out"
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    entry = next(item for item in manifest if item["path"] == "studio/overview.md")
    assert entry["url"] == "https://docs.mistral.ai/studio/overview"
    assert entry["kind"] == "doc"
    assert entry["source_commit"] == "c0ffee"
    assert entry["source_path"] == "src/content/en/docs/studio/overview/page.mdx"
    body = (out / "studio" / "overview.md").read_bytes()
    assert entry["sha256"] == hashlib.sha256(body).hexdigest()
    assert (out / "LICENSE").read_text(encoding="utf-8").startswith("Apache License 2.0")
    assert "c0ffee" in (out / "NOTICE").read_text(encoding="utf-8")


def test_a_page_carries_frontmatter_anchors_partials_and_absolute_links(
    tmp_path: Path, checkout: DocsCheckout, spec_file: Path
) -> None:
    _build(tmp_path, checkout, spec_file)
    metadata, body = split_frontmatter(
        (tmp_path / "out" / "studio" / "overview.md").read_text(encoding="utf-8")
    )
    assert metadata["breadcrumbs"] == ["Studio"]
    assert metadata["locale"] == "en"
    assert body.lstrip().startswith("# Studio Overview")
    assert "## Before you start {#before-you-start}" in body
    assert "Shared guidance that lives in a partial." in body
    assert "[conversations](https://docs.mistral.ai/studio/conversations)" in body
    assert "[quickstart](https://docs.mistral.ai/getting-started/quickstart)" in body
    assert "> **Tip**" in body
    assert "**Python**" in body and "**TypeScript**" in body
    assert "# not a heading" in body
    assert "<MODEL>" in body


def test_a_section_tab_without_a_section_id_produces_no_anchor(
    tmp_path: Path, checkout: DocsCheckout, spec_file: Path
) -> None:
    summary = _build(tmp_path, checkout, spec_file)
    _, body = split_frontmatter(
        (tmp_path / "out" / "studio" / "conversations.md").read_text(encoding="utf-8")
    )
    assert "## Messages {#messages}" in body
    assert "## No anchor here" in body
    assert "{#no-anchor-here}" not in body
    assert summary.suppressed_anchors == 1


def test_a_redirected_duplicate_is_dropped_and_accounted(
    tmp_path: Path, checkout: DocsCheckout, spec_file: Path
) -> None:
    summary = _build(tmp_path, checkout, spec_file)
    assert summary.raw_routes == 3
    assert len(summary.dropped_duplicates) == 1
    dropped = summary.dropped_duplicates[0]
    assert dropped.original_route == "/legacy/overview"
    assert dropped.target_route == "/studio/overview"
    assert dropped.retained_source_path.endswith("studio/overview/page.mdx")
    rendered = format_summary(summary)
    assert "1 dropped as duplicates of another route" in rendered
    assert "/legacy/overview -> /studio/overview" in rendered


def test_breadcrumbs_are_cross_checked_against_the_search_index(
    tmp_path: Path, checkout: DocsCheckout, spec_file: Path, search_docs: Path
) -> None:
    summary = _build(tmp_path, checkout, spec_file, search_docs=search_docs)
    assert summary.breadcrumb_mismatches == []
    assert summary.breadcrumbs_unchecked == 0


def test_a_second_build_removes_files_the_corpus_no_longer_has(
    tmp_path: Path, checkout: DocsCheckout, spec_file: Path
) -> None:
    _build(tmp_path, checkout, spec_file)
    out = tmp_path / "out"
    stale = out / "studio" / "removed.md"
    stale.write_text("stale\n", encoding="utf-8")
    (out / "orphan").mkdir()
    (out / "orphan" / "old.md").write_text("stale\n", encoding="utf-8")

    _build(tmp_path, checkout, spec_file)
    assert not stale.exists()
    assert not (out / "orphan").exists()
    assert (out / "studio" / "overview.md").is_file()


def test_a_missing_licence_stops_the_build(
    tmp_path: Path, checkout: DocsCheckout, spec_file: Path
) -> None:
    (checkout.path / "LICENSE").unlink()
    with pytest.raises(BuildError, match="LICENSE"):
        _build(tmp_path, checkout, spec_file)
    # Nothing may be written, or stale cleanup would delete the licence already on disk.
    assert not (tmp_path / "out").exists()


def test_an_operation_missing_from_the_spec_stops_the_build(
    tmp_path: Path, checkout: DocsCheckout, spec_file: Path
) -> None:
    spec = json.loads(json.dumps(SPEC))
    del spec["paths"]["/v1/models"]
    spec_file.write_text(yaml.safe_dump(spec), encoding="utf-8")
    with pytest.raises(BuildError, match="not in the"):
        _build(tmp_path, checkout, spec_file)


def test_the_cli_reports_a_failed_build(
    tmp_path: Path, checkout: DocsCheckout, spec_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from glossator.corpus.mistral_docs.__main__ import main

    (checkout.path / "LICENSE").unlink()
    status = main(
        [
            "build",
            "--checkout",
            str(checkout.path),
            "--ref",
            "fixture",
            "--out",
            str(tmp_path / "out"),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--openapi-file",
            str(spec_file),
            "--no-search-docs",
        ]
    )
    assert status == 1
    assert "build failed" in capsys.readouterr().out


def test_the_cli_succeeds_on_a_clean_build(
    tmp_path: Path, checkout: DocsCheckout, spec_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from glossator.corpus.mistral_docs.__main__ import main

    status = main(
        [
            "build",
            "--checkout",
            str(checkout.path),
            "--ref",
            "fixture",
            "--out",
            str(tmp_path / "out"),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--openapi-file",
            str(spec_file),
            "--no-search-docs",
        ]
    )
    assert status == 0
    assert "corpus build summary" in capsys.readouterr().out
