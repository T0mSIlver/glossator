"""Model cards and the capability matrix, derived from the docs repo's TypeScript.

Model capabilities exist only as TypeScript object literals rendered by React, so
there is no page to normalize and no table to lift (D-006). These pages are
synthesized instead: one card per model at its live `/models/<slug>` URL, plus one
matrix page at `/models` that answers "which models support X" from a single chunk.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

from . import SITE_ORIGIN
from .tsdata import FUNCTION, TsParseError, parse_named_const, parse_object_after

log = structlog.get_logger(__name__)

MODELS_URL_PREFIX = "/models"

# The localizable descriptions sit inside an arrow function; the text itself is a
# plain template literal, so it is lifted straight from the source.
_DESCRIPTION = re.compile(
    r"\bdescription:\s*l\.text\(\s*`(?P<text>[^`]*)`",
)
_SHORT_DESCRIPTION = re.compile(
    r"\bshortDescription:\s*l\.text\(\s*`(?P<text>[^`]*)`",
)

_ENDPOINT_GROUPS: dict[str, str] = {
    "chat-completions": "Chat completions",
    "conversations": "Agents and conversations",
    "agents": "Agents and conversations",
    "ocr": "Document processing",
    "audio-transcriptions": "Audio",
    "audio-speech": "Audio",
    "embeddings": "Embeddings",
    "moderations": "Moderation",
    "chat-moderations": "Moderation",
    "fim-completions": "Code completion",
    "batch": "Batch",
}


@dataclass(frozen=True)
class Feature:
    key: str
    name: str
    link: str
    endpoints: tuple[str, ...]

    @property
    def group(self) -> str:
        for endpoint in self.endpoints:
            group = _ENDPOINT_GROUPS.get(endpoint)
            if group is not None:
                return group
        return "Other"


@dataclass
class ModelRecord:
    """One model file, read as data."""

    slug: str
    name: str
    raw: dict[str, Any]
    description: str = ""
    short_description: str = ""
    source_path: str = ""

    @property
    def url_path(self) -> str:
        return f"{MODELS_URL_PREFIX}/{self.slug}"

    @property
    def api_names(self) -> list[str]:
        identifiers = self.raw.get("identifiers") or {}
        names = identifiers.get("apiNames") or []
        return [str(name) for name in names]

    @property
    def features(self) -> list[str]:
        capabilities = self.raw.get("capabilities") or {}
        return [str(key) for key in capabilities.get("features") or []]

    @property
    def status(self) -> str:
        return str(self.raw.get("status") or "")

    @property
    def context_length(self) -> str:
        value = self.raw.get("contextLength")
        return str(value) if value else ""


@dataclass
class ModelCatalog:
    models: list[ModelRecord] = field(default_factory=list)
    features: dict[str, Feature] = field(default_factory=dict)
    modalities: dict[str, str] = field(default_factory=dict)
    unknown_features: set[str] = field(default_factory=set)


def load_catalog(repo_root: Path) -> ModelCatalog:
    """Read every model file and the feature/modality tables.

    A file that does not parse raises: a silently skipped model would show up as a
    missing answer, not as a build failure.
    """
    schema_path = repo_root / "src" / "schema" / "models" / "schema.ts"
    schema_source = schema_path.read_text(encoding="utf-8")
    raw_features = parse_named_const(schema_source, "AVAILABLE_FEATURES")
    raw_modalities = parse_named_const(schema_source, "AVAILABLE_MODALITIES")

    catalog = ModelCatalog(
        features={
            key: Feature(
                key=key,
                name=str(value.get("name", key)),
                link=str(value.get("link", "")),
                endpoints=tuple(str(e) for e in value.get("endpoints") or []),
            )
            for key, value in raw_features.items()
            if isinstance(value, dict)
        },
        modalities={
            key: str(value.get("name", key))
            for key, value in raw_modalities.items()
            if isinstance(value, dict)
        },
    )

    models_dir = repo_root / "src" / "schema" / "models" / "models"
    for path in sorted(models_dir.glob("*.ts")):
        if path.name == "index.ts":
            continue
        source = path.read_text(encoding="utf-8")
        try:
            data = parse_object_after(source, "export default")
        except TsParseError as error:
            raise TsParseError(f"{path}: {error}") from error
        slug = data.get("slug")
        name = data.get("name")
        if not isinstance(slug, str) or not isinstance(name, str):
            raise TsParseError(f"{path}: model is missing a string slug or name")
        description = _DESCRIPTION.search(source)
        short = _SHORT_DESCRIPTION.search(source)
        catalog.models.append(
            ModelRecord(
                slug=slug,
                name=name,
                raw={key: value for key, value in data.items() if value is not FUNCTION},
                description=_clean(description.group("text")) if description else "",
                short_description=_clean(short.group("text")) if short else "",
                source_path=str(path.relative_to(repo_root)),
            )
        )

    catalog.models.sort(key=lambda model: model.slug)
    for model in catalog.models:
        for key in model.features:
            if key not in catalog.features:
                catalog.unknown_features.add(key)
    if catalog.unknown_features:
        log.warning("features not in AVAILABLE_FEATURES", keys=sorted(catalog.unknown_features))
    return catalog


def render_model_page(model: ModelRecord, catalog: ModelCatalog) -> str:
    """One model card: identifiers, status, modalities, features, pricing, weights."""
    lines: list[str] = [f"# {model.name}", ""]
    if model.description:
        lines += [model.description, ""]
    elif model.short_description:
        lines += [model.short_description, ""]

    lines += ["## Overview", ""]
    lines += _definition_table(
        [
            ("API names", ", ".join(f"`{name}`" for name in model.api_names)),
            ("Slug", f"`{model.slug}`"),
            ("Status", model.status),
            ("Release date", str(model.raw.get("releaseDate") or "")),
            ("Version", str(model.raw.get("version") or "")),
            ("Type", str(model.raw.get("type") or "")),
            ("Class", str(model.raw.get("class") or "")),
            ("Context length", model.context_length),
            ("Output token limit", str(model.raw.get("outputTokenLimit") or "")),
            ("Legacy", "yes" if model.raw.get("legacy") else "no"),
        ]
    )

    capabilities = model.raw.get("capabilities") or {}
    inputs = [catalog.modalities.get(str(k), str(k)) for k in capabilities.get("input") or []]
    outputs = [catalog.modalities.get(str(k), str(k)) for k in capabilities.get("output") or []]
    lines += ["", "## Modalities", ""]
    lines += [f"- Input: {', '.join(inputs) or 'not documented'}"]
    lines += [f"- Output: {', '.join(outputs) or 'not documented'}"]

    lines += ["", "## Features", ""]
    if model.features:
        for key in model.features:
            feature = catalog.features.get(key)
            if feature is None:
                lines.append(f"- {key}")
                continue
            link = f"{SITE_ORIGIN}{feature.link}" if feature.link.startswith("/") else feature.link
            lines.append(f"- [{feature.name}]({link}) (`{key}`)")
    else:
        lines.append(f"{model.name} exposes no endpoint features in the model catalog.")

    lines += ["", "## Pricing", ""]
    lines += _pricing_lines(model)

    weights = model.raw.get("weights") or []
    if isinstance(weights, list) and weights:
        lines += ["", "## Weights", ""]
        for weight in weights:
            if not isinstance(weight, dict):
                continue
            parts = [str(weight.get("name") or "Weights")]
            if weight.get("parameters"):
                parts.append(f"{weight['parameters']}B parameters")
            if weight.get("license"):
                parts.append(f"license {weight['license']}")
            if weight.get("contextSize") and weight["contextSize"] != "--":
                parts.append(f"context {weight['contextSize']}")
            line = f"- {', '.join(parts)}"
            if weight.get("url"):
                line += f" — [weights]({weight['url']})"
            lines.append(line)

    metadata = model.raw.get("metadata") or {}
    if isinstance(metadata, dict) and any(metadata.values()):
        lines += ["", "## Lifecycle", ""]
        for label, key in (
            ("Deprecated", "deprecated"),
            ("Deprecation date", "deprecationDate"),
            ("Retirement date", "retirementDate"),
            ("Replacement", "replacement"),
        ):
            if metadata.get(key):
                lines.append(f"- {label}: {metadata[key]}")

    links = [
        ("Blog post", model.raw.get("bloglink")),
        ("Paper", model.raw.get("paperlink")),
        ("Playground", model.raw.get("playground")),
    ]
    present = [(label, url) for label, url in links if isinstance(url, str) and url]
    if present:
        lines += ["", "## Links", ""]
        lines += [f"- [{label}]({url})" for label, url in present]

    lines += [
        "",
        "## Capability matrix",
        "",
        f"See the [model capability matrix]({SITE_ORIGIN}{MODELS_URL_PREFIX}) for every "
        "model that shares these features.",
    ]
    return "\n".join(lines).strip() + "\n"


def render_capability_matrix(catalog: ModelCatalog) -> str:
    """The `/models` page: one table per feature group, plus a list per feature."""
    by_group: dict[str, list[Feature]] = defaultdict(list)
    for feature in catalog.features.values():
        by_group[feature.group].append(feature)

    lines: list[str] = [
        "# Model capability matrix",
        "",
        "Which Mistral models support which API features, generated from the model "
        "catalog. Each section covers one group of features: the table has one row "
        "per model and one column per feature, `yes` meaning the model supports it, "
        "and the list under the table names every model that supports each feature.",
        "",
        "## All models",
        "",
    ]
    lines += _definition_rows(
        ["Model", "API names", "Status", "Context", "Release date"],
        [
            [
                f"[{model.name}]({SITE_ORIGIN}{model.url_path})",
                ", ".join(f"`{name}`" for name in model.api_names),
                model.status,
                model.context_length or "—",
                str(model.raw.get("releaseDate") or "—"),
            ]
            for model in catalog.models
        ],
    )

    for group in sorted(by_group):
        features = sorted(by_group[group], key=lambda feature: feature.name)
        models = [
            model
            for model in catalog.models
            if any(key in model.features for key in (f.key for f in features))
        ]
        lines += ["", f"## {group}", ""]
        if not models:
            lines.append("No models in the catalog expose these features.")
            continue
        lines += _definition_rows(
            ["Model", *[feature.name for feature in features]],
            [
                [
                    f"[{model.name}]({SITE_ORIGIN}{model.url_path})",
                    *["yes" if feature.key in model.features else "—" for feature in features],
                ]
                for model in models
            ],
        )
        lines.append("")
        for feature in features:
            supported = [model for model in catalog.models if feature.key in model.features]
            link = f"{SITE_ORIGIN}{feature.link}" if feature.link.startswith("/") else feature.link
            names = ", ".join(
                f"{model.name} (`{model.api_names[0]}`)" if model.api_names else model.name
                for model in supported
            )
            lines.append(
                f"- **[{feature.name}]({link})** (`{feature.key}`), "
                f"{len(supported)} models: {names or 'none'}"
            )

    return "\n".join(lines).strip() + "\n"


def _pricing_lines(model: ModelRecord) -> list[str]:
    pricing = model.raw.get("pricing") or {}
    if not isinstance(pricing, dict):
        return ["Pricing is not published for this model."]
    if pricing.get("free"):
        return ["Free."]
    out: list[str] = []
    for label, key in (("Input", "input"), ("Output", "output")):
        entries = pricing.get(key) or []
        rendered = [_price_entry(entry) for entry in entries if isinstance(entry, dict)]
        rendered = [entry for entry in rendered if entry]
        if rendered:
            out.append(f"- {label}: {'; '.join(rendered)}")
    if not out and pricing.get("price") is not None:
        out.append(f"- {_price_entry(pricing)}")
    return out or ["Pricing is not published for this model."]


def _price_entry(entry: dict[str, Any]) -> str:
    price = entry.get("price")
    if price is None:
        return ""
    denominator = str(entry.get("denominator") or "")
    text = f"{price} USD{denominator}"
    if entry.get("priceEur") is not None:
        text += f" ({entry['priceEur']} EUR{denominator})"
    if entry.get("label"):
        text = f"{entry['label']}: {text}"
    return text


def _definition_table(rows: list[tuple[str, str]]) -> list[str]:
    present = [(label, value) for label, value in rows if value]
    return _definition_rows(["Field", "Value"], [[label, value] for label, value in present])


def _definition_rows(header: list[str], rows: list[list[str]]) -> list[str]:
    out = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    out += ["| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |" for row in rows]
    return out


def _clean(text: str) -> str:
    return " ".join(text.split())
