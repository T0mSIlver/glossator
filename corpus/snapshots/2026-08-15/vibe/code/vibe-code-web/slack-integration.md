---
url: https://docs.mistral.ai/vibe/code/vibe-code-web/slack-integration
title: 'Vibe Code Web for Slack: Quickstart'
breadcrumbs: [Vibe, Code, Vibe Code Web]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/vibe-code-web/slack-integration/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Vibe Code Web for Slack: Quickstart

> **Info**
>
> **AI-generated content:** This app uses AI to generate responses and code. Outputs may be inaccurate, incomplete, or misleading. Do not rely on them as factual, legal, medical, financial, or professional advice. Always verify important information independently. See our [privacy policy](https://mistral.ai/terms#privacy-policy).

Vibe Code Web for Slack lets your team start remote AI coding sessions directly from a Slack thread. The agent reads the thread context, works in an isolated cloud sandbox, and opens a GitHub pull request — without leaving Slack.

[Connect Slack to your Mistral Organization](https://admin.mistral.ai/organization/connectors)

Use this guide after the Vibe Code Web Slack app has been installed and connected to your Vibe account and GitHub repositories.

## Configuration {#configuration}

> **Warning**
>
> You need to be an admin of your Mistral Organization to configure the Slack integration.

1. Open [**Admin Settings**](https://admin.mistral.ai/organization/connectors)
2. **Make sure you are in the right Mistral organization.** Your Mistral organization can only be connected to a single Slack Workspace.
3. In **App Connections** section, click **Connect to Slack**.
4. Complete the OAuth flow to finalise the connection. If you are not an owner of your Slack workspace, you may need to request app installation from a workspace owner.
5. **Mistral Vibe** is now installed in your Slack workspace. You can now [connect to Slack MCP](https://docs.mistral.ai/vibe/code/vibe-code-web/slack-integration#slack-mcp-usage) or [start your first session](https://docs.mistral.ai/vibe/code/vibe-code-web/slack-integration#start-first-session).

## Use Slack MCP {#slack-mcp-usage}

Once Slack App is installed to your Slack workspace, please follow these instructions:

1. Open [**Vibe Work**](https://chat.mistral.ai/connections)
2. Click on **Slack Connector**, then click **Connect**
3. Complete OAuth flow to connect to the right Slack workspace you have
4. Click on [**New Chat**](https://chat.mistral.ai/chat?integrations=019cfb41-5e8a-7350-b162-b2b80604fe5a)
5. Enjoy playing with Slack!

## What you can do from Slack {#what-you-can-do}

> **Warning**
>
> This feature is in progressive rollout. It will be available soon, stay tuned...

Vibe Code Web lets you start a remote coding session from the context already in a Slack thread. The agent uses the thread context, works in an isolated cloud sandbox, and creates a linked Vibe Code Web session. The coding agent can create a pull request for review.

Use Slack when the coding task starts from:

- an incident or on-call thread
- a CI or alert notification
- a customer or support escalation
- a product or engineering discussion
- a code review discussion summarized in Slack
- a small implementation decision already agreed in-thread

## Start your first session {#start-first-session}

1. **Find a Slack thread with enough context for the coding task.** Good context includes:
   - the repository or project name
   - the bug, failing test, or desired behavior
   - links to logs, PRs, issues, or screenshots
   - constraints, such as _"keep the API unchanged"_ or _"only touch docs"_
2. **Mention the Vibe Code app in the thread.**

   ```text
   @Vibe investigate the issue described in this thread and open a PR if there is a clear fix.
   ```

3. **If Vibe needs more information, answer in the thread.** Common clarification questions:
   - Which repository should I use?
   - Which branch should I target?
   - Should I open a PR or only investigate?
   - Is this safe to change, or should I produce a summary first?
4. **Open the Vibe Code Web session link posted by the app.** Use the web session to inspect progress, command output, steer the agent, and review the resulting GitHub branch or pull request.
5. **Review the final code in GitHub.** GitHub remains the source of truth for code review, required checks, comments, approvals, and merge decisions.

## Good first prompts {#good-first-prompts}

Use prompts that are scoped, actionable, and likely to end in a branch or pull request.

| Use case                           | Slack prompt                                                                                                                                         |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Investigate a failing test**     | `@Vibe investigate the failing test in this thread. If the fix is clear, open a PR with the smallest safe change.`                                   |
| **Fix a customer-reported bug**    | `@Vibe use the customer report above to find the likely bug. Open a PR if you can reproduce or identify a clear fix.`                                |
| **Address an alert**               | `@Vibe investigate this alert and check whether there is a code or config fix. Start with a summary, then open a PR only if the change is low risk.` |
| **Apply an agreed product change** | `@Vibe implement the copy/config change we agreed on above and open a PR.`                                                                           |
| **Add missing test coverage**      | `@Vibe add a regression test for the edge case described in this thread. Keep the implementation unchanged unless the test exposes a bug.`           |
| **Update docs**                    | `@Vibe update the docs based on the behavior described above. Open a PR with the doc-only change.`                                                   |
| **Small refactor**                 | `@Vibe refactor the helper discussed above. Keep behavior unchanged and run the relevant tests before opening a PR.`                                 |

## Prompt template {#prompt-template}

For best results, include the repo, the desired outcome, and the review boundary.

```text
@Vibe [task]

Repo/project: [repo name]
Goal: [what should change]
Constraints: [what not to change]
Validation: [test/check to run if known]
Output: open a PR / investigate only / summarize first
```

Example:

```text
@Vibe fix the settings persistence bug described above.

Repo/project: web-app
Goal: the alerts toggle should still be enabled after refresh.
Constraints: do not change the API shape.
Validation: run the settings tests if available.
Output: open a PR if the fix is clear; otherwise summarize what you found.
```

## What happens next {#what-happens-next}

After you mention Vibe Code:

1. The app reads the Slack thread context.
2. It maps the request to a Vibe Code Web project and GitHub repository.
3. If the repository is ambiguous, it asks you to choose.
4. It creates a Vibe Code Web session and posts a link back to Slack.
5. The agent works remotely in a managed sandbox.
6. The result is a GitHub branch or pull request, when a code change is appropriate.

## When to use Slack vs Web vs CLI {#slack-vs-web-vs-cli}

| Start from        | Use when                                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| **Slack**         | The context already lives in a Slack thread: incidents, support reports, alerts, or team decisions.           |
| **Vibe Code Web** | You know the repository and want to start a remote task directly.                                             |
| **Vibe CLI**      | You are already working locally, or the task depends on local files, services, secrets, or environment setup. |

## Best practices {#best-practices}

- Start with small, scoped tasks.
- Name the repository or project when possible.
- Say whether you want a pull request or an investigation summary.
- Include the failing test, error message, stack trace, or expected behavior.
- Avoid asking for broad rewrites from Slack.
- Do not paste secrets into Slack or into the agent prompt.
- Review the resulting branch or pull request in GitHub before merging.

## Good Slack tasks {#good-tasks}

Good Slack-started tasks usually:

- have enough thread context
- are tied to a known repo or project
- can run in an isolated sandbox
- can be validated with tests, build output, or code inspection
- end in a GitHub branch, pull request, or investigation summary

## Less ideal Slack tasks {#less-ideal-tasks}

Avoid Slack-triggered sessions for:

- broad architecture changes without a clear owner
- tasks requiring local-only services, secrets, hardware, or private networks
- vague prompts like _"fix this"_ without logs or expected behavior
- cross-owner GitHub work unless the project and repo mapping is clear
- changes that should be manually designed before implementation

## Data & privacy {#data-privacy}

- Vibe Code Web for Slack uses AI to generate code, summaries, and pull requests. Outputs may be inaccurate — always review before merging.
- Slack thread content shared with the app is processed to fulfill your request and is not used to train Mistral models.
- For full details on data handling, retention, and your rights, see the [Mistral privacy policy](https://mistral.ai/terms#privacy-policy) and [trust center](https://trust.mistral.ai/).
