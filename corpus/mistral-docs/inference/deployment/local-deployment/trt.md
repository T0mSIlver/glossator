---
url: https://docs.mistral.ai/inference/deployment/local-deployment/trt
title: TensorRT
breadcrumbs: [Inference, Deployment, Self-Deployment]
kind: doc
locale: en
source_path: src/content/en/docs/inference/deployment/local-deployment/trt/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
hidden: true
---

# TensorRT

Follow the official TensorRT-LLM documentation to [build the engine](https://github.com/NVIDIA/TensorRT-LLM/tree/main#quick-start).

- For Mistral-7B, you can use the [LLaMA example](https://github.com/NVIDIA/TensorRT-LLM/tree/main/examples/llama#mistral-v01)
- For Mixtral-8X7B, official documentation coming soon...

## Deploying the engine {#deploying-the-engine}

Once the engine is built, it can be deployed using the Triton inference server and its TensorRTLLM backend.

Follow the [official documentation](https://github.com/triton-inference-server/tensorrtllm_backend#using-the-tensorrt-llm-backend).
