# Citation support

Each documentation link in an answer, resolved to the section its anchor names (with subsections) or the whole page, judged by `zai:glm-5.3` against the claim the answer attached it to (`citation-support/v1`). A link to a page outside the corpus scores as unsupported.

| cell | answers citing | links / answer | link support | links supported | answerable with a supported link | to a section | anchor missing | not in corpus |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| vibe-medium35-high / V0 | 1.00 | 1.35 | 0.01 | 0.00 | 0.00 | 0.02 | 0.05 | 0.93 |
| vibe-medium35-high / VA | 0.88 | 1.62 | 0.73 | 0.56 | 0.62 | 0.52 | 0.35 | 0.06 |
| vibe-medium35-high / VB | 0.98 | 1.52 | 0.86 | 0.75 | 0.83 | 0.77 | 0.14 | 0.01 |
| vibe-medium35-high / VC | 1.00 | 1.57 | 0.87 | 0.80 | 0.92 | 0.78 | 0.15 | 0.00 |
| vibe-medium35-high / VD | 0.98 | 1.58 | 0.83 | 0.69 | 0.90 | 0.79 | 0.13 | 0.00 |

`link support` scores supported 1, partial 0.5, unsupported 0 over links; `answerable with a supported link` is the share of answerable questions whose answer carries at least one fully supported link, the page-agnostic replacement for `on gold`. It counts answerable questions other than history rows: a history answer's dates come from the dated snapshots, and no page states when it was added, so every surface scores unsupported there.
