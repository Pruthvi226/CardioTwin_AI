"""Shared constants and prediction safety helpers."""

from __future__ import annotations

from typing import Any


DISCLAIMER = "Research demo only. Not for clinical diagnosis or medical decision-making."


def uncertainty_label(confidence: float) -> str:
    """Map confidence to a compact uncertainty label."""
    if confidence < 0.60:
        return "high"
    if confidence < 0.80:
        return "medium"
    return "low"


def assess_prediction_risk(
    prediction: str,
    confidence: float,
    signal_quality: float,
    explanation: list[str] | None = None,
) -> dict[str, Any]:
    """Return a recruiter-friendly prediction payload with uncertainty flags."""
    notes = list(explanation or [])
    uncertainty = uncertainty_label(confidence)

    if confidence < 0.60:
        risk_flag = "low_confidence"
        notes.append("model confidence is below 0.60")
    elif signal_quality < 0.50:
        risk_flag = "poor_signal_quality"
        notes.append("signal quality is below 0.50")
    elif uncertainty == "high":
        risk_flag = "review_required"
    else:
        risk_flag = "acceptable_demo_prediction"

    if signal_quality < 0.65:
        notes.append("signal quality may affect reliability")

    return {
        "prediction": prediction,
        "confidence": round(float(confidence), 4),
        "uncertainty": uncertainty,
        "signal_quality": round(float(signal_quality), 4),
        "risk_flag": risk_flag,
        "explanation": notes or ["feature pattern is within demo decision range"],
        "disclaimer": DISCLAIMER,
    }

