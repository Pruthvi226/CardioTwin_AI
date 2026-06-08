"""Windowing helpers for PPG arrays and demo CSV files."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class WindowedDataset:
    windows: np.ndarray
    labels: pd.DataFrame


def create_windows(values: np.ndarray, window_size: int, overlap: float) -> np.ndarray:
    """Create overlapping windows from a 1D signal."""
    signal = np.asarray(values, dtype=float)
    if not 0 <= overlap < 1:
        raise ValueError("overlap must be in the range [0, 1)")
    if window_size <= 0:
        raise ValueError("window_size must be positive")
    if signal.size < window_size:
        return np.empty((0, window_size), dtype=float)

    step = max(1, int(round(window_size * (1.0 - overlap))))
    starts = range(0, signal.size - window_size + 1, step)
    return np.stack([signal[start : start + window_size] for start in starts]).astype(np.float32)


def _majority(values: pd.Series) -> int:
    mode = values.mode(dropna=True)
    if mode.empty:
        return 0
    return int(mode.iloc[0])


def window_dataframe(
    frame: pd.DataFrame,
    fs_target: float,
    window_seconds: float,
    overlap: float,
) -> WindowedDataset:
    """Segment a demo-data dataframe into windows with aligned labels."""
    from src.preprocessing.clean_signal import preprocess_ppg
    from src.preprocessing.quality_index import signal_quality_score

    required = {"subject_id", "ppg", "fs", "stress_label", "quality_label", "sbp", "dbp"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    window_size = int(round(fs_target * window_seconds))
    all_windows: list[np.ndarray] = []
    label_rows: list[dict[str, float | int | str]] = []

    for subject_id, group in frame.groupby("subject_id", sort=True):
        source_fs = float(group["fs"].iloc[0])
        clean = preprocess_ppg(group["ppg"].to_numpy(), source_fs, fs_target)
        windows = create_windows(clean, window_size=window_size, overlap=overlap)
        if windows.size == 0:
            continue

        step = max(1, int(round(window_size * (1.0 - overlap))))
        labels = group.reset_index(drop=True)
        ratio = source_fs / fs_target

        for idx, window in enumerate(windows):
            start_target = idx * step
            end_target = start_target + window_size
            start_source = int(round(start_target * ratio))
            end_source = min(len(labels), int(round(end_target * ratio)))
            label_slice = labels.iloc[start_source:end_source]
            if label_slice.empty:
                label_slice = labels.iloc[[-1]]

            all_windows.append(window)
            label_rows.append(
                {
                    "window_id": len(label_rows),
                    "subject_id": str(subject_id),
                    "stress_label": _majority(label_slice["stress_label"]),
                    "quality_label": _majority(label_slice["quality_label"]),
                    "sbp": float(label_slice["sbp"].mean()),
                    "dbp": float(label_slice["dbp"].mean()),
                    "heart_rate": float(label_slice.get("heart_rate", pd.Series([0])).mean()),
                    "activity": _majority(label_slice.get("activity", pd.Series([0]))),
                    "signal_quality_score": float(signal_quality_score(window, fs_target)),
                }
            )

    if not all_windows:
        return WindowedDataset(
            windows=np.empty((0, window_size), dtype=np.float32),
            labels=pd.DataFrame(label_rows),
        )

    return WindowedDataset(windows=np.stack(all_windows).astype(np.float32), labels=pd.DataFrame(label_rows))

