"""Grounded answers over the indexed documentation, with verifiable citations."""

from glossator.answer.citations import Answer, Citation, Trace
from glossator.answer.config import AnswerConfig
from glossator.answer.context import AssembledContext, Source, assemble
from glossator.answer.generation import Strategy
from glossator.answer.llm import (
    CallRecorder,
    JsonlCallRecorder,
    LLMCall,
    MistralLLM,
    TokenUsage,
)
from glossator.answer.service import STRATEGIES, ask

__all__ = [
    "STRATEGIES",
    "Answer",
    "AnswerConfig",
    "AssembledContext",
    "CallRecorder",
    "Citation",
    "JsonlCallRecorder",
    "LLMCall",
    "MistralLLM",
    "Source",
    "Strategy",
    "TokenUsage",
    "Trace",
    "ask",
    "assemble",
]
