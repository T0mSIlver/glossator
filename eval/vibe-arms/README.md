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

## Known biases

- VA's history answers use commit dates while the gold uses the fortnightly snapshot
  grid (D-048: a point date scores at most partial).
- The Vibe `bash` tool description tells the model to prefer `read_file` and `grep`
  tools that the shell arms do not have; the model sometimes calls them and gets an
  unknown-tool error. It costs a turn and applies to V0, VA, VB and VD alike.
- `mined2-066` is a known reference defect in `eval/demo.jsonl` (see its README).
- 30 questions: an interval of about ±0.17 on correctness. Only large gaps are readable.
