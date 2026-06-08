"""Validation checks for demo PPG datasets and processed windows."""

from __future__ import annotations

import numpy as np
import pandas as pd


def validate_raw_demo_frame(frame: pd.DataFrame) -> list[str]:
    """Return human-readable validation issues for a raw demo CSV."""
    issues: list[str] = []
    required = ["subject_id", "time", "ppg", "fs", "stress_label", "quality_label", "sbp", "dbp"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        issues.append(f"Missing columns: {', '.join(missing)}")
        return issues

    if frame.empty:
        issues.append("Dataset is empty.")
    if frame["ppg"].isna().mean() > 0.05:
        issues.append("More than 5% of PPG values are NaN.")
    if not np.isfinite(frame["fs"]).all() or (frame["fs"] <= 0).any():
        issues.append("Sampling frequency must be positive for every row.")
    if frame["stress_label"].nunique() < 2:
        issues.append("Stress labels contain fewer than two classes.")
    if frame["quality_label"].nunique() < 2:
        issues.append("Quality labels contain fewer than two classes.")

    return issues


def validate_processed_windows(windows: np.ndarray, labels: pd.DataFrame) -> list[str]:
    """Return issues found in processed arrays and aligned labels."""
    issues: list[str] = []
    if windows.ndim != 2:
        issues.append("Processed windows must have shape (n_windows, window_length).")
    if len(windows) == 0:
        issues.append("No processed windows were generated.")
    if len(windows) != len(labels):
        issues.append("Window count does not match label count.")
    if not np.isfinite(windows).all():
        issues.append("Processed windows contain NaN or infinite values.")
    if len(labels) and labels["stress_label"].nunique() < 2:
        issues.append("Processed stress labels contain fewer than two classes.")
    return issues

