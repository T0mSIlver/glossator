---
url: https://docs.mistral.ai/studio-api/hidden-collection/usage
title: Hidden collection usage
breadcrumbs: [Studio, Hidden Collection]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/hidden-collection/usage/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
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
