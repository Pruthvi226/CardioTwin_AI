"""Self-supervised pretraining utilities."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.models.ssl_encoder import PPGMaskedAutoencoder


def _mask_batch(batch: torch.Tensor, mask_fraction: float = 0.18) -> torch.Tensor:
    masked = batch.clone()
    width = masked.shape[-1]
    mask_width = max(8, int(width * mask_fraction))
    for item in masked:
        start = torch.randint(0, max(1, width - mask_width), (1,)).item()
        item[..., start : start + mask_width] = 0.0
    return masked


def train_ssl_autoencoder(
    windows: np.ndarray,
    output_dir: str | Path,
    epochs: int = 2,
    batch_size: int = 64,
    learning_rate: float = 1e-3,
    device: str = "cpu",
) -> tuple[PPGMaskedAutoencoder, list[float]]:
    """Train a masked reconstruction model and save it to disk."""
    torch_device = torch.device(device if device == "cuda" and torch.cuda.is_available() else "cpu")
    tensor = torch.tensor(windows, dtype=torch.float32).unsqueeze(1)
    loader = DataLoader(TensorDataset(tensor), batch_size=batch_size, shuffle=True)
    model = PPGMaskedAutoencoder(window_length=windows.shape[1]).to(torch_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
    losses: list[float] = []

    model.train()
    for _ in range(max(1, epochs)):
        epoch_loss = 0.0
        for (batch,) in loader:
            batch = batch.to(torch_device)
            masked = _mask_batch(batch)
            reconstruction, _ = model(masked)
            loss = criterion(reconstruction, batch.squeeze(1))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.item()) * len(batch)
        losses.append(epoch_loss / max(1, len(tensor)))

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output / "ssl_masked_autoencoder.pt")
    return model.cpu(), losses

