---
url: https://docs.mistral.ai/vibe/work/scheduled-tasks
title: Schedule tasks
breadcrumbs: [Vibe, Work]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/work/scheduled-tasks/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Schedule tasks

> **Note**
>
> **Preview.** Scheduled tasks are available in preview. The UI, naming, and options may evolve.

Scheduled tasks let you **run a prompt automatically** at a future date or on a recurring schedule. Work picks up the prompt at the scheduled time, executes it like any other task, and notifies you when the result is ready.

Use them for anything you repeat: a weekly competitive watch, a daily inbox triage, a Monday morning roll-up of unread emails and Slack messages, or a one-off reminder to draft a follow-up next Tuesday.

> **Info**
>
> Scheduled tasks run **in Work mode only** and use the [Workflows](https://docs.mistral.ai/vibe/work/workflows) infrastructure under the hood. They take advantage of every Work capability: [Skills](https://docs.mistral.ai/vibe/work/skills), inline [Connectors](https://docs.mistral.ai/vibe/work/connectors), [Web search](https://docs.mistral.ai/vibe/work/web-search-open-url), [Libraries](https://docs.mistral.ai/vibe/work/libraries), and [Projects](https://docs.mistral.ai/vibe/work/projects). Triggers are **time-based** for now; event-based triggers may follow.

## Common use cases {#use-cases}

Scheduled tasks shine when the **same question** comes back on a regular cadence:

- **Weekly digest**: every Monday morning, summarize your unread emails and Slack messages from the past week.
- **Release summary**: every Friday, generate a weekly release summary from Linear, Notion, and Slack.
- **Meeting briefing**: daily at 9am, prepare a briefing for your first meeting of the day.
- **Tech and competitive watch**: every Monday, summarize the past week's announcements from a list of competitors.
- **One-off reminders**: a single prompt scheduled for next Tuesday to draft a follow-up email referencing today's notes.

## Creating a scheduled task {#creating-a-schedule}

You can create a scheduled task in two ways.

### From the Tasks page {#from-tasks-page}

1. In the sidebar, click `Scheduled`.
2. Click `New Task`.
3. Write the prompt you want Work to run.
4. Click `Schedule` and pick a frequency (see [below](https://docs.mistral.ai/vibe/work/scheduled-tasks#scheduling-options)).
5. Set the time of day.
6. Click `Schedule` to confirm, or `Cancel` to discard.

A confirmation card summarizes the schedule in plain language (for example, *"Every Monday at 9:00"*) so you can double-check before activating it.

### From a chat {#from-a-chat}

You can also ask Work to schedule the current prompt directly in conversation. For example:

- `Schedule this to run every Monday at 9am.`
- `Run this every weekday morning.`
- `Remind me with this prompt next Tuesday at 14:00.`

Work proposes a schedule, you confirm, and the task is added to your Tasks page.

The scheduled task uses **the same Work surface** as a manual prompt: Skills, Connectors, Web search, Libraries, and Projects are all available natively. You may also see **suggested schedules** based on your recent conversations and connected tools.

## Scheduling options {#scheduling-options}

Five frequencies are available:

| Frequency | What you pick |
|---|---|
| `Once` | A single calendar date and time. |
| `Daily` | A time of day. Runs every day at that time. |
| `Weekly` | One or several days of the week, plus a time. |
| `Monthly` | A day of the month, plus a time. |
| `Yearly` | A day and a month (one date per year), plus a time. |

## Tools, Connectors, and approvals {#tools-and-approvals}

A scheduled task runs unattended, so think about **approvals upfront**.

When the prompt triggers a sensitive Connector action (sending an email, posting a message, modifying a file), Work normally asks for confirmation. To let a scheduled task complete without you in front of the screen, pre-authorize the relevant actions with `Always allow` for that Connector. See [Safety and approvals](https://docs.mistral.ai/vibe/work/safety-and-approvals#approvals) and [Per-function Connector permissions](https://docs.mistral.ai/vibe/work/safety-and-approvals#connector-functions).

> **Tip**
>
> Use **read-only** prompts (summarize, brief, monitor) for unattended runs, and reserve **write actions** (send, post, modify) for prompts you'll review before pre-authorizing.

## Notifications and results {#notifications}

When a scheduled task finishes, the result appears in the sidebar with an **unread dot**, just like any other conversation. Open it to:

- Review the output.
- Ask follow-up questions.
- Jump to the **associated chat** if you want to refine the prompt for the next run.

## Managing your schedules {#managing-schedules}

From the `Scheduled` page, you can change a scheduled task at any time:

- **Edit**: update the prompt, frequency, or next run date.
- **Pause**: stop future runs without losing the schedule. Resume it later.
- **Delete**: remove the schedule permanently. Past results stay in the conversation history.

## Limits {#limits}

The number of scheduled tasks you can create at the same time depends on your **plan**. If you hit the limit, pause or delete an existing task to free a slot, or upgrade your plan. See [pricing](https://mistral.ai/pricing) for the current numbers.
