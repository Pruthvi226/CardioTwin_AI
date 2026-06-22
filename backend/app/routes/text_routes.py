"""Symptoms and clinical notes route."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..models.text_model import analyze_text_notes
from ..utils.disclaimer import with_disclaimer


router = APIRouter(tags=["Text"])


class TextPayload(BaseModel):
    symptoms: str | None = Field(default="Dizziness, fatigue, occasional palpitations")
    lifestyle_notes: str | None = Field(default="Low activity and poor sleep during the last week")
    medication_notes: str | None = Field(default="")
    doctor_notes: str | None = Field(default="")
    notes: str | None = Field(default="")


def _dump(model: BaseModel) -> dict[str, Any]:
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


@router.post("/analyze-text")
async def analyze_text(payload: TextPayload | None = None) -> dict:
    data = _dump(payload) if payload else _dump(TextPayload())
    return with_disclaimer(analyze_text_notes(data))

