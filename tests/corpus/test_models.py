"""Reading a model catalog out of TypeScript object literals."""

from __future__ import annotations

from pathlib import Path

import pytest

from glossator.corpus.mistral_docs.models import (
    load_catalog,
    render_capability_matrix,
    render_model_page,
)
from glossator.corpus.mistral_docs.tsdata import TsParseError, parse_named_const

SCHEMA_TS = """
export const AVAILABLE_MODALITIES = {
  text: { name: 'Text', description: 'Text' },
  image: { name: 'Image', description: 'Image' },
  reasoning: { name: 'Reasoning', description: 'Reasoning' },
} as const;

export const AVAILABLE_FEATURES = {
  'chat-completions': {
    name: 'Chat Completions',
    link: '/studio/conversations/chat-completion',
    endpoints: ['chat-completions'],
  },
  'function-calling': {
    name: 'Function Calling',
    link: '/studio/conversations/function-calling',
    endpoints: ['chat-completions', 'conversations'],
  },
  batching: { name: 'Batching', link: '/studio/batch-processing', endpoints: ['batch'] },
} as const satisfies Features;
"""

MODEL_TS = """
import { StaticModel } from '../schema';
export default {
  name: 'Mistral Medium 3.5',
  describe: (l) => ({
    description: l.text(`Our frontier-class multimodal model.`, { context: 'Full description' }),
    shortDescription: l.text(`Frontier-class multimodal.`, { context: 'Short description' }),
  }),
  slug: 'mistral-medium-3-5-26-04',
  releaseDate: '2026-04-28',
  version: '26.04',
  frontier: true,
  class: 'Generalist',
  type: 'Open',
  // A trailing comment, and a block one below.
  /* still data */
  status: 'GA',
  weights: [
    {
      name: 'Weights',
      license: 'Modified MIT',
      url: 'https://huggingface.co/mistralai/Mistral-Medium-3.5-128B',
      parameters: '128',
      minGpuRam: { bf16: '256', fp8: '128', fp4: null, fp4_16: null },
      contextSize: '256k',
    },
  ],
  contextLength: '256k',
  ratings: { speed: 2.0, performance: 4.5, input: 4.0, output: 2.0 },
  pricing: {
    type: 'custom',
    free: false,
    input: [{ type: 'range', price: 1.5, priceEur: 1.25, denominator: '/M Tokens' }],
    output: [{ type: 'range', price: 7.5, priceEur: 6.4, denominator: '/M Tokens' }],
  },
  identifiers: { apiNames: ['mistral-medium-3-5', 'mistral-medium-latest'] },
  capabilities: {
    input: ['text', 'image'],
    output: ['reasoning', 'text'],
    features: ['function-calling', 'chat-completions', 'batching'],
  },
  metadata: {},
  playground: 'https://console.mistral.ai/build/playground',
  legacy: false,
} as const satisfies StaticModel;
"""


def _repo(tmp_path: Path, model_source: str = MODEL_TS) -> Path:
    schema_dir = tmp_path / "src" / "schema" / "models"
    (schema_dir / "models").mkdir(parents=True)
    (schema_dir / "schema.ts").write_text(SCHEMA_TS, encoding="utf-8")
    (schema_dir / "models" / "index.ts").write_text("export const models = [];", encoding="utf-8")
    (schema_dir / "models" / "mistral-medium-3-5-26-04.ts").write_text(
        model_source, encoding="utf-8"
    )
    return tmp_path


def test_catalog_reads_one_model_file(tmp_path: Path) -> None:
    catalog = load_catalog(_repo(tmp_path))
    assert len(catalog.models) == 1
    model = catalog.models[0]
    assert model.name == "Mistral Medium 3.5"
    assert model.slug == "mistral-medium-3-5-26-04"
    assert model.url_path == "/models/mistral-medium-3-5-26-04"
    assert model.api_names == ["mistral-medium-3-5", "mistral-medium-latest"]
    assert model.features == ["function-calling", "chat-completions", "batching"]
    assert model.context_length == "256k"
    assert model.description == "Our frontier-class multimodal model."
    assert catalog.unknown_features == set()


def test_model_page_carries_identifiers_features_and_pricing(tmp_path: Path) -> None:
    catalog = load_catalog(_repo(tmp_path))
    page = render_model_page(catalog.models[0], catalog)
    assert page.startswith("# Mistral Medium 3.5")
    assert "`mistral-medium-latest`" in page
    assert "| Status | GA |" in page
    assert "| Release date | 2026-04-28 |" in page
    assert "- Input: Text, Image" in page
    assert (
        "[Function Calling](https://docs.mistral.ai/studio/conversations/function-calling)" in page
    )
    assert "- Input: 1.5 USD/M Tokens (1.25 EUR/M Tokens)" in page
    assert "Modified MIT" in page


def test_capability_matrix_lists_the_models_per_feature(tmp_path: Path) -> None:
    catalog = load_catalog(_repo(tmp_path))
    matrix = render_capability_matrix(catalog)
    assert "# Model capability matrix" in matrix
    assert "## Chat completions" in matrix
    assert "| Model | Chat Completions | Function Calling |" in matrix
    assert "**[Function Calling]" in matrix
    assert "1 models: Mistral Medium 3.5 (`mistral-medium-3-5`)" in matrix


def test_an_unreadable_model_file_fails_loudly(tmp_path: Path) -> None:
    with pytest.raises(TsParseError):
        load_catalog(_repo(tmp_path, "export default { name: 'Broken', slug: "))


def test_a_model_without_a_slug_fails_loudly(tmp_path: Path) -> None:
    with pytest.raises(TsParseError, match="slug or name"):
        load_catalog(_repo(tmp_path, "export default { name: 'Nameless' } as const;"))


def test_named_const_must_exist() -> None:
    with pytest.raises(TsParseError):
        parse_named_const("export const OTHER = {};", "AVAILABLE_FEATURES")
