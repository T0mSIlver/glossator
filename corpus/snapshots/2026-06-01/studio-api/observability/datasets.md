---
url: https://docs.mistral.ai/studio-api/observability/datasets
title: Datasets
breadcrumbs: [Studio, Observability]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/observability/datasets/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Datasets

Datasets are **curated collections of conversation records** used to evaluate model quality and build regression tests.

Unlike raw traffic in [Explorer](https://docs.mistral.ai/studio-api/observability/explorer), Dataset records are **editable**: fix messages, add expected outputs, remove noise, and shape the data directly from the Studio interface.

## What's in a record {#record-structure}

Each record has three parts:

| Field          | Content                                               | Purpose                                      |
|----------------|-------------------------------------------------------|----------------------------------------------|
| **Conversation**   | System messages, user inputs, assistant responses, and tool calls. | The core data that Judges evaluate. |
| **Properties** | Custom metadata: expected output, category, grading guidance, difficulty, etc. | Judges reference properties in their instructions via `{{ properties.* }}`. |
| **Source**     | Where the record came from: `EXPLORER`, `UPLOADED_FILE`, `DIRECT_INPUT`, or `PLAYGROUND`. | Traceability back to the record's origin. |

### Properties

Properties are what make Datasets more than a list of conversations. They let you attach **structured context** to each record:

- `expected_output`: the ideal response, so a Judge can compare against it.
- `category`: the type of request (e.g., `billing`, `technical`, `general`).
- `grading_guidance`: specific instructions for how the Judge should evaluate this record.
- `difficulty`: a difficulty marker to segment results by complexity.

> **Tip**
>
> Judges can reference any property in their instructions using `{{ properties.your_field_name }}`. See [Instructions guidelines](https://docs.mistral.ai/studio-api/observability/judges#setting-instructions) for details.

## Add data to a Dataset {#add-data}

Click **New dataset**, then choose a source:

### Create manually

Add records by hand in Studio. Define conversation turns, then attach properties and metadata.

Useful for:
- Regression tests targeting a known edge case.
- Golden examples with carefully crafted expected outputs.
- Specific scenarios that don't appear naturally in production traffic.

> **Info**
>
> Properties can be entered as key-value pairs or pasted as raw JSON for bulk editing.

### From the Playground

Import conversations from the [Playground](https://console.mistral.ai/build/playground) — useful if you've been testing agents or prompts and want to reuse those conversations without recreating them manually.

### From a Campaign

Import **all or a subset** of a Campaign's records, **including the Judge's annotations as properties**. This lets you build curated Datasets from evaluated traffic.

### From Explorer

Select events in [Explorer](https://docs.mistral.ai/studio-api/observability/explorer) and click **Export to Dataset**. See the [Explorer guide](https://docs.mistral.ai/studio-api/observability/explorer#export-to-datasets) for details.

### From a file

Upload a JSONL file to import records in bulk. Each line must be a JSON object with `messages` and optionally `properties`:

```json
{"messages": [{"role": "user", "content": "How do I reset my password?"}, {"role": "assistant", "content": "Go to Settings > Security > Reset password."}], "properties": {"expected_output": "Clear reset instructions", "category": "account"}}
{"messages": [{"role": "user", "content": "What's the rate limit?"}], "properties": {"expected_output": "Tier-specific rate limit info", "category": "technical"}}
```

> **Info**
>
> Imports can take some time. Check the status by clicking the **Import Tasks** button.

## Export a Dataset {#download-data}

Click **Actions → Export to JSONL** to export a Dataset as a JSONL file. Each line contains a record with its conversation and properties.

## Best practices {#best-practices}

### Curate your records

Click into any record to edit:

- **Messages**: fix typos, clarify ambiguous inputs, or reshape the conversation to better represent a test case.
- **Properties**: add `expected_output`, `grading_guidance`, or any metadata your Judges need.

### Remove low-value records

Strip out records that add noise:

- **Duplicates**: similar conversations that over-represent one scenario.
- **Out of scope**: records that don't match the Dataset's purpose.
- **Ambiguous**: conversations where even a human couldn't reliably score the response.

### Test before you commit

Run a Judge on a single record before launching a full Campaign. This is the fastest way to verify that your instructions and properties work together. See [Validate before you scale](https://docs.mistral.ai/studio-api/observability/judges#validation-before-scale).

### Keep Datasets healthy

If you reuse Datasets over time (and you should):

- **Name explicitly.** Include scope and date: `support_billing_baseline_2025_06`, not `test_data`.
- **Track sources.** Note where records came from and what curation you applied.
- **Version baselines.** Freeze a baseline Dataset between uses. Create a new version when you need changes.
- **Don't mix unrelated tasks.** Keep "support quality" and "code generation accuracy" in separate Datasets.
- **Check class balance.** If 90% of your records are easy cases, the Dataset won't reveal real problems.

## [Developer] Use Datasets programmatically {#sdk-access}

The [SDK](https://docs.mistral.ai/resources/sdks) lets you create Datasets, import records, and manage data from code.

**Create a Dataset**

**Python**

**V1**

```python
import os
from mistralai import Mistral

mistral = Mistral(
    api_key=os.getenv("MISTRAL_API_KEY", ""),
)

# Create an empty Dataset
dataset = mistral.beta.observability.datasets.create(
    name="Customer Support Analysis Set",
    description="Curated examples for analyzing support agent quality"
)

print(f"Dataset created: {dataset.id}")
```

**V2**

```python
import os
from mistralai.client import Mistral

mistral = Mistral(
    api_key=os.getenv("MISTRAL_API_KEY", ""),
)

# Create an empty Dataset
dataset = mistral.beta.observability.datasets.create(
    name="Customer Support Analysis Set",
    description="Curated examples for analyzing support agent quality"
)

print(f"Dataset created: {dataset.id}")
```

**Add records**

**Python**

```python
# Add a single record with messages and properties
record = mistral.beta.observability.datasets.create_record(
    dataset_id=dataset.id,
    payload={
        "messages": [
            {"role": "user", "content": "How do I reset my password?"},
            {"role": "assistant", "content": "You can reset your password by..."}
        ],
        "model": "mistral-medium-latest"
    },
    properties={
        "expected_output": "Clear password reset instructions",
        "category": "account_management",
        "difficulty": "easy"
    }
)
print(f"Record added: {record.id}")
```

**Import from file or Explorer**

**Python**

```python
# Import from a JSONL file
# First, upload your file to get a file_id:
uploaded_file = mistral.files.upload(
    file={"file_name": "records.jsonl", "content": open("records.jsonl", "rb")}
)

import_task = mistral.beta.observability.datasets.import_from_file(
    dataset_id=dataset.id,
    file_id=uploaded_file.id
)
print(f"Import started: {import_task.id} ({import_task.status})")

# Import from Explorer search results
result = mistral.beta.observability.chat_completion_events.search(
    search_params={
        "filters": {
            "AND": [
                {"field": "timestamp", "op": "gte", "value": "2026-02-01T00:00:00Z"},
                {"field": "timestamp", "op": "lte", "value": "2026-02-07T00:00:00Z"}
            ]
        }
    },
    page_size=100
)

res = mistral.beta.observability.datasets.import_from_explorer(
    dataset_id=dataset.id,
    completion_event_ids=[
        event.event_id for event in result.completion_events.results
    ]
)
print(f"Imported {len(result.completion_events.results)} events into dataset")
```

**List records**

**Python**

```python
# List records in a Dataset
result = mistral.beta.observability.datasets.list_records(
    dataset_id=dataset.id,
    page_size=50
)

for record in result.records.results:
    first_msg = record.payload.messages[0]
    print(f"Record: {first_msg.get('content', '')[:60]}...")
    print(f"  Properties: {record.properties}")
```

## FAQ {#faq}

### Campaign scores are noisy. Is it the Dataset or the Judge? {#campaign-scores-are-noisy-is-it-the-dataset-or-the-judge}

Start with the Dataset. Inspect the low-scoring records: are the inputs ambiguous? Are the properties (expected output, grading guidance) clear enough? Fix the Dataset first, then tune the Judge instructions.

### My Dataset is too broad and results are hard to interpret {#my-dataset-is-too-broad-and-results-are-hard-to-interpret}

Split it into smaller, thematic Datasets. A `support_billing` Dataset and a `support_technical` Dataset will give clearer signals than a single `support` Dataset with everything mixed together.
