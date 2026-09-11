data-testid="conversation-layout">
Which API endpoints can a Mistral batch job target, and how many requests can one batch input file hold?
11:50pm
Used Mistral Docs Ca30
Thought for 1s
The user is asking about Mistral batch job API endpoints and the maximum number of requests per batch input file. This is a specific technical question about Mistral's batch processing capabilities. I need to search the Mistral documentation for this information. Let me use the mistral-docs skill to find accurate, up-to-date information about batch jobs.
Read mistral-docs
Thought for 1s
I need to find information about Mistral batch job endpoints and the maximum number of requests per batch input file. Let me search the Mistral documentation for batch job details.
Mistral Docs Ca30 • Mistral Docs Search
Arguments
q
"batch job API endpoints requests per file"
Response
result
q: "batch job API endpoints requests per file"
[1] https://docs.mistral.ai/studio/batch-processing | section: batch-creation/create-a-new-batch-job
 Batch Processing > Batch Creation > Create a new Batch Job
 Create a new batch job, it will be queued for processing. - Requests Data: The data for the requests to be batched. There are two options: - `input_files`: a list of the batch input file IDs, see how to use [file-batching](https://docs.mistral.ai/studio/batch-processing#file-batching). - `requests`: a list of the requests to be batched, see how to use [inline batching](https://docs.mistral.ai/stud …
 cite: https://docs.mistral.ai/studio/batch-processing#batch-creation
 large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/batch-processing", section="batch-creation/create-a-new-batch-job") reads this section
[2] https://docs.mistral.ai/studio/batch-processing | section: an-end-to-end-example
 Batch Processing > An end-to-end example
 ```python import argparse import json import os import random import time from io import BytesIO import httpx from mistralai.client import File, Mistral def create_client(): """ Create a Mistral client using the API key from environment variables. Returns: Mistral: An instance of the Mistral client. """ return Mistral(api_key=os.environ["MISTRAL_API_KEY"]) def generate_random_string(start, end): " …
 cite: https://docs.mistral.ai/studio/batch-processing#an-end-to-end-example
 large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/batch-processing", section="an-end-to-end-example") reads this section
[3] https://docs.mistral.ai/studio/batch-processing | section: whats-the-max-number-of-requests-in-a-batch
 Batch Processing > FAQ > What's the max number of requests in a batch?
 Currently, there is a maximum limit of 1 million pending requests per workspace. This means you cannot submit a job with more than 1 million requests. Additionally, you cannot submit two jobs with 600,000 requests each at the same time. You would need to wait until the first job has processed at least 200,000 requests, reducing its pending count to 400,000. At that point, the new job with 600,000 …
 cite: https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-requests-in-a-batch
 large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/batch-processing", section="whats-the-max-number-of-requests-in-a-batch") reads this section
[4] https://docs.mistral.ai/studio/batch-processing | section: file-batching
 Batch Processing > Batch Creation > File Batching
 The standard batching approach relies on batch files containing all the requests to be processed. We support up to 1 million requests in a single batch, enabling efficient handling of large volumes of requests at a reduced cost. This is ideal for tasks with high throughput requirements but low latency sensitivity or priority. **Python** ```python created_job = client.batch.jobs.create( input_files …
 cite: https://docs.mistral.ai/studio/batch-processing#file-batching
 large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/batch-processing", section="file-batching") reads this section
[5] https://docs.mistral.ai/studio/batch-processing | section: get-batch-job-results
 Batch Processing > Get/Retrieve > Get batch job results
 Once the batch job is completed, download the results. **Python** ```python output_file_stream = client.files.download(file_id=retrieved_job.output_file) # Write and save the file with open('batch_results.jsonl', 'wb') as f: f.write(output_file_stream.read()) ``` **TypeScript** ```typescript import fs from 'fs'; const outputFileStream = await client.files.download({ fileId: retrievedJob.outputFile …
 cite: https://docs.mistral.ai/studio/batch-processing#get-batch-job-results
 large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/batch-processing", section="get-batch-job-results") reads this section
Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/batch-processing", section="batch-creation/create-a-new-batch-job") to read hit 1 on its page
Thought
The search results show that batch processing documentation exists. I can see references to:
Batch creation with input_files and requests
File batching supporting up to 1 million requests
FAQ about max number of requests
I need to read the specific sections to get the exact details about:
Which API endpoints can be targeted
The maximum number of requests per batch input file
Let me read the batch-creation section and file-batching section to get the precise information.
Mistral Docs Ca30 • Mistral Docs Read Page
Arguments
page_url
"https://docs.mistral.ai/studio/batch-processing"
section
"batch-creation/create-a-new-batch-job"
Response
result
page: https://docs.mistral.ai/studio/batch-processing | "Batch Processing" | section: batch-creation/create-a-new-batch-job
## section: batch-creation/create-a-new-batch-job
 Batch Processing > Batch Creation > Create a new Batch Job
 cite: https://docs.mistral.ai/studio/batch-processing#batch-creation
### Create a new Batch Job
Create a new batch job, it will be queued for processing.
- Requests Data: The data for the requests to be batched. There are two options:
 - `input_files`: a list of the batch input file IDs, see how to use [file-batching](https://docs.mistral.ai/studio/batch-processing#file-batching).
 - `requests`: a list of the requests to be batched, see how to use [inline batching](https://docs.mistral.ai/studio/batch-processing#inline-batching).
- `model`: you can only use one model (e.g., `codestral-latest`) per batch. However, you can run multiple batches on the same files with different models if you want to compare outputs.
- `endpoint`: we currently support `/v1/embeddings`, `/v1/chat/completions`, `/v1/fim/completions`, `/v1/moderations`, `/v1/chat/moderations`, `/v1/ocr`, `/v1/classifications`, `/v1/conversations`, `/v1/audio/transcriptions`.
- `metadata`: optional custom metadata for the batch.
Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/batch-processing", section="file-batching") for the section after it
Mistral Docs Ca30 • Mistral Docs Read Page
Arguments
page_url
"https://docs.mistral.ai/studio/batch-processing"
section
"file-batching"
Response
result
page: https://docs.mistral.ai/studio/batch-processing | "Batch Processing" | section: file-batching
## section: file-batching
 Batch Processing > Batch Creation > File Batching
 cite: https://docs.mistral.ai/studio/batch-processing#file-batching
### File Batching {#file-batching}
The standard batching approach relies on batch files containing all the requests to be processed. We support up to 1 million requests in a single batch, enabling efficient handling of large volumes of requests at a reduced cost. This is ideal for tasks with high throughput requirements but low latency sensitivity or priority.
**Python**
```python
created_job = client.batch.jobs.create(
 input_files=[batch_data.id],
 model="mistral-small-latest",
 endpoint="/v1/chat/completions",
 metadata={"job_type": "testing"}
)
```
**TypeScript**
```typescript
const createdJob = await client.batch.jobs.create({
 inputFiles: [batchData.id],
 model: "mistral-small-latest",
 endpoint: "/v1/chat/completions",
 metadata: {jobType: "testing"}
});
```
**cURL**
```bash
curl --location "https://api.mistral.ai/v1/batch/jobs" \
--header "Authorization: Bearer $MISTRAL_API_KEY" \
--header "Content-Type: application/json" \
--header "Accept: application/json" \
--data '{
 "model": "mistral-small-latest",
 "input_files": [
 "<uuid>"
 ],
 "endpoint": "/v1/chat/completions",
 "metadata": {
 "job_type": "testing"
 }
}'
```
Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/batch-processing", section="inline-batching") for the section after it
Mistral Docs Ca30 • Mistral Docs Read Page
Arguments
page_url
"https://docs.mistral.ai/studio/batch-processing"
section
"whats-the-max-number-of-requests-in-a-batch"
Response
result
page: https://docs.mistral.ai/studio/batch-processing | "Batch Processing" | section: whats-the-max-number-of-requests-in-a-batch
## section: whats-the-max-number-of-requests-in-a-batch
 Batch Processing > FAQ > What's the max number of requests in a batch?
 cite: https://docs.mistral.ai/studio/batch-processing#whats-the-max-number-of-requests-in-a-batch
### What's the max number of requests in a batch? {#whats-the-max-number-of-requests-in-a-batch}
Currently, there is a maximum limit of 1 million pending requests per workspace. This means you cannot submit a job with more than 1 million requests. Additionally, you cannot submit two jobs with 600,000 requests each at the same time. You would need to wait until the first job has processed at least 200,000 requests, reducing its pending count to 400,000. At that point, the new job with 600,000 requests would fit within the limit.
Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/batch-processing", section="whats-the-max-number-of-batch-jobs-one-can-create") for the section after it
Thought for 1s
Based on the documentation I've retrieved, I can now answer the user's question:
API endpoints that batch jobs can target: The documentation explicitly lists the supported endpoints in the "Create a new Batch Job" section. They are:
/v1/embeddings
/v1/chat/completions
/v1/fim/completions
/v1/moderations
/v1/chat/moderations
/v1/ocr
/v1/classifications
/v1/conversations
/v1/audio/transcriptions
Maximum requests per batch input file: The file-batching section states "We support up to 1 million requests in a single batch" and the FAQ confirms "there is a maximum limit of 1 million pending requests per workspace" and "you cannot submit a job with more than 1 million requests."
So a single batch input file can hold up to 1 million requests.
The user wants a concise answer with the specific information. I should format this clearly with the endpoints listed and the maximum number.
A Mistral batch job can target the following API endpoints:
/v1/embeddings, /v1/chat/completions, /v1/fim/completions, /v1/moderations, /v1/chat/moderations, /v1/ocr, /v1/classifications, /v1/conversations, /v1/audio/transcriptions Create a new Batch Job.
One batch input file can hold up to 1 million requests File BatchingWhat's the max number of requests in a batch?.
11:50pm
Think
Vibe can make mistakes. Check answers. Learn more
Handling Mistral tool responses

