"""Synthetic dataset mode for pipeline validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.generate_demo_data import generate_demo_frame


def generate_synthetic_dataset(
    out_path: str | Path = "data/raw/demo_ppg.csv",
    samples: int = 12000,
    fs: float = 64.0,
    subjects: int = 8,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate and persist synthetic PPG data for demo-only validation."""
    frame = generate_demo_frame(samples=samples, fs=fs, subjects=subjects, seed=seed)
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    return frame

