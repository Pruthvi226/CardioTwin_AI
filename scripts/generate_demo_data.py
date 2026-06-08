"""Generate reproducible synthetic PPG data for CardioTwin AI."""

from __future__ import annotations

import argparse
from pathlib import Path
from math import ceil

import numpy as np
import pandas as pd


def _ppg_wave(t: np.ndarray, heart_rate: float, noise: float, rng: np.random.Generator) -> np.ndarray:
    period = 60.0 / heart_rate
    phase = np.mod(t, period)
    systolic = np.exp(-0.5 * ((phase - 0.12) / 0.045) ** 2)
    notch = -0.22 * np.exp(-0.5 * ((phase - 0.28) / 0.025) ** 2)
    diastolic = 0.36 * np.exp(-0.5 * ((phase - 0.38) / 0.07) ** 2)
    baseline = 0.08 * np.sin(2 * np.pi * 0.18 * t)
    return systolic + notch + diastolic + baseline + rng.normal(0, noise, size=t.shape)


def generate_demo_frame(samples: int = 3000, fs: float = 64.0, subjects: int = 8, seed: int = 42) -> pd.DataFrame:
    """Create a synthetic PPG CSV-style dataframe."""
    rng = np.random.default_rng(seed)
    rows: list[pd.DataFrame] = []
    per_subject = max(int(ceil(samples / max(subjects, 1))), int(fs * 12))

    for subject_idx in range(subjects):
        stress = subject_idx % 2
        activity = int(rng.integers(0, 4))
        quality = 0 if subject_idx % 4 == 0 else 1
        heart_rate = 64 + stress * 22 + activity * 7 + rng.normal(0, 3)
        noise = 0.05 if quality else 0.22
        sbp = 112 + stress * 17 + activity * 4 + rng.normal(0, 5)
        dbp = 72 + stress * 9 + activity * 2 + rng.normal(0, 3)
        t = np.arange(per_subject) / fs
        ppg = _ppg_wave(t, heart_rate=heart_rate, noise=noise, rng=rng)

        if quality == 0:
            spike_count = max(1, per_subject // 160)
            spike_idx = rng.choice(per_subject, size=spike_count, replace=False)
            ppg[spike_idx] += rng.normal(2.5, 0.6, size=spike_count)

        frame = pd.DataFrame(
            {
                "subject_id": f"S{subject_idx + 1:02d}",
                "time": t,
                "ppg": ppg,
                "fs": fs,
                "stress_label": stress,
                "quality_label": quality,
                "sbp": sbp,
                "dbp": dbp,
                "heart_rate": heart_rate,
                "activity": activity,
            }
        )
        rows.append(frame)

    data = pd.concat(rows, ignore_index=True)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic PPG demo data.")
    parser.add_argument("--samples", type=int, default=3000)
    parser.add_argument("--out", default="data/raw/demo_ppg.csv")
    parser.add_argument("--fs", type=float, default=64.0)
    parser.add_argument("--subjects", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    frame = generate_demo_frame(samples=args.samples, fs=args.fs, subjects=args.subjects, seed=args.seed)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    print(f"Wrote {len(frame)} samples to {output}")


if __name__ == "__main__":
    main()
