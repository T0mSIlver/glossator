---
url: https://docs.mistral.ai/vibe/work/image-generation
title: Generate images
breadcrumbs: [Vibe, Work]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/work/image-generation/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Generate images

Work can **generate and edit images** directly in the chat interface. Describe what you need **in plain language** and get visuals you can use for presentations, product mockups, marketing materials, and more.

> **Note**
>
> Work uses [Black Forest Labs](https://blackforestlabs.ai) models for image generation.

## Activation {#activation}

1. Click the `+` icon or type `/` in the chat window.
2. Select `Tools` then enable `Image generation`.

Image generation stays active for the current session. You can enable other tools at the same time.

> **Info**
>
> Daily generation limits apply based on your plan. For details, visit our [pricing page](https://mistral.ai/pricing).

## Creating images {#creating-images}

Describe the image you want **in natural language**. You don't need complex prompts or special syntax. Say what you're looking for and Work handles the rest.

For the best results, include:

- **Subject**: what the image shows.
- **Style**: illustration, photorealistic, diagram, flat design, etc.
- **Constraints**: aspect ratio / orientation.

Example prompt: *"Create a flat illustration of a modern office interior with natural light and plants."*

## Editing images {#editing-images}

You can refine generated images or edit existing ones in two ways.

### Continue in the same chat {#continue-same-chat}

After generating an image, describe the changes you want **in a follow-up message**. Work understands you're referring to the previous image and produces an updated version.

Example: *"Add a whiteboard on the back wall. Keep the lighting and color palette unchanged."*

### Upload an image in a new chat {#upload-new-chat}

Start a new chat, then upload an image using the `+` button by selecting `Upload Files`.

Describe the edits you want, and Work generates a new version based on your instructions.

> **Tip**
>
> This is useful when you want to pick up a previous result or edit an image from another source.

## Prompt templates {#prompt-templates}

Here are reusable patterns for common use cases:

| Type | Template |
|------|----------|
| **Scene** | Subject, style (flat/minimal), composition, aspect ratio |
| **Photographic** | Subject, photorealistic style, lighting type, lens, aspect ratio |
| **Product mockup** | Subject, studio shot, background, composition, aspect ratio |
| **Diagram** | Subject, clean lines, readable labels, accessible colors, aspect ratio |
| **Presentation visual** | Subject, slide-friendly composition, brand colors, minimal text, aspect ratio |
| **Marketing material** | Subject, target audience tone, style, brand guidelines, aspect ratio |

## Common use cases {#use-cases}

- **Pitch and deck visuals**: hero images, section dividers, and stylized backgrounds for investor decks or internal presentations.
- **Marketing assets**: campaign banners, landing-page heroes, social posts with consistent brand tone.
- **Product mockups**: render a concept on a neutral background to compare directions before a designer takes over.
- **Internal communications**: header imagery for announcements, onboarding decks, all-hands recap docs.
- **Concept exploration**: generate multiple visual directions from a brief before committing one to production.
- **Diagrams and conceptual illustrations**: process flows, organizational charts, abstract concept visuals for documents and reports.
- **Placeholder visuals during drafting**: get a stand-in image immediately while a final asset is in production.

## Best practices {#best-practices}

- **Be specific.** *"A photorealistic hero image for a fintech landing page, dark background, abstract light trails"* produces better results than *"make a banner."*
- **Iterate.** Treat the first result as a starting point. Refine with follow-up prompts until you're satisfied.
- **Pair with professional tools.** Image generation works best alongside dedicated editing software for final adjustments like precise cropping, color correction, or brand overlays.
- **Download and reuse.** Click the download button on any generated image to save it locally.

> **Tip**
>
> For charts, graphs, and data visualizations, use [Code Interpreter](https://docs.mistral.ai/vibe/chat-legacy/code-interpreter) in Chat instead. It generates accurate visuals from your actual data using Python.

## Limitations {#limitations}

- Prompts or images that contain copyrighted or inappropriate content may be blocked by safety filters.
- Fine details (small text, complex patterns) can sometimes be lost or altered during editing.
