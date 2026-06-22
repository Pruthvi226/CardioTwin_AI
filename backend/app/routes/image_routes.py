"""Medical image/report OCR route."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from ..models.image_model import analyze_medical_image
from ..utils.disclaimer import with_disclaimer
from ..utils.validators import IMAGE_EXTENSIONS, validate_extension
from .request_files import read_optional_upload


router = APIRouter(tags=["Image"])


@router.post("/analyze-image")
async def analyze_image(request: Request) -> dict:
    try:
        raw, filename = await read_optional_upload(request, field_names=("image", "file"))
        if filename:
            validate_extension(filename, IMAGE_EXTENSIONS)
        return with_disclaimer(analyze_medical_image(raw, filename))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

