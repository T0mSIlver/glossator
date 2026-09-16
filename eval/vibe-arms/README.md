# Vibe arms: the same agent, the documentation served five ways

One harness, one model, one set of answer and citation rules; only what the
agent can reach changes. The question it answers: does a coding agent with a
shell over the documentation need glossator's tools at all?

## Arms

| arm | tools | working directory |
|---|---|---|
| V0 | bash | empty (control: memory only) |
| VA | bash | `platform-docs-public` reset to `2e094f7`, git history up to it, every later commit pruned |
| VB | bash | `docs/`: `corpus/mistral-docs` as served; `snapshots/<date>/`: the eight dated corpora |
| VC | `mistral_docs_search`, `mistral_docs_read_page`, `mistral_docs_history` | empty |
| VD | bash + the three tools | as VB |

- Harness: Mistral Vibe CLI, headless (`-p`, `--output streaming`), `--legacy-harness`,
  one `VIBE_HOME` per cell holding only the arm's config and system prompt; project
  context, skills, connectors, telemetry and experiments off.
- Model: `mistral-vibe-cli-latest` (Medium 3.5), thinking `high`, as Vibe ships it.
- System prompt: `ANSWER_RULES` in `src/glossator/eval/consumer/vibe_arms.py`, the same
  for every arm (exact value first, the absence sentence, history as an interval, and
  the citation format with an example link), followed by the arm's environment
  paragraph. The user turn is the consumer evaluation's usual `PROMPT_LEAD` plus the
  question.
- Shell: `$SHELL` is `sandbox-shell`, a bubblewrap wrapper: no network, cleared
  environment (no API key, no MCP token), only the arm's directory and the system
  binaries visible, read-only. Checked in the smoke run: a V0 agent's `git clone`,
  `env` and `find /` found nothing.
- MCP arms call the deployed server (`GLOSSATOR_MCP_TOOLS` empty: all three tools).
- Judge and scoring: the consumer evaluation's own `judge` (GLM 5.3) and `score`.

## Reproduce

```bash
eval/vibe-arms/build-environments ../vibe-arms-scratch/envs
uv run python -m glossator.eval.consumer run --name <run> \
  --consumers vibe-medium35-high --arms V0,VA,VB,VC,VD \
  --questions-path eval/demo.jsonl \
  --scratch-root ../vibe-arms-scratch/cells \
  --environments-root ../vibe-arms-scratch/envs \
  --sandbox-shell eval/vibe-arms/sandbox-shell --fd-path "$(command -v fd)" \
  --mcp-url-v https://<server>/mcp --parallel 6
uv run python -m glossator.eval.consumer judge --run eval/runs/<run>
uv run python -m glossator.eval.consumer score --run eval/runs/<run> --sample-consumer vibe-medium35-high
```

## Predictions, written before the first scored run (16 Sep 2026, 21:50)

1. VB matches or beats VC on exact values, parameter names and API reference rows:
   `rg` finds a literal string that one-sentence search ranks below the top hits.
2. VC beats VB on badly worded questions, where the words in the question are not the
   words on the page.
3. History: VC and VD at or near the shipped 0.80; VB lower, because comparing eight
   directories is many calls; VA answers with commit dates, tighter than the snapshot
   grid the judge's gold uses, and may be scored partial for it.
4. Links: VC and VD resolve best, because they copy `cite:` lines. VB close behind,
   since front matter carries the URL and headings carry `{#anchor}`. VA worst: it must
   slugify headings and map source paths itself.
5. Unanswerable rows: the shell arms do better than VC. A shell agent that greps and
   finds nothing sees the absence; a search always returns plausible neighbours.
6. Cost: VB and VA read more tokens per question than VC (whole files, `cat` of large
   pages); VD mostly calls the tools and uses the shell rarely.
7. V0, the control, answers little correctly and its links resolve poorly.

## Results: `eval/runs/2026-09-16-2145-vibe-arms-demo`

30 questions from `eval/demo.jsonl`, 150 cells, 0 collection errors, 150 judged
(GLM 5.3, `answer-judge/v2`). Work is the shipped Work-proxy run on the same questions
(`2026-09-13-1306-demo-medium35-shipped`): same model, Conversations API instead of
Vibe, Skill as instructions.

