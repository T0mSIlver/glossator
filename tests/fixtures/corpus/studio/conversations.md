---
url: https://docs.mistral.ai/studio/conversations
title: Conversations API
breadcrumbs: [Studio, Conversations]
kind: doc
locale: en
source_path: src/content/en/docs/studio/conversations/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---
# Conversations API {#conversations-api}

The Conversations API persists a sequence of messages and tool calls.

## Reusing conversation state {#reusing-conversation-state}

Create a conversation once, then send its conversation identifier with each later request. The service retains the earlier messages and tool results, so clients do not need to submit the full transcript again. A response includes the identifier needed for the next turn. Applications should store that identifier with their own user session. To branch from an earlier state, create another conversation instead of changing completed entries. Conversation state is separate from local UI history and remains available to another process that has the same credentials and identifier. See [Function calling](https://docs.mistral.ai/studio/conversations/function-calling) for the tool-result sequence.

### Supplying new inputs {#supplying-new-inputs}

New inputs may contain text, images, or tool results. Tool results must name the call identifier returned by the assistant, which lets the service associate an external function result with the pending call. Submit every requested tool result before asking the model to continue. The continued response becomes part of the same conversation and can issue another tool call. The API rejects a tool result whose call identifier is not pending in that conversation. Clients can attach metadata to their own session, but that metadata is not inserted into the model context.
