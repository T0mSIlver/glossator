---
url: https://docs.mistral.ai/studio/workflows/building-workflows/workflow_tags
title: Workflow Tags
breadcrumbs: [Studio Api, Workflows, Building Workflows]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/workflows/building-workflows/workflow_tags/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Workflow Tags

Workflows support searchable metadata tags for filtering and discovery. Tags are filterable strings attached to workflow definitions (not executions) and surfaced in the AI Studio UI and the API.

## Setting Tags

Workflows are created with empty tags during worker registration, then users tag them via the update endpoint:

```http
PUT /v1/workflows/{workflow_identifier}
```

```json
{
  "tags": ["ocr", "document-processing"]
}
```

Updating tags **replaces** the existing tag list. Pass an empty list to clear all tags. Omitting `tags` from the request body leaves the existing tags unchanged.

## Filtering by Tags

The list endpoint accepts tags as a filter parameter with **AND** semantics — only workflows with **all** specified tags are returned:

```http
GET /v1/workflows?tags=ocr&tags=document-processing
```

## Validation

| Rule | Detail |
|------|--------|
| Max length | 100 characters per tag |
| Whitespace | Stripped from both ends |
| Empty tags | Rejected (including whitespace-only) |
| Duplicates | Silently deduplicated |
| Max count | No limit enforced |
