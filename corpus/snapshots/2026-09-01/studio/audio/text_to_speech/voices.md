---
url: https://docs.mistral.ai/studio/audio/text_to_speech/voices
title: Voices
breadcrumbs: [Studio, Audio, Text to Speech]
kind: doc
locale: en
source_path: src/content/en/docs/studio/audio/text_to_speech/voices/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Voices

Save audio samples as reusable voices. Once created, a voice can be referenced by `voice_id` in any [speech generation](https://docs.mistral.ai/studio/audio/text_to_speech/speech) request, avoiding the need to pass `ref_audio` each time.

> **Warning**
>
> **Voice cloning usage policy**: By using this model and its voice cloning feature, you agree to comply with all applicable laws and our usage policy. You are not authorized to use this model for any unlawful purpose, including to impersonate others, clone voices without explicit consent, or engage in fraud, deception, misinformation, disinformation, harm, or the generation of unlawful, harmful, libelous, abusive, harassing, discriminatory, hateful, or privacy-invasive content. You must disclose AI-generated or partially AI-generated content where required by law. We disclaim all liability for non-compliant use.

**Create**

Create a voice by providing a name and a base64-encoded audio sample. The audio sample is used for voice cloning and can be retrieved later via `get_sample_audio`.

**Python**

**V1**

```python
import base64
from pathlib import Path
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

sample_audio_b64 = base64.b64encode(Path("sample.mp3").read_bytes()).decode()

voice = client.audio.voices.create(
    name="my-voice",
    sample_audio=sample_audio_b64,
    sample_filename="sample.mp3",
    languages=["en", "fr"],
    gender="female",
)

print(f"Created voice: {voice.id}")
print(f"Name: {voice.name}")
print(f"Languages: {voice.languages}")
```

**V2**

```python
import base64
from pathlib import Path
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

sample_audio_b64 = base64.b64encode(Path("sample.mp3").read_bytes()).decode()

voice = client.audio.voices.create(
    name="my-voice",
    sample_audio=sample_audio_b64,
    sample_filename="sample.mp3",
    languages=["en", "fr"],
    gender="female",
)

print(f"Created voice: {voice.id}")
print(f"Name: {voice.name}")
print(f"Languages: {voice.languages}")
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";
import { readFileSync } from "fs";

const client = new Mistral({ apiKey: "your-api-key" });

const sampleAudio = readFileSync("sample.mp3").toString("base64");

const voice = await client.audio.voices.create({
  name: "my-voice",
  sampleAudio: sampleAudio,
  sampleFilename: "sample.mp3",
  languages: ["en", "fr"],
  gender: "female",
});

console.log(`Created voice: ${voice.id}`);
console.log(`Name: ${voice.name}`);
console.log(`Languages: ${voice.languages}`);
```

**cURL**

```bash
SAMPLE_AUDIO=$(base64 -i sample.mp3)

curl -X POST "https://api.mistral.ai/v1/audio/voices" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"my-voice\",
    \"sample_audio\": \"$SAMPLE_AUDIO\",
    \"sample_filename\": \"sample.mp3\",
    \"languages\": [\"en\", \"fr\"],
    \"gender\": \"female\"
  }"
```

**Output**

```json
{
  "id": "a3e8f2b1-4c9d-4a6b-8e2f-1c3d5e7a9b0c",
  "name": "my-voice",
  "slug": null,
  "languages": ["en", "fr"],
  "gender": "male",
  "age": null,
  "tags": null,
  "created_at": "2026-03-20T18:34:32.118943Z"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Display name for the voice |
| `sample_audio` | string | Yes | Base64-encoded audio file |
| `sample_filename` | string | No | Original filename (used for format detection) |
| `slug` | string | No | URL-friendly identifier |
| `languages` | string[] | No | Languages the voice supports (e.g. `["en", "fr"]`) |
| `gender` | string | No | Gender label (e.g. `"female"`, `"male"`) |
| `age` | integer | No | Approximate age of the speaker |
| `tags` | string[] | No | Arbitrary tags for filtering |

**List**

List all available voices with offset-based pagination.

**Python**

**V1**

```python
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

limit = 10
offset = 0
all_voices = []

while True:
    page = client.audio.voices.list(limit=limit, offset=offset)
    items = page.items or []
    all_voices.extend(items)

    if offset + len(items) >= page.total:
        break

    offset += len(items)

print(f"Total voices: {len(all_voices)}")
for voice in all_voices:
    print(f"  - {voice.name} ({voice.id})  languages={voice.languages}")
```

**V2**

```python
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

limit = 10
offset = 0
all_voices = []

while True:
    page = client.audio.voices.list(limit=limit, offset=offset)
    items = page.items or []
    all_voices.extend(items)

    if offset + len(items) >= page.total:
        break

    offset += len(items)

print(f"Total voices: {len(all_voices)}")
for voice in all_voices:
    print(f"  - {voice.name} ({voice.id})  languages={voice.languages}")
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const client = new Mistral({ apiKey: "your-api-key" });

const limit = 10;
let offset = 0;
const allVoices = [];

while (true) {
  const page = await client.audio.voices.list({ limit, offset });
  const items = page.items ?? [];

  allVoices.push(...items);

  if (offset + items.length >= page.total) break;

  offset += items.length;
}

console.log(`Total voices: ${allVoices.length}`);
for (const voice of allVoices) {
  console.log(`  - ${voice.name} (${voice.id})  languages=${voice.languages}`);
}
```

**cURL**

```bash
curl "https://api.mistral.ai/v1/audio/voices?limit=10&offset=0" \
  -H "Authorization: Bearer $MISTRAL_API_KEY"
```

**Output**

```json
{
  "items": [
    {
      "id": "a3e8f2b1-4c9d-4a6b-8e2f-1c3d5e7a9b0c",
      "name": "my-voice",
      "slug": null,
      "languages": ["en", "fr"],
      "gender": "male",
      "age": null,
      "tags": null,
      "created_at": "2026-03-20T18:34:32.118943Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

**Get**

Retrieve metadata for a specific voice by its ID.

**Python**

**V1**

```python
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

voice = client.audio.voices.get(voice_id="your-voice-id")

print(f"Name:      {voice.name}")
print(f"Languages: {voice.languages}")
print(f"Gender:    {voice.gender}")
print(f"Created:   {voice.created_at}")
```

**V2**

```python
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

voice = client.audio.voices.get(voice_id="your-voice-id")

print(f"Name:      {voice.name}")
print(f"Languages: {voice.languages}")
print(f"Gender:    {voice.gender}")
print(f"Created:   {voice.created_at}")
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const client = new Mistral({ apiKey: "your-api-key" });

const voice = await client.audio.voices.get({ voiceId: "your-voice-id" });

console.log(`Name:      ${voice.name}`);
console.log(`Languages: ${voice.languages}`);
console.log(`Gender:    ${voice.gender}`);
console.log(`Created:   ${voice.createdAt}`);
```

**cURL**

```bash
curl "https://api.mistral.ai/v1/audio/voices/$VOICE_ID" \
  -H "Authorization: Bearer $MISTRAL_API_KEY"
```

**Output**

```json
{
  "id": "a3e8f2b1-4c9d-4a6b-8e2f-1c3d5e7a9b0c",
  "name": "my-voice",
  "slug": null,
  "languages": ["en", "fr"],
  "gender": "male",
  "age": null,
  "tags": null,
  "created_at": "2026-03-20T18:34:32.118943Z"
}
```

**Update**

Partially update a voice's metadata. Only the fields you provide will be changed.

**Python**

**V1**

```python
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

updated = client.audio.voices.update(
    voice_id="your-voice-id",
    name="my-updated-voice",
    languages=["en", "fr", "es"],
    tags=["narrator", "calm"],
)

print(f"Updated name: {updated.name}")
print(f"Updated languages: {updated.languages}")
```

**V2**

```python
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

updated = client.audio.voices.update(
    voice_id="your-voice-id",
    name="my-updated-voice",
    languages=["en", "fr", "es"],
    tags=["narrator", "calm"],
)

print(f"Updated name: {updated.name}")
print(f"Updated languages: {updated.languages}")
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const client = new Mistral({ apiKey: "your-api-key" });

const updated = await client.audio.voices.update({
  voiceId: "your-voice-id",
  voiceUpdateRequest: {
    name: "my-updated-voice",
    languages: ["en", "fr", "es"],
    tags: ["narrator", "calm"],
  },
});

console.log(`Updated name: ${updated.name}`);
console.log(`Updated languages: ${updated.languages}`);
```

**cURL**

```bash
curl -X PATCH "https://api.mistral.ai/v1/audio/voices/$VOICE_ID" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-updated-voice",
    "languages": ["en", "fr", "es"],
    "tags": ["narrator", "calm"]
  }'
```

**Output**

```json
{
  "id": "a3e8f2b1-4c9d-4a6b-8e2f-1c3d5e7a9b0c",
  "name": "my-updated-voice",
  "slug": null,
  "languages": ["en", "fr", "es"],
  "gender": "male",
  "age": null,
  "tags": ["narrator", "calm"],
  "created_at": "2026-03-20T18:34:32.118943Z"
}
```

**Delete**

Permanently delete a voice. Any speech requests using its `voice_id` will fail after deletion.

**Python**

**V1**

```python
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

result = client.audio.voices.delete(voice_id="your-voice-id")
print(f"Deleted: {result.id}")
```

**V2**

```python
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

result = client.audio.voices.delete(voice_id="your-voice-id")
print(f"Deleted: {result.id}")
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const client = new Mistral({ apiKey: "your-api-key" });

const result = await client.audio.voices.delete({ voiceId: "your-voice-id" });
console.log(`Deleted: ${result.id}`);
```

**cURL**

```bash
curl -X DELETE "https://api.mistral.ai/v1/audio/voices/$VOICE_ID" \
  -H "Authorization: Bearer $MISTRAL_API_KEY"
```

**Output**

```json
{
  "id": "a3e8f2b1-4c9d-4a6b-8e2f-1c3d5e7a9b0c",
  "name": "my-updated-voice",
  "slug": null,
  "languages": ["en", "fr", "es"],
  "gender": "male",
  "age": null,
  "tags": ["narrator", "calm"],
  "created_at": "2026-03-20T18:34:32.118943Z"
}
```

**Sample**

Retrieve the original audio sample that was used to create the voice, returned as raw audio bytes.

**Python**

**V1**

```python
from pathlib import Path
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

audio_bytes = client.audio.voices.get_sample_audio(voice_id="your-voice-id")
Path("voice_sample.wav").write_bytes(audio_bytes)
print("Saved sample to voice_sample.wav")
```

**V2**

```python
from pathlib import Path
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

audio_bytes = client.audio.voices.get_sample_audio(voice_id="your-voice-id")
Path("voice_sample.wav").write_bytes(audio_bytes)
print("Saved sample to voice_sample.wav")
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";
import { writeFileSync } from "fs";

const client = new Mistral({ apiKey: "your-api-key" });

const audioBytes = await client.audio.voices.getSampleAudio({
  voiceId: "your-voice-id",
});
writeFileSync("voice_sample.wav", Buffer.from(audioBytes));
console.log("Saved sample to voice_sample.wav");
```

**cURL**

```bash
curl "https://api.mistral.ai/v1/audio/voices/$VOICE_ID/sample" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  > voice_sample.wav
```
