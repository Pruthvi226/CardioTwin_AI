"""Human-readable summaries and explanations."""

from __future__ import annotations

from typing import Any

from ..utils.disclaimer import DISCLAIMER


def signal_quality_explanation(quality_score: float, artifact_ratio: float) -> str:
    if quality_score >= 80:
        return "The PPG waveform appears reliable with limited artifact burden."
    if quality_score >= 55:
        return "The PPG waveform is usable but shows moderate noise or motion artifacts."
    return "The PPG waveform is noisy, so signal-derived predictions should be reviewed carefully."


def build_multimodal_explanation(
    final_score: float,
    category: str,
    contributions: dict[str, dict[str, float]],
    drivers: list[str],
) -> str:
    top = sorted(contributions.items(), key=lambda item: item[1].get("weighted_points", 0), reverse=True)
    top_names = [name for name, payload in top if payload.get("weighted_points", 0) > 0][:2]
    modality_text = ", ".join(top_names) if top_names else "the available inputs"
    driver_text = ", ".join(drivers[:5]) if drivers else "the submitted health data"
    return (
        f"The final risk score is {final_score:.1f}/100 ({category}). It is influenced mainly by "
        f"{modality_text}, especially {driver_text}."
    )


def collect_warning_flags(*results: dict[str, Any] | None) -> list[dict[str, str]]:
    flags: list[dict[str, str]] = []
    for result in results:
        if not result:
            continue
        for key in ("warning_flags", "warnings"):
            for flag in result.get(key, []) or []:
                if isinstance(flag, dict):
                    flags.append(flag)
                else:
                    flags.append({"label": str(flag), "severity": "info", "detail": str(flag)})
    return flags


def _flag_has_severity(flags: list[dict[str, Any]], *levels: str) -> bool:
    wanted = {level.lower() for level in levels}
    return any(str(flag.get("severity", "")).lower() in wanted for flag in flags)


def _risk_priority(fusion_result: dict[str, Any], warning_flags: list[dict[str, Any]]) -> str:
    category = str(fusion_result.get("risk_category", "")).lower()
    if _flag_has_severity(warning_flags, "emergency"):
        return "Immediate clinical attention pattern"
    if _flag_has_severity(warning_flags, "high") or "high" in category:
        return "Prompt clinical review suggested"
    if "moderate" in category:
        return "Routine clinical review suggested"
    return "Routine self-monitoring with follow-up if symptoms persist"


def _top_modalities(fusion_result: dict[str, Any]) -> list[str]:
    contributions = fusion_result.get("modality_contributions", {}) or {}
    ordered = sorted(contributions.items(), key=lambda item: item[1].get("influence_percent", 0), reverse=True)
    return [f"{name}: {payload.get('influence_percent', 0)}% influence" for name, payload in ordered if payload.get("influence_percent", 0) > 0][:4]


