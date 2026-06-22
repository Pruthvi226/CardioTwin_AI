"""Shared transparent risk, alert, confidence, and recommendation rules."""

from __future__ import annotations

import re
from typing import Any

from .config import clamp, risk_category
from .disclaimer import DISCLAIMER
from .validators import as_bool, as_float


EMERGENCY_TERMS = {
    "severe chest pain",
    "shortness of breath",
    "fainting",
    "syncope",
    "loss of consciousness",
    "blue lips",
    "stroke",
    "crushing chest pain",
}


def get_risk_category(score: float) -> str:
    return risk_category(score)


def text_mentions_very_high_bp(text: str) -> bool:
    match = re.search(r"\b(\d{2,3})\s*/\s*(\d{2,3})\b", text or "")
    if not match:
        return False
    systolic = float(match.group(1))
    diastolic = float(match.group(2))
    return systolic > 180 or diastolic > 120


def text_mentions_low_spo2(text: str) -> bool:
    match = re.search(r"\b(?:spo2|oxygen|o2)\D{0,10}(\d{2,3})\s*%?", text or "", re.I)
    return bool(match and float(match.group(1)) < 90)


def check_emergency_patterns(payload: dict[str, Any]) -> dict[str, Any]:
    patient = payload.get("patient") or payload.get("tabular") or payload.get("vitals") or {}
    text_result = payload.get("text_result") or {}
    image_result = payload.get("image_result") or {}
    raw_text = " ".join(
        [
            str(payload.get("symptoms", "")),
            str(payload.get("notes", "")),
            str(text_result.get("interpretation", "")),
            " ".join(map(str, text_result.get("matched_symptoms", []) or [])),
            str(image_result.get("ocr_text", "")),
        ]
    ).lower()

    systolic = as_float(patient.get("systolic_bp", patient.get("sbp")), 0)
    diastolic = as_float(patient.get("diastolic_bp", patient.get("dbp")), 0)
    spo2 = as_float(patient.get("spo2"), 100)

    flags: list[dict[str, str]] = []
    if "chest pain" in raw_text and "shortness of breath" in raw_text:
        flags.append({"label": "Chest pain with shortness of breath", "severity": "emergency"})
    if systolic > 180 or diastolic > 120:
        flags.append({"label": "Very high blood pressure", "severity": "emergency"})
    if spo2 < 90:
        flags.append({"label": "Low SpO2", "severity": "emergency"})
    if "fainting" in raw_text and "palpitations" in raw_text:
        flags.append({"label": "Fainting with palpitations", "severity": "emergency"})
    if "severe dizziness" in raw_text and (systolic > 160 or text_mentions_very_high_bp(raw_text)):
        flags.append({"label": "Severe dizziness with high BP", "severity": "emergency"})
    if any(term in raw_text for term in EMERGENCY_TERMS) or text_mentions_very_high_bp(raw_text) or text_mentions_low_spo2(raw_text):
        flags.append({"label": "Emergency-related text pattern", "severity": "high"})

    deduped = []
    seen = set()
    for flag in flags:
        if flag["label"] not in seen:
            deduped.append(flag)
            seen.add(flag["label"])

    if any(flag["severity"] == "emergency" for flag in deduped):
        level = "Emergency Warning"
        message = "Emergency warning pattern detected. Please seek immediate medical attention."
    elif deduped:
        level = "High Attention"
        message = "Potential warning pattern detected. Please consult a healthcare professional promptly."
    else:
        level = "Routine"
        message = "No emergency warning pattern was detected from the provided data."

    return {
        "alert_level": level,
        "alert_message": f"{message} This system is not a diagnosis tool.",
        "emergency_flags": deduped,
        "recommended_action": (
            "Seek immediate medical attention now."
            if level == "Emergency Warning"
            else "Monitor symptoms and consult a qualified clinician if symptoms persist or worsen."
        ),
        "disclaimer": DISCLAIMER,
    }


