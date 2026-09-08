"""API reference pages, built from the live OpenAPI spec.

The repo's `src/content/en/api` is 15 MB of generated MDX; the spec it was generated
from is smaller, complete and machine-readable (D-005). `sidebar-metadata.json` maps
operations onto the pages and carries the `elementId` the site uses as an HTML id, so
every emitted section anchor is a real deep link.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
import structlog
import yaml

from . import SITE_ORIGIN

log = structlog.get_logger(__name__)

OPENAPI_URL = "https://docs.mistral.ai/openapi.yaml"
API_URL_PREFIX = "/api"
MAX_SCHEMA_DEPTH = 3
_MAX_ENUM_VALUES = 12
_RELATIVE_LINK = re.compile(r"(\]\()/")


@dataclass(frozen=True)
class OperationRef:
    """One operation as the sidebar places it on a page."""

    element_id: str
    method: str
    path: str
    operation_id: str
    summary: str
    description: str
    tag: str


@dataclass(frozen=True)
class EndpointPage:
    """One `/api/endpoint/<slug>` page and the operations it documents."""

    slug: str
    label: str
    operations: tuple[OperationRef, ...]

    @property
    def url_path(self) -> str:
        return f"{API_URL_PREFIX}/{self.slug}"


@dataclass
class OpenApiSource:
    spec: dict[str, Any]
    md5: str
    origin: str


def load_openapi(
    cache_dir: Path,
    url: str = OPENAPI_URL,
    offline_path: Path | None = None,
    refresh: bool = False,
) -> OpenApiSource:
    """Fetch the spec (or reuse the cached copy) and record its md5."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / "openapi.yaml"
    if offline_path is not None:
        raw = offline_path.read_bytes()
        origin = str(offline_path)
    elif cached.is_file() and not refresh:
        raw = cached.read_bytes()
        origin = f"{url} (cached)"
    else:
        log.info("fetching openapi spec", url=url)
        response = httpx.get(url, timeout=60.0, follow_redirects=True)
        response.raise_for_status()
        raw = response.content
        cached.write_bytes(raw)
        origin = url
    digest = hashlib.md5(raw, usedforsecurity=False).hexdigest()
    spec = yaml.safe_load(raw.decode("utf-8"))
    if not isinstance(spec, dict) or "paths" not in spec:
        raise ValueError(f"{origin} is not an OpenAPI document")
    log.info("openapi loaded", origin=origin, md5=digest, paths=len(spec["paths"]))
    return OpenApiSource(spec=spec, md5=digest, origin=origin)


def load_endpoint_pages(repo_root: Path) -> list[EndpointPage]:
    """Read `sidebar-metadata.json` into one page per endpoint slug."""
    metadata_path = repo_root / "src" / "content" / "en" / "api" / "sidebar-metadata.json"
    entries = json.loads(metadata_path.read_text(encoding="utf-8"))
    pages: list[EndpointPage] = []
    for entry in entries:
        slug = entry.get("slug")
        if not isinstance(slug, str) or not slug.startswith("endpoint/"):
            continue
        operations: list[OperationRef] = []
        for tag in entry.get("tags") or []:
            tag_name = str(tag.get("name") or "")
            for operation in tag.get("operations") or []:
                operations.append(
                    OperationRef(
                        element_id=str(operation.get("elementId") or ""),
                        method=str(operation.get("method") or "").upper(),
                        path=str(operation.get("path") or ""),
                        operation_id=str(operation.get("operationId") or ""),
                        summary=str(operation.get("summary") or ""),
                        description=str(operation.get("description") or ""),
                        tag=tag_name,
                    )
                )
        pages.append(
            EndpointPage(
                slug=slug,
                label=str(entry.get("sidebarLabel") or slug),
                operations=tuple(operations),
            )
        )
    return pages


