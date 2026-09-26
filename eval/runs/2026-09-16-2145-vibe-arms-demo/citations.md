# Citation support

Each documentation link in an answer, resolved to the section its anchor names (with subsections) or the whole page, judged by `zai:glm-5.3` against the claim the answer attached it to (`citation-support/v1`). A link to a page outside the corpus scores as unsupported.

| cell | answers citing | links / answer | link support | links supported | answerable with a supported link | to a section | anchor missing | not in corpus |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| vibe-medium35-high / V0 | 0.97 | 1.13 | 0.06 | 0.03 | 0.00 | 0.06 | 0.12 | 0.79 |
| vibe-medium35-high / VA | 0.80 | 1.33 | 0.75 | 0.60 | 0.80 | 0.60 | 0.30 | 0.05 |
| vibe-medium35-high / VB | 0.90 | 1.57 | 0.71 | 0.51 | 0.80 | 0.66 | 0.15 | 0.00 |
| vibe-medium35-high / VC | 1.00 | 1.80 | 0.79 | 0.67 | 0.85 | 0.78 | 0.09 | 0.00 |
| vibe-medium35-high / VD | 1.00 | 1.50 | 0.77 | 0.62 | 0.85 | 0.76 | 0.13 | 0.00 |

`link support` scores supported 1, partial 0.5, unsupported 0 over links; `answerable with a supported link` is the share of answerable questions whose answer carries at least one fully supported link, the page-agnostic replacement for `on gold`. It counts answerable questions other than history rows: a history answer's dates come from the dated snapshots, and no page states when it was added, so every surface scores unsupported there.
