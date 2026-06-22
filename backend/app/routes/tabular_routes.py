"""Tabular patient/vitals route."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..models.tabular_model import analyze_tabular
from ..utils.disclaimer import with_disclaimer


router = APIRouter(tags=["Tabular"])


class PatientPayload(BaseModel):
    age: float | None = Field(default=48)
    gender: str | None = Field(default="Female")
    height: float | None = Field(default=168)
    weight: float | None = Field(default=78)
    heart_rate: float | None = Field(default=88)
    systolic_bp: float | None = Field(default=138)
    diastolic_bp: float | None = Field(default=86)
    spo2: float | None = Field(default=96)
    sleep_hours: float | None = Field(default=5.8)
    activity_level: str | None = Field(default="low")
    smoking_status: bool | str | None = Field(default=False)
    diabetes_history: bool | str | None = Field(default=False)
    hypertension_history: bool | str | None = Field(default=True)
    existing_risk_factors: list[str] | str | None = Field(default_factory=list)


def _dump(model: BaseModel) -> dict[str, Any]:
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


@router.post("/analyze-tabular")
async def analyze_patient_tabular(payload: PatientPayload | None = None) -> dict:
    data = _dump(payload) if payload else _dump(PatientPayload())
    return with_disclaimer(analyze_tabular(data))

