"""Model-card generation for demo submissions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


from src.utils.common import DISCLAIMER


def generate_model_card(metrics: pd.DataFrame, out_path: str | Path) -> None:
    """Write a concise model card markdown file."""
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    best = metrics.dropna(subset=["f1_score"]).sort_values("f1_score", ascending=False).head(1)
    best_text = "No classification metrics were generated."
    if not best.empty:
        row = best.iloc[0]
        best_text = f"Best classifier: {row['model']} with weighted F1={row['f1_score']:.3f}."

    content = f"""# CardioTwin AI Model Card

## Intended Use
Demo-ready PPG signal analytics for representation learning, signal quality review, and predictive modeling experiments.

## Performance Snapshot
{best_text}

## Data
The default workflow uses synthetic PPG-like signals for reproducible pipeline validation. Real clinical or wearable datasets require separate validation and governance.

## Limitations
- Synthetic data is not a substitute for clinical validation.
- Predictions may be sensitive to subject variability, sensor placement, motion artifacts, and dataset shift.
- Outputs should be interpreted as research signals, not clinical advice.

## Safety Disclaimer
{DISCLAIMER}
"""
    output.write_text(content, encoding="utf-8")

