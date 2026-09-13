---
url: https://docs.mistral.ai/vibe/work/libraries
title: Add context with Libraries
breadcrumbs: [Vibe, Work]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/work/libraries/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Add context with Libraries

Libraries are **persistent knowledge bases** you build from your own documents and web pages.

Attach a Library to any task and Work **searches its contents in real time**, returning answers **based on your data** with direct references to the source material.

> **Info**
>
> Unlike [file uploads](https://docs.mistral.ai/vibe/work/files-and-canvas), which last for a single chat, Libraries persist across sessions. Upload once, use everywhere.

## Common use cases {#use-cases}

Libraries work best when you need the same set of documents available across multiple tasks:

- **Internal documentation**: upload your company handbook, IT policies, or HR guidelines and let your team ask questions in natural language.
- **Product specs and release notes**: keep technical specifications in a Library so product, sales, and support teams can all reference the same source of truth.
- **Research and reports**: build a Library from industry reports, white papers, or academic articles and query them without re-reading hundreds of pages.
- **Client or project knowledge**: create a Library per client or project with contracts, briefs, and meeting notes for quick retrieval.
- **Onboarding material**: build a Library of onboarding docs so new hires can ask Work questions in natural language.

## Creating and populating a Library {#creating-a-library}

1. Open the `Libraries` page from the sidebar.
2. Click `New Library`.
3. Give it a descriptive name. This is visible to others if you share the Library, so choose something meaningful (for example, `Q1 product specs` or `Engineering onboarding`).

### Uploading documents {#uploading-documents}

Drag and drop files into the Library, or click `Upload` to browse your device. You can upload up to **100 files at once**, with a maximum file size of **100 MB per file**.

A status indicator shows processing progress. Most standard documents (a few MB) process in seconds to a couple of minutes. Larger or more complex files take longer.

### Adding web pages {#adding-web-pages}

You can also add external web pages to a Library:

1. Click `Webpage` in the Library view.
2. Enter one or more URLs.
3. Click `Index`.

> **Note**
>
> Only the text content of the page is indexed. Child pages, images, and charts aren't included. If you need the full visual content, download the page and upload it as a file instead.

## Supported formats {#supported-formats}

Libraries accept the same formats as [file uploads](https://docs.mistral.ai/vibe/work/files-and-canvas):

| Category | Formats |
|----------|---------|
| **Documents** | PDF, Word (`.docx`, `.doc`), PowerPoint (`.pptx`, `.ppt`), ODT, EPUB, RTF |
| **Spreadsheets** | Excel (`.xlsx`, `.xls`), CSV, ODS, Numbers |
| **Images** | PNG, JPEG, WebP, GIF |
| **Text and markup** | TXT, Markdown, RST, LaTeX |
| **Data formats** | JSON, JSONL, XML, YAML |
| **Code files** | Python, JavaScript/TypeScript, Java, Go, Rust, C/C++, Ruby, PHP, SQL, and more |
| **Email** | EML, MSG |

## Using Libraries in tasks {#using-libraries}

### Attaching a Library to a chat {#attaching-a-library}

In any chat, click the `+` button then select `Libraries` and search for the Library of your choice or create one from scratch. You can attach **multiple Libraries** to a single chat.

### Querying your documents {#querying-documents}

Once attached, Work searches across all documents in the Library to answer your task. Ask naturally:

- *"What does our refund policy say about international orders?"*
- *"Summarize the key findings from the Q2 market analysis."*
- *"Find all references to data retention in the compliance docs."*

> **Tip**
>
> To query a single document instead of the full Library, click `+`, select `Upload Files`, choose your Library, and pick the specific document you want to attach. You can also mention the document by name in your prompt to help Work focus its search.

### Verifying sources {#verifying-sources}

Each response includes **numbered footnotes** linked to the original source material. Click a footnote to jump to the relevant passage. To see every reference used in a response, click the `Sources` button at the bottom of the message.

This makes it easy to verify answers against your original documents before using them in reports, emails, or presentations.

## Sharing and permissions {#sharing}

By default, a new Library is **private** (only you can see and use it).

### Sharing with specific people {#sharing-specific-people}

1. Open the `Libraries` page.
2. Select the Library you want to share.
3. Click `Share` to open the access modal.
4. Search for users by name or email and assign a permission level:
   - **Collaborator**: can use the Library, upload or delete documents, and modify settings.
   - **Viewer**: can use the Library in their own chats but can't modify it.

### Sharing with your entire organization {#sharing-organization}

In the same modal, toggle `Entire organization` and choose whether everyone gets Collaborator or Viewer access.

> **Note**
>
> Recipients may need to refresh the page to see newly shared Libraries in their list.

## Managing Libraries {#managing-libraries}

### Viewing and downloading documents {#viewing-documents}

Open a Library and click any document in the list. The right panel shows the processed content and an auto-generated summary. Click `Download` in the panel or use the three-dots menu to save the original file.

### Renaming a Library {#renaming-library}

Rename a Library from its settings. The change is visible to all users who have access (they may need to refresh).

### Deleting a Library {#deleting-library}

Delete a Library from the `Libraries` page. This removes it permanently for everyone, including all uploaded documents.

> **Caution**
>
> Deleting a Library is permanent and can't be undone. All documents inside are removed from our systems.

## Limits and processing {#limits}

- **No restriction** on the number of Libraries you can create.
- Up to **100 files** can be uploaded at once per Library.
- Maximum file size: **100 MB** per file.
- Each document uses processing capacity based on its size. Your monthly allowance resets automatically and is shared across all your Libraries.

> **Info**
>
> If you've reached your processing limit for the month, new uploads are paused until the allowance resets. Existing Libraries and their content remain fully usable.

## Data and privacy {#data-privacy}

- Documents are stored securely in our European cloud infrastructure.
- Storage lasts as long as the Library exists in an active account. Deleting a Library or your account triggers permanent removal from our systems.
- Training policies depend on your plan. You can [opt out](https://help.mistral.ai/en/articles/455207-can-i-opt-out-of-my-input-or-output-data-being-used-for-training) of data training at any time.

For more details, see our [privacy policy](https://mistral.ai/terms#privacy-policy) and [trust center](https://trust.mistral.ai/).
