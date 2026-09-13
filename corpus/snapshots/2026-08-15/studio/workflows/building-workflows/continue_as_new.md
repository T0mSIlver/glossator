---
url: https://docs.mistral.ai/studio/workflows/building-workflows/continue_as_new
title: Continue-As-New
breadcrumbs: [Studio, Workflows, Building Workflows]
kind: doc
locale: en
source_path: src/content/en/docs/studio/workflows/building-workflows/continue_as_new/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Continue-As-New

Continue-As-New resets the workflow's event history while carrying forward its state, enabling indefinitely long-running workflows without hitting history size limits.

## When to use {#when-to-use}

- Long-running workflows that iterate indefinitely
- When workflow history approaches size limits (~50K events or 50MB)
- Workflows that need to run for weeks or months

## How it works {#how-it-works}

When `continue_as_new()` is called, the current run completes and a new run starts fresh from the beginning with the provided state. The event history is reset, while the state you pass to `continue_as_new()` is carried forward.

**Important:** Your workflow's `run` method must accept the carry-forward state as parameters to restore its state when continuing as new.

Use `workflows.workflow.should_continue_as_new()` to check whether the current run is approaching the history limit; it returns `True` when the event history is close to the cap.

**Python**

```python
import mistralai.workflows as workflows
from pydantic import BaseModel

class ProcessorState(BaseModel):
    page: int = 0
    total_processed: int = 0

@workflows.workflow.define(name="long-running-processor")
class LongRunningProcessor:
    @workflows.workflow.entrypoint
    async def run(self, page: int = 0, total_processed: int = 0):  # State parameters are required
        while True:
            # Process current page
            result = await process_page(page)
            total_processed += result.count
            page += 1

            # When history grows large, restart with a fresh history
            if workflows.workflow.should_continue_as_new():
                workflows.workflow.continue_as_new(ProcessorState(page=page, total_processed=total_processed))
```

For the related concept on the canonical Workflows page, see [Building Workflows > Workflows > Continue-as-new](https://docs.mistral.ai/studio/workflows/building-workflows/workflows#continue-as-new) and [Core Concepts > Workflows > Determinism](https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/workflows#determinism).
