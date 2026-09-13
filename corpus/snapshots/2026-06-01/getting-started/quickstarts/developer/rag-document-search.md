---
url: https://docs.mistral.ai/getting-started/quickstarts/developer/rag-document-search
title: Set up RAG with document search
breadcrumbs: [Getting started, Quickstarts, Developer]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/developer/rag-document-search/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Set up RAG with document search

Upload documents to a Library and query them in a chat completion.

- Create a Library and upload a file
- The model retrieves relevant passages from your documents
- Answers are grounded in your content instead of general knowledge

**Time to complete:** ~10 minutes

## Prerequisites {#prerequisites}

- A Mistral API key (see [Get your API key](https://docs.mistral.ai/getting-started/quickstarts/developer/first-api-request#step-1) if you don't have one yet)
- Python 3.9+ or Node.js 18+ installed
- The Mistral SDK installed (see [Install the SDK](https://docs.mistral.ai/getting-started/quickstarts/developer/first-api-request#step-2) if you haven't yet)
- A document to upload (PDF, TXT, or DOCX)

## Step 1: Create a Library {#step-1}

A Library is a container for documents that the model can search during conversations.

**Python**

```python
import os
from mistralai import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# Create a library
library = client.files.upload(
    file=open("company-handbook.pdf", "rb"),
    purpose="retrieval",
)
print(f"File uploaded: {library.id}")
```

**TypeScript**

```typescript
import { Mistral } from '@mistralai/mistralai';
import fs from 'fs';

const client = new Mistral({ apiKey: process.env.MISTRAL_API_KEY });

const library = await client.files.upload({
  file: fs.createReadStream('company-handbook.pdf'),
  purpose: 'retrieval',
});
console.log(`File uploaded: ${library.id}`);
```

**cURL**

```bash
curl https://api.mistral.ai/v1/files \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -F "file=@company-handbook.pdf" \
  -F "purpose=retrieval"
```

## Step 2: Wait for processing {#step-2}

We process and index the document for retrieval. Check the status before querying.

**Python**

```python
import time

# Wait for the file to be processed
while True:
    file_info = client.files.retrieve(file_id=library.id)
    if file_info.status == "processed":
        print("File ready for retrieval")
        break
    print(f"Status: {file_info.status}... waiting")
    time.sleep(2)
```

**TypeScript**

```typescript
// Wait for the file to be processed
let fileInfo = await client.files.retrieve({ fileId: library.id });
while (fileInfo.status !== 'processed') {
  console.log(`Status: ${fileInfo.status}... waiting`);
  await new Promise((r) => setTimeout(r, 2000));
  fileInfo = await client.files.retrieve({ fileId: library.id });
}
console.log('File ready for retrieval');
```

We typically process small files (under 10 pages) in under 30 seconds. Larger documents may take a few minutes.

## Step 3: Query with RAG {#step-3}

Ask a question and include the file reference so the model retrieves relevant passages before answering.

**Python**

```python
response = client.chat.complete(
    model="mistral-medium-latest",
    messages=[
        {
            "role": "user",
            "content": "What is our company's remote work policy?",
        }
    ],
    documents=[{"type": "file", "id": library.id}],
)

print(response.choices[0].message.content)
```

**TypeScript**

```typescript
const response = await client.chat.complete({
  model: 'mistral-medium-latest',
  messages: [
    {
      role: 'user',
      content: "What is our company's remote work policy?",
    },
  ],
  documents: [{ type: 'file', id: library.id }],
});

console.log(response.choices[0].message.content);
```

## Step 4: Verify {#verify}

The response should reference information from your uploaded document instead of general knowledge. For example, if you uploaded a company handbook and asked about remote work policy, you should see specific details like:

> "According to the handbook, employees may work remotely up to 3 days per week with manager approval. Remote work requests must be submitted through the HR portal..."

Look for:

- Specific details, names, or policies from your document
- Answers grounded in the uploaded content rather than generic advice
- Reduced hallucination compared to the same question without documents

If the response seems generic, confirm the file status is `processed` and that the `documents` parameter is included in your request.

## What's next {#whats-next}

- [All developer quickstarts](https://docs.mistral.ai/#quickstarts)

- [Platform overview](https://docs.mistral.ai/getting-started/platform-overview)
