"""Computer-vision branch training on PPG spectrograms."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.models.resnet_spectrogram import SpectrogramCNN
from src.training.finetune_predictive import predict_torch_classifier


def train_spectrogram_cnn(
    x_train: np.ndarray,
    y_train: np.ndarray,
    output_dir: str | Path,
    epochs: int = 3,
    batch_size: int = 64,
    learning_rate: float = 1e-3,
    device: str = "cpu",
) -> SpectrogramCNN:
    """Train a lightweight CNN on spectrogram tensors."""
    torch_device = torch.device(device if device == "cuda" and torch.cuda.is_available() else "cpu")
    tensor_x = torch.tensor(x_train, dtype=torch.float32)
    tensor_y = torch.tensor(y_train, dtype=torch.long)
    loader = DataLoader(TensorDataset(tensor_x, tensor_y), batch_size=batch_size, shuffle=True)
    model = SpectrogramCNN(n_classes=max(2, int(np.max(y_train)) + 1)).to(torch_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()

    model.train()
    for _ in range(max(1, epochs)):
        for batch_x, batch_y in loader:
            batch_x = batch_x.to(torch_device)
            batch_y = batch_y.to(torch_device)
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    torch.save(model.cpu().state_dict(), output / "SpectrogramCNN_stress.pt")
    return model


__all__ = ["train_spectrogram_cnn", "predict_torch_classifier"]
