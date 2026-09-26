---
url: https://docs.mistral.ai/studio/hidden-collection/troubleshooting
title: Hidden collection troubleshooting
breadcrumbs: [Studio, Hidden Collection]
kind: doc
locale: en
source_path: src/content/en/docs/studio/hidden-collection/troubleshooting/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
hidden: true
---

# Hidden collection troubleshooting

This page checks that nested hidden pages keep normal metadata and headings.

## Page returns 404

If this page returns 404, check that default-locale rewrites still include hidden routes.

## Page appears in navigation

If this page appears in navigation, check hidden category filtering in `getSidebar`.
