"""Guardrailed report-grounded chatbot service."""

from __future__ import annotations

from typing import Any

from ..utils.disclaimer import DISCLAIMER


def answer_question(question: str, context: dict[str, Any]) -> dict[str, str]:
    question_lower = (question or "").lower()
    fusion = context.get("fusion_result") or context.get("fusion") or context
    response = "I can answer based on the generated report and submitted data only."

    if "why" in question_lower and "risk" in question_lower:
        response = fusion.get("explanation") or fusion.get("final_explanation") or "The risk score is based on signal, vitals, symptoms, and report findings."
    elif "factor" in question_lower or "affected" in question_lower or "most" in question_lower:
        dominant = fusion.get("dominant_modality", "the highest weighted risk input")
        response = f"The strongest available influence appears to be {dominant}."
    elif "ppg" in question_lower or "signal" in question_lower:
        signal = context.get("signal_result") or {}
        response = signal.get("explanation") or f"PPG reliability is listed as {signal.get('reliability', 'not available')}."
    elif "monitor" in question_lower:
        response = "Monitor blood pressure, heart rate, SpO2, sleep, symptoms, and signal quality trends."
    elif "report" in question_lower or "ocr" in question_lower:
        image = context.get("image_result") or {}
        response = image.get("summary") or "The report reader extracts visible values and summarizes OCR text when available."
    elif "doctor" in question_lower and "patient" in question_lower:
        response = "Doctor summaries are structured and clinical-style; patient summaries use simpler language and monitoring guidance."

    return {
        "answer": f"{response} This is not medical advice or a diagnosis.",
        "safety_disclaimer": DISCLAIMER,
    }