def clinician_assist(
    patient: dict[str, Any] | None,
    signal_result: dict[str, Any],
    tabular_result: dict[str, Any],
    text_result: dict[str, Any],
    image_result: dict[str, Any],
    fusion_result: dict[str, Any],
) -> dict[str, Any]:
    """Build a practitioner-facing decision-support summary, not a diagnosis."""
    warning_flags = fusion_result.get("warning_flags", []) or []
    vitals = tabular_result.get("vitals_summary", {}) or {}
    overview = patient or {}
    priority = _risk_priority(fusion_result, warning_flags)
    missing_inputs = fusion_result.get("missing_inputs", []) or []

    key_findings = []
    if vitals:
        key_findings.append(
            f"Vitals: BP {vitals.get('systolic_bp', 'NA')}/{vitals.get('diastolic_bp', 'NA')}, "
            f"HR {vitals.get('heart_rate', 'NA')}, SpO2 {vitals.get('spo2', 'NA')}, BMI {vitals.get('bmi', 'NA')}."
        )
    if signal_result:
        key_findings.append(
            f"PPG: quality {signal_result.get('quality_score', 'NA')}, reliability {signal_result.get('reliability', 'NA')}, "
            f"estimated HR {signal_result.get('heart_rate_estimate', 'NA')} bpm."
        )
    if text_result.get("matched_symptoms"):
        key_findings.append(f"Symptoms detected: {', '.join(map(str, text_result.get('matched_symptoms', [])))}.")
    if image_result.get("extracted_values"):
        key_findings.append(f"Report/OCR values: {image_result.get('extracted_values')}.")
    for driver in fusion_result.get("top_risk_drivers", [])[:4]:
        key_findings.append(f"Driver: {driver}.")

    suggested_review_questions = [
        "Confirm whether symptoms are current, worsening, exertional, or associated with syncope, dyspnea, diaphoresis, or radiating pain.",
        "Repeat abnormal BP, HR, SpO2, or PPG readings with a validated device and proper measurement technique.",
        "Review medications, caffeine/stimulant use, smoking status, diabetes/hypertension history, and relevant family history.",
        "Inspect original report images when OCR confidence is limited or report values drive risk.",
    ]
    if signal_result.get("reliability") in {"Noisy", "Review Needed"}:
        suggested_review_questions.append("Repeat PPG acquisition with reduced motion and adequate sensor contact before relying on signal-derived features.")
    if missing_inputs:
        suggested_review_questions.append(f"Collect missing modalities if clinically relevant: {', '.join(missing_inputs)}.")

    recommended_actions = [
        "Use this output as triage and summarization support only; confirm clinically before acting.",
        "Prioritize review of high/emergency warning flags and abnormal vitals.",
        "Document data quality limitations when sharing or presenting this result.",
    ]
    if _flag_has_severity(warning_flags, "emergency"):
        recommended_actions.insert(0, "Escalate according to local emergency/triage protocol if the warning pattern reflects current symptoms or readings.")

    return {
        "intended_user": "medical_practitioner",
        "purpose": "Decision-support summary for review, triage, and patient discussion; not autonomous diagnosis.",
        "triage_priority": priority,
        "risk_score": fusion_result.get("final_risk_score"),
        "risk_category": fusion_result.get("risk_category"),
        "clinical_snapshot": {
            "age": overview.get("age", vitals.get("age", "not provided")),
            "gender": overview.get("gender", vitals.get("gender", "not provided")),
            "bp": f"{vitals.get('systolic_bp', 'NA')}/{vitals.get('diastolic_bp', 'NA')}",
            "heart_rate": vitals.get("heart_rate", signal_result.get("heart_rate_estimate", "not available")),
            "spo2": vitals.get("spo2", "not available"),
            "bmi": vitals.get("bmi", "not available"),
        },
        "key_findings": key_findings[:8] or ["No major structured findings available from submitted data."],
        "top_modalities": _top_modalities(fusion_result),
        "data_quality": {
            "confidence_score": fusion_result.get("confidence_score"),
            "confidence_reason": fusion_result.get("confidence_reason"),
            "missing_inputs": missing_inputs,
            "reliability_warning": fusion_result.get("reliability_warning", ""),
        },
        "suggested_review_questions": suggested_review_questions,
        "recommended_actions": recommended_actions,
        "handoff_note": (
            f"CardioTwin triage priority: {priority}. Risk {fusion_result.get('final_risk_score', 'NA')}/100 "
            f"({fusion_result.get('risk_category', 'NA')}); confidence {fusion_result.get('confidence_score', 'NA')}/100. "
            f"Top drivers: {', '.join(map(str, fusion_result.get('top_risk_drivers', [])[:3])) or 'not available'}."
        ),
        "safety_boundary": DISCLAIMER,
    }


