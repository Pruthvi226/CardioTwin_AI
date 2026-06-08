"""Signal quality scoring for PPG windows."""

from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks
from scipy.stats import kurtosis, skew


def signal_quality_score(window: np.ndarray, fs: float = 64.0) -> float:
    """Return a heuristic quality score in [0, 1] for a PPG window."""
    values = np.asarray(window, dtype=float)
    if values.size == 0 or not np.isfinite(values).all():
        return 0.0
    if values.std() < 1e-6:
        return 0.0

    normalized = (values - values.mean()) / (values.std() + 1e-8)
    peaks, _ = find_peaks(normalized, distance=max(1, int(0.35 * fs)), prominence=0.15)
    expected_min = max(1, int((values.size / fs) * 0.7))
    expected_max = max(expected_min + 1, int((values.size / fs) * 3.0))
    peak_score = 1.0 if expected_min <= len(peaks) <= expected_max else 0.45

    skew_score = 1.0 - min(abs(float(skew(normalized))) / 3.0, 1.0)
    kurt_score = 1.0 - min(abs(float(kurtosis(normalized)) - 1.5) / 8.0, 1.0)
    saturation = float(np.mean(np.abs(normalized) > 4.0))
    saturation_score = 1.0 - min(saturation * 10.0, 1.0)
    noise_score = 1.0 - min(float(np.std(np.diff(normalized))) / 2.5, 1.0)

    score = 0.35 * peak_score + 0.2 * skew_score + 0.2 * kurt_score + 0.15 * saturation_score + 0.1 * noise_score
    return float(np.clip(score, 0.0, 1.0))


def quality_label(window: np.ndarray, fs: float = 64.0, threshold: float = 0.62) -> int:
    """Convert the quality score into a binary demo label."""
    return int(signal_quality_score(window, fs) >= threshold)