| arm | correctness | api ref (3) | cross page (3) | history (5) | single page (14) | unanswerable (5) | links resolve | on gold | cost, 30 q | input tok / q | calls / q | p50 s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V0 no docs | 0.23 | 0.33 | 0.33 | 0.20 | 0.21 | 0.20 | 0.22 | 0.04 | $0.81 | 7.8k | 2.7 | 16 |
| VA raw repo | 0.42 | 0.83 | 0.67 | 0.00* | 0.57 | 0.00 | 0.92 | 0.64 | $2.42 | 225k | 18.2 | 36 |
| VB files | 0.62 | 0.67 | 0.83 | 1.00 | 0.57 | 0.20 | 0.97 | 0.68 | $1.48 | 110k | 11.7 | 17 |
| VC tools | 0.63 | 0.83 | 0.83 | 1.00 | 0.57 | 0.20 | 0.98 | 0.84 | $1.37 | 48k | 5.1 | 15 |
| VD files + tools | 0.67 | 0.83 | 0.67 | 1.00 | 0.61 | 0.40 | 0.98 | 0.76 | $0.95 | 53k | 5.3 | 14 |
| Work (shipped) | 0.60 | 0.33 | 0.67 | 0.80 | 0.64 | 0.40 | 0.96 | 0.72 | | 7.4k | 5.4 | 19 |

Costs are Vibe's own session accounting at list price. \* See VA below.

**Reading.** VB, VC, VD and Work are one result: 0.60–0.67 on 30 questions, inside the
±0.17 interval. On correctness, a shell over glossator's normalised pages is as good as
the three tools, and the tools add nothing a shell agent could not get from the files.
What the tools do buy is budget: under half the tokens (48k against 110k per question).
VD, given both, called the tools 104 times and the shell 45 times, and cost least.

**Citations: `on gold` overstated the tools' lead.** Every demo question lists exactly
one gold page, and the documentation often states a fact twice (guide and API
reference). `cite-check` (`citations.md`, `citations.jsonl`) resolves each link to the
section its anchor names and has GLM 5.3 judge whether that passage states the claim
the link is attached to. On the 20 answerable questions that are not history rows:

| arm | on gold | answer has a supported link | supported or partial | supported link, not the gold page | gold page, section does not support |
|---|---:|---:|---:|---:|---:|
| V0 | 0.00 | 0.00 | 0.10 | 0 | 0 |
| VA | 0.70 | 0.80 | 0.85 | 4 | 2 |
| VB | 0.70 | 0.80 | 1.00 | 5 | 3 |
| VC | 0.80 | 0.85 | 0.95 | 2 | 1 |
| VD | 0.75 | 0.85 | 0.95 | 3 | 1 |

The ten-point gap on the gold page becomes one question in twenty. Per link, the tools
are more precise (67% of VC's links fully supported against 51% for VB; VB cites more
pages loosely), and they land on a named section more often (0.78 against 0.66).
History rows are excluded: the dates come from the snapshots, no page states them, and
every arm's history citations score unsupported. Calibration: the five citations
checked by hand before the run agree with the judge, and a random sample of fourteen
verdicts reads right; one of the hand checks was the reviewer's error, not the
judge's (`tool_choice: "none"` is defined on the chat endpoint page only).

The raw repository is the one real gap, 0.42, and it is not the single-page rows (0.57,
level with every other arm). It is:
- **History, 0 of 5, mostly a scoring artifact.** VA answers from `git log` commit
  dates. Four of its five intervals are compatible with, and narrower than, the
  fortnightly snapshot interval in the gold (hist-003: 14–20 Aug inside 15 Aug–1 Sep),
  and the judge scores every interval that is not the gold's as wrong. The fifth hit the
  turn limit. A reference that accepted any interval inside the gold's would score VA
  near the others. What the snapshots buy is the date grid the gold was written on,
  not the ability to answer.
- **Turn limit.** 4 VA cells (and 1 VB cell) hit the 40-turn cap with no answer.
- **Unanswerable, 0 of 5.** Three of the five are turn-limit cells: VA kept searching
  for what does not exist.

## Results: `eval/runs/2026-09-16-2300-vibe-arms-consumer60`