def patient_guidance(fusion_result: dict[str, Any], warning_flags: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a common-user explanation in plain language."""
    category = fusion_result.get("risk_category", "Unknown risk")
    score = fusion_result.get("final_risk_score", "not available")
    emergency = _flag_has_severity(warning_flags, "emergency")
    high = _flag_has_severity(warning_flags, "high")

    if emergency:
        what_it_means = (
            "The information you entered matches an emergency warning pattern. The system cannot diagnose you, "
            "but this pattern should be taken seriously if it reflects what is happening now."
        )
        what_to_do = [
            "Seek immediate medical attention now or contact local emergency services if symptoms are current or severe.",
            "Share your symptoms, blood pressure, oxygen level, and any report findings with a qualified clinician.",
            "Do not use this app to decide that urgent symptoms are safe.",
        ]
    elif high or str(category).lower().startswith("high"):
        what_it_means = (
            "Your inputs show several higher-attention signals. This does not mean you have a disease, "
            "but it is worth discussing with a healthcare professional soon."
        )
        what_to_do = [
            "Repeat unusual readings with a reliable device if possible.",
            "Book a medical review, especially if symptoms continue, worsen, or are new for you.",
            "Keep a note of symptom timing, activity, sleep, and readings to show the clinician.",
        ]
    elif "moderate" in str(category).lower():
        what_it_means = "Your result suggests a moderate risk-awareness level based on the submitted data."
        what_to_do = [
            "Monitor readings over the next few days and look for trends.",
            "Improve basics such as sleep, activity, hydration, and medication adherence as advised by your clinician.",
            "Consult a healthcare professional if symptoms persist or readings stay abnormal.",
        ]
    else:
        what_it_means = "Your result appears lower-risk from the submitted data, but it is not a medical clearance."
        what_to_do = [
            "Continue routine monitoring and healthy habits.",
            "Repeat the analysis if new symptoms or abnormal readings appear.",
            "Ask a healthcare professional if you are worried or have a known condition.",
        ]

    return {
        "intended_user": "common_user",
        "simple_status": f"Current educational risk score: {score}/100 ({category}).",
        "what_it_means": what_it_means,
        "what_to_do_now": what_to_do,
        "when_to_seek_help": [
            "Chest pain, fainting, severe breathlessness, blue lips, or stroke-like symptoms.",
            "Very high blood pressure readings such as systolic over 180 or diastolic over 120.",
            "Oxygen saturation below 90%, especially with breathing difficulty.",
            "Any symptom that feels severe, sudden, unusual, or rapidly worsening.",
        ],
        "confidence_note": fusion_result.get("confidence_reason", "Confidence depends on data quality and completeness."),
        "not_a_diagnosis": DISCLAIMER,
    }


def doctor_summary(
    patient: dict[str, Any] | None,
    signal_result: dict[str, Any],
    tabular_result: dict[str, Any],
    text_result: dict[str, Any],
    image_result: dict[str, Any],
    fusion_result: dict[str, Any],
) -> str:
    assist = clinician_assist(patient, signal_result, tabular_result, text_result, image_result, fusion_result)
    snapshot = assist["clinical_snapshot"]
    findings = "\n".join(f"- {item}" for item in assist["key_findings"])
    actions = "\n".join(f"- {item}" for item in assist["recommended_actions"])
    questions = "\n".join(f"- {item}" for item in assist["suggested_review_questions"][:4])
    return "\n".join(
        [
            f"Clinical assist priority: {assist['triage_priority']}.",
            f"Patient snapshot: age={snapshot.get('age')}, gender={snapshot.get('gender')}, BP={snapshot.get('bp')}, "
            f"HR={snapshot.get('heart_rate')}, SpO2={snapshot.get('spo2')}, BMI={snapshot.get('bmi')}.",
            f"Risk result: {assist.get('risk_score')}/100 ({assist.get('risk_category')}); confidence {assist['data_quality'].get('confidence_score')}/100.",
            "Key findings:",
            findings,
            "Suggested practitioner review:",
            questions,
            "Recommended use:",
            actions,
            f"Disclaimer: {DISCLAIMER}",
        ]
    )


def patient_summary(fusion_result: dict[str, Any], warning_flags: list[dict[str, str]]) -> str:
    guidance = patient_guidance(fusion_result, warning_flags)
    steps = " ".join(guidance["what_to_do_now"][:2])
    return f"{guidance['simple_status']} {guidance['what_it_means']} {steps}"