"""Alerts, summaries, recommendations, demos, and health-memory routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..models.fusion_model import calculate_multimodal_risk
from ..services.alert_service import check_alerts, recommendations
from ..services.explanation_service import clinician_assist, doctor_summary, patient_guidance, patient_summary
from ..services.health_memory_service import compare_last, history, save
from ..services.synthetic_patient_generator import demo_patients
from ..utils.disclaimer import DISCLAIMER
from ..utils.risk_rules import reliability_score


router = APIRouter(tags=["Alerts and Memory"])


class GenericPayload(BaseModel):
    payload: dict[str, Any] | None = None
    signal_result: dict[str, Any] | None = None
    tabular_result: dict[str, Any] | None = None
    text_result: dict[str, Any] | None = None
    image_result: dict[str, Any] | None = None
    fusion_result: dict[str, Any] | None = None
    patient: dict[str, Any] | None = None
    symptoms: str | None = None
    notes: str | None = None
    patient_id: str | None = None


def _dump(model: BaseModel | None) -> dict[str, Any]:
    if not model:
        return {}
    data = model.model_dump() if hasattr(model, "model_dump") else model.dict()
    nested = data.pop("payload", None) or {}
    return {**nested, **{key: value for key, value in data.items() if value is not None}}


@router.post("/check-alerts")
async def check_alerts_route(payload: GenericPayload | None = None) -> dict[str, Any]:
    return check_alerts(_dump(payload))


@router.post("/generate-summary")
async def generate_summary_route(payload: GenericPayload | None = None) -> dict[str, Any]:
    data = _dump(payload)
    fusion = data.get("fusion_result") or calculate_multimodal_risk(
        data.get("signal_result"),
        data.get("tabular_result"),
        data.get("text_result"),
        data.get("image_result"),
        data.get("patient"),
    )
    flags = fusion.get("warning_flags", [])
    clinician = clinician_assist(data.get("patient"), data.get("signal_result") or {}, data.get("tabular_result") or {}, data.get("text_result") or {}, data.get("image_result") or {}, fusion)
    guidance = patient_guidance(fusion, flags)
    return {
        "doctor_summary": doctor_summary(data.get("patient"), data.get("signal_result") or {}, data.get("tabular_result") or {}, data.get("text_result") or {}, data.get("image_result") or {}, fusion),
        "patient_summary": patient_summary(fusion, flags),
        "clinician_assist": clinician,
        "patient_guidance": guidance,
        "audience_modes": {
            "medical_practitioner": clinician,
            "common_user": guidance,
        },
        "disclaimer": DISCLAIMER,
    }


@router.post("/generate-recommendations")
async def recommendations_route(payload: GenericPayload | None = None) -> dict[str, Any]:
    data = _dump(payload)
    result = recommendations(data)
    result.update(reliability_score(data))
    return result


@router.get("/demo-patients")
async def demo_patients_route() -> dict[str, Any]:
    return {"demo_patients": demo_patients(), "disclaimer": DISCLAIMER}


@router.post("/save-reading")
async def save_reading_route(payload: GenericPayload | None = None) -> dict[str, Any]:
    return save(_dump(payload))


@router.get("/history")
async def history_route(limit: int = Query(default=25, ge=1, le=200)) -> dict[str, Any]:
    return history(limit)


@router.get("/compare-last-reading")
async def compare_last_reading_route() -> dict[str, Any]:
    return compare_last()

