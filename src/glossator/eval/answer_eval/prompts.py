"""The judge's prompts.

A verdict is only comparable to another verdict written by the same words, so the
version and the hashes are recorded with every run and a rewording is a new version,
not an edit.
"""

from __future__ import annotations

import hashlib

JUDGE_VERSION = "answer-judge/v2"

JUDGE_SYSTEM = """You grade answers produced by a documentation question-answering system over Mistral AI's platform documentation.

You are given the question, a short reference answer written by the dataset, the answer under test, and the citations the answer carries. Each citation shows its number, the quote used in the answer, and the cited passage verbatim. Page titles, URLs, and other page identifiers are withheld. You have no other access to the documentation: if a claim is not supported by a passage shown to you, it is not supported.

Grade three things, independently.

1. correctness: does the answer under test agree with the reference answer on the substance the question asks about? "correct" means a developer following it would be right; "partial" means it is right as far as it goes but leaves out something the reference answer states; "wrong" means it contradicts the reference answer, answers a different question, or invents a fact. Extra correct detail is not a penalty. Different wording is not a penalty. For a question the documentation cannot answer, the reference answer says so, and only an answer that declines to answer is correct.

2. groundedness: count the factual claims the answer makes -- statements about the product that could be checked, not pleasantries, headings, or restatements of the question -- and count how many of them are supported by the passages shown with the citations. Judge support against those passages alone, never against what you happen to know about Mistral.

3. citation relevance: for each citation, does the passage it points at support the sentence it is attached to in the answer? A citation that supports some other sentence, or nothing in the answer, is not relevant.

Be strict and be brief. Every reason is one sentence."""

JUDGE_USER = """QUESTION
{question}

REFERENCE ANSWER
{reference_answer}

ANSWER UNDER TEST
{answer_markdown}

CITATIONS IN THE ANSWER UNDER TEST
{citations}"""

JUDGE_NO_CITATIONS = "(the answer carries no verified citation)"

JUDGE_CITATION = """[{n}]
quoted by the answer: "{quote}"
passage the citation points at, verbatim:
{source_text}"""

JUDGE_PROMPT_HASHES = {
    name: hashlib.sha256(prompt.encode()).hexdigest()[:16]
    for name, prompt in {
        "judge_system": JUDGE_SYSTEM,
        "judge_user": JUDGE_USER,
        "judge_citation": JUDGE_CITATION,
    }.items()
}
