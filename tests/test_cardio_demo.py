"""Smoke tests for the demo-ready CardioTwin path."""

from __future__ import annotations

import unittest

from scripts.generate_demo_data import generate_demo_frame
from src.features.mdi_features import build_feature_table
from src.preprocessing.segment_windows import window_dataframe


class CardioTwinSmokeTest(unittest.TestCase):
    def test_demo_data_preprocesses_into_features(self) -> None:
        frame = generate_demo_frame(samples=1800, subjects=4, seed=7)
        windowed = window_dataframe(frame, fs_target=64.0, window_seconds=8.0, overlap=0.5)
        self.assertGreater(len(windowed.windows), 0)
        self.assertEqual(len(windowed.windows), len(windowed.labels))

        features = build_feature_table(windowed.windows, windowed.labels, fs=64.0)
        self.assertIn("mdi_score", features.columns)
        self.assertIn("stress_label", features.columns)
        self.assertTrue(features["mdi_score"].between(0, 1).all())


if __name__ == "__main__":
    unittest.main()

