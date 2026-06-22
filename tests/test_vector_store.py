"""Tests for local vector retrieval."""

from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd

from src.retrieval.vector_store import build_feature_vector_index, load_vector_index, query_similar_windows


class TestVectorStore(unittest.TestCase):
    def test_build_load_and_query_feature_index(self) -> None:
        features = pd.DataFrame(
            [
                {
                    "window_id": 0,
                    "mean": 0.0,
                    "std": 1.0,
                    "spectral_entropy": 0.2,
                    "mdi_score": 0.1,
                    "stress_label": 0,
                    "quality_label": 1,
                    "signal_quality_score": 0.91,
                },
                {
                    "window_id": 1,
                    "mean": 1.0,
                    "std": 0.5,
                    "spectral_entropy": 0.8,
                    "mdi_score": 0.9,
                    "stress_label": 1,
                    "quality_label": 1,
                    "signal_quality_score": 0.87,
                },
            ]
        )

        index_path = Path("models/vector_store_test_index.joblib")
        try:
            build_feature_vector_index(
                features,
                ["mean", "std", "spectral_entropy", "mdi_score"],
                index_path,
                n_neighbors=2,
            )

            vector_index = load_vector_index(index_path)
            self.assertIsNotNone(vector_index)

            matches = query_similar_windows(features.iloc[[0]], vector_index, top_k=2)
            self.assertEqual(len(matches), 2)
            self.assertEqual(matches[0]["metadata"]["window_id"], 0)
            self.assertGreaterEqual(matches[0]["similarity"], matches[1]["similarity"])
        finally:
            try:
                index_path.unlink(missing_ok=True)
            except PermissionError:
                pass


if __name__ == "__main__":
    unittest.main()
