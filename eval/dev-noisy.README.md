# eval/dev-noisy.jsonl

Badly worded variants of development questions, for measuring the answer strategies out of the distribution the development set was generated in. Every generated question was written by a model from the section that answers it, so it is well worded by construction (D-020a); these are the same questions as a user would have typed them, with the same gold sources and the same reference answers.

- Questions: 105 of 120 attempted (api_reference 18, capability 17, cross_page 17, post_cutoff 19, single_page 17, unanswerable 17); languages: {'en': 105}
- Noise kinds (`generator.noise`): typos 24, keywords 24, vague 24, chatty 18, wrong_term 15
- sha256: `df892be3ea190383acf69b5df647781f6f093d7f2e76b1ea22ec724da7b3bd68`
- Source: `eval/dev.jsonl` (sha256 `acf3c2e1...`), the 120-question stratified subset at seed 0, which `--limit 120 --seed 0` reproduces
- Perturbation run (records, calls, README, figures): `2026-09-09-1222-dev-noisy`
- Perturber: `glm-5.3` through the z.ai coding plan, thinking disabled, seed 0, prompts `perturb-v1`; typos are generated in code and need no model
- Each row's `generator` carries `noise`, `perturbed_from`, `original_question` and, for `wrong_term`, `noise_substitution`

Fifteen variants were dropped and recorded: seven asked something else, five added a fact the original did not carry, two came back unchanged, and one lost its provider call to a 429. `wrong_term` and `chatty` account for all of them, which is why those two kinds are the smallest.

Regenerate with:

```
uv run python -m glossator.eval.perturb --dataset eval/dev.jsonl --out eval/dev-noisy.jsonl \
    --n 120 --seed 0 --provider zai --model glm-5.3 --name dev-noisy
```
