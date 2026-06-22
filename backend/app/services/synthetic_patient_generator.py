"""Demo patient library for one-click simulations."""

from __future__ import annotations

from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def demo_patients() -> list[dict[str, Any]]:
    ppg = str(DATA_DIR / "sample_ppg.csv")
    image = str(DATA_DIR / "sample_report.png")
    return [
        {
            "id": "healthy_student",
            "name": "Healthy student",
            "vitals": {"age": 22, "gender": "Female", "height": 165, "weight": 58, "heart_rate": 72, "systolic_bp": 112, "diastolic_bp": 72, "spo2": 99, "sleep_hours": 7.8, "activity_level": "high"},
            "symptoms": "No major symptoms. Good sleep and regular exercise.",
            "sample_ppg_data_path": ppg,
            "sample_report_image": image,
            "expected_output": "Low Risk",
        },
        {
            "id": "high_bp_adult",
            "name": "High BP adult",
            "vitals": {"age": 54, "gender": "Male", "height": 172, "weight": 88, "heart_rate": 90, "systolic_bp": 156, "diastolic_bp": 96, "spo2": 96, "sleep_hours": 6, "activity_level": "low", "hypertension_history": True},
            "symptoms": "Headache and fatigue after stressful work days.",
            "sample_ppg_data_path": ppg,
            "sample_report_image": image,
            "expected_output": "Moderate Risk",
        },
        {
            "id": "low_spo2_case",
            "name": "Low SpO2 case",
            "vitals": {"age": 46, "gender": "Other", "height": 170, "weight": 76, "heart_rate": 96, "systolic_bp": 130, "diastolic_bp": 84, "spo2": 89, "sleep_hours": 5.5, "activity_level": "moderate"},
            "symptoms": "Shortness of breath and weakness.",
            "sample_ppg_data_path": ppg,
            "sample_report_image": image,
            "expected_output": "High Risk",
        },
        {
            "id": "noisy_ppg_case",
            "name": "Noisy PPG case",
            "vitals": {"age": 35, "gender": "Female", "height": 160, "weight": 67, "heart_rate": 84, "systolic_bp": 122, "diastolic_bp": 80, "spo2": 97, "sleep_hours": 6.5, "activity_level": "moderate"},
            "symptoms": "No symptoms, but wearable reading was taken during movement.",
            "sample_ppg_data_path": ppg,
            "sample_report_image": image,
            "expected_output": "Mild Risk with signal review",
        },
        {
            "id": "emergency_symptom_case",
            "name": "Emergency symptom case",
            "vitals": {"age": 61, "gender": "Male", "height": 175, "weight": 91, "heart_rate": 118, "systolic_bp": 168, "diastolic_bp": 104, "spo2": 92, "sleep_hours": 4.5, "activity_level": "low"},
            "symptoms": "Severe chest pain with shortness of breath and sweating.",
            "sample_ppg_data_path": ppg,
            "sample_report_image": image,
            "expected_output": "Emergency Warning",
        },
        {
            "id": "low_sleep_high_hr",
            "name": "Low sleep + high heart rate case",
            "vitals": {"age": 39, "gender": "Female", "height": 166, "weight": 72, "heart_rate": 108, "systolic_bp": 132, "diastolic_bp": 84, "spo2": 96, "sleep_hours": 3.8, "activity_level": "low"},
            "symptoms": "Fatigue, palpitations, poor sleep, and stress.",
            "sample_ppg_data_path": ppg,
            "sample_report_image": image,
            "expected_output": "Moderate Risk",
        },
        {
            "id": "unclear_report_case",
            "name": "Report image unclear case",
            "vitals": {"age": 44, "gender": "Male", "height": 178, "weight": 80, "heart_rate": 82, "systolic_bp": 126, "diastolic_bp": 82, "spo2": 97, "sleep_hours": 6.8, "activity_level": "moderate"},
            "symptoms": "Mild headache. Report image is unclear.",
            "sample_ppg_data_path": ppg,
            "sample_report_image": image,
            "expected_output": "Mild Risk with lower confidence",
        },
        {
            "id": "moderate_cv_risk",
            "name": "Moderate cardiovascular risk case",
            "vitals": {"age": 58, "gender": "Female", "height": 162, "weight": 82, "heart_rate": 94, "systolic_bp": 145, "diastolic_bp": 88, "spo2": 95, "sleep_hours": 5.2, "activity_level": "low", "diabetes_history": True},
            "symptoms": "Dizziness, fatigue, and occasional palpitations.",
            "sample_ppg_data_path": ppg,
            "sample_report_image": image,
            "expected_output": "Moderate Risk",
        },
    ]

