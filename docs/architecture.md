# Architecture in ten lines

1. The repository vendors 411 normalized documentation pages at a pinned source commit.
2. The corpus adapter converts the documentation MDX, OpenAPI file, and model data to Markdown.
3. Ingestion splits pages at headings with a 600-token target and a 1,024-token cap.
4. Mistral embeddings map each chunk to 1,024 dimensions (128 stays as a measured variant).
5. Vespa stores one schema for each index variant, and one more for the dated snapshots.
6. Vespa combines BM25 and vector features in a two-phase ranking profile.
7. The MCP server exposes search, whole-page reads and history; every result is addressed by `url#anchor`.
8. The answer layer gathers context, generates structured output and verifies quoted citations, behind the HTTP API.
9. FastAPI and MCP share lazily constructed `SearchEngine` instances.
10. Evaluation records every query, model call, hit, score, citation, cost, and latency.

The index variants and the retrieval grid are in
[`retrieval.md`](retrieval.md); the HTTP routes and environment in
[`api.md`](api.md); the MCP tool contract in [`mcp.md`](mcp.md); what the
corpus is and where it comes from in [`corpus.md`](corpus.md).
