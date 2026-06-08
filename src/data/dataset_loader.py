"""Stable loaders for the CardioTwin demo data contract."""

from __future__ import annotations

from pathlib import Path
from io import StringIO

import numpy as np
import pandas as pd


def load_demo_csv(path: str | Path) -> pd.DataFrame:
    """Load the demo PPG CSV with predictable dtypes."""
    frame = pd.read_csv(path)
    numeric_columns = ["time", "ppg", "fs", "stress_label", "quality_label", "sbp", "dbp", "heart_rate", "activity"]
    for column in numeric_columns:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def save_processed_npz(path: str | Path, windows: np.ndarray, labels: pd.DataFrame) -> None:
    """Save processed windows and aligned labels as one portable artifact."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output, windows=windows.astype(np.float32), labels=labels.to_json(orient="records"))


def load_processed_npz(path: str | Path) -> tuple[np.ndarray, pd.DataFrame]:
    """Load processed windows and labels saved by ``save_processed_npz``."""
    artifact = np.load(path, allow_pickle=False)
    windows = artifact["windows"].astype(np.float32)
    labels_json = str(artifact["labels"])
    labels = pd.read_json(StringIO(labels_json), orient="records")
    return windows, labels
