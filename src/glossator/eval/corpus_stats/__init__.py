"""Page sizes of the vendored corpus, counted with the Medium 3.5 tokenizer.

The surface redesign (D-029a) needs to know how many pages one ``read_page``
call can carry at an 8k- or 16k-token budget, and that depends on how large a
documentation page actually is in the tokens of the model that reads the result.
Every page of the vendored corpus is therefore measured with the real Mistral
Medium 3.5 tokenizer (model id ``mistral-medium-2604``), beside the character
count and the chunk count under the shipped ``sec1024`` chunking.

The tokenizer is *not* the one ``glossator.answer.context`` counts with: that
loader pins ``MistralTokenizer.v1()`` so context budgets stay comparable with
the chunk sizes the chunker built from them (D-010a). v1 is an older model's
sentencepiece tokenizer; Medium 3.5 uses tekken, so this module loads it
explicitly from the model's repository through ``MistralTokenizer.from_hf_hub``
and the numbers here are never mixed with v1 counts.

The figure is a hand-written SVG (matplotlib is not a dependency and the charts
module has no histogram shape): a log-x histogram with reference lines at the
budgets a tool call plausibly has.

Usage:
    uv run --with huggingface_hub python -m glossator.eval.corpus_stats
"""