def generate_recommendations(payload: dict[str, Any]) -> dict[str, Any]:
    patient = payload.get("patient") or payload.get("tabular") or payload
    signal = payload.get("signal_result") or {}
    text = payload.get("text_result") or {}

    systolic = as_float(patient.get("systolic_bp"), 120)
    diastolic = as_float(patient.get("diastolic_bp"), 80)
    sleep = as_float(patient.get("sleep_hours"), 7)
    activity = str(patient.get("activity_level", "moderate")).lower()
    spo2 = as_float(patient.get("spo2"), 98)
    weight = as_float(patient.get("weight"), 0)
    height = as_float(patient.get("height"), 0)
    bmi = as_float(patient.get("bmi"), 0)
    if bmi <= 0 and height > 0 and weight > 0:
        bmi = weight / ((height / 100) ** 2)

    lifestyle: list[str] = []
    monitoring: list[str] = []
    if systolic >= 130 or diastolic >= 80:
        lifestyle.append("Track blood pressure consistently and reduce high-salt processed foods.")
        monitoring.append("Repeat BP readings at consistent times and review elevated values with a clinician.")
    if sleep < 7:
        lifestyle.append("Prioritize 7-8 hours of sleep and track whether better sleep improves heart rate and BP.")
    if activity in {"low", "sedentary", "inactive"}:
        lifestyle.append("Add gentle activity such as walking if safe and appropriate for your health status.")
    if bmi >= 25:
        lifestyle.append("Consider nutrition and activity habits that support a healthier BMI over time.")
    if as_bool(patient.get("smoking_status")):
        lifestyle.append("Seek support for smoking cessation because smoking increases cardiovascular risk.")
    if spo2 < 95:
        monitoring.append("Monitor oxygen saturation and seek care if low readings persist or symptoms worsen.")
    if signal.get("quality_score", 100) < 60:
        monitoring.append("Repeat the PPG reading with less motion because signal quality was limited.")
    if text.get("matched_symptoms"):
        monitoring.append("Track symptom timing, severity, and triggers before speaking with a healthcare professional.")

    if not lifestyle:
        lifestyle.append("Maintain balanced sleep, activity, hydration, and routine health monitoring.")
    if not monitoring:
        monitoring.append("Continue periodic monitoring and compare future readings for trend changes.")

    return {
        "lifestyle_recommendations": lifestyle,
        "monitoring_recommendations": monitoring,
        "doctor_consultation_note": "Consult a qualified healthcare professional for persistent, severe, or concerning symptoms.",
        "safety_disclaimer": DISCLAIMER,
    }


def reliability_score(results: dict[str, Any]) -> dict[str, Any]:
    signal = results.get("signal_result") or {}
    tabular = results.get("tabular_result") or {}
    text = results.get("text_result") or {}
    image = results.get("image_result") or {}

    text_present = bool(text.get("input_present") or text.get("matched_symptoms") or text.get("extracted_symptoms"))
    image_present = bool(image and not image.get("demo_mode") and (image.get("ocr_text") or image.get("extracted_values")))
    signal_present = bool(signal)
    tabular_present = bool(tabular)

    missing = [
        name for name, present in {
            "signal": signal_present,
            "tabular": tabular_present,
            "text": text_present,
            "image": image_present,
        }.items()
        if not present
    ]

    score = 100.0
    reasons = []
    if signal:
        quality = as_float(signal.get("quality_score", signal.get("signal_quality")), 50)
        score -= max(0, 75 - quality) * 0.35
        rejected = as_float(signal.get("features", {}).get("rejected_interval_ratio"), 0)
        score -= rejected * 8
        if quality < 60:
            reasons.append("PPG signal quality is limited.")
        if rejected > 0.35:
            reasons.append("PPG peak intervals are unstable.")
    if tabular:
        completeness = as_float(tabular.get("input_completeness"), 0)
        if completeness <= 0:
            completeness = len([v for v in tabular.get("vitals_summary", {}).values() if v not in (None, "", "not provided")]) / 8
        score -= max(0, 1 - completeness) * 18
        if tabular.get("missing_critical_fields"):
            reasons.append("Some critical vitals are missing.")
    if text and not text_present:
        score -= 8
        reasons.append("Symptom details are limited.")
    if image:
        if image.get("demo_mode") or not image.get("extracted_values"):
            score -= 12
            reasons.append("Medical report image clarity or extracted values are limited.")
    score -= len(missing) * 8

    if missing:
        reasons.append(f"Missing modalities: {', '.join(missing)}.")
    if not reasons:
        reasons.append("Most available inputs are complete and internally consistent.")

    return {
        "confidence_score": round(clamp(score), 2),
        "confidence_reason": " ".join(reasons),
        "missing_inputs": missing,
        "reliability_warning": "Missing or low-quality inputs reduce reliability." if missing or score < 70 else "",
    }
