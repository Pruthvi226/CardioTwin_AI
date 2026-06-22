"""Physiological anomaly detection using transparent statistical rules."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..utils.disclaimer import DISCLAIMER
from ..utils.validators import as_float


def detect_anomaly(payload: dict[str, Any]) -> dict[str, Any]:
    records = payload.get("records") or payload.get("history") or []
    current = payload.get("current") or payload
    flags: list[str] = []

    if records:
        for metric, label in [
            ("heart_rate", "Sudden HR spike"),
            ("spo2", "Low SpO2 event"),
            ("systolic_bp", "Abnormal BP jump"),
            ("signal_quality", "Noisy PPG pattern"),
        ]:
            values = [as_float(row.get(metric), np.nan) for row in records if isinstance(row, dict)]
            values = [value for value in values if np.isfinite(value)]
            current_value = as_float(current.get(metric), np.nan)
            if len(values) >= 3 and np.isfinite(current_value):
                mean = float(np.mean(values))
                std = float(np.std(values)) or 1.0
                z_score = abs((current_value - mean) / std)
                if z_score >= 2.5:
                    flags.append(label)

    if as_float(current.get("heart_rate"), 75) > 125:
        flags.append("Sudden HR spike")
    if as_float(current.get("spo2"), 98) < 90:
        flags.append("Low SpO2 event")
    if as_float(current.get("systolic_bp"), 120) >= 180 or as_float(current.get("diastolic_bp"), 80) >= 120:
        flags.append("Abnormal BP jump")
    if as_float(current.get("signal_quality"), 100) < 45:
        flags.append("Noisy PPG pattern")

    unique_flags = list(dict.fromkeys(flags))
    severity = "high" if any(flag in unique_flags for flag in ["Low SpO2 event", "Abnormal BP jump"]) else "medium" if unique_flags else "low"
    return {
        "anomaly_detected": bool(unique_flags),
        "anomaly_type": unique_flags,
        "severity": severity,
        "explanation": (
            f"Detected physiological anomaly pattern(s): {', '.join(unique_flags)}."
            if unique_flags
            else "No strong anomaly pattern was detected from the available data."
        ),
        "disclaimer": DISCLAIMER,
    }

