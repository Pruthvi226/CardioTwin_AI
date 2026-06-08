"""Compact 1D CNN-LSTM classifier for raw PPG windows."""

from __future__ import annotations

import torch
from torch import nn


class CNNLSTMClassifier(nn.Module):
    """Small deep model suitable for fast demo training on CPU."""

    def __init__(self, n_classes: int = 2) -> None:
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(1, 24, kernel_size=9, padding=4),
            nn.BatchNorm1d(24),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(24, 48, kernel_size=7, padding=3),
            nn.BatchNorm1d(48),
            nn.ReLU(),
            nn.MaxPool1d(2),
        )
        self.lstm = nn.LSTM(input_size=48, hidden_size=48, num_layers=1, batch_first=True)
        self.head = nn.Sequential(nn.Dropout(0.15), nn.Linear(48, n_classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim == 2:
            x = x.unsqueeze(1)
        features = self.conv(x)
        sequence = features.transpose(1, 2)
        _, (hidden, _) = self.lstm(sequence)
        return self.head(hidden[-1])

