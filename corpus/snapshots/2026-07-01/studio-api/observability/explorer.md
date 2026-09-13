---
url: https://docs.mistral.ai/studio-api/observability/explorer
title: Explorer
breadcrumbs: [Studio, Observability]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/observability/explorer/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Explorer

Explorer is your **window into production traffic**.

It lets you **search, filter, and inspect every chat completion event** flowing through your Workspace.

> **Info**
>
> Explorer is restricted to **Workspace administrators**.

## What you can do {#what-you-can-do}

- **Search and filter** events by model, tool usage, message content, latency, etc.
- **Inspect** any conversation records (messages, tool calls, and metadata).
- **Export** filtered events to [Datasets](https://docs.mistral.ai/studio-api/observability/datasets).
- **Automate** by creating [Judges](https://docs.mistral.ai/studio-api/observability/judges) and [Campaigns](https://docs.mistral.ai/studio-api/observability/campaigns) directly from your filter results.

## Filter language {#filter-language}

Explorer supports a **structured filter language**.

You write conditions on event fields and combine them with `AND`, `OR`, and parentheses.

### Available operators

| Operator          | Meaning                          | Example                                       |
|-------------------|----------------------------------|-----------------------------------------------|
| `=`               | Equals                           | `model_name = "mistral-medium-2508"`          |
| `!=`              | Not equals                       | `model_name != "mistral-medium-2508"`         |
| `contains`        | Substring match                  | `model_name contains "large"`                 |
| `includes`        | List contains value              | `invoked_tools includes "web_search"`         |
| `excludes`        | List doesn't include value       | `invoked_tools excludes "web_search"`         |
| `>`               | Greater than                     | `total_time_elapsed > 5`                      |
| `<`               | Less than                        | `total_time_elapsed < 2`                      |
| `>=`              | Greater than or equal            | `total_time_elapsed >= 5`                     |
| `<=`              | Less than or equal               | `total_time_elapsed <= 2`                     |
| `isnull`          | Is null                          | `api_agent_id isnull False`                   |
| `length_equals`   | List length equals               | `invoked_tools length_equals 3`               |
| `starts_with`     | Starts with substring            | `model_name startswith "mistral-med"`         |
| `ends_with`       | Ends with substring              | `model_name endswith "-2508"`                 |
| `matches`         | Regex match                      | `model_name matches ".+-8b-.+"`              |

### Available fields

| Field (UI label) | Filter name | Type | Description |
|---|---|---|---|
| Date | `timestamp` | datetime | Time when the request was processed |
| Model | `model_name` | string | Name of the model that generated the response |
| Prompt | `last_user_message_preview` | string | Preview of the last user message |
| Response | `response_messages_preview` | string | Preview of the assistant's response |
| Tools: Invoked tools | `invoked_tools` | list | Tools called during the request |
| Computation duration (s) | `total_time_elapsed` | number | Total request duration in seconds |
| Input Tokens | `input_tokens` | number | Number of input tokens consumed |
| Output Tokens | `output_tokens` | number | Number of output tokens generated |
| API Agent ID | `api_agent_id` | string | ID of the agent that handled the request, if any |
| Event ID | `event_id` | string | Unique identifier for the event |
| Correlation ID | `correlation_id` | string | Identifier used to trace a request across systems |
| First system message | `first_system_message` | string | Preview of the first system prompt |
| Metadata | `metadata` | object | Custom key-value metadata attached to the request |

### Examples

**Filter by model and tool usage:**

```text
model_name = "mistral-medium-2508" AND invoked_tools includes "web_search"
```

**Filter by model family with code output:**

```text
(model_name contains "large" OR model_name contains "small") AND invoked_tools includes "code_interpreter"
```

**Filter by response time:**

```text
total_time_elapsed > 5
```

**Combine multiple conditions:**

```text
model_name = "mistral-large" AND total_time_elapsed > 5 AND (last_user_message_preview contains "password" OR response_messages_preview contains "error")
```

> **Tip**
>
> Use the **autocomplete dropdown** to select from the suggested fields and values as you type.

### Query design tips

1. **Start broad** with a time range, then narrow down.
2. **Add one business-relevant condition** (e.g., a specific tool, feature, or model).
3. **Add one technical condition** (e.g., latency, message content, or specific tools).
4. **Scan a few results** before exporting. Make sure the sample is relevant.

## Inspect events {#inspect-events}

Click any event in the results list to see the full detail view. Each event includes:

- A **feed of messages**, including the full conversation (user inputs, assistant responses, and system prompts).
- A **list of properties** (model name, token counts, computation duration, and any tools invoked by the model).

## Export to a Dataset {#export-to-datasets}

Once you've filtered to a useful set of events, you can **export them** to a [Dataset](https://docs.mistral.ai/studio-api/observability/datasets).

1. Select one or more events using the checkboxes
2. Click **Add to dataset**.
3. Choose an existing Dataset or create a new one.

**Treat Dataset exports as snapshots**. Use descriptive names (e.g., `support_web_search_2026_02`) and clear descriptions to enable accurate comparisons over time.

> **Tip**
>
> Found a useful filter? Reuse it to create a [Judge](https://docs.mistral.ai/studio-api/observability/judges) or [Campaign](https://docs.mistral.ai/studio-api/observability/campaigns) directly from the Explorer UI.

## [Developer] Use Explorer programmatically {#sdk-access}

All Explorer functionality is available via the [SDK](https://docs.mistral.ai/resources/sdks). Use it to automate searches, build reporting pipelines, or integrate with custom tooling.

**Search events**

Search for events using the same filter structure as the UI, but expressed as nested dictionaries.

**Python**

**V1**

```python
import os
from mistralai import Mistral

mistral = Mistral(
    api_key=os.getenv("MISTRAL_API_KEY", ""),
)

# Search for events matching specific criteria
result = mistral.beta.observability.chat_completion_events.search(
    search_params={
        "filters": {
            "AND": [
                {"field": "timestamp", "op": "gte", "value": "2026-01-15T00:00:00Z"},
                {"field": "timestamp", "op": "lte", "value": "2026-01-16T00:00:00Z"},
                {"field": "model_name", "op": "eq", "value": "mistral-medium-2508"},
                {"field": "invoked_tools", "op": "includes", "value": "web_search"}
            ]
        }
    },
    extra_fields=["model_name"],
    page_size=20
)

print(f"Found {len(result.completion_events.results)} events")
for event in result.completion_events.results:
    print(f"{event.event_id}: {event.extra_fields.get('model_name')}")
```

**V2**

```python
import os
from mistralai.client import Mistral

mistral = Mistral(
    api_key=os.getenv("MISTRAL_API_KEY", ""),
)

# Search for events matching specific criteria
result = mistral.beta.observability.chat_completion_events.search(
    search_params={
        "filters": {
            "AND": [
                {"field": "timestamp", "op": "gte", "value": "2026-01-15T00:00:00Z"},
                {"field": "timestamp", "op": "lte", "value": "2026-01-16T00:00:00Z"},
                {"field": "model_name", "op": "eq", "value": "mistral-medium-2508"},
                {"field": "invoked_tools", "op": "includes", "value": "web_search"}
            ]
        }
    },
    extra_fields=["model_name"],
    page_size=20
)

print(f"Found {len(result.completion_events.results)} events")
for event in result.completion_events.results:
    print(f"{event.event_id}: {event.extra_fields.get('model_name')}")
```

**Complex filters with AND/OR:**

**Python**

```python
# Combine conditions with nested AND/OR
events = mistral.beta.observability.chat_completion_events.search(
    search_params={
        "filters": {
            "AND": [
                {"field": "model_name", "op": "eq", "value": "mistral-large"},
                {"field": "total_time_elapsed", "op": "gt", "value": 5},
                {
                    "OR": [
                        {"field": "last_user_message_preview", "op": "contains", "value": "password"},
                        {"field": "invoked_tools", "op": "includes", "value": "web_search"}
                    ]
                }
            ]
        }
    }
)
print(f"Found {len(events.completion_events.results)} events")
```

**Discover fields**

Not sure which fields you can filter on? List them programmatically.

**Python**

```python
# List all available filter fields
fields = mistral.beta.observability.chat_completion_events.fields.list()

for field in fields.field_definitions:
    print(f"{field.name} ({field.type}) — operators: {field.supported_operators}")

# Get available values for a specific field
options = mistral.beta.observability.chat_completion_events.fields.fetch_options(
    field_name="model_name",
    operator="startswith"
)
print(f"Available models: {options.options}")
```

**Export to dataset**

Export search results directly to a dataset without going through the UI.

**Python**

```python
# 1. Search for events
result = mistral.beta.observability.chat_completion_events.search(
    search_params={
        "filters": {
            "AND": [
                {"field": "timestamp", "op": "gte", "value": "2026-02-01T00:00:00Z"},
                {"field": "timestamp", "op": "lte", "value": "2026-02-07T00:00:00Z"},
                {"field": "model_name", "op": "eq", "value": "mistral-medium-2508"}
            ]
        }
    },
    page_size=100
)

# 2. Create a dataset
dataset = mistral.beta.observability.datasets.create(
    name="weekly_review_2026_02_w1",
    description="Medium model traffic, first week of Feb 2026"
)
print(f"Dataset created: {dataset.id}")

# 3. Import the matching events
res = mistral.beta.observability.datasets.import_from_explorer(
    dataset_id=dataset.id,
    completion_event_ids=[
        event.event_id for event in result.completion_events.results
    ]
)
print(f"Imported {len(result.completion_events.results)} events")
```

## FAQ {#faq}

### My filters return no results {#my-filters-return-no-results}

Start by expanding the time range. If that doesn't help, remove all conditions except the time range and add them back one at a time. This usually reveals which condition is too restrictive.

### Results are too noisy to be useful {#results-are-too-noisy-to-be-useful}

Narrow the scope: filter to one model and one use case. Add a condition on a specific tool or output flag. A smaller, focused set is more actionable than a large, noisy one.

### I can't see Explorer in my sidebar {#i-cant-see-explorer-in-my-sidebar}

Explorer is restricted to Workspace administrators on Enterprise-tier plans. Check with your Workspace admin if you don't have access.

### Export is blocked or the button is greyed out {#export-is-blocked-or-the-button-is-greyed-out}

Make sure you've selected at least one event. If the button is still disabled, check your Workspace role. You need admin permissions to create Datasets.
