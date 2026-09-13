---
url: https://docs.mistral.ai/models/deployment/local-deployment
title: Self-Deployment
breadcrumbs: [Models, Deployment]
kind: doc
locale: en
source_path: src/content/en/docs/models/deployment/local-deployment/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Self-Deployment

Mistral AI models can be **self-deployed on your own infrastructure** through various
inference engines. We recommend using [vLLM](https://vllm.readthedocs.io/), a
highly-optimized Python-only serving framework which can expose an OpenAI-compatible
API.

Other inference engine alternatives include
[TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) and
[TGI](https://huggingface.co/docs/text-generation-inference/index).

You can also leverage specific tools to facilitate infrastructure management, such as
[SkyPilot](https://skypilot.readthedocs.io) or [Cerebrium](https://www.cerebrium.ai).

> **Tip**
>
> For full-stack enterprise deployment, from efficient model inference to team management, we recommend [reaching out to us](https://mistral.ai/contact).
