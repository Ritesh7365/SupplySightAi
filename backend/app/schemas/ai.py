"""AI insight request/response schemas."""

from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from app.schemas.common import ORMModel


class AiAskRequest(ORMModel):
    question: str = Field(min_length=3, max_length=1000)


class AiInsightResponse(ORMModel):
    question: str
    answer: str
    sources: List[str] = Field(default_factory=list)
    model: str
    intent: Optional[str] = None
    response_time_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
