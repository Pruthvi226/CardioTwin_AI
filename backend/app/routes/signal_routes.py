"""PPG upload and signal analysis routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from ..models.signal_model import analyze_signal_csv, summarize_signal_upload
from ..utils.disclaimer import with_disclaimer
from ..utils.validators import SIGNAL_EXTENSIONS, validate_extension
from .request_files import read_optional_upload


router = APIRouter(tags=["Signal"])


@router.post("/upload-signal")
async def upload_signal(request: Request) -> dict:
    try:
        raw, filename = await read_optional_upload(request)
        if raw is None:
            raise ValueError("Upload a CSV file or send CSV bytes in the request body.")
        validate_extension(filename or "signal.csv", SIGNAL_EXTENSIONS)
        payload = summarize_signal_upload(raw)
        payload["filename"] = filename or "raw_body.csv"
        return with_disclaimer(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/analyze-signal")
async def analyze_signal(request: Request) -> dict:
    try:
        raw, filename = await read_optional_upload(request)
        content_type = request.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            raw = None
            filename = None
        if filename:
            validate_extension(filename, SIGNAL_EXTENSIONS)
        payload = analyze_signal_csv(raw)
        payload["filename"] = filename or "sample_ppg.csv"
        return with_disclaimer(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

