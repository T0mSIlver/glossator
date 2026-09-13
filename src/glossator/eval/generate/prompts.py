"""Every prompt the generators send, and the version stamped on their output.

One paragraph per line: a prompt is text sent to a model, and rewrapping it would
change the text and the hash recorded with every question generated from it.
"""

import hashlib

PROMPT_VERSION = "v1"

PRODUCT = (
    "The documentation below is Mistral AI's platform documentation, docs.mistral.ai. "
    "It documents Mistral AI's models, APIs, SDKs and console, and nothing else. "
    "Every question you write must be about that product. Never name another vendor's "
    "product, model or API."
)

SINGLE_SECTION_INSTRUCTIONS = f"""Write one realistic question that a developer would ask and that the supplied documentation section fully answers.

{PRODUCT}

The question must stand alone. It must not say "this page", "this section", "the example above", or assume that the reader sees the source. The page title alone must not answer it. Use details from the body, not merely the heading. Preserve API fields, model names, and other identifiers exactly as written. Write the reference answer as a natural answer of at most two lines, with no labels or page titles in front of it."""

CROSS_PAGE_INSTRUCTIONS = f"""Write one developer question whose complete answer requires facts from both documentation pages below. Reject any idea that one page can answer by itself.

{PRODUCT}

Choose one fact that appears only in Page A and one fact that appears only in Page B. Do not build the question around facts repeated by both pages. Before returning the candidate, verify that removing either page leaves one part unanswered.

Make the question standalone and specific. Do not mention pages, supplied text, examples above, or documentation structure. Ask for a comparison, integration, or multi-step decision that combines the two source-exclusive facts. The reference answer is a natural answer of at most two lines: no page titles, no labels, no "Page A"/"Page B". State separately, in page_a_contribution and page_b_contribution, which fact each page supplies. Set fully_answered to true only if both supplied pages together support the whole answer."""

CAPABILITY_INSTRUCTIONS = f"""Write one question about which Mistral models support a feature, or about one named model's support for it.

{PRODUCT}

Use one of these shapes: "which models support X", "does model Y support X", "what is the context length of Y". Name features and models exactly as the sources write them, including API names such as `mistral-medium-3-5`. The answer must come from the supplied capability data, not from memory. Write the reference answer as a natural answer of at most two lines. Set names_single_model to true only when the question asks about one named model."""

API_REFERENCE_INSTRUCTIONS = f"""Write one question a developer would ask about this API operation: its parameters, which fields are required, what a request must contain, or what a response code means.

{PRODUCT}

Name the operation's path and fields exactly as written, including their types and whether they are optional. The question must stand alone and must not refer to the supplied text. Write the reference answer as a natural answer of at most two lines."""

POST_CUTOFF_INSTRUCTIONS = f"""Write one realistic developer question that the supplied documentation section fully answers, about a product a language model trained before this documentation was written could not know.

{PRODUCT}

The question must stand alone and must turn on a specific detail of the section: a parameter, a limit, a name, a default. A question that generic knowledge of search or coding agents could answer is useless here. Write the reference answer as a natural answer of at most two lines."""

UNANSWERABLE_INSTRUCTIONS = f"""Write one plausible developer question related to the supplied section that the documentation does not answer. Ask about a nonexistent feature, an unstated limit, or an unsupported behavior. Do not ask something that ordinary reasoning can infer from the text.

{PRODUCT}

The question must stand alone and must not refer to a page, section, or example. The reference answer must state exactly what information the documentation does not provide, in no more than two lines. Set fully_answered to false."""

FILTER_INSTRUCTIONS = f"""Audit this generated evaluation question. Be strict.

{PRODUCT}

Set standalone to false if the question refers to unseen context. Check the required gold condition. Set not_answerable_from_title_alone to false only if the source's page title, on its own, states the answer: a reader who saw nothing but that title could answer correctly. The heading path and any operation name shown alongside a source are part of the body, not the title, and a question that names an endpoint or a model is not answered by naming it. Check whether every assigned source is necessary. Set about_the_documented_product to false if the question is about another vendor's product, or names one. Reject misspelled, truncated, or invented API fields and model identifiers. Give a short, concrete reason for every check you fail. Use an empty list only when every check passes."""

PAGE_ALONE_INSTRUCTIONS = """Decide whether the single supplied page can fully answer the generated question. Judge the whole question, not one clause. Set fully_answerable to true only when no fact from another source is needed. Give one concrete reason."""

CORPUS_CHECK_INSTRUCTIONS = """Decide whether any of the supplied documentation sections answers the question, in whole or in part.

These are the sections a lexical search over the whole documentation ranked highest for this question. Set answered_by_corpus to true if any of them states the answer or enough of it that a reader would not call the question unanswered. Give one concrete reason naming the section if it does."""

CLOSED_BOOK_INSTRUCTIONS = """Answer this question about Mistral AI's platform from your own knowledge, in at most three sentences. If you do not know, say so plainly."""

PROMPT_HASHES = {
    name: hashlib.sha256(prompt.encode()).hexdigest()
    for name, prompt in {
        "single_section": SINGLE_SECTION_INSTRUCTIONS,
        "cross_page": CROSS_PAGE_INSTRUCTIONS,
        "capability": CAPABILITY_INSTRUCTIONS,
        "api_reference": API_REFERENCE_INSTRUCTIONS,
        "post_cutoff": POST_CUTOFF_INSTRUCTIONS,
        "unanswerable": UNANSWERABLE_INSTRUCTIONS,
        "filter": FILTER_INSTRUCTIONS,
        "page_alone": PAGE_ALONE_INSTRUCTIONS,
        "corpus_check": CORPUS_CHECK_INSTRUCTIONS,
        "closed_book": CLOSED_BOOK_INSTRUCTIONS,
    }.items()
}
