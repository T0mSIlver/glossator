---
url: https://docs.mistral.ai/models/deployment/local-deployment/trt
title: TensorRT
breadcrumbs: [Models, Deployment, Self-Deployment]
kind: doc
locale: en
source_path: src/content/en/docs/models/deployment/local-deployment/trt/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# TensorRT

Follow the official TensorRT-LLM documentation to [build the engine](https://github.com/NVIDIA/TensorRT-LLM/tree/main#quick-start).

- For Mistral-7B, you can use the [LLaMA example](https://github.com/NVIDIA/TensorRT-LLM/tree/main/examples/llama#mistral-v01)
- For Mixtral-8X7B, official documentation coming soon...

## Deploying the engine {#deploying-the-engine}

Once the engine is built, it can be deployed using the Triton inference server and its TensorRTLLM backend.

Follow the [official documentation](https://github.com/triton-inference-server/tensorrtllm_backend#using-the-tensorrt-llm-backend).
