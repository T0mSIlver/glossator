---
url: https://docs.mistral.ai/deployment/self-deployment
title: Self-deployment
breadcrumbs:
  - Deployment
  - Self-deployment
kind: doc
locale: en
source_path: src/content/en/docs/deployment/self-deployment/page.mdx
source_commit: 2e094f7
---

# Self-deployment

Open-weight Mistral models can run on your own hardware. This page covers serving
them with vLLM, which is the configuration we test against.

Self-deployment is the right choice when data residency, network isolation or
sustained high volume make the API impractical. It is the wrong choice when your
volume is bursty: an idle GPU costs the same as a busy one.

## Hardware {#hardware}

Memory is the binding constraint. A rough figure for weights alone is two bytes
per parameter at bf16, before the KV cache, which grows with context length and
batch size.

| Model | Parameters | Minimum GPU memory | Tested configuration |
| --- | --- | --- | --- |
| Ministral 3 8B | 8B | 24 GB | 1x A10G |
| Mistral Small 4 | 24B | 60 GB | 1x H100 |
| Mistral NeMo | 12B | 32 GB | 1x A100 40GB |
| Codestral Mamba | 7B | 24 GB | 1x A10G |

Quantisation to fp8 roughly halves the weight memory at a small quality cost, and
is usually the difference between fitting a model on one card and needing two.

## Serving with vLLM {#serving-with-vllm}

Install vLLM and start an OpenAI-compatible server. The API surface matches the
hosted one closely enough that a client can be pointed at it by changing the base
URL alone.

```bash
pip install vllm

vllm serve mistralai/Ministral-3-8B-Instruct \
  --tokenizer-mode mistral \
  --config-format mistral \
  --load-format mistral \
  --max-model-len 32768
```

The three `mistral` format flags matter. Without them vLLM applies a HuggingFace
chat template that does not match the model's own tokenizer, and the model answers
noticeably worse for reasons that are hard to see from the output.

### Function calling

Tool calls need a parser so that vLLM can turn the model's raw output into the
structured `tool_calls` field a client expects:

```bash
vllm serve mistralai/Ministral-3-8B-Instruct \
  --tokenizer-mode mistral \
  --config-format mistral \
  --load-format mistral \
  --enable-auto-tool-choice \
  --tool-call-parser mistral
```

Without `--enable-auto-tool-choice`, tool calls come back as text in the content
field and every client that reads `tool_calls` sees an empty list.

### Context length and the KV cache

`--max-model-len` sets the context window the server advertises. Set it to what
you actually need: the KV cache is preallocated from what is left after the
weights, so an unnecessarily long context reduces the number of concurrent
requests the server can hold.

If startup fails with an out-of-memory error while allocating the cache, lower
`--max-model-len` before reaching for `--gpu-memory-utilization`.

## Verifying the deployment {#verifying-the-deployment}

Send one request and compare it against the same prompt on the hosted API. A
mismatch in the chat template shows up as a subtly worse answer rather than as an
error, so a smoke test that only checks for HTTP 200 will not catch it.

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistralai/Ministral-3-8B-Instruct",
    "messages": [{"role": "user", "content": "Reply with the single word OK."}]
  }'
```

## Observability {#observability}

vLLM exposes Prometheus metrics on `/metrics`. The four worth alerting on are
time to first token, time per output token, the number of running requests, and
the KV cache utilisation. A cache that sits near 100% means requests are being
preempted and latency will be erratic.
