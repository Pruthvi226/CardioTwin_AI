"""Signal-processing facade for PPG workflow reuse."""

from __future__ import annotations

import numpy as np

from .preprocessing import clean_ppg_signal


def normalize_signal(signal: np.ndarray) -> np.ndarray:
    values = np.asarray(signal, dtype=float)
    if values.size == 0:
        return values
    spread = np.std(values) or 1.0
    return (values - np.mean(values)) / spread


def noisy_segment_ratio(signal: np.ndarray) -> float:
    values = np.asarray(signal, dtype=float)
    if values.size < 4:
        return 1.0
    derivative = np.diff(values)
    threshold = max(np.std(derivative) * 2.8, 1e-6)
    return float(np.mean(np.abs(derivative) > threshold))


def prepare_ppg(signal: np.ndarray) -> dict:
    cleaned = clean_ppg_signal(signal)
    return {
        "cleaned": cleaned,
        "normalized": normalize_signal(cleaned),
        "noisy_segment_ratio": noisy_segment_ratio(signal),
    }

