---
url: https://docs.mistral.ai/studio-api/conversations/structured-output
title: Structured Output
breadcrumbs: [Studio, Conversations]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/conversations/structured-output/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Structured Outputs

When utilizing LLMs as agents or steps within a lengthy process, chain, or pipeline, it is often necessary for the outputs to adhere to a specific structured format. JSON is the most commonly used format for this purpose.

> **Tip**
>
> Before continuing, we recommend reading the [Chat Completions](https://docs.mistral.ai/studio-api/conversations/chat-completion) documentation to learn more about the chat completions API and how to use it before proceeding.

We offer a reliable method to obtain structured output in your desired format.

Our system includes a built-in mode for JSON output, along with the capability to use custom structured outputs.

> **Warning**
>
> For JSON mode, it is essential to explicitly instruct the model in your prompt to output JSON and specify the desired format.
>
> Custom structured outputs are more reliable and are recommended whenever possible. However, it is still advisable to iterate on your prompts.
> Use JSON mode when more flexibility in the output is required while maintaining a JSON structure, and customize it if you want to enforce a clearer format to improve reliability.

## Structured Outputs Available {#structured-outputs}

- [Custom](https://docs.mistral.ai/studio-api/conversations/structured-output/custom): Use your own schema to enforce a specific format.
- [JSON](https://docs.mistral.ai/studio-api/conversations/structured-output/json_mode): To enforce a JSON output.
