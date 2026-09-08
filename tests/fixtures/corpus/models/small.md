---
url: https://docs.mistral.ai/models/mistral-small-latest
title: Mistral Small
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/mistral-small.ts
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---
# Mistral Small {#mistral-small}

Mistral Small is a general-purpose model for low-latency applications.

## Capabilities {#capabilities}

Mistral Small accepts text input and produces text output. It supports function calling and structured outputs, including JSON responses constrained by a supplied schema. Its context window holds 128,000 tokens. The model can follow tool definitions in chat completion requests but the client remains responsible for executing tools. It supports English, French, German, Spanish, and several other languages. Image input is not supported by this model card. Use the dated model identifier when an application needs a fixed behavior, or the latest alias when accepting automatic upgrades. Capability flags describe API features and do not guarantee that every prompt produces valid business data.

## Deployment identifiers {#deployment-identifiers}

Use mistral-small-latest for the moving alias and mistral-small-2506 for the dated release in this fixture. Both identifiers use the chat completions endpoint. The dated identifier remains stable while the alias may move after a newer compatible release. Record the response model in evaluation artifacts so results can be traced to the resolved version. Serverless availability depends on the account region, and self-deployment uses a separate artifact name. The model card does not promise a fixed requests-per-minute limit because quotas are assigned to each account and deployment tier.
