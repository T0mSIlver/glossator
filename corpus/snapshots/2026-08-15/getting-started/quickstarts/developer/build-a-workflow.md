---
url: https://docs.mistral.ai/getting-started/quickstarts/developer/build-a-workflow
title: Build a workflow
breadcrumbs: [Getting started, Quickstarts, Developer]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/developer/build-a-workflow/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Build a workflow

Workflows let you run multi-step AI pipelines that survive crashes, retries, and long waits. Your code runs in your environment; Mistral handles orchestration, state, and observability.

By the end of this quickstart you'll have a working workflow running locally, triggered from the Mistral Console.

**Time to complete:** ~15 minutes

## Prerequisites {#prerequisites}

- A Mistral API key (see [Send your first API request](https://docs.mistral.ai/getting-started/quickstarts/developer/first-api-request#step-1) if you don't have one yet)
- [Python](https://www.python.org/downloads/) 3.12 or later
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed (`uvx` ships with it)

## Step 1: Scaffold your project {#step-1}

Run the following command in your terminal:

```bash
uvx mistralai-workflows-cli setup
```

The CLI scaffolds a ready-to-run Python project and prompts you for your Mistral API key. Enter the key when asked — it's stored in the project's environment configuration.

Open the generated directory (default name: `my-workflow`) in your editor.

## Step 2: Understand the workflow {#step-2}

Open `src/workflows/hello.py`. The scaffolded project includes a minimal example:

```python
from pydantic import BaseModel
import mistralai.workflows as workflows


class HelloInput(BaseModel):
    name: str = "World"


@workflows.activity()
async def greet(name: str) -> str:
    return f"Hello, {name}! Welcome to Mistral Workflows."


@workflows.workflow.define(
    name="hello-world",
    workflow_display_name="Hello World",
    workflow_description="A minimal hello-world workflow.",
)
class HelloWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, input: HelloInput) -> str:
        return await greet(input.name)
```

Two things to notice:

- `@workflows.activity()` marks a function as a durable step. If the process crashes mid-run, the platform replays from the last completed activity.
- `@workflows.workflow.define` registers the workflow with a name you'll use to trigger it.

## Step 3: Start the worker {#step-3}

From the root of your project, run:

```bash
make start-worker
```

The worker connects to the Mistral API, registers your workflow, and waits for tasks. Keep this terminal open.

## Step 4: Trigger the workflow {#step-4}

With the worker running, open a second terminal and trigger an execution using the Makefile command:

```bash
make execute workflow=hello-world input='{"name": "World"}'
```

Or trigger it from the [Mistral Console](https://console.mistral.ai):

1. Navigate to **Workflows** in the sidebar.
2. Select **hello-world**.
3. Click **Start Workflow** and pass `{"name": "World"}` as input.
4. Open the **Executions** tab to watch it run.

## Verify {#verify}

The execution completes with:

```json
{
  "result": "Hello, World! Welcome to Mistral Workflows."
}
```

If the worker terminal shows a connection error, confirm your API key is set correctly and that the worker process is still running.

Press `Ctrl+C` to stop the worker when you're done.

## What's next {#whats-next}

- [Core concepts](https://docs.mistral.ai/studio/workflows/getting-started/core_concepts)

- [Cookbook examples](https://docs.mistral.ai/studio/workflows/getting-started/cookbook_examples)

- [Build a durable agent](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents)

- [All developer quickstarts](https://docs.mistral.ai/#quickstarts)
