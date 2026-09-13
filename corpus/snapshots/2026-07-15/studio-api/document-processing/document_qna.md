---
url: https://docs.mistral.ai/studio-api/document-processing/document_qna
title: Document QnA
breadcrumbs: [Studio, Document AI]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/document-processing/document_qna/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Document AI QnA

The Document QnA capability combines OCR with large language model capabilities to enable natural language interaction with document content. This allows you to extract information and insights from documents by asking questions in natural language.

> **Tip**
>
> Before continuing, we recommend reading the [Chat Completions](https://docs.mistral.ai/studio-api/conversations/chat-completion) documentation to learn more about the chat completions API and how to use it before proceeding.

## Before You Start {#before-you-start}

### Workflow and Capabilities

The workflow consists of two main steps:

![Document QnA Graph](https://docs.mistral.ai/img/document_qna.png)

1. Document AI: OCR extracts text, structure, and formatting, creating a machine-readable version of the document.

2. Language Model Understanding: The extracted document content is analyzed by a large language model. You can ask questions or request information in natural language. The model understands context and relationships within the document and can provide relevant answers based on the document content.

### Key Capabilities {#workflow-key-capabilities}

- Question answering about specific document content
- Information extraction and summarization
- Document analysis and insights
- Multi-document queries and comparisons
- Context-aware responses that consider the full document

### Common Use Cases {#common-use-cases}

- Analyzing research papers and technical documents
- Extracting information from business documents
- Processing legal documents and contracts
- Building document Q&A applications
- Automating document-based workflows

## Usage {#usage}

### Leverage Document QnA

The examples below show how to interact with a PDF document using natural language.

**QnA with a PDF Url**

Be sure the URL is **public** and accessible by our API.

**Python**

**V1**

```python
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-small-latest"

client = Mistral(api_key=api_key)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "what is the last sentence in the document"
            },
            {
                "type": "document_url",
                "document_url": "https://arxiv.org/pdf/1805.04770"
            }
        ]
    }
]

chat_response = client.chat.complete(
    model=model,
    messages=messages
)
```

**V2**

```python
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-small-latest"

client = Mistral(api_key=api_key)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "what is the last sentence in the document"
            },
            {
                "type": "document_url",
                "document_url": "https://arxiv.org/pdf/1805.04770"
            }
        ]
    }
]

chat_response = client.chat.complete(
    model=model,
    messages=messages
)
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const apiKey = process.env["MISTRAL_API_KEY"];

const client = new Mistral({
  apiKey: apiKey,
});

const chatResponse = await client.chat.complete({
  model: "mistral-small-latest",
  messages: [
    {
      role: "user",
      content: [
        {
          type: "text",
          text: "what is the last sentence in the document",
        },
        {
          type: "document_url",
          documentUrl: "https://arxiv.org/pdf/1805.04770",
        },
      ],
    },
  ],
});
```

**cURL**

```bash
curl https://api.mistral.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MISTRAL_API_KEY}" \
  -d '{
    "model": "mistral-small-latest",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "what is the last sentence in the document"
          },
          {
            "type": "document_url",
            "document_url": "https://arxiv.org/pdf/1805.04770"
          }
        ]
      }
    ]
  }'
```

**Output**

```json
{
  "id": "7b98be65bb7b475ca2456a92f9ed0049",
  "created": 1756753708,
  "model": "mistral-small-latest",
  "usage": {
    "prompt_tokens": 13707,
    "total_tokens": 13764,
    "completion_tokens": 57
  },
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "tool_calls": null,
        "content": "The last sentence in the document is:\n\n\"Zaremba, W., Sutskever, I., and Vinyals, O. Recurrent neural network regularization. arXiv:1409.2329, 2014.\""
      }
    }
  ]
}
```

**QnA with a Base64 Encoded PDF**

You can perform QnA with any PDF by encoding them in base64 and sending them as part of the chat completion request.

**Python**

**V1**

```python
import base64
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-small-latest"

client = Mistral(api_key=api_key)

def encode_pdf(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

pdf_path = "path_to_your_pdf.pdf"
base64_pdf = encode_pdf(pdf_path)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "what is the last sentence in the document"
            },
            {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{base64_pdf}"
            }
        ]
    }
]

chat_response = client.chat.complete(
    model=model,
    messages=messages
)
```

**V2**

```python
import base64
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-small-latest"

client = Mistral(api_key=api_key)

def encode_pdf(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

pdf_path = "path_to_your_pdf.pdf"
base64_pdf = encode_pdf(pdf_path)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "what is the last sentence in the document"
            },
            {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{base64_pdf}"
            }
        ]
    }
]

chat_response = client.chat.complete(
    model=model,
    messages=messages
)
```

**TypeScript**

```typescript
import { Mistral } from '@mistralai/mistralai';
import fs from 'fs';

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({ apiKey: apiKey });

async function encodePdf(pdfPath) {
    const pdfBuffer = fs.readFileSync(pdfPath);
    const base64Pdf = pdfBuffer.toString('base64');
    return base64Pdf;
}

const pdfPath = "path_to_your_pdf.pdf";
const base64Pdf = await encodePdf(pdfPath);

const chatResponse = await client.chat.complete({
  model: "mistral-small-latest",
  messages: [
    {
      role: "user",
      content: [
        {
          type: "text",
          text: "what is the last sentence in the document",
        },
        {
          type: "document_url",
          documentUrl: "data:application/pdf;base64," + base64Pdf,
        },
      ],
    },
  ],
});
```

**cURL**

```bash
curl https://api.mistral.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MISTRAL_API_KEY}" \
  -d '{
    "model": "mistral-small-latest",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "what is the last sentence in the document"
          },
          {
            "type": "document_url",
            "document_url": "data:application/pdf;base64,<base64_pdf>"
          }
        ]
      }
    ]
  }'
```

**Output**

```json
{
  "id": "7b98be65bb7b475ca2456a92f9ed0049",
  "created": 1756753708,
  "model": "mistral-small-latest",
  "usage": {
    "prompt_tokens": 13707,
    "total_tokens": 13764,
    "completion_tokens": 57
  },
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "tool_calls": null,
        "content": "The last sentence in the document is:\n\n\"Zaremba, W., Sutskever, I., and Vinyals, O. Recurrent neural network regularization. arXiv:1409.2329, 2014.\""
      }
    }
  ]
}
```

**QnA with an Uploaded PDF**

You can also upload a PDF file in our Cloud and get the QnA results from the uploaded PDF by retrieving a signed url. Document QnA is under the umbrela OCR, the method for uploading and handling files will hence be the same.

### Upload a File

First, you will have to upload your PDF file to our cloud, this file will be stored and only accessible via an API key.

**Python**

**V1**

```python
from mistralai.client import Mistral
import os

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

uploaded_pdf = client.files.upload(
    file={
        "file_name": "2201.04234v3.pdf",
        "content": open("2201.04234v3.pdf", "rb"),
    },
    purpose="ocr"
)
```

**V2**

```python
from mistralai.client import Mistral
import os

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

uploaded_pdf = client.files.upload(
    file={
        "file_name": "2201.04234v3.pdf",
        "content": open("2201.04234v3.pdf", "rb"),
    },
    purpose="ocr"
)
```

**TypeScript**

```typescript
import { Mistral } from '@mistralai/mistralai';
import fs from 'fs';

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({apiKey: apiKey});

const uploadedFile = fs.readFileSync('2201.04234v3.pdf');
const uploadedPdf = await client.files.upload({
    file: {
        fileName: "2201.04234v3.pdf",
        content: uploadedFile,
    },
    purpose: "ocr"
});
```

**cURL**

```bash
curl https://api.mistral.ai/v1/files \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -F purpose="ocr" \
  -F file="@2201.04234v3.pdf"
```

**Output**

```json
{
  "id": "9a90b93c-0e7d-4dd7-8520-07d051404d11",
  "object": "file",
  "bytes": 560027,
  "created_at": 1756754478,
  "filename": "1805.04770v2.pdf",
  "purpose": "ocr",
  "sample_type": "ocr_input",
  "num_lines": 0,
  "mimetype": "application/pdf",
  "source": "upload",
  "signature": "..."
}
```

### Retrieve File

Once the file uploaded, you can retrieve it at any point.

**Python**

```python
retrieved_file = client.files.retrieve(file_id=uploaded_pdf.id)
```

**TypeScript**

```typescript
const retrievedFile = await client.files.retrieve({
    fileId: uploadedPdf.id
});
```

**cURL**

```bash
curl -X GET "https://api.mistral.ai/v1/files/$id" \
     -H "Accept: application/json" \
     -H "Authorization: Bearer $MISTRAL_API_KEY"
```

**Output**

```json
{
  "id": "9a90b93c-0e7d-4dd7-8520-07d051404d11",
  "object": "file",
  "bytes": 560027,
  "created_at": 1756754478,
  "filename": "1805.04770v2.pdf",
  "purpose": "ocr",
  "sample_type": "ocr_input",
  "num_lines": 0,
  "mimetype": "application/pdf",
  "source": "upload",
  "signature": "...",
  "deleted": false
}
```

### Get Signed Url

For QnA with Documents, you can get a signed url to access the file. An optional `expiry` parameter allow you to automatically expire the signed url after n hours.

**Python**

```python
signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
```

**TypeScript**

```typescript
const signedUrl = await client.files.getSignedUrl({
    fileId: uploadedPdf.id,
});
```

**cURL**

```bash
curl -X GET "https://api.mistral.ai/v1/files/$id/url?expiry=24" \
     -H "Accept: application/json" \
     -H "Authorization: Bearer $MISTRAL_API_KEY"
```

**Output**

```json
{
  "url": "https://mistralaifilesapiprodswe.blob.core.windows.net/fine-tune/.../.../9a90b93c0e7d4dd7852007d051404d11.pdf?se=2025-09-02T19%3A22%3A08Z&sp=r&sv=2025-01-05&sr=b&sig=..."
}
```

### Get Chat Completion Result

You can now query any LLM with the signed url.

**Python**

```python
model =  "mistral-small-latest"

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "what is the last sentence in the document"
            },
            {
                "type": "document_url",
                "document_url": signed_url.url
            }
        ]
    }
]

chat_response = client.chat.complete(
    model=model,
    messages=messages
)
```

**TypeScript**

```typescript
const chatResponse = await client.chat.complete({
  model: "mistral-small-latest",
  messages: [
    {
      role: "user",
      content: [
        {
          type: "text",
          text: "what is the last sentence in the document",
        },
        {
          type: "document_url",
          documentUrl: signedUrl.url,
        },
      ],
    },
  ],
});
```

**cURL**

```bash
curl https://api.mistral.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MISTRAL_API_KEY}" \
  -d '{
    "model": "mistral-small-latest",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "what is the last sentence in the document"
          },
          {
            "type": "document_url",
            "document_url": "https://mistralaifilesapiprodswe.blob.core.windows.net/fine-tune/.../.../22e2e88f167d4f3d982aadd977a54ec3.pdf?se=2025-08-30T10%3A53%3A22Z&sp=r&sv=2025-01-05&sr=b&sig=..."
          }
        ]
      }
    ]
  }'
```

**Output**

```json
{
  "id": "4ccfdc97996241eb9fe4375d947c671b",
  "created": 1756754528,
  "model": "mistral-small-latest",
  "usage": {
    "prompt_tokens": 13707,
    "total_tokens": 13764,
    "completion_tokens": 57
  },
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "tool_calls": null,
        "content": "The last sentence in the document is:\n\n\"Zaremba, W., Sutskever, I., and Vinyals, O. Recurrent neural network regularization. arXiv:1409.2329, 2014.\""
      }
    }
  ]
}
```

### Delete File

Once everything done, you can optionally delete the pdf file from our cloud unless you wish to reuse it later.

**Python**

```python
client.files.delete(file_id=file.id)
```

**TypeScript**

```typescript
await client.files.delete(fileId=file.id);
```

**cURL**

```bash
curl -X DELETE https://api.mistral.ai/v1/files/${file_id} \
-H "Authorization: Bearer ${MISTRAL_API_KEY}"
```

**Output**

```json
{
  "id": "9a90b93c-0e7d-4dd7-8520-07d051404d11",
  "object": "file",
  "deleted": true
}
```

## Cookbooks {#cookbooks}

For more information on how to make use of Document QnA, we have the following [Document QnA Cookbook](https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/ocr/document_understanding.ipynb) with a simple example.

### Are there any limits regarding the Document QnA API? {#are-there-any-limits-regarding-the-document-qna-api}

Yes, there are certain limitations for the Document QnA API. Uploaded document files must not exceed 50 MB in size and should be no longer than 1,000 pages.
