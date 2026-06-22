"""Late-fusion risk model for multimodal health inputs."""

from __future__ import annotations

from typing import Any

from ..services.explanation_service import (
    build_multimodal_explanation,
    clinician_assist,
    collect_warning_flags,
    doctor_summary,
    patient_guidance,
    patient_summary,
)
from ..utils.config import clamp, get_fusion_weights, risk_category
from ..utils.risk_rules import reliability_score
from ..utils.validators import percentage


MODALITIES = ("signal", "tabular", "text", "image")


def _score(result: dict[str, Any] | None) -> float:
    if not result:
        return 0.0
    return clamp(float(result.get("risk_score", result.get("final_risk_score", 0.0))))


def _confidence(result: dict[str, Any] | None) -> float:
    if not result:
        return 0.0
    return clamp(float(result.get("confidence_score", result.get("confidence", 50.0))))


def _has_evidence(name: str, result: dict[str, Any] | None) -> bool:
    if not result:
        return False
    if name == "text":
        return bool(result.get("input_present") or result.get("matched_symptoms") or result.get("extracted_symptoms"))
    if name == "image":
        return bool(result.get("ocr_text") or result.get("extracted_text") or result.get("extracted_values"))
    return True


def _quality_factor(name: str, result: dict[str, Any] | None) -> float:
    if not _has_evidence(name, result):
        return 0.0

    factor = _confidence(result) / 100.0
    if name == "signal":
        reliability = str(result.get("reliability", "")).lower()
        if "noisy" in reliability:
            factor *= 0.65
        elif "review" in reliability:
            factor *= 0.82
    elif name == "image" and result.get("demo_mode"):
        factor *= 0.55

    return clamp(factor, 0.05, 1.0)


def _effective_weights(weights: dict[str, float], results: dict[str, dict[str, Any] | None]) -> dict[str, float]:
    raw_weights = {
        name: weights.get(name, 0.0) * _quality_factor(name, results.get(name))
        for name in MODALITIES
    }
    total = sum(raw_weights.values())
    if total <= 0:
        return {name: 0.0 for name in MODALITIES}
    return {name: raw_weights[name] / total for name in MODALITIES}


def _safety_score_floor(warning_flags: list[dict[str, Any]]) -> tuple[float, str]:
    severities = {str(flag.get("severity", "")).lower() for flag in warning_flags}
    if "emergency" in severities:
        return 82.0, "Emergency warning pattern detected."
    if "high" in severities:
        return 55.0, "High-attention warning pattern detected."
    return 0.0, ""


def _drivers(name: str, result: dict[str, Any] | None) -> list[str]:
    if not result:
        return []
    if name == "signal":
        return [
            f"PPG quality {result.get('quality_score', result.get('signal_quality', 'unknown'))}",
            f"estimated HR {result.get('heart_rate_estimate', result.get('heart_rate', 'unknown'))} bpm",
        ]
    if name == "tabular":
        summary = result.get("vitals_summary", {})
        return [
            f"BP {summary.get('systolic_bp', 'unknown')}/{summary.get('diastolic_bp', 'unknown')}",
            f"sleep {summary.get('sleep_hours', 'unknown')} hours",
            f"BMI {summary.get('bmi', result.get('bmi', 'unknown'))}",
        ]
    if name == "text":
        symptoms = result.get("matched_symptoms") or result.get("extracted_symptoms") or []
        return [f"symptom '{item}'" for item in symptoms[:4]]
    if name == "image":
        values = result.get("extracted_values", {})
        return [f"report {key}={value}" for key, value in list(values.items())[:4]]
    return []


