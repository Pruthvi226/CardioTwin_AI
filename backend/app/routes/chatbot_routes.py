"""Health twin chat assistant route."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from ..services.chatbot_service import answer_question


router = APIRouter(tags=["Chatbot"])


class ChatPayload(BaseModel):
    question: str
    context: dict[str, Any] | None = None


@router.post("/chat")
async def chat(payload: ChatPayload) -> dict[str, str]:
    return answer_question(payload.question, payload.context or {})

