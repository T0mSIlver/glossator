# Corpus provenance

- Source repository: `mistralai/platform-docs-public`.
- Source commit: `2e094f7bbe1395de4a738a3483def3573143d973`, dated 2026-09-07.
- License: Apache-2.0, preserved in `corpus/mistral-docs/LICENSE` and `corpus/NOTICE`.
- Contents: 296 documentation pages, 49 API reference pages, and 66 model cards.

```bash
make corpus-refresh
make corpus-refresh REF=<commit-or-tag>
make corpus-check
make snapshots
```

`make corpus-check` runs offline corpus tests and validates every URL and anchor
against the live site. CI runs the live check weekly.

The eight dated corpora used by the history tool live under
`corpus/snapshots/`. To add a stored date, add it to `SNAPSHOT_DATES` in
`glossator.corpus.snapshots`, run `make snapshots`, review the new manifest row,
then run `uv run python -m glossator.changelog build` and commit the corpus,
manifest, and changelog together.

Page sizes in Mistral Medium 3.5 tokens, which decided how `read_page` reads a
large page, are measured in `../eval/corpus-stats/`.
