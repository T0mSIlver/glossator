---
url: https://docs.mistral.ai/resources/deprecated/finetuning/classifier_factory
title: Classifier Factory
breadcrumbs: [Resources, Deprecated features, Fine-Tuning]
kind: doc
locale: en
source_path: src/content/en/docs/resources/deprecated/finetuning/classifier_factory/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Classifier Factory

> **Deprecated**
>
> This feature is deprecated and is no longer actively supported.

In various domains and enterprises, classification models play a crucial role in enhancing efficiency, improving user experience, and ensuring compliance. These models serve diverse purposes, including but not limited to:

- Moderation: Classification models are essential for moderating services and classifying unwanted content. For instance, our [moderation service](https://docs.mistral.ai/resources/deprecated/guardrailing/#moderation-api) helps in identifying and filtering inappropriate or harmful content in real-time, ensuring a safe and respectful environment for users.
- **Intent Detection**: These models help in understanding user intent and behavior. By analyzing user interactions, they can predict the user's next actions or needs, enabling personalized recommendations and improved customer support.
- **Sentiment Analysis**: Emotion and sentiment detection models analyze text data to determine the emotional tone behind words. This is particularly useful in social media monitoring, customer feedback analysis, and market research, where understanding public sentiment can drive strategic decisions.
- **Data Clustering**: Classification models can group similar data points together, aiding in data organization and pattern recognition. This is beneficial in market segmentation, where businesses can identify distinct customer groups for targeted marketing campaigns.
- **Fraud Detection**: In the financial sector, classification models help in identifying fraudulent transactions by analyzing patterns and anomalies in transaction data. This ensures the security and integrity of financial systems.
- **Spam Filtering**: Email services use classification models to filter out spam emails, ensuring that users receive only relevant and safe communications.
- **Recommendation Systems**: Classification models power recommendation engines by categorizing user preferences and suggesting relevant products, movies, or content based on past behavior and preferences.

By leveraging classification models, organizations can make data-driven decisions, improve operational efficiency, and deliver better products and services to their customers.

For this reason, we designed a friendly and easy way to make your own classifiers. Leveraging our small but highly efficient models and training methods, the Classifier Factory is both available directly in the [AI Studio](https://console.mistral.ai/build/finetuned-models) and our API.

## Before You Start {#before-you-start}

### Dataset

To fine-tune a model, you need to provide a dataset that contains the data you want to train on, it is also recommended to have a validation dataset and a test dataset.

The dataset must be in a specific format, and you can upload it to the Mistral Cloud before launching the fine-tuning job.

**Dataset Format**

Data must be stored in JSON Lines (`.jsonl`) files, which allow storing multiple JSON objects, each on a new line.

We provide two endpoints:

- `v1/classifications`: To classify raw text.
- `v1/chat/classifications`: To classify chats and multi-turn interactions.

There are 2 main kinds of classification models\***\*:\*\***

- Single Target
- Multi-Target

**Single Target**

For single label classification, data must have the label name and the value for that corresponding label. Example:

**v1/classifications**

```json
{
  "text": "I love this product!",
  "labels": {
    "sentiment": "positive" // positive/neutral/negative
  }
}
```

**v1/chat/classifications**

```json
{
  "messages": [{ "role": "user", "content": "I love this product!" }],
  "labels": {
    "sentiment": "positive" // positive/neutral/negative
  }
}
```

For multiple labels, you can provide a list:

**v1/classifications**

```json
{
  "text": "I love this product!",
  "labels": {
    "sentiment": ["positive", "neutral"]
  }
}
```

**v1/chat/classifications**

```json
{
  "messages": [{ "role": "user", "content": "I love this product!" }],
  "labels": {
    "sentiment": ["positive", "neutral"]
  }
}
```

When using the result model, you will be able to retrieve the scores for the corresponding label and value.

Note that the files must be in JSONL format, meaning every JSON object must be flattened into a single line, and each JSON object is on a new line.

Raw `.jsonl` file example.

```json
{"text": "I love this product!", "labels": {"sentiment": "positive"}}
{"text": "The game was amazing.", "labels": {"sentiment": "positive"}}
{"text": "The new policy is controversial.", "labels": {"sentiment": "neutral"}}
{"text": "I don't like the new design.", "labels": {"sentiment": "negative"}}
{"text": "The team won the championship.", "labels": {"sentiment": "positive"}}
{"text": "The economy is in a bad shape.", "labels": {"sentiment": "negative"}}
...
```

- Label data must be a dictionary with the label name as the key and the label value as the value.

**Multi-Target**

You can also have multiple targets and not only a single one. This is useful if you want to classify different aspects of the same content independently. Example:

**v1/classifications**

```json
{
  "text": "I love this product!",
  "labels": {
    "sentiment": "positive", // positive/neutral/negative
    "is-english": "yes" // yes/no, boolean
  }
}
```

**v1/chat/classifications**

```json
{
  "messages": [{ "role": "user", "content": "I love this product!" }],
  "labels": {
    "sentiment": "positive", // positive/neutral/negative
    "is-english": "yes" // yes/no, boolean
  }
}
```

- Each target is independent of each other, meaning the scores for each label will also be independent.

**Upload a file**

Once you have the data file with the right format, you can upload the data file to the Mistral Client, making them available for use in fine-tuning jobs.

**Python**

**V1**

```python
from mistralai.client import Mistral
import os

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

training_data = client.files.upload(
    file={
        "file_name": "training_file.jsonl",
        "content": open("training_file.jsonl", "rb"),
    }
)

validation_data = client.files.upload(
    file={
        "file_name": "validation_file.jsonl",
        "content": open("validation_file.jsonl", "rb"),
    }
)
```

**V2**

```python
from mistralai.client import Mistral
import os

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

training_data = client.files.upload(
    file={
        "file_name": "training_file.jsonl",
        "content": open("training_file.jsonl", "rb"),
    }
)

validation_data = client.files.upload(
    file={
        "file_name": "validation_file.jsonl",
        "content": open("validation_file.jsonl", "rb"),
    }
)
```

**TypeScript**

```typescript
import { Mistral } from '@mistralai/mistralai';
import fs from 'fs';

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({ apiKey: apiKey });

const training_file = fs.readFileSync('training_file.jsonl');
const training_data = await client.files.upload({
  file: {
    fileName: 'training_file.jsonl',
    content: training_file,
  },
});

const validation_file = fs.readFileSync('validation_file.jsonl');
const validation_data = await client.files.upload({
  file: {
    fileName: 'validation_file.jsonl',
    content: validation_file,
  },
});
```

**cURL**

```bash
curl https://api.mistral.ai/v1/files \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -F purpose="fine-tune" \
  -F file="@training_file.jsonl"

curl https://api.mistral.ai/v1/files \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -F purpose="fine-tune" \
  -F file="@validation_file.jsonl"
```

## Jobs Management {#jobs-management}

### Create and Manage Fine-tuning Jobs

To create your custom model, you need to create a fine-tuning job. You can fully manage jobs via our API, from creation, to starting, monitoring and cancellation.

**Fine-tuning Job**

A fine-tuning job corresponds to a single training run. You can create a fine-tuning job with the following parameters:

### Create a fine-tuning job

- model: the specific model you would like to fine-tune. The choice is `ministral-3b-latest`.
- training_files: a collection of training file IDs, which can consist of a single file or multiple files.
- validation_files: a collection of validation file IDs, which can consist of a single file or multiple files.
- hyperparameters: two adjustable hyperparameters, "training_steps" and "learning_rate", that users can modify.
- auto_start:
  - `auto_start=True`: Your job will be launched immediately after validation.
  - `auto_start=False` (default): You can manually start the training after validation by sending a POST request to `/fine_tuning/jobs/<uuid>/start`.
- integrations: external integrations we support such as Weights and Biases for metrics tracking during training.

**Python**

```python
# create a fine-tuning job
created_jobs = client.fine_tuning.jobs.create(
    model="ministral-3b-latest",
    job_type="classifier",
    training_files=[{"file_id": training_data.id, "weight": 1}],
    validation_files=[validation_data.id],
    hyperparameters={
        "training_steps": 10,
        "learning_rate":0.0001
    },
    auto_start=False,
#   integrations=[
#       {
#           "project": "finetuning",
#           "api_key": "WANDB_KEY",
#       }
#   ]
)
```

**TypeScript**

```typescript
const createdJob = await client.fineTuning.jobs.create({
  model: 'ministral-3b-latest',
  jobType: 'classifier',
  trainingFiles: [{ fileId: training_data.id, weight: 1 }],
  validationFiles: [validation_data.id],
  hyperparameters: {
    trainingSteps: 10,
    learningRate: 0.0001,
  },
  autoStart: false,
  //  integrations:[
  //      {
  //          project: "finetuning",
  //          apiKey: "WANDB_KEY",
  //      }
  //  ],
});
```

**cURL**

```bash
curl https://api.mistral.ai/v1/fine_tuning/jobs \
--header "Authorization: Bearer $MISTRAL_API_KEY" \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data '{
  "model": "ministral-3b-latest",
  "job_type": "classifier",
  "training_files": [
    "<uuid>"
  ],
  "validation_files": [
    "<uuid>"
  ],
  "hyperparameters": {
    "training_steps": 10,
    "learning_rate": 0.0001
  },
  "auto_start": false
}'
```

### Job Status

After creating a fine-tuning job, you can check the job status using:

**Python**

```python 
client.fine_tuning.jobs.get(job_id = created_jobs.id)
```

**TypeScript**

```typescript
await client.fineTuning.jobs.get({ jobId: createdJob.id });
```

**cURL**

```bash
curl https://api.mistral.ai/v1/fine_tuning/jobs/<jobid> \
--header "Authorization: Bearer $MISTRAL_API_KEY"
```

### Start a fine-tuning job

Initially, the job status will be `"QUEUED"`. After a brief period, the status will update to `"VALIDATED"`. At this point, you can proceed to start the fine-tuning job:

**Python**

```python
# start a fine-tuning job
client.fine_tuning.jobs.start(job_id = created_jobs.id)

created_jobs
```

**TypeScript**

```typescript
await client.fineTuning.jobs.start({ jobId: createdJob.id });
```

**cURL**

```bash
curl -X POST https://api.mistral.ai/v1/fine_tuning/jobs/<jobid>/start \
--header "Authorization: Bearer $MISTRAL_API_KEY"
```

**List/retrieve/cancel jobs**

You can also list jobs, retrieve a job, or cancel a job.

### List jobs

You can filter and view a list of jobs using various parameters such as `page`, `page_size`, `model`, `created_after`, `created_by_me`, `status`, `wandb_project`, `wandb_name`, and `suffix`. Check out our [API specs](https://docs.mistral.ai/api/#tag/fine-tuning) for details.

**Python**

```python
jobs = client.fine_tuning.jobs.list()
```

**TypeScript**

```typescript
const jobs = await client.fineTuning.jobs.list();
```

**cURL**

```bash
curl https://api.mistral.ai/v1/fine_tuning/jobs \
--header "Authorization: Bearer $MISTRAL_API_KEY"
```

### Retrieve a job

You can retrieve a job and information by its ID.

**Python**

```python
retrieved_jobs = client.fine_tuning.jobs.get(job_id = created_jobs.id)
```

**TypeScript**

```typescript
const retrievedJob = await client.fineTuning.jobs.get({ jobId: createdJob.id });
```

**cURL**

```bash
curl https://api.mistral.ai/v1/fine_tuning/jobs/<jobid> \
--header "Authorization: Bearer $MISTRAL_API_KEY"
```

### Cancel a job

You can also cancel a job by its ID if needed.

**Python**

```python
canceled_jobs = client.fine_tuning.jobs.cancel(job_id = created_jobs.id)
```

**TypeScript**

```typescript
const canceledJob = await client.fineTuning.jobs.cancel({
  jobId: createdJob.id,
});
```

**cURL**

```bash
curl -X POST https://api.mistral.ai/v1/fine_tuning/jobs/<jobid>/cancel \
--header "Authorization: Bearer $MISTRAL_API_KEY"
```

## Fine-tuned Model {#fine-tuned-models}

### Use and Delete Fine-tuned Models

Once your fine-tuning job is done, you can use your fine-tuned custom model to classify your data and use it in your applications.

### Use a fine-tuned model {#use-finetuned-model}

Below is an example of how to use a fine-tuned model to classify your data.

**Python**

```python
# You will be able to see the fine-tuned model name via `retrieved_job.fine_tuned_model`
classifier_response = client.classifiers.classify(
    model=retrieved_job.fine_tuned_model,
    inputs=["It's nice", "It's terrible", "Why not"],
)
# Use `classify_chat` to classify chats and multiturn interactions.
```

**TypeScript**

```typescript
// You will be able to see the fine-tuned model name via `retrievedJob.fine_tuned_model`
const classifierResponse = await client.classifiers.classify({
  model: retrievedJob.fine_tuned_model,
  inputs: ["It's nice", "It's terrible", 'Why not'],
});
// Use `classifyChat` to classify chats and multiturn interactions.
```

**cURL**

```bash
curl "https://api.mistral.ai/v1/classifications" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
    "model": "ft:classifier:ministral-3b-latest:XXX:20250401:XXX",
    "input": ["It's nice", "It's terrible", "Why not"]
  }'
```

### Delete a fine-tuned model {#delete-finetuned-model}

You can delete a fine-tuned model if you no longer need it.

**Python**

```python
client.models.delete(model_id=retrieved_job.fine_tuned_model)
```

**TypeScript**

```typescript
await client.models.delete({ modelId: retrieved_job.fine_tuned_model });
```

**cURL**

```bash
curl --location --request DELETE 'https://api.mistral.ai/v1/models/ft:classifier:ministral-3b-latest:XXX:20250401:XXX' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY"
```

## Cookbooks {#cookbooks}

Explore our guides and [cookbooks](https://github.com/mistralai/cookbook) leveraging the Classifier Factory:

- [Intent Classification](https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/classifier_factory/intent_classification.ipynb): Creating a single-target, single-label, intent classification model to predict user actions and improve customer interactions.
- [Moderation Classifier](https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/classifier_factory/moderation_classifier.ipynb): Build a single-target, multi-label, simple moderation model to label public comments.
- [Product Classification](https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/classifier_factory/product_classification.ipynb): Create a multi-target, single-label and multi-label, food classification model to categorize dishes and their country of origin and compare to classic LLM solutions, enhancing recipe recommendations and dietary planning.

## FAQ {#faq}

### Which models can we fine-tune to create our own classifiers? {#which-models-can-we-fine-tune-to-create-our-own-classifiers}

Currently, the classifier factory supports `ministral-3b`.

### Where can I find the pricing? {#where-can-i-find-the-pricing}

You can find it on our [pricing page](https://mistral.ai/pricing#api-pricing) in the "fine-tunable models" section of our API Pricing.
