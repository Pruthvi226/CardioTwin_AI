"""Shared feature helpers for the hybrid scoring modules."""

from __future__ import annotations

import re
from typing import Any

from ..utils.config import clamp, risk_category


def score_band(score: float) -> str:
    return risk_category(score)


def warning(label: str, severity: str, detail: str) -> dict[str, str]:
    return {"label": label, "severity": severity, "detail": detail}


def bp_stage(systolic: float, diastolic: float) -> str:
    if systolic >= 180 or diastolic >= 120:
        return "Hypertensive crisis range"
    if systolic >= 140 or diastolic >= 90:
        return "Hypertension stage 2 range"
    if systolic >= 130 or diastolic >= 80:
        return "Hypertension stage 1 range"
    if systolic >= 120 and diastolic < 80:
        return "Elevated range"
    return "Normal range"


def bmi_stage(bmi: float) -> str:
    if bmi <= 0:
        return "Unknown"
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Healthy range"
    if bmi < 30:
        return "Overweight"
    return "Obesity range"


def extract_numeric_indicators(text: str) -> dict[str, Any]:
    values: dict[str, Any] = {}
    if not text:
        return values

    bp_match = re.search(r"\b(?:bp|blood pressure)?\s*(\d{2,3})\s*/\s*(\d{2,3})\b", text, re.I)
    if bp_match:
        values["systolic_bp"] = float(bp_match.group(1))
        values["diastolic_bp"] = float(bp_match.group(2))

    patterns = {
        "heart_rate": r"\b(?:hr|heart rate|pulse)\s*[:=-]?\s*(\d{2,3})\b",
        "spo2": r"\b(?:spo2|oxygen saturation|o2 sat)\s*[:=-]?\s*(\d{2,3})\s*%?",
        "glucose": r"\b(?:glucose|sugar)\s*[:=-]?\s*(\d{2,3})\b",
        "cholesterol": r"\b(?:total cholesterol|cholesterol)\s*[:=-]?\s*(\d{2,3})\b",
        "ldl": r"\bldl\s*[:=-]?\s*(\d{2,3})\b",
        "hba1c": r"\bhba1c\s*[:=-]?\s*(\d{1,2}(?:\.\d+)?)\b",
        "troponin": r"\btroponin\s*[:=-]?\s*(\d+(?:\.\d+)?)\b",
    }
    for name, pattern in patterns.items():
        match = re.search(pattern, text, re.I)
        if match:
            values[name] = float(match.group(1))
    return values


def contribution_dict(scores: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, value) for value in scores.values())
    if total <= 0:
        return {name: 0.0 for name in scores}
    return {name: round(clamp(value / total * 100), 2) for name, value in scores.items()}

