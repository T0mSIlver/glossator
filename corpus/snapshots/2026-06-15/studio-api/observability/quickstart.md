---
url: https://docs.mistral.ai/studio-api/observability/quickstart
title: Quickstart
breadcrumbs: [Studio, Observability]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/observability/quickstart/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Quickstart

> **Info**
>
> This guide walks through the Observability workflow in [Studio](http://console.mistral.ai).
>
> **Are you a developer?** Look for the `API & SDK Implementation` callout included in each step:
> - it shows the **exact SDK method(s)** for the same action,
> - and links to the corresponding section in the API/SDK docs.

## What you'll get {#what-youll-get}

By the end of this guide, you will have:

- A **filtered view** of your production traffic showing relevant conversations.
- A **Judge** that automatically identifies and scores/labels these conversations for you.
- A completed **Campaign** that applies the Judge across your traffic at scale.
- A **Dataset** built from the Campaign results.

## Before you start {#before-you-start}

Make sure you have:

- An **Enterprise-tier** Organization.
- **Admin access** to the Observability features in your Organization.
- A production traffic with **chat completion events**.

## Step 1: Explore production traffic {#step-1}

Click **Observe** then open **Explorer** in the sidebar.

Your goal is to find a filter combination that surfaces **relevant conversations** (e.g. failure modes, low-quality responses, or specific behaviors you want to investigate).

1. Start with a **broad time range** (e.g., last 7 days) and **one model** (e.g., `mistral-medium-2508`).
2. **Experiment with filters** until you find a combination that suits your needs. For example:
   - `invoked_tools includes "web_search"` to isolate tool-using conversations.
   - `last_user_message_preview contains "reset password"` to find conversations about a specific topic.
   - `total_time_elapsed > 5` to find slow responses.
3. **Click into individual events** to inspect messages, tool calls, and metadata.

> **Tip**
>
> Refining your filters **improves Judge and Campaign accuracy**. This step helps you define "relevant" before automating evaluations.

![The Explorer view with the filter bar showing `model_name = 'mistral-medium-2508'` and a date range. Below, a list of events with columns for timestamp, model, tokens, and latency. One event is expanded showing the full conversation.](https://docs.mistral.ai/img/observability_explorer_ui.png)

The Explorer view with the filter bar showing `model_name = "mistral-medium-2508"` and a date range.

API & SDK Implementation

[In the SDK](https://docs.mistral.ai/studio-api/observability/explorer#sdk-access), use the `chat_completion_events.search()` method to filter your events programmatically.

## Step 2: Create a Judge {#step-2}

You have identified a filter combination that surfaces relevant conversations. You will now create a Judge to **evaluate them automatically**.

1. Go to **Judges** in the sidebar and click **Create Judge**.
2. **Select a model** among the available options.
3. Provide clear instructions detailing **how to evaluate the conversations**. For example:

    ```text
    Rate how helpful the assistant's response is to the user's question.
    Consider whether the response is accurate, relevant, and complete.
    ```

4. **Add tools** (Optional):
   - Enable **Web Search** to give the Judge access to the internet.
   - Choose **Code Interpreter** to let the Judge run its own Python code.
5. **Select a Judge type** and provide the corresponding labels or score ranges:
   - **Classification** for discrete labels (e.g. `helpful` / `not helpful`).
   - **Regression** for a numeric score (e.g., 0 to 5).

6. Click **Create Judge**, provide a name and description, and confirm.

![The Judge creation form showing an instruction text area, the output type selector (Classification selected with two options: 'helpful' and 'not helpful'), and the model dropdown.](https://docs.mistral.ai/img/observability_judges_create.png)

The Judge creation form with instructions, output type, and model selection.

> **Tip**
>
> [Test your Judge](https://docs.mistral.ai/studio-api/observability/judges#validation-before-scale) on real records **before running a Campaign**.

API & SDK Implementation

[In the SDK](https://docs.mistral.ai/studio-api/observability/judges#sdk-access), use `judges.create()` and pass your instructions and other parameters in the function.

## Step 3: Run a Campaign {#step-3}

A **Campaign** evaluates a set of filtered events and **applies your Judge** to them. To run a Campaign:

1. Go to **Campaigns** in the sidebar and click **Create Campaign**.
2. In the Campaign creation form :
    + Select the **Judge** you created in Step 2.
    + Select a **time range** (e.g., last 7 days).
    + **Define your filters** (reuse the same filter conditions from Step 1, or widen the scope if needed)
    + Limit the **number of events** to process (ranging from 100 to 10,000).
3. Click **Create Campaign**, set a Campaign name and description, then confirm.

**Campaigns run in the background**. Check back later in the [Campaigns dashboard](https://console.mistral.ai/observability/campaigns) for results.

![The campaign detail view showing: the Judge used, the time range, the filter conditions and the number of events considered](https://docs.mistral.ai/img/observability_campaign_run.png)

Create a new Campaign and apply a Judge.

API & SDK Implementation

[In the SDK](https://docs.mistral.ai/studio-api/observability/campaigns#sdk-access), use `campaigns.create()` to define filters and attach your Judge, then monitor progress with `campaigns.fetch_status()`.

## Step 4: Save results to a Dataset {#step-4}

Your Campaign has completed. All events are now **annotated with the Judge's output** and you can **save them to a Dataset**:

1. **Select the relevant events** (you may apply additional filters).
2. Click **Actions** and choose between adding the matching events to a **new Dataset** or append them to an existing one.

> **Tip**
>
> Campaigns annotations are linked to their original events. View them anytime in [Explorer](https://docs.mistral.ai/studio-api/observability/explorer).

API & SDK Implementation

In the SDK (see [Campaigns](https://docs.mistral.ai/studio-api/observability/campaigns#sdk-access) & [Datasets](https://docs.mistral.ai/studio-api/observability/datasets#sdk-access)), use `campaigns.list_events()` then `datasets.import_from_explorer()` to pipe the matching events directly into a dataset.

## Congratulations {#whats-next}

Congratulations! You have created a **curated, annotated Dataset**, built from **real production data**.

Want to learn more? **Explore the following deep dives** in the Observability docs:

- **[Explorer](https://docs.mistral.ai/studio-api/observability/explorer)**: Query specific events and filter production logs.
- **[Judges](https://docs.mistral.ai/studio-api/observability/judges)**: Design complex instructions, schemas, and validation techniques.
- **[Campaigns](https://docs.mistral.ai/studio-api/observability/campaigns)**: Annotate thousands of production events in bulk.
- **[Datasets](https://docs.mistral.ai/studio-api/observability/datasets)**: Manage record structures, curation, and file imports.

## Troubleshooting {#troubleshooting}

### Explorer shows no events {#explorer-shows-no-events}

Expand your time range filter. If you are using a narrow window (e.g., last hour), try the last 7 days instead. If Explorer is still empty, confirm that your project has active chat completion traffic and that you have admin access to the Workspace.

### I cannot export events to a dataset {#i-cannot-export-events-to-a-dataset}

Check your Workspace permissions. Dataset creation and export require admin-level access. If you have the correct role but still cannot export, ensure you have selected at least one event in the UI.

### Judge scores seem inconsistent {#judge-scores-seem-inconsistent}

Your Judge instructions might be too vague. Be explicit about the definitions for each score or class. Test the Judge on 5 to 10 records manually before running a full Campaign. See the [dedicated section on Judges validation](https://docs.mistral.ai/studio-api/observability/judges#validation-before-scale) for guidance.

### The Campaign is pending or stuck {#the-campaign-is-pending-or-stuck}

Campaigns run asynchronously and large event sets take longer. Check the Campaign status in the UI. If a Campaign halts completely, check the status for specific event errors.

### Campaign annotations don't look right {#campaign-annotations-dont-look-right}

The issue is likely in the Judge, not the Campaign. Review the Judge's instructions and test it on a few individual events. See [Judges — validate before you scale](https://docs.mistral.ai/studio-api/observability/judges#validation-before-scale).
