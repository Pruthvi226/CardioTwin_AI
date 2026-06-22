"""Signal and file preprocessing helpers."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PREFERRED_SIGNAL_COLUMNS = ("ppg", "signal", "value", "amplitude", "waveform", "raw_ppg")
PREFERRED_TIME_COLUMNS = ("time", "timestamp", "seconds", "t")


def read_csv_bytes(raw: bytes) -> pd.DataFrame:
    if not raw:
        raise ValueError("No CSV data was provided.")
    try:
        dataframe = pd.read_csv(BytesIO(raw))
    except Exception as exc:  # pandas raises several parser-specific errors
        raise ValueError("Could not parse the uploaded CSV file.") from exc
    if dataframe.empty:
        raise ValueError("The uploaded CSV file is empty.")
    return dataframe


def read_csv_path(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def find_signal_column(dataframe: pd.DataFrame) -> str:
    lower_lookup = {column.lower().strip(): column for column in dataframe.columns}
    for candidate in PREFERRED_SIGNAL_COLUMNS:
        if candidate in lower_lookup:
            return lower_lookup[candidate]

    numeric_columns = dataframe.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_columns:
        raise ValueError("No numeric PPG/signal column was found in the CSV.")
    return numeric_columns[-1] if len(numeric_columns) > 1 else numeric_columns[0]


def find_time_column(dataframe: pd.DataFrame) -> str | None:
    lower_lookup = {column.lower().strip(): column for column in dataframe.columns}
    for candidate in PREFERRED_TIME_COLUMNS:
        if candidate in lower_lookup:
            return lower_lookup[candidate]
    return None


def infer_sampling_rate(times: np.ndarray | None, default_fs: float = 64.0) -> float:
    if times is None or len(times) < 3:
        return default_fs
    diffs = np.diff(times.astype(float))
    diffs = diffs[np.isfinite(diffs) & (diffs > 0)]
    if len(diffs) == 0:
        return default_fs
    median_step = float(np.median(diffs))
    if median_step <= 0:
        return default_fs
    return float(np.clip(1.0 / median_step, 1.0, 512.0))


def dataframe_to_signal(dataframe: pd.DataFrame) -> dict[str, Any]:
    signal_column = find_signal_column(dataframe)
    time_column = find_time_column(dataframe)

    signal = pd.to_numeric(dataframe[signal_column], errors="coerce").to_numpy(dtype=float)
    valid = np.isfinite(signal)
    if valid.sum() < 5:
        raise ValueError("The signal column has too few numeric samples.")

    times = None
    if time_column is not None:
        times = pd.to_numeric(dataframe[time_column], errors="coerce").to_numpy(dtype=float)
        if len(times) == len(signal):
            valid = valid & np.isfinite(times)
        else:
            times = None

    signal = signal[valid]
    if times is not None:
        times = times[valid]

    fs = infer_sampling_rate(times)
    if times is None:
        times = np.arange(len(signal), dtype=float) / fs

    return {
        "signal": signal,
        "timestamps": times,
        "sampling_rate": fs,
        "signal_column": signal_column,
        "time_column": time_column,
        "columns": dataframe.columns.tolist(),
    }


def clean_ppg_signal(signal: np.ndarray, window: int = 7) -> np.ndarray:
    values = np.asarray(signal, dtype=float)
    if values.size == 0:
        return values

    finite_mask = np.isfinite(values)
    if not finite_mask.all():
        indexes = np.arange(values.size)
        values = np.interp(indexes, indexes[finite_mask], values[finite_mask])

    centered = values - np.median(values)
    scale = np.percentile(np.abs(centered), 95)
    if scale <= 1e-8:
        scale = np.std(centered) or 1.0
    normalized = centered / scale

    window = max(3, int(window) | 1)
    if normalized.size < window:
        return normalized
    kernel = np.ones(window, dtype=float) / window
    smoothed = np.convolve(normalized, kernel, mode="same")
    return smoothed


def demo_ppg_signal(duration_seconds: float = 18.0, fs: float = 64.0) -> dict[str, Any]:
    times = np.arange(0, duration_seconds, 1.0 / fs)
    base = 0.58 + 0.28 * np.sin(2 * np.pi * 1.18 * times)
    dicrotic = 0.06 * np.sin(2 * np.pi * 2.36 * times + 0.6)
    drift = 0.03 * np.sin(2 * np.pi * 0.08 * times)
    motion = np.where((times > 7.5) & (times < 8.6), 0.12 * np.sin(2 * np.pi * 9 * times), 0.0)
    signal = base + dicrotic + drift + motion
    return {"signal": signal, "timestamps": times, "sampling_rate": fs}


def chart_points(raw: np.ndarray, cleaned: np.ndarray, timestamps: np.ndarray, limit: int = 500) -> list[dict[str, float]]:
    if len(raw) == 0:
        return []
    stride = max(1, len(raw) // limit)
    points = []
    for index in range(0, len(raw), stride):
        points.append(
            {
                "time": round(float(timestamps[index]), 3),
                "raw": round(float(raw[index]), 4),
                "cleaned": round(float(cleaned[index]), 4),
            }
        )
    return points

