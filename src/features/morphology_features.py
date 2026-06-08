"""Morphology and variability features for PPG windows."""

from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks
from scipy.stats import kurtosis, skew

from src.preprocessing.quality_index import signal_quality_score


def extract_morphology_features(window: np.ndarray, fs: float = 64.0) -> dict[str, float]:
    """Extract interpretable PPG morphology features from one window."""
    values = np.asarray(window, dtype=float)
    if values.size == 0:
        raise ValueError("window must not be empty")

    normalized = (values - values.mean()) / (values.std() + 1e-8)
    peaks, properties = find_peaks(normalized, distance=max(1, int(0.35 * fs)), prominence=0.15)
    troughs, _ = find_peaks(-normalized, distance=max(1, int(0.35 * fs)))

    peak_values = normalized[peaks] if len(peaks) else np.array([0.0])
    trough_values = normalized[troughs] if len(troughs) else np.array([0.0])
    ppi = np.diff(peaks) / fs if len(peaks) > 1 else np.array([])
    diff_values = np.diff(normalized)

    duration = values.size / fs
    heart_rate = 60.0 * len(peaks) / max(duration, 1e-8)
    rmssd = float(np.sqrt(np.mean(np.diff(ppi) ** 2))) if len(ppi) > 1 else 0.0
    amplitude = float(np.mean(peak_values) - np.mean(trough_values))

    return {
        "mean": float(np.mean(normalized)),
        "std": float(np.std(normalized)),
        "skewness": float(skew(normalized)),
        "kurtosis": float(kurtosis(normalized)),
        "n_peaks": float(len(peaks)),
        "heart_rate_proxy": float(heart_rate),
        "ppi_mean": float(np.mean(ppi)) if len(ppi) else 0.0,
        "ppi_std": float(np.std(ppi)) if len(ppi) else 0.0,
        "rmssd": rmssd,
        "pulse_amplitude": amplitude,
        "peak_prominence_mean": float(np.mean(properties.get("prominences", [0.0]))),
        "slope_mean": float(np.mean(np.abs(diff_values))) if len(diff_values) else 0.0,
        "slope_max": float(np.max(np.abs(diff_values))) if len(diff_values) else 0.0,
        "area_under_curve": float(np.trapezoid(np.maximum(normalized, 0.0)) / fs),
        "zero_crossings": float(np.sum(np.diff(np.signbit(normalized)))),
        "signal_quality_score": float(signal_quality_score(normalized, fs)),
    }