The consumer evaluation's fixed 60 (40 mined stratified, 20 fresh, seed 0; 12
unanswerable, no history rows), same arms, harness and model, run on the Vibe plan key.
300 cells, 0 collection errors, 300 judged, 376 links checked by `cite-check`, 0 errors.
Interval on correctness about ±0.12.

| arm | correctness | api ref (14) | capability (5) | cross page (8) | post cutoff (3) | single page (18) | unanswerable (12) | answerable with a supported link (48) | links supported | anchor missing | cost, 60 q | input tok / q | stopped at the turn cap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V0 no docs | 0.23 | 0.43 | 0.20 | 0.06 | 0.17 | 0.22 | 0.17 | 0.00 | 0.00 | 0.05 | $1.09 | 7k | 0 |
| VA raw repo | 0.60 | 0.71 | 0.20 | 0.75 | 0.83 | 0.61 | 0.46 | 0.62 | 0.56 | 0.35 | $5.34 | 201k | 7 |
| VB files | 0.63 | 0.71 | 0.90 | 0.69 | 0.83 | 0.56 | 0.46 | 0.83 | 0.75 | 0.14 | $2.68 | 86k | 1 |
| VC tools | 0.68 | 0.71 | 0.60 | 0.81 | 0.67 | 0.72 | 0.54 | **0.92** | **0.80** | 0.15 | **$1.81** | 53k | 0 |
| VD files + tools | 0.64 | 0.75 | 0.60 | 0.75 | 0.83 | 0.64 | 0.42 | 0.90 | 0.69 | 0.13 | $2.32 | 85k | 1 |

**Reading, both runs together.**
- **Correctness does not separate the documentation arms.** 0.60–0.68 here, 0.62–0.67
  on the demo set, every gap inside the interval. On ordinary questions even the raw
  repository keeps up (0.60); its 0.42 on the demo set was history scored against a
  snapshot grid it did not have, absence, and turn limits.
- **Citations separate them, and in an order.** Answers carrying a link whose section
  states the claim: tools 0.92, files 0.83, raw repository 0.62. The raw repository
  links a heading anchor the site does not have on 35% of its links (it slugifies
  headings the site leaves unanchored) and hits the turn cap on 7 of 60. Glossator's
  normalised pages close most of that gap; the tools close the rest.
- **Budget separates them most.** Tools $1.81 and 53k input tokens a question; files
  $2.68 and 86k; raw repository $5.34 and 201k, at 2.6 times the latency.
- **Given both, the agent does not get better.** VD is level with VC on correctness and
  supported answers, reads more and costs more.
- **Absence stays the weakest row on every surface** (0.42–0.54 on 12 unanswerables).

So the corpus adapter is what makes a documentation corpus usable by an agent at all,
and the three tools are what make it cheap and cite precisely; a shell over the same
files gets most of the way on correctness and costs half as much again.

**Predictions against results.**
1. VB ≥ VC on exact values and API reference: not separable at n = 3.
2. VC > VB on badly worded questions: not measurable with this set; single-page rows tie.
3. History: VC and VD at the shipped 0.80 or above, held (1.00). VB lower: wrong, VB
   got 5 of 5 with `ls` and a `for` loop over the dated directories, 4 to 13 calls. VA partial: worse, scored wrong.
4. Links: held in direction, weaker than it first looked. Tools resolve best and are
   most precise per link; by supporting passage rather than gold page, VC and VD lead
   VA and VB by one question in twenty.
5. Unanswerable, shell arms better: wrong. VB 0.20, VA 0.00; only VD matched Work's
   0.40. Every arm answered `mined2-055` with an invented 128-tool limit and
   `mined2-066` from the Agents FAQ (the known reference defect).
6. Cost: held for tokens (VA 4.7×, VB 2.3× VC); VD cheapest overall.
7. V0 low: held, 0.23, links resolve 0.22.

## Known biases

- VA's history answers use commit dates while the gold uses the fortnightly snapshot
  grid (D-048: a point date scores at most partial).
- The Vibe `bash` tool description tells the model to prefer `read_file` and `grep`
  tools that the shell arms do not have; the model sometimes calls them and gets an
  unknown-tool error. It costs a turn and applies to V0, VA, VB and VD alike.
- `mined2-066` is a known reference defect in `eval/demo.jsonl` (see its README).
- 30 questions: an interval of about ±0.17 on correctness. Only large gaps are readable.
