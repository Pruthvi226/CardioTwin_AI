"""Compare tracked experiment runs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def compare_runs(path: str | Path = "reports/metrics/experiment_runs.csv") -> pd.DataFrame:
    """Return runs sorted by weighted F1 when available."""
    csv_path = Path(path)
    if not csv_path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(csv_path)
    if "weighted_f1" in frame.columns:
        frame = frame.sort_values("weighted_f1", ascending=False)
    return frame

