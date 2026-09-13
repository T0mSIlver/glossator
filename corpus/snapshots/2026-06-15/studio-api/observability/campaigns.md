---
url: https://docs.mistral.ai/studio-api/observability/campaigns
title: Campaigns
breadcrumbs: [Studio, Observability]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/observability/campaigns/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Campaigns

Campaigns let you **batch-annotate production traffic** using a [Judge](https://docs.mistral.ai/studio-api/observability/judges). You define a filter, pick a Judge, and the Campaign **runs the Judge on every matching event**, writing the annotations back into [Explorer](https://docs.mistral.ai/studio-api/observability/explorer).

## When to use Campaigns {#when-to-use}

Campaigns are the right tool when you want to **score existing production traffic** at scale. Common scenarios:

- **Detect problematic behavior:** your agent might be rude, off-topic, or giving inaccurate answers. Run a Campaign with a rudeness or quality Judge to find out.
- **Tag traffic for analysis:** classify a batch of events (e.g., `code` / `search` / `general`) and filter by category in Explorer.
- **Build quality-labeled Datasets:** run a Campaign, then export the annotated events to a Dataset.

## How to run a Campaign {#how-to-run}

#### Prerequisite: create a Judge

Before creating a Campaign, you need a [Judge](https://docs.mistral.ai/studio-api/observability/judges) that defines your quality criteria.

A Campaign uses a **single Judge**. To run multiple checks on the same traffic, create separate Campaigns.

#### Step 1: Filter events

Select a **time range**, then **add filter conditions** to narrow the scope (see [Explorer filter syntax](https://docs.mistral.ai/studio-api/observability/explorer#filter-language)).

> **Tip**
>
> If your filter returns too many events, set a **maximum number of events** (from 100 to 10,000).

#### Step 2: Launch the Campaign

Start the Campaign. It runs in the background: you can close the tab and check progress later in the Campaign details.

#### Step 3: Analyze results

Once complete, matching events appear **with annotations** in the **Judge output** column. From there you can:

- **Filter by annotation value** to surface flagged events (e.g., labeled `rude` or scored below 3).
- **Inspect individual events** to verify the Judge's assessments.
- **Export to a Dataset** for further review or analysis.

## [Developer] Use Campaigns programmatically {#sdk-access}

The [SDK](https://docs.mistral.ai/resources/sdks) lets you **create and monitor Campaigns from code**. Useful for scheduled quality checks, automated alerting pipelines, or CI/CD integration.

**Create a Campaign**

**Python**

**V1**

```python
import os
from mistralai import Mistral

mistral = Mistral(
    api_key=os.getenv("MISTRAL_API_KEY", ""),
)

# Create a Campaign to annotate last week's support conversations
campaign = mistral.beta.observability.campaigns.create(
    name="Support Quality Review - Week 3",
    description="Evaluate quality of customer support responses from last week",
    judge_id="judge-456",  # replace with your Judge ID
    search_params={
        "filters": {
            "AND": [
                {"field": "timestamp", "op": "gte", "value": "2026-01-15T00:00:00Z"},
                {"field": "timestamp", "op": "lt", "value": "2026-01-22T00:00:00Z"},
                {"field": "model_name", "op": "eq", "value": "mistral-medium-2508"}
            ]
        }
    },
    max_nb_events=5000
)

print(f"Campaign created: {campaign.id} — {campaign.name}")
```

**V2**

```python
import os
from mistralai.client import Mistral

mistral = Mistral(
    api_key=os.getenv("MISTRAL_API_KEY", ""),
)

# Create a Campaign to annotate last week's support conversations
campaign = mistral.beta.observability.campaigns.create(
    name="Support Quality Review - Week 3",
    description="Evaluate quality of customer support responses from last week",
    judge_id="judge-456",  # replace with your Judge ID
    search_params={
        "filters": {
            "AND": [
                {"field": "timestamp", "op": "gte", "value": "2026-01-15T00:00:00Z"},
                {"field": "timestamp", "op": "lt", "value": "2026-01-22T00:00:00Z"},
                {"field": "model_name", "op": "eq", "value": "mistral-medium-2508"}
            ]
        }
    },
    max_nb_events=5000
)

print(f"Campaign created: {campaign.id} — {campaign.name}")
```

**Monitor and read results**

**Python**

```python
# Check Campaign status
status = mistral.beta.observability.campaigns.fetch_status(
    campaign_id=campaign.id
)
print(f"Status: {status.status}")

# List annotated events once the Campaign completes
annotated_events = mistral.beta.observability.campaigns.list_events(
    campaign_id=campaign.id,
    page_size=100
)

for event in annotated_events.completion_events.results:
    # Annotations are stored in extra_fields with the Judge ID as key
    annotation = event.extra_fields.get("__judge_<judge-id>")
    print(f"Event {event.event_id}: {annotation}")
```

**List and delete**

**Python**

```python
# List all Campaigns
campaigns = mistral.beta.observability.campaigns.list(page_size=20)
for c in campaigns.campaigns.results:
    print(f"{c.name} (id: {c.id})")

# Search Campaigns by name
support_campaigns = mistral.beta.observability.campaigns.list(q="support")

# Get Campaign details
campaign = mistral.beta.observability.campaigns.fetch(
    campaign_id="campaign-123"  # replace with your Campaign ID
)
print(f"Campaign: {campaign.name}")

# Delete a Campaign
mistral.beta.observability.campaigns.delete(
    campaign_id="campaign-123"  # replace with your Campaign ID
)
print("Campaign deleted")
```

## FAQ {#faq}

### Campaign creation failed with a filter error {#campaign-creation-failed-with-a-filter-error}

If no events match your filter, the API won't create the Campaign and returns an error. Check your filter conditions, especially the time range. Try running the same filter in Explorer first to confirm it returns results.

### Can I change the filter after starting a Campaign? {#can-i-change-the-filter-after-starting-a-campaign}

No. Filters lock when the Campaign starts. If the scope is wrong, create a new Campaign with the correct filter.

### Annotations don't look right {#annotations-dont-look-right}

The issue is likely in the Judge, not the Campaign. Review the Judge's instructions and test it on a few individual records. See [Judges — validate before you scale](https://docs.mistral.ai/studio-api/observability/judges#validation-before-scale).

### I need more than 10,000 events {#i-need-more-than-10000-events}

Split the work into multiple Campaigns with non-overlapping filters (e.g., by date range or model). Each Campaign can process up to 10,000 events.

### How long does a Campaign take? {#how-long-does-a-campaign-take}

It depends on the number of events and the Judge model's throughput. Campaigns run asynchronously. You don't need to keep the tab open. Check the Campaign status in the UI or via the SDK.

### If I delete a Campaign, are the annotations lost? {#if-i-delete-a-campaign-are-the-annotations-lost}

No. Annotations are written directly onto the events in Explorer. Deleting a Campaign removes the Campaign definition, but the annotations it produced remain on the events.
