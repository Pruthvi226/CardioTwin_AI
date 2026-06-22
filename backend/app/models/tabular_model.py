"""Structured patient/vitals risk scoring."""

from __future__ import annotations

from typing import Any

from ..services.feature_extraction import bmi_stage, bp_stage, contribution_dict, score_band, warning
from ..utils.config import clamp
from ..utils.validators import as_bool, as_float, percentage


EXPECTED_FIELDS = (
    "age",
    "gender",
    "height",
    "weight",
    "heart_rate",
    "systolic_bp",
    "diastolic_bp",
    "spo2",
    "sleep_hours",
    "activity_level",
    "smoking_status",
    "diabetes_history",
    "hypertension_history",
)


def _activity_risk(activity: str) -> float:
    normalized = (activity or "").strip().lower()
    if normalized in {"high", "active", "athlete"}:
        return 0
    if normalized in {"moderate", "medium"}:
        return 6
    if normalized in {"low", "sedentary", "inactive"}:
        return 16
    return 8


def _provided(data: dict[str, Any], key: str) -> bool:
    if key == "systolic_bp":
        return data.get("systolic_bp", data.get("sbp")) not in (None, "")
    if key == "diastolic_bp":
        return data.get("diastolic_bp", data.get("dbp")) not in (None, "")
    return data.get(key) not in (None, "")


def _input_completeness(data: dict[str, Any]) -> float:
    provided = sum(1 for field in EXPECTED_FIELDS if _provided(data, field))
    return provided / len(EXPECTED_FIELDS)


def _safety_floor(systolic: float, diastolic: float, spo2: float) -> tuple[float, str]:
    if systolic > 180 or diastolic > 120:
        return 85.0, "Very high blood pressure threshold crossed."
    if spo2 < 90:
        return 82.0, "Low oxygen saturation threshold crossed."
    if systolic >= 160 or diastolic >= 100:
        return 65.0, "Stage 2 hypertension range detected."
    return 0.0, ""


def analyze_tabular(data: dict[str, Any]) -> dict[str, Any]:
    age = as_float(data.get("age"), 40)
    height_cm = as_float(data.get("height"), 0)
    weight_kg = as_float(data.get("weight"), 0)
    heart_rate = as_float(data.get("heart_rate"), 75)
    systolic = as_float(data.get("systolic_bp", data.get("sbp")), 120)
    diastolic = as_float(data.get("diastolic_bp", data.get("dbp")), 80)
    spo2 = as_float(data.get("spo2"), 98)
    sleep_hours = as_float(data.get("sleep_hours"), 7)
    activity = str(data.get("activity_level", "moderate"))

    bmi = as_float(data.get("bmi"), 0)
    if bmi <= 0 and height_cm > 0 and weight_kg > 0:
        bmi = weight_kg / ((height_cm / 100.0) ** 2)

    scores = {
        "age": 0 if age < 45 else min(18, (age - 40) * 0.55),
        "blood_pressure": max(0.0, systolic - 118) * 0.55 + max(0.0, diastolic - 76) * 0.75,
        "heart_rate": max(0.0, abs(heart_rate - 75) - 12) * 0.8,
        "spo2": max(0.0, 96 - spo2) * 4.5,
        "bmi": max(0.0, bmi - 24.9) * 1.8 if bmi else 0,
        "sleep": max(0.0, 7 - sleep_hours) * 5.0,
        "activity": _activity_risk(activity),
        "risk_factors": 0,
    }

    factor_count = 0
    for key in ("smoking_status", "diabetes_history", "hypertension_history"):
        if as_bool(data.get(key)):
            factor_count += 1
    existing = data.get("existing_risk_factors") or []
    if isinstance(existing, str):
        existing = [part.strip() for part in existing.split(",") if part.strip()]
    factor_count += len(existing)
    scores["risk_factors"] = min(24, factor_count * 8)

    raw_risk_score = clamp(sum(scores.values()))
    floor, floor_reason = _safety_floor(systolic, diastolic, spo2)
    risk_score = clamp(max(raw_risk_score, floor))

    flags = []
    if systolic > 180 or diastolic > 120:
        flags.append(warning("Very high blood pressure", "emergency", f"Submitted BP is {systolic:.0f}/{diastolic:.0f} mmHg."))
    elif systolic >= 140 or diastolic >= 90:
        flags.append(warning("Elevated blood pressure", "high", f"Submitted BP is {systolic:.0f}/{diastolic:.0f} mmHg."))
    elif systolic >= 130 or diastolic >= 80:
        flags.append(warning("Borderline blood pressure", "medium", f"Submitted BP is {systolic:.0f}/{diastolic:.0f} mmHg."))
    if spo2 < 90:
        flags.append(warning("Low oxygen saturation", "emergency", f"SpO2 is {spo2:.0f}%."))
    elif spo2 < 94:
        flags.append(warning("Low oxygen saturation", "high", f"SpO2 is {spo2:.0f}%."))
    if sleep_hours < 5:
        flags.append(warning("Low sleep duration", "medium", f"Reported sleep is {sleep_hours:.1f} hours."))
    if factor_count:
        flags.append(warning("Existing risk factors", "medium", f"{factor_count} risk factor(s) were reported."))

    completeness = _input_completeness(data)
    critical_fields = ("heart_rate", "systolic_bp", "diastolic_bp", "spo2")
    missing_critical = [field for field in critical_fields if not _provided(data, field)]
    confidence = clamp(55.0 + completeness * 35.0 - len(missing_critical) * 6.0)

    return {
        "risk_score": percentage(risk_score),
        "raw_risk_score": percentage(raw_risk_score),
        "risk_category": score_band(risk_score),
        "bp_trend_prediction": bp_stage(systolic, diastolic),
        "vitals_summary": {
            "age": age,
            "gender": data.get("gender", "not provided"),
            "heart_rate": heart_rate,
            "systolic_bp": systolic,
            "diastolic_bp": diastolic,
            "spo2": spo2,
            "sleep_hours": sleep_hours,
            "activity_level": activity,
            "bmi": round(bmi, 1) if bmi else None,
            "bmi_category": bmi_stage(bmi),
        },
        "feature_scores": {name: round(value, 2) for name, value in scores.items()},
        "feature_contributions": contribution_dict(scores),
        "summary": (
            f"BP is in the {bp_stage(systolic, diastolic).lower()}, BMI is {bmi_stage(bmi).lower()}, "
            f"and reported activity is {activity.lower()}."
        ),
        "warning_flags": flags,
        "bmi": round(bmi, 1) if bmi else None,
        "tabular_risk_score": percentage(risk_score),
        "risk_factors": [flag["label"] for flag in flags],
        "protective_factors": [
            item for item in [
                "healthy SpO2" if spo2 >= 96 else "",
                "adequate sleep" if sleep_hours >= 7 else "",
                "active lifestyle" if activity.lower() in {"high", "active"} else "",
            ] if item
        ],
        "explanation": (
            f"Tabular risk is driven by {bp_stage(systolic, diastolic).lower()}, "
            f"BMI {round(bmi, 1) if bmi else 'unknown'}, sleep {sleep_hours:.1f} hours, "
            f"and {factor_count} reported risk factor(s)."
        ),
        "input_completeness": round(completeness, 3),
        "missing_critical_fields": missing_critical,
        "safety_floor_applied": risk_score > raw_risk_score,
        "safety_floor_reason": floor_reason,
        "confidence_score": percentage(confidence),
    }
