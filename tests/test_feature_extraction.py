import unittest

import numpy as np
import pandas as pd

from src.features.extract_features import extract_features


class TestFeatureExtraction(unittest.TestCase):
    def test_expected_columns_exist(self):
        windows = np.random.default_rng(1).normal(size=(3, 512)).astype("float32")
        labels = pd.DataFrame({"stress_label": [0, 1, 0], "quality_label": [1, 1, 0]})
        features = extract_features(windows, labels)
        for column in ["mean", "std", "signal_energy", "dominant_frequency", "spectral_entropy", "mdi_score"]:
            self.assertIn(column, features.columns)


if __name__ == "__main__":
    unittest.main()

