"""The Medium 3.5 tokenizer, loaded from the model's own repository."""

from __future__ import annotations

from typing import Any, Protocol

from mistral_common.tokens.tokenizers.mistral import MistralTokenizer

MEDIUM_MODEL_ID = "mistral-medium-2604"
"""The fixed id Mistral's API answers for Mistral Medium 3.5 (D-017a)."""

MEDIUM_TOKENIZER_REPO = "mistralai/Mistral-Medium-3.5-128B"
"""Repository ``mistral-common``'s ``from_hf_hub`` reads the tekken tokenizer
file from; the model weights are never downloaded, only ``tekken.json``."""

MEDIUM_CONTEXT_TOKENS = 256_000
"""The 256k context Mistral Medium 3.5's model card states
(``/models/mistral-medium-3-5-26-04``); the corpus total is stated against it."""


class TokenCounter(Protocol):
    def __call__(self, text: str) -> int: ...


def load_medium_tokenizer() -> MistralTokenizer[Any, Any, Any, Any, Any]:
    """The tokenizer Mistral Medium 3.5 tokenizes requests with.

    ``huggingface_hub`` is not a project dependency, so the command line in the
    package docstring passes it with ``--with``; a plain ``uv run`` fails here
    with instructions rather than an import error half way through.
    """
    try:
        return MistralTokenizer.from_hf_hub(MEDIUM_TOKENIZER_REPO)
    except ImportError as error:  # pragma: no cover - depends on the environment
        raise RuntimeError(
            "loading the Medium 3.5 tokenizer needs huggingface_hub; run "
            "`uv run --with huggingface_hub python -m glossator.eval.corpus_stats`"
        ) from error


def medium_counter(
    tokenizer: MistralTokenizer[Any, Any, Any, Any, Any],
) -> TokenCounter:
    def count(text: str) -> int:
        return len(tokenizer.instruct_tokenizer.tokenizer.encode(text, bos=False, eos=False))

    return count
