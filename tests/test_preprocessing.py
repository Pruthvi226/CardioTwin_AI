import unittest

import numpy as np

from src.preprocessing.clean_signal import preprocess_ppg


class TestPreprocessing(unittest.TestCase):
    def test_preprocess_removes_nan_and_preserves_signal(self):
        signal = np.sin(np.linspace(0, 20, 640))
        signal[5] = np.nan
        cleaned = preprocess_ppg(signal, fs_original=64.0, fs_target=64.0)
        self.assertEqual(cleaned.shape[0], signal.shape[0])
        self.assertFalse(np.isnan(cleaned).any())


if __name__ == "__main__":
    unittest.main()

