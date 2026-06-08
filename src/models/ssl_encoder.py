"""Self-supervised encoder with masked reconstruction pretraining."""

from __future__ import annotations

import torch
from torch import nn


class PPGEncoder(nn.Module):
    """Compact convolutional encoder that returns a fixed embedding."""

    def __init__(self, embedding_dim: int = 64) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(1, 24, kernel_size=9, padding=4),
            nn.BatchNorm1d(24),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(24, 48, kernel_size=7, padding=3),
            nn.BatchNorm1d(48),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(48, embedding_dim, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim == 2:
            x = x.unsqueeze(1)
        return self.net(x).squeeze(-1)


class PPGMaskedAutoencoder(nn.Module):
    """Masked-signal reconstruction model plus reusable encoder."""

    def __init__(self, window_length: int, embedding_dim: int = 64) -> None:
        super().__init__()
        self.encoder = PPGEncoder(embedding_dim=embedding_dim)
        self.reconstruction_head = nn.Sequential(
            nn.Linear(embedding_dim, 128),
            nn.ReLU(),
            nn.Linear(128, window_length),
        )
        self.projection_head = nn.Sequential(
            nn.Linear(embedding_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        embedding = self.encoder(x)
        reconstruction = self.reconstruction_head(embedding)
        projection = self.projection_head(embedding)
        return reconstruction, projection


class SSLFineTuneClassifier(nn.Module):
    """Classifier head used after SSL pretraining."""

    def __init__(self, encoder: PPGEncoder, n_classes: int = 2) -> None:
        super().__init__()
        self.encoder = encoder
        self.head = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, n_classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.encoder(x))

