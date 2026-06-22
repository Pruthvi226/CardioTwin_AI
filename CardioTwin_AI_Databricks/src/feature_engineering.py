"""Feature extraction utilities for PPG windows."""

from __future__ import annotations

from typing import Iterable

import numpy as np
from scipy.signal import find_peaks


def _as_array(values: Iterable[float]) -> np.ndarray:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return np.zeros(1, dtype=float)
    return np.nan_to_num(arr, nan=float(np.nanmean(arr)) if np.isfinite(arr).any() else 0.0)


def count_peaks(values: Iterable[float], sampling_rate: int = 100) -> int:
    """Estimate the number of pulse peaks in a signal window."""

    arr = _as_array(values)
    distance = max(1, int(0.30 * sampling_rate))
    prominence = max(float(np.std(arr)) * 0.20, 1e-6)
    peaks, _ = find_peaks(arr, distance=distance, prominence=prominence)
    return int(len(peaks))


def heart_rate_approx(values: Iterable[float], sampling_rate: int = 100) -> float:
    """Approximate heart rate from peak count and window length."""

    arr = _as_array(values)
    duration_seconds = max(float(arr.size) / float(sampling_rate), 1e-6)
    return float(count_peaks(arr, sampling_rate) * 60.0 / duration_seconds)


def extract_ppg_features(values: Iterable[float], sampling_rate: int = 100) -> dict:
    """Create window-level features from one cleaned PPG signal."""

    arr = _as_array(values)
    peak_count = count_peaks(arr, sampling_rate)
    signal_min = float(np.min(arr))
    signal_max = float(np.max(arr))
    signal_range = signal_max - signal_min

    diff = np.diff(arr) if arr.size > 1 else np.array([0.0])
    systolic_proxy = float(np.percentile(arr, 95))
    diastolic_proxy = float(np.percentile(arr, 5))

    return {
        "mean_amplitude": float(np.mean(arr)),
        "std_amplitude": float(np.std(arr)),
        "min_amplitude": signal_min,
        "max_amplitude": signal_max,
        "amplitude_range": float(signal_range),
        "peak_count": int(peak_count),
        "heart_rate_approx": heart_rate_approx(arr, sampling_rate),
        "signal_energy": float(np.mean(np.square(arr))),
        "mean_abs_change": float(np.mean(np.abs(diff))),
        "systolic_proxy": systolic_proxy,
        "diastolic_proxy": diastolic_proxy,
        "pulse_pressure_proxy": float(systolic_proxy - diastolic_proxy),
    }
