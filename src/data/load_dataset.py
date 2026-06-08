"""Dataset-mode loading helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.dataset_loader import load_demo_csv


REAL_DATASET_NOTE = (
    "Real dataset mode expects a CSV at data/raw/real_ppg.csv with columns: "
    "subject_id,time,ppg,fs,stress_label,quality_label,sbp,dbp,heart_rate,activity. "
    "Download WESAD or another governed wearable PPG dataset manually and convert it to this schema."
)


def dataset_path_for_mode(dataset: str) -> Path:
    if dataset == "synthetic":
        return Path("data/raw/demo_ppg.csv")
    if dataset == "real":
        return Path("data/raw/real_ppg.csv")
    raise ValueError("dataset must be 'synthetic' or 'real'")


def load_dataset(dataset: str = "synthetic") -> pd.DataFrame:
    """Load synthetic or real-mode data using the shared CSV schema."""
    path = dataset_path_for_mode(dataset)
    if not path.exists():
        if dataset == "real":
            raise FileNotFoundError(REAL_DATASET_NOTE)
        raise FileNotFoundError(f"Synthetic data not found at {path}. Run scripts/run_full_pipeline.py --dataset synthetic.")
    return load_demo_csv(path)

