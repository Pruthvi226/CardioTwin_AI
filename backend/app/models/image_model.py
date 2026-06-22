"""Medical report image OCR and indicator extraction."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from ..services.feature_extraction import bp_stage, extract_numeric_indicators, score_band, warning
from ..utils.config import clamp
from ..utils.validators import percentage


SAMPLE_REPORT_TEXT = (
    "ECG: sinus rhythm. BP 138/86. HR 88. SpO2 96%. "
    "Total cholesterol 212. LDL 136. Glucose 118. Impression: borderline cardiovascular risk."
)


def _ocr_image(raw: bytes | None) -> str:
    if not raw:
        return ""
    try:
        from PIL import Image
        import pytesseract

        image = Image.open(BytesIO(raw))
        return pytesseract.image_to_string(image).strip()
    except Exception:
        return ""


def _bytes_to_possible_text(raw: bytes | None) -> str:
    if not raw:
        return ""
    try:
        decoded = raw.decode("utf-8", errors="ignore")
    except Exception:
        return ""
    return decoded if any(token in decoded.lower() for token in ("bp", "ecg", "cholesterol", "glucose", "spo2")) else ""


def analyze_medical_image(raw: bytes | None = None, filename: str | None = None) -> dict[str, Any]:
    ocr_text = _ocr_image(raw) or _bytes_to_possible_text(raw)
    demo_mode = raw is None or not ocr_text.strip()
    if not ocr_text.strip():
        ocr_text = SAMPLE_REPORT_TEXT

    extracted = extract_numeric_indicators(ocr_text)
    scores = {
        "blood_pressure": 0.0,
        "oxygen": max(0.0, 95 - float(extracted.get("spo2", 98))) * 4.0,
        "lipids": max(0.0, float(extracted.get("ldl", 100)) - 120) * 0.22
        + max(0.0, float(extracted.get("cholesterol", 180)) - 200) * 0.12,
        "glucose": max(0.0, float(extracted.get("glucose", 95)) - 110) * 0.18,
        "troponin": 28.0 if float(extracted.get("troponin", 0)) > 0.04 else 0.0,
        "keyword_findings": 0.0,
    }

    if "systolic_bp" in extracted and "diastolic_bp" in extracted:
        scores["blood_pressure"] = max(0.0, extracted["systolic_bp"] - 120) * 0.45 + max(0.0, extracted["diastolic_bp"] - 80) * 0.6

    lowered = ocr_text.lower()
    for term in ("abnormal ecg", "arrhythmia", "borderline", "hypertrophy"):
        if term in lowered:
            scores["keyword_findings"] += 10
    for term in ("ischemia", "stemi", "myocardial infarction", "acute coronary"):
        if term in lowered:
            scores["keyword_findings"] += 22

    risk_score = clamp(sum(scores.values()))
    flags = []
    if "troponin" in extracted and extracted["troponin"] > 0.04:
        flags.append(warning("Elevated troponin text", "high", "OCR detected troponin above the common rule-based threshold."))
    if "systolic_bp" in extracted and "diastolic_bp" in extracted:
        stage = bp_stage(extracted["systolic_bp"], extracted["diastolic_bp"])
        if "Hypertension" in stage or "crisis" in stage:
            flags.append(warning("Report BP finding", "medium", f"OCR detected BP in the {stage.lower()}."))
    if any(term in lowered for term in ("ischemia", "stemi", "myocardial infarction", "acute coronary")):
        flags.append(warning("High-attention report keyword", "high", "OCR text contained a potentially urgent cardiovascular term."))
    elif scores["keyword_findings"] > 0:
        flags.append(warning("Report keyword finding", "medium", "OCR text contained potentially relevant cardiovascular terms."))

    summary = (
        "OCR extracted report-like values and cardiovascular keywords."
        if extracted
        else "No structured values were extracted; demo report text was used."
    )

    return {
        "risk_score": percentage(risk_score),
        "risk_category": score_band(risk_score),
        "filename": filename or "sample_report.png",
        "ocr_text": ocr_text[:1600],
        "extracted_values": extracted,
        "image_feature_scores": {name: round(value, 2) for name, value in scores.items()},
        "summary": summary,
        "extracted_text": ocr_text[:1600],
        "report_summary": summary,
        "image_risk_score": percentage(risk_score),
        "image_quality_note": "OCR text extracted" if not demo_mode else "Demo or unclear image fallback used",
        "explanation": summary,
        "warning_flags": flags,
        "confidence_score": percentage(min(45, 72 if extracted else 42) if demo_mode else (72 if extracted else 42)),
        "demo_mode": demo_mode,
    }