def calculate_multimodal_risk(
    signal_result: dict[str, Any] | None,
    tabular_result: dict[str, Any] | None,
    text_result: dict[str, Any] | None,
    image_result: dict[str, Any] | None,
    patient: dict[str, Any] | None = None,
) -> dict[str, Any]:
    weights = get_fusion_weights()
    results = {
        "signal": signal_result,
        "tabular": tabular_result,
        "text": text_result,
        "image": image_result,
    }

    effective_weights = _effective_weights(weights, results)
    weighted_points = {name: effective_weights[name] * _score(result) for name, result in results.items()}
    pre_escalation_score = clamp(sum(weighted_points.values()))

    warning_flags = collect_warning_flags(signal_result, tabular_result, text_result, image_result)
    safety_floor, safety_reason = _safety_score_floor(warning_flags)
    final_score = clamp(max(pre_escalation_score, safety_floor))
    category = risk_category(final_score)

    total_points = sum(weighted_points.values())
    contributions = {}
    for name in MODALITIES:
        result = results.get(name)
        influence = (weighted_points[name] / total_points * 100.0) if total_points > 0 else 0.0
        contributions[name] = {
            "weight": round(effective_weights[name], 3),
            "configured_weight": round(weights[name], 3),
            "quality_factor": round(_quality_factor(name, result), 3),
            "available": _has_evidence(name, result),
            "risk_score": percentage(_score(result)),
            "weighted_points": round(weighted_points[name], 2),
            "influence_percent": round(influence, 2),
        }

    available = [name for name, result in results.items() if _has_evidence(name, result)]
    completeness = len(available) / 4.0
    base_confidence = sum(effective_weights[name] * _confidence(result) for name, result in results.items())
    base_confidence = clamp(base_confidence * (0.72 + 0.28 * completeness))

    drivers: list[str] = []
    for name, result in sorted(results.items(), key=lambda item: weighted_points[item[0]], reverse=True):
        drivers.extend(_drivers(name, result))
    warning_drivers = [
        str(flag.get("label"))
        for flag in warning_flags
        if flag.get("label") and str(flag.get("severity", "")).lower() in {"high", "emergency"}
    ]
    top_drivers = []
    for driver in warning_drivers + drivers:
        if "unknown" in driver.lower() or driver in top_drivers:
            continue
        top_drivers.append(driver)
        if len(top_drivers) >= 6:
            break

    reliability = reliability_score({
        "signal_result": signal_result,
        "tabular_result": tabular_result,
        "text_result": text_result,
        "image_result": image_result,
    })
    explanation = build_multimodal_explanation(final_score, category, contributions, top_drivers)

    fusion = {
        "final_risk_score": percentage(final_score),
        "pre_escalation_risk_score": percentage(pre_escalation_score),
        "risk_category": category,
        "blood_pressure_trend_prediction": (
            tabular_result or {}
        ).get("bp_trend_prediction")
        or (signal_result or {}).get("bp_prediction", {}).get("trend", "Not available"),
        "modality_contributions": contributions,
        "fusion_method": "reliability_adjusted_late_fusion",
        "effective_fusion_weights": {name: round(value, 3) for name, value in effective_weights.items()},
        "configured_fusion_weights": {name: round(value, 3) for name, value in weights.items()},
        "dominant_modality": max(contributions, key=lambda name: contributions[name]["weighted_points"]),
        "top_risk_drivers": top_drivers,
        "confidence_score": percentage(min(base_confidence, reliability["confidence_score"])),
        "confidence_reason": reliability["confidence_reason"],
        "missing_inputs": reliability["missing_inputs"],
        "reliability_warning": reliability["reliability_warning"],
        "safety_escalation_applied": final_score > pre_escalation_score,
        "safety_escalation_reason": safety_reason,
        "explanation": explanation,
        "final_explanation": explanation,
        "warning_flags": warning_flags,
        "limitations": [
            "Hybrid scoring remains rule-based until validated clinical datasets are connected.",
            "Reliability-adjusted fusion reduces missing-input dilution but cannot create clinical certainty.",
            "OCR and symptom matching can miss context and must be reviewed by qualified professionals.",
        ],
    }
    fusion["clinician_assist"] = clinician_assist(patient, signal_result or {}, tabular_result or {}, text_result or {}, image_result or {}, fusion)
    fusion["patient_guidance"] = patient_guidance(fusion, warning_flags)
    fusion["doctor_summary"] = doctor_summary(patient, signal_result or {}, tabular_result or {}, text_result or {}, image_result or {}, fusion)
    fusion["patient_summary"] = patient_summary(fusion, warning_flags)
    fusion["audience_modes"] = {
        "medical_practitioner": fusion["clinician_assist"],
        "common_user": fusion["patient_guidance"],
    }
    return fusion
