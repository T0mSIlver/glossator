"""Snapshot labelling settings and the judge's structured verdict."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

CURRENT_CORPUS = Path("corpus/mistral-docs")
PRIMARY_JUDGE = "glm-5.3"
SECONDARY_JUDGE = "glm-5.3-flash"
LABEL_SEED = 0
PAGE_PROMPT_CHARS = 6000


@dataclass(frozen=True, slots=True)
class Span:
    """A supporting span and the page it was cited from at the pinned commit."""

    page: str
    text: str


class FactVerdict(BaseModel):
    model_config = ConfigDict(frozen=True)

    classification: Literal["stated", "different_value", "not_stated"]
    reason: str
    page: str | None = None
    evidence: str = ""
