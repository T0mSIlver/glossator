"""The rewording and filter prompts, versioned with every row they produce."""

from __future__ import annotations

from glossator.eval.perturb.models import CHATTY, KEYWORDS, VAGUE, WRONG_TERM

PROMPT_VERSION = "perturb-v1"

SYSTEM = (
    "You degrade the wording of questions about Mistral AI's platform documentation, to "
    "test a documentation search system on badly worded input. You never change what is "
    "being asked and you never add information. The degraded question must have exactly "
    "the same correct answer as the original: same feature, same parameter, same model, "
    "same scope. Do not answer the question. Do not explain yourself. Return JSON only."
)

KIND_INSTRUCTIONS: dict[str, str] = {
    KEYWORDS: (
        "Reduce the question to three to six search keywords, the way someone types into a "
        "search box. Keep the words that carry the subject, including identifiers and model "
        "names. Drop question words, articles and grammar. Add no word the question does not "
        "imply."
    ),
    VAGUE: (
        "Rewrite the question as a user who does not know the product's vocabulary would ask "
        "it. Replace the documentation's terms with everyday descriptions of the same thing, "
        "in one sentence. Keep numbers and quoted values. Do not name the feature, the "
        "parameter or the endpoint the original names, and do not describe a different one."
    ),
    WRONG_TERM: (
        "Replace exactly one product term in the question with a plausible wrong one, the way "
        "a user who half-remembers the documentation would: `temperature` for `top_p`, agent "
        "for workflow, embeddings for tokenization. Change nothing else: the rest of the "
        "question must stay word for word, and what is being asked about must still be "
        "recognizable from the rest. Report the term you removed and the one you put in its "
        "place."
    ),
    CHATTY: (
        "Bury the question in two sentences of context about what the user is building, in "
        "the first person. The request must still be there and must still be the only thing "
        "asked. Invent nothing about the product: the context is about the user's own project "
        "and may not state or assume any fact about Mistral's platform."
    ),
}

FILTER_INSTRUCTIONS = (
    "Two versions of a question about Mistral AI's platform documentation are below: the "
    "original, and a deliberately degraded rewording of it. Decide whether the degraded "
    "version still asks for the same thing, so that a correct answer to the original is a "
    "correct answer to it.\n\n"
    "Judge intent, not quality. Bad grammar, misspellings, missing question words, bare "
    "keywords, vagueness, a wrong product term and irrelevant surrounding chatter are all "
    "expected here and none of them is a reason to fail it. Set asks_the_same_thing to "
    "false only when the degraded version asks about a different feature, parameter, model "
    "or scope, when it has become so unspecific that several different documentation "
    "sections would answer it equally well, or when the request has disappeared. Set "
    "adds_facts to true if the degraded version states or assumes anything about Mistral's "
    "platform that the original did not. Give one concrete reason."
)