class SpecRenderer:
    """Renders operations to readable markdown, resolving `$ref` as it goes."""

    def __init__(self, spec: dict[str, Any]) -> None:
        self.spec = spec
        self.missing_operations: list[str] = []

    def render_page(self, page: EndpointPage) -> str:
        lines = [f"# {page.label} API", ""]
        lines.append(
            f"Reference for the {page.label} endpoints of the Mistral API, generated "
            "from the OpenAPI specification."
        )
        for operation in page.operations:
            lines += ["", *self._render_operation(operation)]
        return "\n".join(lines).strip() + "\n"

    def _render_operation(self, ref: OperationRef) -> list[str]:
        spec_operation = self._find_operation(ref)
        heading = ref.summary or ref.operation_id
        lines = [f"## {heading} {{#{ref.element_id}}}", ""]
        lines.append(f"`{ref.method} {ref.path}`")
        if spec_operation is None:
            self.missing_operations.append(ref.operation_id)
            lines += ["", "This operation is listed on the site but absent from the spec."]
            return lines
        description = str(spec_operation.get("description") or ref.description or "").strip()
        if description and description != heading:
            lines += ["", description]
        lines += ["", f"- Operation id: `{ref.operation_id}`"]
        if ref.tag:
            lines.append(f"- Tag: {ref.tag}")
        if spec_operation.get("deprecated"):
            lines.append("- Deprecated: yes")

        parameters = self._collect_parameters(ref, spec_operation)
        if parameters:
            lines += ["", "### Parameters", ""]
            lines += parameters

        body = self._render_request_body(spec_operation)
        if body:
            lines += ["", "### Request body", ""]
            lines += body

        responses = self._render_responses(spec_operation)
        if responses:
            lines += ["", "### Responses", ""]
            lines += responses
        return lines

    # -- spec lookup ---------------------------------------------------------

    def _find_operation(self, ref: OperationRef) -> dict[str, Any] | None:
        path_item = self.spec.get("paths", {}).get(ref.path)
        if isinstance(path_item, dict):
            operation = path_item.get(ref.method.lower())
            if isinstance(operation, dict):
                return operation
        for item in self.spec.get("paths", {}).values():
            if not isinstance(item, dict):
                continue
            for operation in item.values():
                if isinstance(operation, dict) and operation.get("operationId") == ref.operation_id:
                    return operation
        return None

    def resolve(self, node: Any, seen: frozenset[str] = frozenset()) -> tuple[Any, frozenset[str]]:
        """Follow `$ref` chains, refusing to revisit a schema already on the path.

        `anyOf: [T, null]` is collapsed to `T` on the way: the spec uses it for every
        optional field, and spelling it out swamps the summary.
        """
        nullable = False
        while True:
            if isinstance(node, dict) and "$ref" in node:
                ref = str(node["$ref"])
                if ref in seen:
                    return {"title": ref.rsplit("/", 1)[-1], "x-cycle": True}, seen
                seen = seen | {ref}
                node = self._dereference(ref)
                if node is None:
                    return {}, seen
                continue
            collapsed = _collapse_nullable(node)
            if collapsed is not None:
                nullable = True
                node = collapsed
                continue
            break
        if nullable and isinstance(node, dict):
            node = {**node, "x-nullable": True}
        return node, seen

    def _dereference(self, ref: str) -> Any:
        if not ref.startswith("#/"):
            return None
        node: Any = self.spec
        for part in ref[2:].split("/"):
            key = part.replace("~1", "/").replace("~0", "~")
            if not isinstance(node, dict) or key not in node:
                return None
            node = node[key]
        return node

    # -- pieces --------------------------------------------------------------

    def _collect_parameters(self, ref: OperationRef, spec_operation: dict[str, Any]) -> list[str]:
        raw: list[Any] = list(spec_operation.get("parameters") or [])
        path_item = self.spec.get("paths", {}).get(ref.path)
        if isinstance(path_item, dict):
            raw = list(path_item.get("parameters") or []) + raw
        lines: list[str] = []
        for entry in raw:
            parameter, _ = self.resolve(entry)
            if not isinstance(parameter, dict):
                continue
            schema, _ = self.resolve(parameter.get("schema") or {})
            annotations = [_type_name(schema, self)]
            annotations.append("required" if parameter.get("required") else "optional")
            annotations.append(f"in {parameter.get('in', 'query')}")
            line = f"- `{parameter.get('name', '?')}` ({', '.join(a for a in annotations if a)})"
            description = _one_line(parameter.get("description") or "")
            if description:
                line += f" — {description}"
            lines.append(line)
        return lines

    def _render_request_body(self, spec_operation: dict[str, Any]) -> list[str]:
        body, _ = self.resolve(spec_operation.get("requestBody") or {})
        if not isinstance(body, dict) or not body.get("content"):
            return []
        lines: list[str] = []
        required = " (required)" if body.get("required") else ""
        for media_type, media in body["content"].items():
            if not isinstance(media, dict):
                continue
            schema, seen = self.resolve(media.get("schema") or {})
            name = _ref_name(media.get("schema"))
            header = f"`{media_type}`{required}"
            if name:
                header += f", schema `{name}`"
            lines += [header, ""]
            lines += self.describe_schema(schema, depth=0, seen=seen) or ["- Not documented."]
            lines.append("")
        while lines and not lines[-1]:
            lines.pop()
        return lines

    def _render_responses(self, spec_operation: dict[str, Any]) -> list[str]:
        lines: list[str] = []
        for code, entry in (spec_operation.get("responses") or {}).items():
            response, seen = self.resolve(entry)
            if not isinstance(response, dict):
                continue
            description = _one_line(response.get("description") or "")
            line = f"- `{code}`"
            if description:
                line += f" — {description}"
            media_types = list((response.get("content") or {}).keys())
            schema_names = []
            for media_type in media_types:
                media = response["content"][media_type]
                if isinstance(media, dict) and isinstance(media.get("schema"), dict):
                    name = media["schema"].get("$ref")
                    if isinstance(name, str):
                        schema_names.append(name.rsplit("/", 1)[-1])
            if media_types:
                line += f" ({', '.join(media_types)}"
                if schema_names:
                    line += f", schema {', '.join(dict.fromkeys(schema_names))}"
                line += ")"
            lines.append(line)
        return lines

    # -- schema summary ------------------------------------------------------

    def describe_schema(
        self, schema: Any, depth: int, seen: frozenset[str], indent: str = ""
    ) -> list[str]:
        """Summarize a schema as a bullet list, capped at `MAX_SCHEMA_DEPTH` levels."""
        schema, seen = self.resolve(schema, seen)
        if not isinstance(schema, dict):
            return []
        combined = _combinator(schema)
        if combined is not None:
            keyword, options = combined
            combined_lines = [f"{indent}- one of ({keyword}):"]
            for option in options[:6]:
                option_schema, option_seen = self.resolve(option, seen)
                name = _ref_name(option) or _type_name(option_schema, self)
                combined_lines.append(f"{indent}  - {name}")
                if depth + 1 < MAX_SCHEMA_DEPTH:
                    combined_lines += self.describe_schema(
                        option_schema, depth + 2, option_seen, indent + "    "
                    )
            return combined_lines
        if schema.get("type") == "array" or "items" in schema:
            items, item_seen = self.resolve(schema.get("items") or {}, seen)
            if depth >= MAX_SCHEMA_DEPTH:
                return []
            return self.describe_schema(items, depth + 1, item_seen, indent)
        properties = schema.get("properties")
        if not isinstance(properties, dict):
            return []
        required = set(schema.get("required") or [])
        lines: list[str] = []
        for name, raw_property in properties.items():
            child, child_seen = self.resolve(raw_property, seen)
            type_text = _type_name(child, self)
            # A `$ref` name says more than "object", except when the target is an
            # enum, where the allowed values are the useful part.
            named = "" if isinstance(child, dict) and "enum" in child else _ref_name(raw_property)
            annotations = [named or type_text]
            annotations.append("required" if name in required else "optional")
            line = f"{indent}- `{name}` ({', '.join(a for a in annotations if a)})"
            raw = raw_property if isinstance(raw_property, dict) else {}
            description = _one_line(
                raw.get("description")
                or (child.get("description") if isinstance(child, dict) else "")
                or ""
            )
            if description:
                line += f" — {description}"
            lines.append(line)
            if depth + 1 < MAX_SCHEMA_DEPTH:
                lines += self.describe_schema(child, depth + 1, child_seen, indent + "  ")
        return lines


