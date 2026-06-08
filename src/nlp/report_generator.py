"""Template-based experiment report generation."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def generate_experiment_summary(metrics_df: pd.DataFrame) -> str:
    """Generate a structured summary from metrics rows."""
    classification = metrics_df.dropna(subset=["f1_score"]).copy()
    regression = metrics_df.dropna(subset=["mae"]).copy()

    if classification.empty:
        best_text = "No classification model was evaluated."
        insight = "Run the training stage to compare stress and signal-quality classifiers."
    else:
        best = classification.sort_values("f1_score", ascending=False).iloc[0]
        best_text = (
            f"Best model: {best['model']}\n"
            f"Weighted F1-score: {best['f1_score']:.3f}\n"
            f"Accuracy: {best['accuracy']:.3f}"
        )
        insight = (
            "Deep raw-window and spectrogram models test whether learned waveform or image representations "
            "beat interpretable morphology features. Classical models remain useful for feature-level explanations."
        )

    bp_text = "BP regression was not evaluated."
    if not regression.empty:
        best_bp = regression.sort_values("mae", ascending=True).iloc[0]
        bp_text = f"Best BP regressor: {best_bp['model']} with MAE={best_bp['mae']:.2f} and RMSE={best_bp['rmse']:.2f}."

    return f"""# CardioTwin AI Experiment Report

## Executive Summary
CardioTwin AI converts PPG windows into cleaned signals, morphology/MDI features, spectrogram images, predictive models, and an automated experiment narrative.

## Best Classification Result
{best_text}

## Regression Snapshot
{bp_text}

## Key Insight
{insight}

## Failure Cases To Inspect
- Low signal-quality windows with motion-like noise.
- Subject-level shifts in heart-rate proxy and pulse amplitude.
- Synthetic-to-real dataset gap when moving beyond the demo dataset.

## Recommended Next Experiments
- Tune window length, augmentation strength, and learning rate.
- Add subject-wise splits for stronger leakage control.
- Validate on WESAD/BIDMC/VitalDB or another governed dataset before making clinical claims.

## Safety Note
This is a research/demo AI analytics tool, not a medical diagnosis system.
"""


def generate_report(metrics_path: str | Path, out_path: str | Path) -> str:
    """Read metrics CSV and write a markdown report."""
    metrics = pd.read_csv(metrics_path)
    report = generate_experiment_summary(metrics)
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a CardioTwin AI experiment report.")
    parser.add_argument("--metrics", default="results/metrics.csv")
    parser.add_argument("--out", default="reports/experiment_report.md")
    args = parser.parse_args()
    generate_report(args.metrics, args.out)


if __name__ == "__main__":
    main()

