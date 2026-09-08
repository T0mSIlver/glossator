"""Rendering one OpenAPI operation onto its endpoint page."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from glossator.corpus.mistral_docs.openapi import OpenApiSource, SpecRenderer, render_api_pages

SPEC = {
    "openapi": "3.1.0",
    "info": {"title": "Test", "version": "1"},
    "paths": {
        "/v1/files/{file_id}": {
            "get": {
                "operationId": "files_api_routes_retrieve_file",
                "summary": "Retrieve File",
                "description": "Returns information about a specific file.",
                "parameters": [
                    {
                        "name": "file_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                    },
                    {
                        "name": "expiry",
                        "in": "query",
                        "required": False,
                        "description": "Hours before the URL expires.",
                        "schema": {"type": "integer"},
                    },
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/FileRequest"}}
                    },
                },
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/GetFileResponse"}
                            }
                        },
                    },
                    "422": {"description": "Validation Error"},
                },
            }
        }
    },
    "components": {
        "schemas": {
            "FileRequest": {
                "type": "object",
                "required": ["purpose"],
                "properties": {
                    "purpose": {
                        "type": "string",
                        "enum": ["fine-tune", "batch"],
                        "description": "What the file is for.",
                    },
                    "sampling": {
                        "anyOf": [{"type": "number"}, {"type": "null"}],
                        "description": "Optional sampling ratio.",
                    },
                    "owner": {"$ref": "#/components/schemas/Owner"},
                    "children": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/FileRequest"},
                    },
                },
            },
            "Owner": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
            },
            "GetFileResponse": {"type": "object", "properties": {"id": {"type": "string"}}},
        }
    },
}

SIDEBAR = [
    {
        "sidebarLabel": "Files",
        "slug": "endpoint/files",
        "tags": [
            {
                "name": "files",
                "operations": [
                    {
                        "elementId": "operation-files_api_routes_retrieve_file",
                        "method": "get",
                        "path": "/v1/files/{file_id}",
                        "operationId": "files_api_routes_retrieve_file",
                        "summary": "Retrieve File",
                        "description": "Returns information about a specific file.",
                    }
                ],
            }
        ],
    }
]


def _repo(tmp_path: Path) -> Path:
    api_dir = tmp_path / "src" / "content" / "en" / "api"
    api_dir.mkdir(parents=True)
    (api_dir / "sidebar-metadata.json").write_text(json.dumps(SIDEBAR), encoding="utf-8")
    return tmp_path


def _source() -> OpenApiSource:
    return OpenApiSource(spec=SPEC, md5="deadbeef", origin="test")


def test_endpoint_page_url_and_anchor(tmp_path: Path) -> None:
    result = render_api_pages(_repo(tmp_path), _source())
    assert len(result.pages) == 1
    page, markdown = result.pages[0]
    assert page.url_path == "/api/endpoint/files"
    assert "## Retrieve File {#operation-files_api_routes_retrieve_file}" in markdown
    assert result.missing_operations == []


def test_operation_body_covers_method_parameters_schema_and_responses(tmp_path: Path) -> None:
    _, markdown = render_api_pages(_repo(tmp_path), _source()).pages[0]
    assert "`GET /v1/files/{file_id}`" in markdown
    assert "Returns information about a specific file." in markdown
    assert "- `file_id` (string (uuid), required, in path)" in markdown
    assert "- `expiry` (integer, optional, in query) — Hours before the URL expires." in markdown
    assert "`application/json` (required), schema `FileRequest`" in markdown
    assert "- `purpose` (enum: 'fine-tune', 'batch', required) — What the file is for." in markdown
    # `anyOf: [number, null]` is the spec's way of saying optional; it reads as one type.
    assert "- `sampling` (number or null, optional) — Optional sampling ratio." in markdown
    assert "- `owner` (Owner, optional)" in markdown
    assert "  - `name` (string, optional)" in markdown
    assert "- `200` — OK (application/json, schema GetFileResponse)" in markdown
    assert "- `422` — Validation Error" in markdown


def test_recursive_schemas_stop_at_the_depth_cap(tmp_path: Path) -> None:
    _, markdown = render_api_pages(_repo(tmp_path), _source()).pages[0]
    # `children` recurses into FileRequest; nothing may nest past three levels.
    indents = [
        len(line) - len(line.lstrip(" "))
        for line in markdown.split("\n")
        if line.lstrip().startswith("- `")
    ]
    assert max(indents) <= 4


def test_an_operation_missing_from_the_spec_is_reported(tmp_path: Path) -> None:
    sidebar = json.loads(json.dumps(SIDEBAR))
    sidebar[0]["tags"][0]["operations"][0]["operationId"] = "gone"
    sidebar[0]["tags"][0]["operations"][0]["path"] = "/v1/gone"
    api_dir = tmp_path / "src" / "content" / "en" / "api"
    api_dir.mkdir(parents=True)
    (api_dir / "sidebar-metadata.json").write_text(json.dumps(sidebar), encoding="utf-8")
    result = render_api_pages(tmp_path, _source())
    assert result.missing_operations == ["gone"]


def test_the_spec_round_trips_through_yaml(tmp_path: Path) -> None:
    # The live spec is YAML; the renderer must not depend on a JSON-only shape.
    path = tmp_path / "openapi.yaml"
    path.write_text(yaml.safe_dump(SPEC), encoding="utf-8")
    renderer = SpecRenderer(yaml.safe_load(path.read_text(encoding="utf-8")))
    schema, seen = renderer.resolve({"$ref": "#/components/schemas/Owner"})
    assert schema["properties"]["name"]["type"] == "string"
    assert seen == frozenset({"#/components/schemas/Owner"})
