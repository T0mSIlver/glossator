---
url: https://docs.mistral.ai/studio/conversations/function-calling
title: Function calling
breadcrumbs: [Studio, Conversations]
kind: doc
locale: en
source_path: src/content/en/docs/studio/conversations/function-calling/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---
# Function calling {#function-calling}

Function calling lets a model request code that the application executes.

## Tool execution loop {#tool-execution-loop}

Define each tool with a name, description, and JSON Schema for its arguments. When the model returns a tool call, validate the arguments and execute the named function in the application. Send the result back as a tool message that carries the original call identifier. The model uses that result when it writes its next response. The API does not run the function and cannot inspect side effects in the application. A model can request several tools in one response, and the client must return a result for each request before continuing. Combine this sequence with the [Conversations API](https://docs.mistral.ai/studio/conversations) to retain the prior messages without resending them.

## Choosing tool mode {#choosing-tool-mode}

The tool choice setting controls whether the model may answer directly, must call one of the supplied tools, or must call a named tool. Automatic mode lets the model decide between text and a tool call. Required mode guarantees a tool call but does not select which definition it uses. Selecting a named tool constrains the choice to that definition. The application must still validate all arguments because generation can produce values outside business rules even when the JSON shape is valid. Use a narrow description when tools have overlapping purposes so the model can distinguish them.
