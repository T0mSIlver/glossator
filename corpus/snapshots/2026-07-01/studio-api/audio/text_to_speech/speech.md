---
url: https://docs.mistral.ai/studio-api/audio/text_to_speech/speech
title: Speech Generation
breadcrumbs: [Studio, Audio, Text to Speech]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/audio/text_to_speech/speech/page.mdx
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Speech Generation

Generate speech from text using a [saved voice](https://docs.mistral.ai/studio-api/audio/text_to_speech/voices) (`voice_id`) or a one-off reference audio clip (`ref_audio`).

## Generate {#generate}

**Saved Voice**

Generate speech using a previously [saved voice](https://docs.mistral.ai/studio-api/audio/text_to_speech/voices) (`voice_id`) identifier.

**Basic**

**Python**

**V1**

```python
import base64
from pathlib import Path
from mistralai import Mistral

client = Mistral(api_key="your-api-key")

response = client.audio.speech.complete(
    model="voxtral-mini-tts-2603",
    input="Hello! This is Voxtral, Mistral's text-to-speech model.",
    voice_id="your-voice-id",
    response_format="mp3",
)

Path("output.mp3").write_bytes(base64.b64decode(response.audio_data))
print("Saved to output.mp3")
```

**V2**

```python
import base64
from pathlib import Path
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

response = client.audio.speech.complete(
    model="voxtral-mini-tts-2603",
    input="Hello! This is Voxtral, Mistral's text-to-speech model.",
    voice_id="your-voice-id",
    response_format="mp3",
)

Path("output.mp3").write_bytes(base64.b64decode(response.audio_data))
print("Saved to output.mp3")
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";
import { writeFileSync } from "fs";

const client = new Mistral({ apiKey: "your-api-key" });

const response = await client.audio.speech.complete({
  model: "voxtral-mini-tts-2603",
  input: "Hello! This is Voxtral, Mistral's text-to-speech model.",
  voiceId: "your-voice-id",
  responseFormat: "mp3",
});

writeFileSync("output.mp3", response.audioData);
console.log("Saved to output.mp3");
```

**cURL**

```bash
curl -X POST "https://api.mistral.ai/v1/audio/speech" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "voxtral-mini-tts-2603",
    "input": "Hello! This is Voxtral, Mistral'\''s text-to-speech model.",
    "voice_id": "your-voice-id",
    "response_format": "mp3"
  }' | jq -r '.audio_data' | base64 -d > output.mp3
```

**Output**

```json
{
  "audio_data": "SUQzBAAAAAAAIlRTU0UAAAAOAAADTGF2ZjYxLjcu...<base64_encoded_audio>"
}
```

**Streaming**

Each chunk is a `speech.audio.delta` event with a base64-encoded audio fragment. The stream ends with a `speech.audio.done` event containing usage info.

> **Tip**
>
> Use `response_format="pcm"` for the lowest streaming latency (~0.7s time-to-first-audio vs ~2s for `mp3`).

**Python**

**V1**

```python
import base64
from mistralai import Mistral

client = Mistral(api_key="your-api-key")

audio_chunks = []

with client.audio.speech.complete(
    model="voxtral-mini-tts-2603",
    input="Streaming makes voice agents feel more responsive and natural.",
    voice_id="your-voice-id",
    response_format="opus",
    stream=True,
) as stream:
    for event in stream:
        if event.event == "speech.audio.delta":
            audio_chunks.append(base64.b64decode(event.data.audio_data))
        elif event.event == "speech.audio.done":
            print(f"Done. Tokens used: {event.data.usage}")

audio_bytes = b"".join(audio_chunks)
with open("output_streamed.opus", "wb") as f:
    f.write(audio_bytes)
```

**V2**

```python
import base64
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

audio_chunks = []

with client.audio.speech.complete(
    model="voxtral-mini-tts-2603",
    input="Streaming makes voice agents feel more responsive and natural.",
    voice_id="your-voice-id",
    response_format="opus",
    stream=True,
) as stream:
    for event in stream:
        if event.event == "speech.audio.delta":
            audio_chunks.append(base64.b64decode(event.data.audio_data))
        elif event.event == "speech.audio.done":
            print(f"Done. Tokens used: {event.data.usage}")

audio_bytes = b"".join(audio_chunks)
with open("output_streamed.opus", "wb") as f:
    f.write(audio_bytes)
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";
import { writeFileSync } from "fs";

const client = new Mistral({ apiKey: "your-api-key" });

const stream = await client.audio.speech.complete({
  model: "voxtral-mini-tts-2603",
  input: "Streaming makes voice agents feel more responsive and natural.",
  voiceId: "your-voice-id",
  responseFormat: "opus",
  stream: true,
});

const audioChunks: Uint8Array[] = [];

for await (const event of stream) {
  if (event.event === "speech.audio.delta") {
    audioChunks.push(Buffer.from(event.data.audioData, "base64"));
  } else if (event.event === "speech.audio.done") {
    console.log("Done. Tokens used:", event.data.usage);
  }
}

const audioBytes = Buffer.concat(audioChunks);
writeFileSync("output_streamed.opus", audioBytes);
```

**Output**

```json
[
  {
    "event": "speech.audio.delta",
    "data": {
      "audio_data": "<base64_audio_chunk>"
    }
  },
  {
    "event": "speech.audio.delta",
    "data": {
      "audio_data": "<base64_audio_chunk>"
    }
  },
  {
    "event": "speech.audio.done",
    "data": {
      "usage": {
        "prompt_tokens": 56,
        "completion_tokens": 94080,
        "total_tokens": 94136
      }
    }
  }
]
```

**Ref Audio**

Pass a base64-encoded audio clip directly via `ref_audio` to clone a voice on the fly, without creating a saved voice.

**Basic**

**Python**

**V1**

```python
import base64
from pathlib import Path
from mistralai import Mistral

client = Mistral(api_key="your-api-key")

ref_audio_b64 = base64.b64encode(Path("sample.mp3").read_bytes()).decode()

response = client.audio.speech.complete(
    model="voxtral-mini-tts-2603",
    input="This speech will sound like the voice in the reference audio.",
    ref_audio=ref_audio_b64,
    response_format="wav",
)

Path("output.wav").write_bytes(base64.b64decode(response.audio_data))
```

**V2**

```python
import base64
from pathlib import Path
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

ref_audio_b64 = base64.b64encode(Path("sample.mp3").read_bytes()).decode()

response = client.audio.speech.complete(
    model="voxtral-mini-tts-2603",
    input="This speech will sound like the voice in the reference audio.",
    ref_audio=ref_audio_b64,
    response_format="wav",
)

Path("output.wav").write_bytes(base64.b64decode(response.audio_data))
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";
import { readFileSync, writeFileSync } from "fs";

const client = new Mistral({ apiKey: "your-api-key" });

const refAudio = readFileSync("sample.mp3").toString("base64");

const response = await client.audio.speech.complete({
  model: "voxtral-mini-tts-2603",
  input: "This speech will sound like the voice in the reference audio.",
  refAudio: refAudio,
  responseFormat: "wav",
});

writeFileSync("output.wav", response.audioData);
```

**cURL**

```bash
REF_AUDIO=$(base64 -i sample.mp3)

curl -X POST "https://api.mistral.ai/v1/audio/speech" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"voxtral-mini-tts-2603\",
    \"input\": \"This speech will sound like the voice in the reference audio.\",
    \"ref_audio\": \"$REF_AUDIO\",
    \"response_format\": \"wav\"
  }" | jq -r '.audio_data' | base64 -d > output.wav
```

**Output**

```json
{
  "audio_data": "UklGRv////9XQVZFZm10IBAAAAABAAEAwF0AAIC7...<base64_encoded_audio>"
}
```

**Streaming**

Each chunk is a `speech.audio.delta` event with a base64-encoded audio fragment. The stream ends with a `speech.audio.done` event containing usage info.

> **Tip**
>
> Use `response_format="pcm"` for the lowest streaming latency (~0.7s time-to-first-audio vs ~2s for `mp3`).

**Python**

**V1**

```python
import base64
from pathlib import Path
from mistralai import Mistral

client = Mistral(api_key="your-api-key")

ref_audio_b64 = base64.b64encode(Path("sample.mp3").read_bytes()).decode()
audio_chunks = []

with client.audio.speech.complete(
    model="voxtral-mini-tts-2603",
    input="Streaming makes voice agents feel more responsive and natural.",
    ref_audio=ref_audio_b64,
    response_format="opus",
    stream=True,
) as stream:
    for event in stream:
        if event.event == "speech.audio.delta":
            audio_chunks.append(base64.b64decode(event.data.audio_data))
        elif event.event == "speech.audio.done":
            print(f"Done. Tokens used: {event.data.usage}")

audio_bytes = b"".join(audio_chunks)
with open("output_streamed.opus", "wb") as f:
    f.write(audio_bytes)
```

**V2**

```python
import base64
from pathlib import Path
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")

ref_audio_b64 = base64.b64encode(Path("sample.mp3").read_bytes()).decode()
audio_chunks = []

with client.audio.speech.complete(
    model="voxtral-mini-tts-2603",
    input="Streaming makes voice agents feel more responsive and natural.",
    ref_audio=ref_audio_b64,
    response_format="opus",
    stream=True,
) as stream:
    for event in stream:
        if event.event == "speech.audio.delta":
            audio_chunks.append(base64.b64decode(event.data.audio_data))
        elif event.event == "speech.audio.done":
            print(f"Done. Tokens used: {event.data.usage}")

audio_bytes = b"".join(audio_chunks)
with open("output_streamed.opus", "wb") as f:
    f.write(audio_bytes)
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";
import { readFileSync, writeFileSync } from "fs";

const client = new Mistral({ apiKey: "your-api-key" });

const refAudio = readFileSync("sample.mp3").toString("base64");
const stream = await client.audio.speech.complete({
  model: "voxtral-mini-tts-2603",
  input: "Streaming makes voice agents feel more responsive and natural.",
  refAudio: refAudio,
  responseFormat: "opus",
  stream: true,
});

const audioChunks: Uint8Array[] = [];

for await (const event of stream) {
  if (event.event === "speech.audio.delta") {
    audioChunks.push(Buffer.from(event.data.audioData, "base64"));
  } else if (event.event === "speech.audio.done") {
    console.log("Done. Tokens used:", event.data.usage);
  }
}

const audioBytes = Buffer.concat(audioChunks);
writeFileSync("output_streamed.opus", audioBytes);
```

**Output**

```json
[
  {
    "event": "speech.audio.delta",
    "data": {
      "audio_data": "<base64_audio_chunk>"
    }
  },
  {
    "event": "speech.audio.delta",
    "data": {
      "audio_data": "<base64_audio_chunk>"
    }
  },
  {
    "event": "speech.audio.done",
    "data": {
      "usage": {
        "prompt_tokens": 56,
        "completion_tokens": 94080,
        "total_tokens": 94136
      }
    }
  }
]
```

## `ref_audio` Guidelines

When using `ref_audio` for zero-shot cloning:

- **Duration**: 3–25 seconds
- **Single speaker only**
- **Clean recording** with no background noise
- **Neutral prosody** — avoid excessive pausing or disfluencies
- **Expressive pitch** (flat voices produce flat output)

## Best Practices {#best-practices}

### Text Prompt Guidelines {#text-prompt-guidelines}

- **Language match**: the voice prompt should be in the same language as the text prompt for best results.
- **Cross-lingual prompts**: the model also supports cross-lingual voice transfer. For example, a French voice prompt with English text will produce French-accented English.
- **Verbalizable form**: convert numbers and symbols to their spoken equivalent to avoid ambiguity. For example, use `one thousand two hundred thirty four` instead of `1234`, or `twelve thirty four` depending on context.
- **No rich formatting**: avoid markdown, emojis, or special characters in the text — they will not be rendered and may degrade output quality.
- **Abbreviations**: spell out abbreviations for better pronunciation. Use `F-B-I` or `F.B.I.` instead of `FBI`.
- **Length**: keep prompts under 300 words for best results.

> **Warning**
>
> The TTS API includes content moderation. Requests containing certain text will be rejected with a `403` error. Keep your text inputs within acceptable use guidelines.

## Response Audio Formats {#response-formats}

| Format | Description |
|--------|-------------|
| `mp3` | Compressed, suitable for most use cases |
| `wav` | Uncompressed PCM, highest quality |
| `pcm` | Raw float32 LE samples — recommended for streaming (lowest latency) |
| `flac` | Lossless compression |
| `opus` | Low bitrate, good for streaming |
