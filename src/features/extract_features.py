"""Unified feature extraction entry point."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.frequency_features import extract_frequency_features
from src.features.mdi_features import add_mdi_score
from src.features.morphology_features import extract_morphology_features


def extract_features(windows: np.ndarray, labels: pd.DataFrame | None = None, fs: float = 64.0) -> pd.DataFrame:
    """Return a clean feature dataframe for PPG windows."""
    rows: list[dict[str, float | int]] = []
    for idx, window in enumerate(windows):
        row: dict[str, float | int] = {"window_id": int(idx)}
        row.update(extract_morphology_features(window, fs=fs))
        row.update(extract_frequency_features(window, fs=fs))
        row["signal_energy"] = float(np.sum(np.square(window)))
        row["min"] = float(np.min(window))
        row["max"] = float(np.max(window))
        rows.append(row)

    features = add_mdi_score(pd.DataFrame(rows))
    if labels is not None and not labels.empty:
        label_frame = labels.reset_index(drop=True).drop(columns=[c for c in labels.columns if c in features.columns], errors="ignore")
        features = pd.concat([features.reset_index(drop=True), label_frame], axis=1)
    return features

