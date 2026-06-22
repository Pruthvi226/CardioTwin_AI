"""Symptom and clinical-note interpretation."""

from __future__ import annotations

import re
from typing import Any

from ..services.feature_extraction import contribution_dict, score_band, warning
from ..utils.config import clamp
from ..utils.validators import percentage


NEGATION_PATTERN = re.compile(
    r"\b(no|not|denies|denied|without|negative for|free of|absence of|never had)\b",
    re.IGNORECASE,
)

EMERGENCY_TERMS = {
    "severe chest pain": 45,
    "chest pain radiating": 45,
    "fainting": 38,
    "loss of consciousness": 42,
    "stroke": 45,
    "blue lips": 42,
    "severe shortness of breath": 45,
}

HIGH_TERMS = {
    "chest pain": 28,
    "shortness of breath": 26,
    "breathlessness": 24,
    "palpitations": 18,
    "dizziness": 16,
    "severe dizziness": 24,
    "syncope": 30,
    "irregular heartbeat": 22,
    "left arm pain": 24,
}

MEDIUM_TERMS = {
    "fatigue": 10,
    "headache": 8,
    "poor sleep": 8,
    "stress": 8,
    "swelling": 12,
    "nausea": 8,
    "sedentary": 8,
}

LOW_TERMS = {
    "mild discomfort": 4,
    "exercise": -4,
    "balanced diet": -4,
}


def _is_negated(lowered: str, start_index: int) -> bool:
    window = lowered[max(0, start_index - 45):start_index]
    # Stop negation scope at a sentence boundary so "no chest pain. dizziness" keeps dizziness active.
    sentence_fragment = re.split(r"[.!?;\n]", window)[-1]
    return bool(NEGATION_PATTERN.search(sentence_fragment))


def _match_terms(text: str, terms: dict[str, int]) -> tuple[dict[str, int], list[str]]:
    lowered = text.lower()
    matched: dict[str, int] = {}
    negated: list[str] = []
    for term, score in terms.items():
        for match in re.finditer(re.escape(term), lowered):
            if _is_negated(lowered, match.start()):
                if term not in negated:
                    negated.append(term)
                continue
            matched[term] = score
            break
    return matched, negated


def _combination_score(matched_terms: set[str]) -> tuple[float, list[dict[str, str]]]:
    flags: list[dict[str, str]] = []
    score = 0.0
    chest_pain = "chest pain" in matched_terms or "severe chest pain" in matched_terms or "chest pain radiating" in matched_terms
    breathing_issue = "shortness of breath" in matched_terms or "severe shortness of breath" in matched_terms or "breathlessness" in matched_terms
    fainting = "fainting" in matched_terms or "syncope" in matched_terms or "loss of consciousness" in matched_terms

    if chest_pain and breathing_issue:
        score = max(score, 55.0)
        flags.append(warning(
            "Chest pain with breathing difficulty",
            "emergency",
            "Emergency warning pattern detected from symptom combination.",
        ))
    if fainting and "palpitations" in matched_terms:
        score = max(score, 50.0)
        flags.append(warning(
            "Fainting with palpitations",
            "emergency",
            "Emergency warning pattern detected from symptom combination.",
        ))
    return score, flags


def analyze_text_notes(data: dict[str, Any]) -> dict[str, Any]:
    parts = [
        str(data.get("symptoms", "")),
        str(data.get("lifestyle_notes", "")),
        str(data.get("medication_notes", "")),
        str(data.get("doctor_notes", "")),
        str(data.get("notes", "")),
    ]
    text = "\n".join(part for part in parts if part.strip())
    input_present = bool(text.strip())

    emergency, negated_emergency = _match_terms(text, EMERGENCY_TERMS)
    high, negated_high = _match_terms(text, HIGH_TERMS)
    medium, negated_medium = _match_terms(text, MEDIUM_TERMS)
    low, negated_low = _match_terms(text, LOW_TERMS)

    matched_terms = set(emergency) | set(high) | set(medium)
    combination_risk, combination_flags = _combination_score(matched_terms)

    scores = {
        "emergency_terms": sum(emergency.values()),
        "high_risk_terms": sum(high.values()),
        "medium_risk_terms": sum(medium.values()),
        "combination_patterns": combination_risk,
        "protective_terms": min(0, sum(low.values())),
    }
    risk_score = clamp(
        scores["emergency_terms"]
        + scores["high_risk_terms"]
        + scores["medium_risk_terms"]
        + scores["combination_patterns"]
        + scores["protective_terms"]
    )
    if emergency or combination_flags:
        severity = "Emergency warning"
        risk_score = max(risk_score, 82)
    elif risk_score >= 51:
        severity = "High"
    elif risk_score >= 26:
        severity = "Medium"
    else:
        severity = "Low"

    flags = []
    for term in emergency:
        flags.append(warning("Emergency symptom", "emergency", f"Reported phrase: {term}."))
    flags.extend(combination_flags)
    for term in high:
        flags.append(warning("Cardiovascular symptom", "high", f"Reported symptom: {term}."))
    for term in medium:
        flags.append(warning("General symptom/lifestyle factor", "medium", f"Reported factor: {term}."))

    matched = list(emergency) + list(high) + list(medium)
    negated_terms = negated_emergency + negated_high + negated_medium + negated_low
    interpretation = (
        "Emergency warning symptoms were detected. Seek urgent professional care if this reflects current symptoms."
        if emergency or combination_flags
        else "Symptoms suggest elevated cardiovascular review priority."
        if high
        else "Symptoms currently appear low to moderate based on keyword screening."
        if input_present
        else "No symptom text was provided, so symptom-based risk was not available."
    )

    confidence = 48
    if input_present:
        confidence = 68 if matched else 58
    if emergency or combination_flags:
        confidence = 78

    return {
        "risk_score": percentage(risk_score),
        "risk_category": score_band(risk_score),
        "symptom_severity": severity,
        "matched_symptoms": matched,
        "negated_symptoms": negated_terms,
        "symptom_scores": scores,
        "symptom_contributions": contribution_dict({key: max(0.0, value) for key, value in scores.items()}),
        "interpretation": interpretation,
        "warning_flags": flags,
        "extracted_symptoms": matched,
        "symptom_risk_score": percentage(risk_score),
        "emergency_flags": [flag for flag in flags if flag.get("severity") == "emergency"],
        "explanation": interpretation,
        "confidence_score": percentage(confidence),
        "input_present": input_present,
        "text_length": len(text),
    }
