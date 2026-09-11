# Corpus map

A single HTML page that shows the vendored docs.mistral.ai corpus the way the
MCP tools name it: paths, pages, sections, anchors, keys, chunks, the share of
characters inside code fences, and the sections flagged as noise (D-047). Tom
read it to decide the section key and citation link design; the terms it
defines are the ones DECISIONS.md D-047 fixes.

Build it from the repository root:

```bash
uv run python eval/corpus-map/corpus_map.py eval/corpus-map/corpus.json
uv run python eval/corpus-map/build.py eval/corpus-map
```

`corpus_map.py` uses the same loader and chunker as the index, so its counts
match the served index exactly (411 pages, 4,016 sections, 4,440 chunks at
commit 2e094f7). `build.py` injects the JSON into `template.html` and writes
`corpus-map.html`, about 2 MB, which is not committed.
