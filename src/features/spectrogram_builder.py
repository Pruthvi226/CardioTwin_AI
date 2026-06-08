"""Convert PPG windows into spectrogram image tensors and previews."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import spectrogram


def window_to_spectrogram(window: np.ndarray, fs: float = 64.0, image_size: int = 64) -> np.ndarray:
    """Return a normalized square spectrogram image for one PPG window."""
    frequencies, times, power = spectrogram(
        np.asarray(window, dtype=float),
        fs=fs,
        nperseg=min(128, len(window)),
        noverlap=min(96, max(0, len(window) // 4)),
        scaling="spectrum",
    )
    del frequencies, times
    image = np.log1p(power)
    image = image - image.min()
    image = image / (image.max() + 1e-8)

    row_idx = np.linspace(0, image.shape[0] - 1, image_size).astype(int)
    col_idx = np.linspace(0, image.shape[1] - 1, image_size).astype(int)
    return image[np.ix_(row_idx, col_idx)].astype(np.float32)


def build_spectrogram_tensor(windows: np.ndarray, fs: float = 64.0, image_size: int = 64) -> np.ndarray:
    """Convert all windows to ``(n, 1, image_size, image_size)`` tensors."""
    images = [window_to_spectrogram(window, fs=fs, image_size=image_size) for window in windows]
    return np.expand_dims(np.stack(images).astype(np.float32), axis=1)


def save_spectrogram_preview(window: np.ndarray, out_path: str | Path, fs: float = 64.0) -> None:
    """Save a recruiter-friendly spectrogram preview image."""
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image = window_to_spectrogram(window, fs=fs, image_size=128)
    plt.figure(figsize=(6, 4))
    plt.imshow(image, aspect="auto", origin="lower", cmap="magma")
    plt.title("PPG Spectrogram View")
    plt.xlabel("Time bins")
    plt.ylabel("Frequency bins")
    plt.colorbar(label="Log power")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()

