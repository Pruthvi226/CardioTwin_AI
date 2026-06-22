"""Lightweight schema helpers for SQLite payloads."""

from __future__ import annotations

from typing import Any, TypedDict


class ReadingRecord(TypedDict, total=False):
    id: int
    created_at: str
    patient_id: str
    final_risk_score: float
    risk_category: str
    systolic_bp: float
    diastolic_bp: float
    heart_rate: float
    spo2: float
    sleep_hours: float
    signal_quality: float
    payload: dict[str, Any]

