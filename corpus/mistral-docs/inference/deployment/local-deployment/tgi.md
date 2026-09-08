---
url: https://docs.mistral.ai/inference/deployment/local-deployment/tgi
title: TGI
breadcrumbs: [Inference, Deployment, Self-Deployment]
kind: doc
locale: en
source_path: src/content/en/docs/inference/deployment/local-deployment/tgi/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
hidden: true
---

# Text Generation Inference

Text Generation Inference (TGI) is a toolkit for deploying and serving Large Language Models (LLMs). TGI enables high-performance text generation for the most popular open-access LLMs. Among other features, it has quantization, tensor parallelism, token streaming, continuous batching, flash attention, guidance, and more.
The easiest way of getting started with TGI is using the official Docker container.

## Deploying {#deploying}

**Mistral-7B**

```bash
model=mistralai/Mistral-7B-Instruct-v0.3
```

**Mixtral-8X7B**

```bash
model=mistralai/Mixtral-8x7B-Instruct-v0.1
```

**Mixtral-8X22B**

```bash
model=mistralai/Mixtral-8x22B-Instruct-v0.1
```

```bash
volume=$PWD/data # share a volume with the Docker container to avoid downloading weights every run
docker run --gpus all --shm-size 1g -p 8080:80 -v $volume:/data  \
    -e HUGGING_FACE_HUB_TOKEN=$HUGGING_FACE_HUB_TOKEN \
    ghcr.io/huggingface/text-generation-inference:2.0.3 \
    --model-id $model
```

This will spawn a TGI instance exposing an OpenAI-like API, as documented in the [API section](https://docs.mistral.ai/api).
Make sure to set the `HUGGING_FACE_HUB_TOKEN` environment variable to your [Hugging Face user access token](https://huggingface.co/docs/hub/security-tokens). To use Mistral models, you must first visit the corresponding model page and fill out the small form. You then automatically get access to the model.
If the model does not fit in your GPU, you can also use quantization methods (AWQ, GPTQ, etc.). You can find all TGI launch options at [their documentation](https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/launcher).

## Using the API {#using-the-api}

### With Chat-Compatible Endpoint {#chat-compatible-endpoint}

TGI supports the [Messages API](https://huggingface.co/docs/text-generation-inference/en/messages_api), which is compatible with Mistral and OpenAI Chat Completion API.

**Using MistralClient**

```python
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# Initialize the client but point it to TGI
client = MistralClient(api_key="-", endpoint="http://127.0.0.1:8080")
chat_response = client.chat(
    model="-",
    messages=[
      ChatMessage(role="user", content="What is the best French cheese?")
    ]
)
print(chat_response.choices[0].message.content)
```

**Using OpenAI Client**

```python
from openai import OpenAI

# Initialize the client but point it to TGI
client = OpenAI(api_key="-", base_url="http://127.0.0.1:8080/v1")
chat_response = client.chat.completions.create(
    model="-",
    messages=[
      {"role": "user", "content": "What is deep learning?"}
    ]
)
print(chat_response)
```

**Using cURL**

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
    -X POST \
    -d '{
  "model": "tgi",
  "messages": [
    {
      "role": "user",
      "content": "What is deep learning?"
    }
  ]
}' \
    -H 'Content-Type: application/json'
```

### Using a Generate Endpoint {#generate-endpoint}

If you want more control over what you send to the server, you can use the `generate` endpoint. In this case, you're responsible for formatting the prompt with the correct template and stop tokens.

**Using Python**

```python
# Make sure to install the huggingface_hub package before
from huggingface_hub import InferenceClient

client = InferenceClient(model="http://127.0.0.1:8080")
client.text_generation(prompt="What is Deep Learning?")
```

**Using JavaScript**

```typescript
async function query() {
  const response = await fetch('http://127.0.0.1:8080/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      inputs: 'What is Deep Learning?',
    }),
  });
  return response.json();
}

query().then(response => {
  console.log(response);
});
```

**Using cURL**

```bash
curl 127.0.0.1:8080/generate \
-X POST \
-d '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":20}}' \
-H 'Content-Type: application/json'
```
