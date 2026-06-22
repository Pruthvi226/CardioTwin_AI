"""Downloadable clinical-style report generation."""

from __future__ import annotations

from io import BytesIO
from textwrap import wrap
from typing import Any

from ..utils.disclaimer import DISCLAIMER


def _report_context(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    fusion = payload.get("fusion_result", payload)
    components = payload.get("component_results", {}) or {}
    recommendations = components.get("recommendations", {}) or {}
    alert = components.get("alert", {}) or {}
    anomaly = components.get("anomaly", {}) or {}
    return fusion, recommendations, alert, anomaly


def _plain_text_report(payload: dict[str, Any]) -> bytes:
    fusion, recommendations, alert, anomaly = _report_context(payload)
    lines = [
        "CardioTwin AI: Multimodal Health Risk Digital Twin Report",
        "",
        f"Final risk score: {fusion.get('final_risk_score', 'not available')}",
        f"Risk category: {fusion.get('risk_category', 'not available')}",
        f"Confidence: {fusion.get('confidence_score', 'not available')}",
        f"Confidence reason: {fusion.get('confidence_reason', 'not available')}",
        "",
        "Clinical assist summary:",
        str(fusion.get("doctor_summary", "No doctor summary available.")),
        "",
        "Practitioner handoff:",
        str((fusion.get("clinician_assist") or {}).get("handoff_note", "No practitioner handoff available.")),
        "",
        "Plain-language patient summary:",
        str(fusion.get("patient_summary", "No patient summary available.")),
        "",
        "What to do now:",
        "; ".join((fusion.get("patient_guidance") or {}).get("what_to_do_now", [])) or "No patient guidance generated.",
        "",
        "Recommendations:",
        "; ".join(recommendations.get("lifestyle_recommendations", []) + recommendations.get("monitoring_recommendations", [])) or "No recommendations generated.",
        "",
        "Alert and anomaly status:",
        str(alert.get("alert_message", "No alert generated.")),
        str(anomaly.get("explanation", "No anomaly analysis generated.")),
        "",
        "Limitations:",
        "; ".join(fusion.get("limitations", [])),
        "",
        f"Disclaimer: {DISCLAIMER}",
    ]
    return "\n".join(lines).encode("utf-8")


def generate_report(payload: dict[str, Any]) -> tuple[bytes, str, str]:
    """Generate a PDF report when reportlab is installed, otherwise return text."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        return _plain_text_report(payload), "text/plain", "multimodal_health_risk_report.txt"

    fusion, recommendations, alert, anomaly = _report_context(payload)
    buffer = BytesIO()
    page = canvas.Canvas(buffer, pagesize=letter)
    _, height = letter
    y = height - 48

    def draw_line(text: str, size: int = 10, gap: int = 15) -> None:
        nonlocal y
        page.setFont("Helvetica", size)
        for part in wrap(str(text), width=96):
            if y < 72:
                page.showPage()
                y = height - 48
                page.setFont("Helvetica", size)
            page.drawString(48, y, part)
            y -= gap

    page.setTitle("CardioTwin AI Health Risk Report")
    page.setFont("Helvetica-Bold", 17)
    page.drawString(48, y, "CardioTwin AI: Multimodal Health Risk Digital Twin Report")
    y -= 30

    page.setFont("Helvetica-Bold", 12)
    page.drawString(48, y, f"Risk Score: {fusion.get('final_risk_score', 'not available')}/100")
    page.drawString(250, y, f"Category: {fusion.get('risk_category', 'not available')}")
    y -= 24

    contributions = fusion.get("modality_contributions", {}) or {}
    if contributions:
        draw_line("Modality contribution chart", size=12, gap=16)
        chart_x = 70
        for name, item in contributions.items():
            influence = float(item.get("influence_percent", 0))
            bar_width = min(360, influence * 3.6)
            page.setFillColor(colors.HexColor("#0f766e"))
            page.rect(chart_x + 95, y - 2, bar_width, 10, fill=1, stroke=0)
            page.setFillColor(colors.black)
            page.setFont("Helvetica", 9)
            page.drawString(chart_x, y - 1, name.title())
            page.drawString(chart_x + 465, y - 1, f"{influence:.1f}%")
            y -= 18
        y -= 8

    draw_line(f"Confidence: {fusion.get('confidence_score', 'not available')} - {fusion.get('confidence_reason', '')}", size=10, gap=14)
    y -= 6
    draw_line("Clinical assist summary", size=12, gap=18)
    draw_line(fusion.get("doctor_summary", "No doctor summary available."))
    clinician = fusion.get("clinician_assist") or {}
    if clinician:
        draw_line(f"Practitioner handoff: {clinician.get('handoff_note', 'No handoff note available.')}")
        for item in clinician.get("recommended_actions", [])[:4]:
            draw_line(f"- {item}")
    y -= 6
    draw_line("Plain-language patient summary", size=12, gap=18)
    draw_line(fusion.get("patient_summary", "No patient summary available."))
    guidance = fusion.get("patient_guidance") or {}
    if guidance:
        draw_line(guidance.get("what_it_means", ""))
        for item in guidance.get("what_to_do_now", [])[:4]:
            draw_line(f"- {item}")
    y -= 6
    draw_line("Personalized recommendations", size=12, gap=18)
    recommendation_items = recommendations.get("lifestyle_recommendations", []) + recommendations.get("monitoring_recommendations", [])
    for item in recommendation_items or ["No recommendations generated."]:
        draw_line(f"- {item}")
    y -= 6
    draw_line("Alert and anomaly status", size=12, gap=18)
    draw_line(alert.get("alert_message", "No alert generated."))
    draw_line(anomaly.get("explanation", "No anomaly analysis generated."))
    y -= 6
    draw_line("Warning flags", size=12, gap=18)
    for flag in fusion.get("warning_flags", []) or [{"label": "None", "detail": "No warning flags generated."}]:
        draw_line(f"- {flag.get('label')}: {flag.get('detail')}")
    y -= 6
    draw_line("Limitations", size=12, gap=18)
    for item in fusion.get("limitations", []) or ["Educational rule-based prototype only."]:
        draw_line(f"- {item}")
    y -= 6
    draw_line(f"Disclaimer: {DISCLAIMER}", size=9, gap=13)

    page.save()
    return buffer.getvalue(), "application/pdf", "multimodal_health_risk_report.pdf"