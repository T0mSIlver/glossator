---
url: https://docs.mistral.ai/studio-api/hidden-collection/troubleshooting
title: Hidden collection troubleshooting
breadcrumbs: [Studio, Hidden Collection]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/hidden-collection/troubleshooting/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
hidden: true
---

# Hidden collection troubleshooting

This page checks that nested hidden pages keep normal metadata and headings.

## Page returns 404

If this page returns 404, check that default-locale rewrites still include hidden routes.

## Page appears in navigation

If this page appears in navigation, check hidden category filtering in `getSidebar`.
