---
url: https://docs.mistral.ai/studio-api/hidden-collection/usage
title: Hidden collection usage
breadcrumbs: [Studio, Hidden Collection]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/hidden-collection/usage/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
hidden: true
---

# Hidden collection usage

This page checks that hidden child pages can contain regular documentation content.

## Send a test request

Use any placeholder request while validating the page behavior:

```bash
curl https://example.com/hidden-collection/test
```

## Expected result

The page should render the code block and remain excluded from generated discovery surfaces.
