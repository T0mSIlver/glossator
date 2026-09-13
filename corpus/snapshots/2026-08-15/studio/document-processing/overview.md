---
url: https://docs.mistral.ai/studio/document-processing/overview
title: Document Processing
breadcrumbs: [Studio, Document AI]
kind: doc
locale: en
source_path: src/content/en/docs/studio/document-processing/overview/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Document AI

Mistral Document AI offers enterprise-level document processing, combining OCR technology with advanced structured data extraction.

![document_ai_graph](https://docs.mistral.ai/img/document_ai_overview.png)

Use multilingual support, annotations, and adaptable workflows for all document types to extract, comprehend, and analyze information. See the full list of [supported languages](https://docs.mistral.ai/resources/languages#ocr).

## Document AI services {#document-ai-services}

Use `client.ocr.process` in our SDK clients or the `https://api.mistral.ai/v1/ocr` endpoint to access the following services:

- [OCR Processor](https://docs.mistral.ai/studio/document-processing/basic_ocr): Discover our OCR model and its capabilities.
- [Annotations](https://docs.mistral.ai/studio/document-processing/annotations): Annotate and extract data from your documents using built-in structured outputs.
- [Document QnA](https://docs.mistral.ai/studio/document-processing/document_qna): Combine our models with OCR technology for document question answering.
