"""Live simulation, trend analysis, and anomaly routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..models.anomaly_model import detect_anomaly
from ..models.trend_model import analyze_trends, live_simulation
from .request_files import read_optional_upload


router = APIRouter(tags=["Trends"])


class RecordsPayload(BaseModel):
    records: list[dict[str, Any]] | None = None
    current: dict[str, Any] | None = None


def _dump(model: BaseModel | None) -> dict[str, Any]:
    if not model:
        return {}
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


@router.get("/live-simulation")
async def get_live_simulation() -> dict[str, Any]:
    return live_simulation()


@router.post("/analyze-trends")
async def analyze_trend_route(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        data = await request.json()
        return analyze_trends(records=data.get("records") or data.get("history"))
    raw, _ = await read_optional_upload(request)
    return analyze_trends(raw=raw)


@router.post("/detect-anomaly")
async def detect_anomaly_route(payload: RecordsPayload | None = None) -> dict[str, Any]:
    return detect_anomaly(_dump(payload))

