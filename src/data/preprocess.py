"""High-level preprocessing functions for CardioTwin AI."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.preprocessing.clean_signal import preprocess_ppg
from src.preprocessing.segment_windows import WindowedDataset, window_dataframe


def preprocess_signal(values: np.ndarray, fs_original: float, fs_target: float = 64.0) -> np.ndarray:
    """Clean one raw PPG trace."""
    return preprocess_ppg(values, fs_original=fs_original, fs_target=fs_target)


def preprocess_frame(
    frame: pd.DataFrame,
    fs_target: float = 64.0,
    window_seconds: float = 8.0,
    overlap: float = 0.5,
) -> WindowedDataset:
    """Clean and window a dataframe using the shared demo schema."""
    return window_dataframe(frame, fs_target=fs_target, window_seconds=window_seconds, overlap=overlap)

