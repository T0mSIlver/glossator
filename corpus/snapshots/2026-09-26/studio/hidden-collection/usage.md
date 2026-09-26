---
url: https://docs.mistral.ai/studio/hidden-collection/usage
title: Hidden collection usage
breadcrumbs: [Studio, Hidden Collection]
kind: doc
locale: en
source_path: src/content/en/docs/studio/hidden-collection/usage/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
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
