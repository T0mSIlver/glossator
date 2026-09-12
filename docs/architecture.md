# Architecture in ten lines

1. The repository vendors 411 normalized documentation pages at a pinned source commit.
2. The corpus adapter converts the documentation MDX, OpenAPI file, and model data to Markdown.
3. Ingestion splits at headings with a 600-token target; large code and table blocks stay intact.
4. Mistral embeddings map each chunk to 1,024 dimensions (128 stays as a measured variant).
5. Vespa stores one schema for each index variant, and one more for the dated snapshots.
6. Vespa combines BM25 and vector features in a two-phase ranking profile.
7. The MCP server exposes search, whole-page reads and history; every hit and section prints its key and the link to cite, and history reads a precomputed changelog of the dated snapshots.
8. The answer layer gathers context, generates structured output and verifies quoted citations, behind the HTTP API.
9. FastAPI and MCP both use `SearchEngine`; each entry point constructs its own instances.
10. Evaluation records every query, model call, hit, score, citation, cost, and latency.

[`retrieval.md`](retrieval.md) covers index variants and the retrieval grid.
[`api.md`](api.md) lists HTTP routes and environment variables.
[`mcp.md`](mcp.md) defines the MCP tools. [`corpus.md`](corpus.md) records the
corpus source and conversion.