@dataclass
class ApiRenderResult:
    pages: list[tuple[EndpointPage, str]] = field(default_factory=list)
    missing_operations: list[str] = field(default_factory=list)
    operation_count: int = 0


def render_api_pages(repo_root: Path, source: OpenApiSource) -> ApiRenderResult:
    renderer = SpecRenderer(source.spec)
    result = ApiRenderResult()
    for page in load_endpoint_pages(repo_root):
        result.pages.append((page, renderer.render_page(page)))
        result.operation_count += len(page.operations)
    result.missing_operations = renderer.missing_operations
    if result.missing_operations:
        log.warning("operations missing from spec", count=len(result.missing_operations))
    return result


def _collapse_nullable(schema: Any) -> Any | None:
    """If a combinator is just `T` or `null`, return `T`; otherwise `None`."""
    if not isinstance(schema, dict):
        return None
    for keyword in ("anyOf", "oneOf"):
        options = schema.get(keyword)
        if not isinstance(options, list):
            continue
        non_null = [
            option
            for option in options
            if not (isinstance(option, dict) and option.get("type") == "null")
        ]
        if len(non_null) == 1 and len(non_null) < len(options):
            return non_null[0]
    return None


def _ref_name(node: Any) -> str:
    if isinstance(node, dict) and isinstance(node.get("$ref"), str):
        return str(node["$ref"]).rsplit("/", 1)[-1]
    return ""


