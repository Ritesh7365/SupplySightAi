"""AI Insights API router — Groq LangChain copilot with rules fallback."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.deps import DbSession, OptionalUser
from app.schemas.ai import AiAskRequest, AiInsightResponse
from app.schemas.common import OPENAPI_ERROR_RESPONSES
from app.services.ai_service import AiInsightService

router = APIRouter(
    prefix="/ai",
    tags=["AI Insights"],
    responses=OPENAPI_ERROR_RESPONSES,
)


@router.post(
    "/ask",
    response_model=AiInsightResponse,
    summary="Ask the analytics copilot",
    description=(
        "Groq-powered LangChain assistant grounded in analytics views. "
        "Falls back to the rules engine when GROQ_API_KEY is missing or Groq fails."
    ),
)
def ask_ai(
    body: AiAskRequest,
    db: DbSession,
    _user: OptionalUser,
) -> AiInsightResponse:
    return AiInsightService(db).ask(body.question)


@router.post(
    "/ask/stream",
    summary="Ask the analytics copilot (SSE stream)",
    description=(
        "Optional streaming endpoint. Emits Server-Sent Events. "
        "Falls back to a single rules-engine payload when Groq is unavailable."
    ),
)
def ask_ai_stream(
    body: AiAskRequest,
    db: DbSession,
    _user: OptionalUser,
) -> StreamingResponse:
    service = AiInsightService(db)
    return StreamingResponse(
        service.ask_stream_events(body.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
