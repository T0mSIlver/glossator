---
url: https://docs.mistral.ai/resources/observability-integrations
title: Observability integrations
breadcrumbs: [Resources]
kind: doc
locale: en
source_path: src/content/en/docs/resources/observability-integrations/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Observability integrations

Observability helps you understand how model calls behave across prompts, tools, retrieval steps, and application workflows. Use this page to choose what to monitor and where to find third-party integrations for Mistral applications.

## What to monitor {#what-to-monitor}

A large language model (LLM) application can include one model call or many calls across agents, retrieval systems, and tools. Start by collecting enough context to debug user-facing behavior and compare changes over time.

Track these areas first:

- **Inputs:** prompt templates, user messages, retrieved context, tool inputs, and memory used by the request.
- **Model configuration:** model identifier, sampling parameters, tool configuration, and any application-specific options.
- **Outputs:** generated text, tool calls, structured output, citations, and formatting decisions.
- **Runtime signals:** latency, token usage, cost, errors, retries, and status codes.
- **Quality signals:** evaluations, human feedback, annotations, and regression datasets.

## Workflow patterns to trace {#workflow-patterns}

Trace each step that can change the final answer. For retrieval-augmented generation (RAG), trace document retrieval, ranking, context assembly, and generation. For agent workflows, trace each model call, tool call, handoff, retry, and final response.

These traces help you answer operational questions:

- Which prompt, model, or tool version produced the response?
- Which retrieved documents influenced the answer?
- Where did latency or cost increase?
- Which step returned an error or unexpected output?
- Which examples should become evaluation data?

## Integration options {#integration-options}

Mistral works with several observability tools through SDK integrations, OpenTelemetry, and cookbook examples. Choose the tool that fits your stack and operational needs.

- [LangSmith](https://github.com/mistralai/cookbook/tree/main/third_party/langchain) — Trace LangChain applications that call Mistral models.

- [Langfuse](https://langfuse.com/docs/integrations/mistral-sdk) — Trace Mistral SDK calls and inspect prompts, outputs, metadata, and evaluations.

- [Arize Phoenix](https://docs.arize.com/phoenix/tracing/integrations-tracing/mistralai) — Trace chat completions, agents, tool calls, and RAG pipelines with Phoenix.

- [Weights and Biases Weave](https://weave-docs.wandb.ai/guides/integrations/mistral/) — Monitor Mistral calls, inputs, outputs, errors, and evaluation metrics.

- [MLflow](https://github.com/mistralai/cookbook/tree/main/third_party/MLflow) — Use MLflow tracing for Mistral chat and embedding calls.

- [phospho](https://github.com/mistralai/cookbook/tree/main/third_party/phospho) — Analyze user messages and feedback from Mistral-powered applications.

## Cookbook examples {#cookbook-examples}

Use the Mistral cookbook when you want implementation examples instead of product-specific setup pages:

- [LangChain examples](https://github.com/mistralai/cookbook/tree/main/third_party/langchain)
- [Phoenix tracing example](https://github.com/mistralai/cookbook/blob/main/third_party/Phoenix/arize_phoenix_tracing.ipynb)
- [Weights and Biases examples](https://github.com/mistralai/cookbook/tree/main/third_party/wandb)
- [MLflow tracing example](https://github.com/mistralai/cookbook/blob/main/third_party/MLflow/mistral-mlflow-tracing.ipynb)
- [phospho examples](https://github.com/mistralai/cookbook/tree/main/third_party/phospho)

## Next steps {#next-steps}

After you choose an observability tool, define the events that matter for your application. We recommend starting with model inputs, model outputs, tool calls, latency, token usage, and errors. Add evaluation datasets and user feedback after the basic traces are reliable.
