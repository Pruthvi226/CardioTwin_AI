import unittest

import torch

from src.models.cnn_lstm import CNNLSTMClassifier
from src.models.transformer_encoder import TransformerPPGClassifier


class TestModelOutputShape(unittest.TestCase):
    def test_cnn_lstm_output_shape(self):
        model = CNNLSTMClassifier(n_classes=2)
        output = model(torch.randn(4, 1, 512))
        self.assertEqual(tuple(output.shape), (4, 2))

    def test_transformer_output_shape(self):
        model = TransformerPPGClassifier(window_length=512, n_classes=2)
        output = model(torch.randn(4, 1, 512))
        self.assertEqual(tuple(output.shape), (4, 2))


if __name__ == "__main__":
    unittest.main()

