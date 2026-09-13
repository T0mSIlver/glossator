"""Structured output: the schema a call demands, and the JSON object in a model's reply."""

from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel


def schema_fingerprint(response_schema: type[BaseModel]) -> str:
    """Hash of the JSON Schema a call demands.

    Part of the cache key: editing a schema's fields without renaming the class
    would otherwise return an answer shaped for the old fields.
    """
    encoded = json.dumps(response_schema.model_json_schema(), sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def extract_json_object(text: str) -> str:
    """The first balanced JSON object in ``text``.

    Models wrap the object in a markdown fence or follow it with a sentence often
    enough that recovering the object locally is cheaper than paying for another
    call. Returns the input unchanged when no object is found, so that the
    validation error the caller sees is about the model's answer, not about this.
    """
    start = text.find("{")
    if start == -1:
        return text
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return text


def with_schema(
    messages: list[dict[str, str]], response_schema: type[BaseModel]
) -> list[dict[str, str]]:
    schema_instruction = (
        "Return one JSON object and no prose. It must validate against this JSON Schema:\n"
        + json.dumps(response_schema.model_json_schema(), sort_keys=True)
    )
    if messages and messages[0].get("role") == "system":
        messages[0] = {
            **messages[0],
            "content": messages[0]["content"] + "\n\n" + schema_instruction,
        }
    else:
        messages.insert(0, {"role": "system", "content": schema_instruction})
    return messages
