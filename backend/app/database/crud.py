"""CRUD helpers for health memory."""

from __future__ import annotations

import json
from typing import Any

from ..utils.validators import as_float
from .db import get_connection, init_db


def save_reading(payload: dict[str, Any]) -> dict[str, Any]:
    init_db()
    patient = payload.get("patient") or payload.get("tabular_result", {}).get("vitals_summary", {})
    fusion = payload.get("fusion_result") or payload
    signal = payload.get("signal_result") or {}
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO readings (
                patient_id, final_risk_score, risk_category, systolic_bp, diastolic_bp,
                heart_rate, spo2, sleep_hours, signal_quality, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(payload.get("patient_id", "demo")),
                as_float(fusion.get("final_risk_score", fusion.get("risk_score")), 0),
                str(fusion.get("risk_category", "Unknown")),
                as_float(patient.get("systolic_bp"), 0),
                as_float(patient.get("diastolic_bp"), 0),
                as_float(patient.get("heart_rate"), 0),
                as_float(patient.get("spo2"), 0),
                as_float(patient.get("sleep_hours"), 0),
                as_float(signal.get("quality_score", signal.get("signal_quality")), 0),
                json.dumps(payload),
            ),
        )
        connection.commit()
        return {"id": cursor.lastrowid, "saved": True}


def list_readings(limit: int = 25) -> list[dict[str, Any]]:
    init_db()
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["payload"] = json.loads(item.pop("payload_json"))
        result.append(item)
    return result


def compare_last_reading() -> dict[str, Any]:
    readings = list_readings(limit=2)
    if len(readings) < 2:
        return {"previous_reading": None, "current_reading": readings[0] if readings else None, "changes": {}, "risk_delta": 0, "explanation": "Not enough saved readings to compare."}
    current, previous = readings[0], readings[1]
    changes = {}
    for metric in ["final_risk_score", "systolic_bp", "diastolic_bp", "heart_rate", "spo2", "sleep_hours", "signal_quality"]:
        changes[metric] = round(as_float(current.get(metric), 0) - as_float(previous.get(metric), 0), 2)
    risk_delta = changes.get("final_risk_score", 0)
    explanation = f"Compared to your last session, risk changed by {risk_delta:+.1f} points."
    return {"previous_reading": previous, "current_reading": current, "changes": changes, "risk_delta": risk_delta, "explanation": explanation}

