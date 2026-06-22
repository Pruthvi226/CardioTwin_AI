"""Report export route."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Response
from pydantic import BaseModel

from ..services.report_generator import generate_report


router = APIRouter(tags=["Reports"])


class ReportPayload(BaseModel):
    fusion_result: dict[str, Any] | None = None
    component_results: dict[str, Any] | None = None
    patient: dict[str, Any] | None = None


def _dump(model: BaseModel) -> dict[str, Any]:
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


@router.post("/generate-report")
async def generate_report_endpoint(payload: ReportPayload | None = None) -> Response:
    data = _dump(payload) if payload else {}
    content, media_type, filename = generate_report(data)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

