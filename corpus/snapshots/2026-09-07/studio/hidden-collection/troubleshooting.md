---
url: https://docs.mistral.ai/studio/hidden-collection/troubleshooting
title: Hidden collection troubleshooting
breadcrumbs: [Studio, Hidden Collection]
kind: doc
locale: en
source_path: src/content/en/docs/studio/hidden-collection/troubleshooting/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
hidden: true
---

# Hidden collection troubleshooting

This page checks that nested hidden pages keep normal metadata and headings.

## Page returns 404

If this page returns 404, check that default-locale rewrites still include hidden routes.

## Page appears in navigation

If this page appears in navigation, check hidden category filtering in `getSidebar`.
