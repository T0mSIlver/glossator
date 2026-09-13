---
url: https://docs.mistral.ai/studio/workflows/managing-workflows-in-production/execution_context
title: Execution Context
breadcrumbs: [Studio, Workflows, Managing Workflows in Production]
kind: doc
locale: en
source_path: src/content/en/docs/studio/workflows/managing-workflows-in-production/execution_context/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Execution Context

Access runtime information about the current workflow execution from within workflow code.

## Getting the execution ID {#getting-the-execution-id}

**Python**

```python
import mistralai.workflows as workflows

execution_id = workflows.get_execution_id()
```

This returns the unique identifier for the current execution, useful for logging, correlating with external systems, or passing to activities that need to reference the parent execution.

## Example usage {#example-usage}

**Python**

```python
import mistralai.workflows as workflows

@workflows.workflow.define(name="tracked_workflow")
class TrackedWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, params: MyParams) -> MyResult:
        execution_id = workflows.get_execution_id()

        # Pass execution ID to activities for correlation
        result = await process_with_tracking(params, execution_id)
        return result
```
