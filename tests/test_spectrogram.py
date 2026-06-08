import unittest

import numpy as np

from src.features.spectrogram import create_spectrogram


class TestSpectrogram(unittest.TestCase):
    def test_spectrogram_shape(self):
        image = create_spectrogram(np.sin(np.linspace(0, 12, 512)), image_size=64)
        self.assertEqual(image.shape, (64, 64))
        self.assertFalse(np.isnan(image).any())


if __name__ == "__main__":
    unittest.main()

