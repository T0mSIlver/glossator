# eval/demo.jsonl

The thirty questions the Mistral Work demo is measured on: the Skill plus the `mistral-docs`
Connector, on a Mistral model with reasoning, through the Conversations API stand-in
(`glossator.eval.work_proxy`). Every row is traceable: the modern and unanswerable rows are
copied verbatim from the mined sets, id included, with `generator.demo_source` naming the
file; the history rows are new and name their evidence.

- Questions: 30 (history 5, single_page 14, unanswerable 5, api_reference 3, cross_page 3);
  languages: {'en': 30}
- sha256: `739c1066cb6464e42630591fa6ab62097808420cc6a2eb5c8f6903277207e2b2`

## Selection

**Twenty modern, realistic rows** from `eval/mined.jsonl` and `eval/mined-v2.jsonl`: real
stumbles on agents, MCP, Connectors, the Vibe CLI, the Search Toolkit, reasoning and model
lifecycle. Nothing on OCR or fine-tuning, and nothing a model answers from memory: every
row asks for a value, a rule or a name that sits on one documented section published after
the models' training data.

**Five unanswerable rows** on the same products, including the Search Toolkit evaluation
question that a Work session searched thirteen times for (D-044a). A correct answer says
what the documentation does say and that it does not answer the question.

**Five history rows** (`type: history`), answerable only through `mistral_docs_history`.
The gold carries `between`: the two adjacent stored snapshot dates the change lies between
(D-041 grid, fortnightly). A reference answer never names a day, and an answer that states
a point date scores at most partial (D-048).

| id | change | between | evidence |
|---|---|---|---|
| hist-001 | the Vibe CLI configuration page's model table gained GLM 5.2 | 2026-08-15 and 2026-09-01 | Work session of 2026-09-12 (the `question` form's failure, D-048); `section_history` |
| hist-002 | the GLM 5.2 model page was added | 2026-08-01 and 2026-08-15 | `phrase_history("zai-glm-5-2")` |
| hist-003 | the Agentic Search page was added | 2026-08-15 and 2026-09-01 | snapshot labels of mined-074 and mined-083 |
| hist-004 | the custom vector store page gained the partial-updates section | 2026-09-01 and 2026-09-07 | snapshot label of dev-089; `phrase_history("PatchableIndex")` |
| hist-005 | the Reasoning guide moved from `/studio-api/` to `/studio/` | 2026-08-01 and 2026-08-15 | the snapshot corpora; the August rename of D-041a |

## Known defect

`mined2-066` (which models can be chained in handoffs) is labelled unanswerable, but the
Agents introduction FAQ states that only `mistral-medium-latest` and `mistral-large-latest`
are supported (`studio/agents/introduction#which-models-are-supported`). An answer that
cites it is grounded; the judge, which sees no served passages in a consumer run, scored it
wrong in `2026-09-12-1102-demo-medium35` (D-049a). The row stays as mined so the set keeps
its digest; read that cell as a reference defect.

## Regenerate

The selection is a fixed list of ids plus the five handwritten rows; the builder lives with the
run that first used the set. Validate with `validate_against_corpus` as the mined sets are.
