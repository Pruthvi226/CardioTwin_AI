"""Tiny Transformer baseline for future fine-tuning experiments."""

from __future__ import annotations

import torch
from torch import nn


class TransformerPPGClassifier(nn.Module):
    """A compact Transformer classifier for 1D PPG windows."""

    def __init__(self, window_length: int = 512, d_model: int = 64, n_classes: int = 2) -> None:
        super().__init__()
        self.patch = nn.Conv1d(1, d_model, kernel_size=16, stride=8, padding=4)
        tokens = max(1, window_length // 8)
        self.position = nn.Parameter(torch.zeros(1, tokens, d_model))
        layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=4, batch_first=True, dropout=0.1)
        self.encoder = nn.TransformerEncoder(layer, num_layers=2)
        self.head = nn.Linear(d_model, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim == 2:
            x = x.unsqueeze(1)
        tokens = self.patch(x).transpose(1, 2)
        tokens = tokens + self.position[:, : tokens.shape[1], :]
        encoded = self.encoder(tokens)
        return self.head(encoded.mean(dim=1))

