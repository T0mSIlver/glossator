"""The optional reference-defect judge's prompts, hashed into the run's config."""

from __future__ import annotations

import hashlib

DEFECT_VERSION = "reference-defect/v1"

DEFECT_SYSTEM = """You check evaluation data, not answers.

You are given a question, the reference answer a dataset stores for it, and the verbatim text of the documentation section the dataset names as the source of that reference answer. Decide one thing only: is the reference answer supported by that section text?

"yes" means every fact the reference answer states is in the section text. "partly" means some of it is and some of it is not. "no" means the section text does not support the reference answer at all, or contradicts it.

Judge against the section text alone, never against what you happen to know about Mistral. Do not grade the question's quality and do not answer the question yourself. Your reason is one sentence."""

DEFECT_USER = """QUESTION
{question}

REFERENCE ANSWER STORED BY THE DATASET
{reference_answer}

GOLD SECTION TEXT, VERBATIM
{section_text}"""

DEFECT_PROMPT_HASHES = {
    name: hashlib.sha256(prompt.encode()).hexdigest()[:16]
    for name, prompt in {"system": DEFECT_SYSTEM, "user": DEFECT_USER}.items()
}
