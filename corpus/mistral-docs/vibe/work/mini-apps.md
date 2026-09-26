---
url: https://docs.mistral.ai/vibe/work/mini-apps
title: Mini apps
breadcrumbs: [Vibe, Work]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/work/mini-apps/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
---

# Mini apps

Vibe Work can build interactive mini apps: self-contained React applications that run directly in the Canvas panel. Describe what you want and Work generates the code and renders the app live.

## Create a mini app {#create}

Describe the app you want in plain language. Work generates the code and renders it immediately.

Example prompts:

- *"Build a unit converter for length, weight, and temperature."*
- *"Create a Pomodoro timer with start, pause, and reset controls."*
- *"Make a quiz app with five questions about world capitals."*
- *"Build a color palette generator that lets me adjust hue and saturation."*

The app appears inline in the chat as a preview panel and is interactive right away. Click buttons, fill forms, and use it as you normally would. Click `Expand` at the bottom of the panel to open it in the side Canvas view.

## Switch between preview and code {#preview-and-code}

The Canvas panel has two views, toggled with the icons in the top-left corner:

- **Preview** (eye icon): renders the running app. This is the default view.
- **Code** (`<>` icon): shows the source files. A file list appears on the left; click any file to open it in the editor.

## Iterate on the app {#iterate}

Refine the app by continuing the conversation in chat:

- *"Add a dark mode toggle."*
- *"Change the button colors to match our brand."*
- *"Add a reset button that clears all inputs."*

Work updates the code and re-renders the app. You can also edit source files directly in the code view.

## Download the source code {#download}

To download the app as a ZIP archive:

Click the download icon in the top-right corner of the Canvas panel.

The ZIP contains the full source files (`index.js`, `styles.css`, and any other files Work created) and can be opened in any code editor or deployed to a static host.

## Share the app {#share}

To share a live, interactive version of the app:

1. Click `Share` in the top-right corner of the Canvas panel.
2. Toggle `Link accessible to anyone` on.
3. Click `Copy link` to copy the public URL, or use one of the `Share to` buttons to send it directly via email, X, LinkedIn, Reddit, or WhatsApp.

Anyone with the link can view and interact with the app. Your chat messages aren't shared. Only the app itself is accessible through the link.

To stop sharing, return to the Share dialog and toggle `Link accessible to anyone` off.
