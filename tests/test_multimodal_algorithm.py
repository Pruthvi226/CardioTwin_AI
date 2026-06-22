"""Focused tests for the improved multimodal scoring algorithm."""

from __future__ import annotations

import unittest

from backend.app.models.fusion_model import calculate_multimodal_risk
from backend.app.models.tabular_model import analyze_tabular
from backend.app.models.text_model import analyze_text_notes


class MultimodalAlgorithmTest(unittest.TestCase):
    def test_negated_symptoms_do_not_create_high_risk_matches(self) -> None:
        result = analyze_text_notes({"symptoms": "No chest pain or shortness of breath. Mild fatigue today."})

        self.assertNotIn("chest pain", result["matched_symptoms"])
        self.assertNotIn("shortness of breath", result["matched_symptoms"])
        self.assertIn("chest pain", result["negated_symptoms"])
        self.assertLess(result["risk_score"], 30)

    def test_symptom_combination_applies_emergency_floor(self) -> None:
        result = analyze_text_notes({"symptoms": "I have chest pain and shortness of breath."})

        self.assertGreaterEqual(result["risk_score"], 82)
        self.assertTrue(any(flag["severity"] == "emergency" for flag in result["warning_flags"]))

    def test_fusion_reweights_available_modalities_instead_of_diluting_missing_inputs(self) -> None:
        tabular = analyze_tabular({
            "age": 58,
            "gender": "male",
            "height": 172,
            "weight": 88,
            "heart_rate": 94,
            "systolic_bp": 162,
            "diastolic_bp": 104,
            "spo2": 95,
            "sleep_hours": 5,
            "activity_level": "low",
            "hypertension_history": True,
        })

        fusion = calculate_multimodal_risk(None, tabular, None, None, {})

        self.assertEqual(fusion["fusion_method"], "reliability_adjusted_late_fusion")
        self.assertAlmostEqual(fusion["effective_fusion_weights"]["tabular"], 1.0, places=3)
        self.assertIn("signal", fusion["missing_inputs"])
        self.assertGreaterEqual(fusion["final_risk_score"], tabular["risk_score"] - 0.01)

    def test_fusion_returns_practitioner_and_common_user_modes(self) -> None:
        patient = {
            "age": 58,
            "gender": "male",
            "height": 172,
            "weight": 88,
            "heart_rate": 94,
            "systolic_bp": 162,
            "diastolic_bp": 104,
            "spo2": 95,
            "sleep_hours": 5,
            "activity_level": "low",
            "hypertension_history": True,
        }
        tabular = analyze_tabular(patient)
        text = analyze_text_notes({"symptoms": "I have chest pain and shortness of breath."})

        fusion = calculate_multimodal_risk(None, tabular, text, None, patient)

        self.assertIn("clinician_assist", fusion)
        self.assertIn("patient_guidance", fusion)
        self.assertEqual(fusion["audience_modes"]["medical_practitioner"]["intended_user"], "medical_practitioner")
        self.assertEqual(fusion["audience_modes"]["common_user"]["intended_user"], "common_user")
        self.assertIn("triage_priority", fusion["clinician_assist"])
        self.assertIn("what_to_do_now", fusion["patient_guidance"])
        self.assertIn("diagnosis", fusion["patient_guidance"]["not_a_diagnosis"].lower())


if __name__ == "__main__":
    unittest.main()