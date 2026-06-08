"""Signal quality assessment for PPG windows."""

from __future__ import annotations

import numpy as np

from src.preprocessing.quality_index import signal_quality_score


def assess_signal_quality(window: np.ndarray, fs: float = 64.0) -> dict[str, float | bool | str]:
    """Return signal quality score, noise/artifact flags, and stability diagnostics."""
    values = np.asarray(window, dtype=float)
    if values.size == 0:
        return {
            "signal_quality_score": 0.0,
            "noise_flag": True,
            "amplitude_stability": 0.0,
            "missing_ratio": 1.0,
            "artifact_warning": "empty signal window",
        }

    missing_ratio = float(np.mean(~np.isfinite(values)))
    clean = np.nan_to_num(values, nan=np.nanmedian(values[np.isfinite(values)]) if np.isfinite(values).any() else 0.0)
    rolling_std = np.std(np.array_split(clean, max(1, min(8, len(clean) // max(1, int(fs))))), axis=1)
    amplitude_stability = float(1.0 / (1.0 + np.std(rolling_std)))
    score = float(signal_quality_score(clean, fs=fs))
    noise_flag = bool(score < 0.50 or missing_ratio > 0.05)

    if missing_ratio > 0.05:
        warning = "missing values detected"
    elif score < 0.50:
        warning = "noisy or artifact-prone window"
    elif amplitude_stability < 0.50:
        warning = "unstable amplitude"
    else:
        warning = "no major artifact warning"

    return {
        "signal_quality_score": round(score, 4),
        "noise_flag": noise_flag,
        "amplitude_stability": round(amplitude_stability, 4),
        "missing_ratio": round(missing_ratio, 4),
        "artifact_warning": warning,
    }

