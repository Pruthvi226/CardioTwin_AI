"""Spectrogram generation for the Computer Vision branch."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.features.spectrogram_builder import build_spectrogram_tensor, window_to_spectrogram


def create_spectrogram(window: np.ndarray, fs: float = 64.0, image_size: int = 64) -> np.ndarray:
    """Convert one 1D window into a spectrogram array."""
    return window_to_spectrogram(window, fs=fs, image_size=image_size)


def save_spectrogram_arrays(windows: np.ndarray, out_dir: str | Path = "data/processed/spectrograms", fs: float = 64.0) -> np.ndarray:
    """Save spectrogram arrays and PNG previews under data/processed/spectrograms."""
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    tensor = build_spectrogram_tensor(windows, fs=fs)
    np.save(output / "spectrogram_tensor.npy", tensor)
    for idx, image in enumerate(tensor[:12, 0]):
        plt.imsave(output / f"spectrogram_{idx:03d}.png", image, cmap="magma")
    return tensor

