"""MDI-style feature table construction."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.morphology_features import extract_morphology_features


def _scaled(series: pd.Series) -> pd.Series:
    values = series.astype(float)
    spread = values.max() - values.min()
    if spread <= 1e-12:
        return pd.Series(np.zeros(len(values)), index=series.index)
    return (values - values.min()) / spread


def add_mdi_score(features: pd.DataFrame) -> pd.DataFrame:
    """Add a morphology-derived index score for ranking physiological stress."""
    result = features.copy()
    components = {
        "heart_rate_proxy": 0.30,
        "rmssd": -0.20,
        "pulse_amplitude": -0.15,
        "slope_mean": 0.20,
        "signal_quality_score": -0.15,
    }

    score = pd.Series(np.zeros(len(result)), index=result.index, dtype=float)
    for column, weight in components.items():
        if column in result.columns:
            scaled = _scaled(result[column])
            score += weight * (scaled if weight >= 0 else 1.0 - scaled)

    result["mdi_score"] = _scaled(score)
    return result


def build_feature_table(windows: np.ndarray, labels: pd.DataFrame, fs: float = 64.0) -> pd.DataFrame:
    """Build one feature row per PPG window and append aligned labels."""
    rows = []
    for idx, window in enumerate(windows):
        row = {"window_id": int(idx)}
        row.update(extract_morphology_features(window, fs=fs))
        rows.append(row)

    feature_frame = add_mdi_score(pd.DataFrame(rows))
    if labels.empty:
        return feature_frame

    label_frame = labels.reset_index(drop=True).copy()
    duplicate_columns = [column for column in label_frame.columns if column in feature_frame.columns]
    if duplicate_columns:
        label_frame = label_frame.drop(columns=duplicate_columns)
    return pd.concat([feature_frame.reset_index(drop=True), label_frame], axis=1)
