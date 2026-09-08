"""Rendering one OpenAPI operation onto its endpoint page."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from glossator.corpus.mistral_docs.openapi import (
    OpenApiSource,
    OperationRef,
    SpecRenderer,
    render_api_pages,
)

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
            "ConversationRequest": {
                "allOf": [
                    {"$ref": "#/components/schemas/ConversationBase"},
                    {
                        "type": "object",
                        "required": ["inputs"],
                        "properties": {"inputs": {"type": "string"}},
                    },
                ],
                "description": "Start a conversation.",
            },
            "ConversationBase": {
                "type": "object",
                "required": ["agent_id"],
                "properties": {
                    "agent_id": {"type": "string", "description": "Which agent answers."},
                    "tools": {
                        "type": "array",
                        "items": {
                            "oneOf": [
                                {"$ref": "#/components/schemas/Tool1"},
                                {"$ref": "#/components/schemas/Tool2"},
                                {"$ref": "#/components/schemas/Tool3"},
                                {"$ref": "#/components/schemas/Tool4"},
                                {"$ref": "#/components/schemas/Tool5"},
                                {"$ref": "#/components/schemas/Tool6"},
                                {"$ref": "#/components/schemas/CustomConnector"},
                            ]
                        },
                    },
                    "sampling": {
                        "type": "number",
                        "description": (
                            "How random the answer is.\n\n```bash\ncurl -d 'sampling=0.2'\n```\n"
                        ),
                    },
                },
            },
            **{
                f"Tool{index}": {"type": "object", "properties": {"kind": {"type": "string"}}}
                for index in range(1, 7)
            },
            "CustomConnector": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
            },
        }
    },
}

CONVERSATION_PATHS = {
    "/v1/conversations": {
        "post": {
            "operationId": "start_conversation",
            "summary": "Start Conversation",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ConversationRequest"}
                    }
                },
            },
            "responses": {"200": {"description": "OK"}},
        }
    },
    "/v1/conversations#stream": {
        "post": {
            "operationId": "start_conversation_stream",
            "summary": "Start Conversation Stream",
            "responses": {"200": {"description": "OK"}},
        }
    },
}

CONVERSATION_SIDEBAR = [
    {
        "sidebarLabel": "Conversations",
        "slug": "endpoint/beta/conversations",
        "tags": [
            {
                "name": "conversations",
                "operations": [
                    {
                        "elementId": "operation-start_conversation",
                        "method": "post",
                        "path": "/v1/conversations",
                        "operationId": "start_conversation",
                        "summary": "Start Conversation",
                    },
                    {
                        "elementId": "operation-start_conversation_stream",
                        "method": "post",
                        "path": "/v1/conversations#stream",
                        "operationId": "start_conversation_stream",
                        "summary": "Start Conversation Stream",
                    },
                ],
            }
        ],
    }
]

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


def _conversation_repo(tmp_path: Path) -> Path:
    api_dir = tmp_path / "src" / "content" / "en" / "api"
    api_dir.mkdir(parents=True)
    (api_dir / "sidebar-metadata.json").write_text(
        json.dumps(CONVERSATION_SIDEBAR), encoding="utf-8"
    )
    return tmp_path


def _conversation_source() -> OpenApiSource:
    spec = json.loads(json.dumps(SPEC))
    spec["paths"].update(CONVERSATION_PATHS)
    return OpenApiSource(spec=spec, md5="deadbeef", origin="test")


def _conversation_markdown(tmp_path: Path) -> str:
    result = render_api_pages(_conversation_repo(tmp_path), _conversation_source())
    return result.pages[0][1]


def test_all_of_branches_are_merged_into_the_request_body(tmp_path: Path) -> None:
    markdown = _conversation_markdown(tmp_path)
    assert "- Not documented." not in markdown
    # Both the referenced branch and the inline branch contribute properties.
    assert "- `agent_id` (string, required) - Which agent answers." in markdown.replace(
        "\u2014", "-"
    )
    assert "- `inputs` (string, required)" in markdown


def test_every_combinator_alternative_is_listed(tmp_path: Path) -> None:
    markdown = _conversation_markdown(tmp_path)
    assert "- one of 7 (oneOf):" in markdown
    # The seventh alternative used to be cut off by a hard limit of six.
    assert "CustomConnector" in markdown


def test_a_synthetic_fragment_is_not_part_of_the_request_path(tmp_path: Path) -> None:
    markdown = _conversation_markdown(tmp_path)
    assert "`POST /v1/conversations`" in markdown
    assert "#stream`" not in markdown
    # The fragment still identifies the section, because that is a real HTML id.
    assert "{#operation-start_conversation_stream}" in markdown


@pytest.mark.parametrize("suffix", ["#stream", "#id", "#idOrName"])
def test_fragment_suffixes_are_stripped_from_the_path(suffix: str) -> None:
    ref = OperationRef(
        element_id="operation-x",
        method="GET",
        path="/v1/connectors/{connector_id}" + suffix,
        operation_id="x",
        summary="X",
        description="",
        tag="",
    )
    assert ref.request_path == "/v1/connectors/{connector_id}"


def test_a_multiline_description_keeps_its_fenced_example(tmp_path: Path) -> None:
    markdown = _conversation_markdown(tmp_path)
    lines = markdown.split("\n")
    bullet = next(line for line in lines if line.lstrip().startswith("- `sampling`"))
    assert bullet.endswith("How random the answer is.")
    # The fence has to start at a line of its own to still read as code.
    fence = next(index for index, line in enumerate(lines) if line.strip() == "```bash")
    assert lines[fence - 1].strip() == ""
    assert lines[fence].startswith("  ")
