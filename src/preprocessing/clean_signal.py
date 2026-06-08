"""PPG cleaning, filtering, resampling, and normalization."""

from __future__ import annotations

import numpy as np
from scipy import signal as scipy_signal
from scipy.interpolate import interp1d


def remove_nan_and_outliers(values: np.ndarray, z_limit: float = 5.0) -> np.ndarray:
    """Replace NaNs and extreme spikes with interpolated local values."""
    signal = np.asarray(values, dtype=float).copy()
    if signal.size == 0:
        return signal

    finite = np.isfinite(signal)
    if not finite.any():
        return np.zeros_like(signal, dtype=float)

    idx = np.arange(signal.size)
    signal[~finite] = np.interp(idx[~finite], idx[finite], signal[finite])

    median = np.median(signal)
    mad = np.median(np.abs(signal - median)) + 1e-8
    robust_z = 0.6745 * (signal - median) / mad
    outliers = np.abs(robust_z) > z_limit
    if outliers.any() and (~outliers).any():
        signal[outliers] = np.interp(idx[outliers], idx[~outliers], signal[~outliers])

    return signal


def bandpass_filter(
    values: np.ndarray,
    fs: float,
    low: float = 0.5,
    high: float = 8.0,
    order: int = 3,
) -> np.ndarray:
    """Apply a Butterworth bandpass filter in the PPG frequency range."""
    signal = np.asarray(values, dtype=float)
    if signal.size < max(order * 9, 32):
        return signal.copy()

    nyquist = 0.5 * fs
    low_norm = max(low / nyquist, 1e-5)
    high_norm = min(high / nyquist, 0.99)
    if low_norm >= high_norm:
        return signal.copy()

    b, a = scipy_signal.butter(order, [low_norm, high_norm], btype="bandpass")
    return scipy_signal.filtfilt(b, a, signal)


def resample_signal(values: np.ndarray, fs_original: float, fs_target: float) -> np.ndarray:
    """Resample a signal to the target frequency with linear interpolation."""
    signal = np.asarray(values, dtype=float)
    if signal.size == 0 or np.isclose(fs_original, fs_target):
        return signal.copy()

    duration = signal.size / float(fs_original)
    target_size = max(1, int(round(duration * fs_target)))
    t_original = np.linspace(0.0, duration, signal.size, endpoint=False)
    t_target = np.linspace(0.0, duration, target_size, endpoint=False)
    interpolator = interp1d(t_original, signal, kind="linear", fill_value="extrapolate")
    return interpolator(t_target)


def zscore_normalize(values: np.ndarray) -> np.ndarray:
    """Normalize a signal to zero mean and unit variance."""
    signal = np.asarray(values, dtype=float)
    return (signal - signal.mean()) / (signal.std() + 1e-8)


def preprocess_ppg(
    values: np.ndarray,
    fs_original: float,
    fs_target: float = 64.0,
    bandpass: tuple[float, float] = (0.5, 8.0),
) -> np.ndarray:
    """Clean, bandpass filter, resample, and normalize a raw PPG trace."""
    signal = remove_nan_and_outliers(values)
    signal = bandpass_filter(signal, fs_original, low=bandpass[0], high=bandpass[1])
    signal = resample_signal(signal, fs_original, fs_target)
    return zscore_normalize(signal)

