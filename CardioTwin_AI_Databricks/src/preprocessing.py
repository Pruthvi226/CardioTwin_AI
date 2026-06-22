"""PPG preprocessing helpers for CardioTwin AI Databricks.

The functions are intentionally small and notebook-friendly. They can be used
inside Databricks UDFs or in local scripts for quick experiments.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence

import numpy as np


def parse_ppg_values(raw_values: str | Sequence[float] | None) -> List[float]:
    """Convert a semicolon-separated PPG string into a list of floats.

    Empty tokens are kept as NaN so the preprocessing step can measure missing
    signal percentage before imputation.
    """

    if raw_values is None:
        return []

    if isinstance(raw_values, (list, tuple, np.ndarray)):
        parsed = []
        for value in raw_values:
            try:
                parsed.append(float(value))
            except (TypeError, ValueError):
                parsed.append(float("nan"))
        return parsed

    parsed = []
    for token in str(raw_values).split(";"):
        cleaned = token.strip()
        if cleaned == "" or cleaned.lower() in {"nan", "none", "null"}:
            parsed.append(float("nan"))
        else:
            parsed.append(float(cleaned))
    return parsed


def missing_fraction(values: Iterable[float]) -> float:
    """Return the fraction of samples that are missing or not finite."""

    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return 1.0
    return float(np.mean(~np.isfinite(arr)))


def impute_missing(values: Iterable[float]) -> np.ndarray:
    """Fill missing samples using linear interpolation.

    If an entire window is missing, a zero signal is returned. This keeps the
    pipeline from crashing while allowing quality rules to reject that window.
    """

    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return arr

    valid_mask = np.isfinite(arr)
    if valid_mask.all():
        return arr
    if not valid_mask.any():
        return np.zeros_like(arr)

    x = np.arange(arr.size)
    arr[~valid_mask] = np.interp(x[~valid_mask], x[valid_mask], arr[valid_mask])
    return arr


def moving_average(values: Iterable[float], window_size: int = 5) -> np.ndarray:
    """Apply a light moving-average smoother to reduce high-frequency noise."""

    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0 or window_size <= 1:
        return arr

    window_size = min(int(window_size), arr.size)
    kernel = np.ones(window_size, dtype=float) / window_size
    pad_left = window_size // 2
    pad_right = window_size - 1 - pad_left
    padded = np.pad(arr, (pad_left, pad_right), mode="edge")
    return np.convolve(padded, kernel, mode="valid")


def zscore_normalize(values: Iterable[float], epsilon: float = 1e-8) -> np.ndarray:
    """Normalize a PPG window to zero mean and unit variance."""

    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return arr

    mean_value = float(np.mean(arr))
    std_value = float(np.std(arr))
    if std_value < epsilon:
        return np.zeros_like(arr)
    return (arr - mean_value) / std_value


def clean_ppg_window(
    raw_values: str | Sequence[float] | None,
    smoothing_window: int = 5,
    max_missing_fraction: float = 0.20,
    min_signal_std: float = 0.02,
) -> dict:
    """Parse, impute, smooth, normalize, and quality-filter one PPG window."""

    parsed = parse_ppg_values(raw_values)
    miss_frac = missing_fraction(parsed)
    imputed = impute_missing(parsed)
    smoothed = moving_average(imputed, window_size=smoothing_window)
    normalized = zscore_normalize(smoothed)
    signal_std = float(np.std(imputed)) if imputed.size else 0.0

    is_usable = miss_frac <= max_missing_fraction and signal_std >= min_signal_std
    if miss_frac > max_missing_fraction:
        reject_reason = "too_many_missing_samples"
    elif signal_std < min_signal_std:
        reject_reason = "low_variance_signal"
    else:
        reject_reason = "accepted"

    return {
        "clean_signal": [float(x) for x in smoothed],
        "normalized_signal": [float(x) for x in normalized],
        "missing_fraction": float(miss_frac),
        "signal_std": signal_std,
        "is_usable": bool(is_usable),
        "reject_reason": reject_reason,
    }