def _combinator(schema: dict[str, Any]) -> tuple[str, list[Any]] | None:
    for keyword in ("oneOf", "anyOf"):
        options = schema.get(keyword)
        if isinstance(options, list) and len(options) > 1:
            return keyword, options
    return None


def _type_name(schema: Any, renderer: SpecRenderer) -> str:
    if not isinstance(schema, dict):
        return ""
    if schema.get("x-cycle"):
        return str(schema.get("title") or "object")
    enum = schema.get("enum")
    if isinstance(enum, list) and enum:
        values = ", ".join(repr(value) for value in enum[:_MAX_ENUM_VALUES])
        suffix = ", ..." if len(enum) > _MAX_ENUM_VALUES else ""
        return f"enum: {values}{suffix}"
    declared = schema.get("type")
    if isinstance(declared, list):
        return " | ".join(str(item) for item in declared)
    suffix = " or null" if schema.get("x-nullable") else ""
    if declared == "array":
        raw_items = schema.get("items") or {}
        items, _ = renderer.resolve(raw_items)
        inner = _ref_name(raw_items) or _type_name(items, renderer)
        return (f"array of {inner}" if inner else "array") + suffix
    if isinstance(declared, str):
        fmt = schema.get("format")
        return (f"{declared} ({fmt})" if fmt else declared) + suffix
    for keyword in ("oneOf", "anyOf", "allOf"):
        if keyword in schema:
            return "object" + suffix
    title = schema.get("title")
    return (str(title) if isinstance(title, str) else "object") + suffix


def _one_line(text: str) -> str:
    """Flatten to one line and make site-relative markdown links absolute."""
    return _RELATIVE_LINK.sub(rf"\1{SITE_ORIGIN}/", " ".join(str(text).split()))
