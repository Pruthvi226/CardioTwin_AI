"""Rule-based signal quality scoring for PPG windows."""

from __future__ import annotations

from typing import Iterable

import numpy as np
from scipy.signal import find_peaks


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return float(max(lower, min(upper, value)))


def _as_array(values: Iterable[float]) -> np.ndarray:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return np.zeros(1, dtype=float)
    if not np.isfinite(arr).all():
        finite_mean = float(np.nanmean(arr)) if np.isfinite(arr).any() else 0.0
        arr = np.nan_to_num(arr, nan=finite_mean)
    return arr


def peak_consistency_score(values: Iterable[float], sampling_rate: int = 100) -> float:
    """Score how regularly peaks appear across the signal window."""

    arr = _as_array(values)
    prominence = max(float(np.std(arr)) * 0.20, 1e-6)
    distance = max(1, int(0.30 * sampling_rate))
    peaks, _ = find_peaks(arr, distance=distance, prominence=prominence)
    if len(peaks) < 2:
        return 0.35

    intervals = np.diff(peaks)
    interval_cv = float(np.std(intervals) / (np.mean(intervals) + 1e-8))
    return clamp(1.0 - interval_cv / 0.60)


def noise_score(values: Iterable[float]) -> float:
    """Estimate noise from excessive sample-to-sample movement."""

    arr = _as_array(values)
    if arr.size < 3:
        return 0.50

    roughness = float(np.mean(np.abs(np.diff(arr))) / (np.std(arr) + 1e-8))
    return clamp(1.0 - (roughness - 0.15) / 1.25)


def amplitude_stability_score(values: Iterable[float]) -> float:
    """Score whether amplitude range is present but not erratic."""

    arr = _as_array(values)
    signal_range = float(np.max(arr) - np.min(arr))
    if signal_range <= 1e-8:
        return 0.0

    iqr = float(np.percentile(arr, 75) - np.percentile(arr, 25))
    ratio = iqr / signal_range
    return clamp(1.0 - abs(ratio - 0.45) / 0.45)


def variance_score(values: Iterable[float]) -> float:
    """Reward windows with enough variance to show a pulse waveform."""

    arr = _as_array(values)
    std_value = float(np.std(arr))
    if std_value < 0.02:
        return 0.0
    if std_value > 0.80:
        return 0.75
    return clamp(std_value / 0.25)


def quality_score(
    clean_values: Iterable[float],
    missing_fraction: float = 0.0,
    sampling_rate: int = 100,
) -> dict:
    """Return a 0-1 quality score and component scores."""

    missing_component = clamp(1.0 - float(missing_fraction))
    variance_component = variance_score(clean_values)
    peak_component = peak_consistency_score(clean_values, sampling_rate)
    noise_component = noise_score(clean_values)
    amplitude_component = amplitude_stability_score(clean_values)

    total = (
        0.25 * missing_component
        + 0.20 * variance_component
        + 0.25 * peak_component
        + 0.15 * noise_component
        + 0.15 * amplitude_component
    )

    return {
        "missing_score": missing_component,
        "variance_score": variance_component,
        "peak_consistency_score": peak_component,
        "noise_score": noise_component,
        "amplitude_stability_score": amplitude_component,
        "signal_quality_score": clamp(total),
    }
