"""Frequency-domain features for PPG windows."""

from __future__ import annotations

import numpy as np
from scipy.signal import welch


def extract_frequency_features(window: np.ndarray, fs: float = 64.0) -> dict[str, float]:
    """Compute compact frequency-domain features."""
    values = np.asarray(window, dtype=float)
    freqs, power = welch(values, fs=fs, nperseg=min(256, len(values)))
    total_power = float(np.sum(power) + 1e-12)
    probs = power / total_power
    spectral_entropy = float(-np.sum(probs * np.log2(probs + 1e-12)) / np.log2(len(probs) + 1e-12))
    dominant_frequency = float(freqs[int(np.argmax(power))]) if len(freqs) else 0.0
    band = (freqs >= 0.5) & (freqs <= 8.0)
    ppg_band_power = float(np.sum(power[band]))
    return {
        "frequency_power": total_power,
        "dominant_frequency": dominant_frequency,
        "spectral_entropy": spectral_entropy,
        "ppg_band_power": ppg_band_power,
    }

