"""Evaluate saved CardioTwin metrics and export JSON summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def export_metric_json(metrics_path: str | Path = "results/metrics.csv") -> None:
    metrics = pd.read_csv(metrics_path)
    Path("reports/metrics").mkdir(parents=True, exist_ok=True)
    classification = metrics.dropna(subset=["f1_score"]).to_dict(orient="records")
    regression = metrics.dropna(subset=["mae"]).to_dict(orient="records")
    Path("reports/metrics/classification_metrics.json").write_text(json.dumps(classification, indent=2), encoding="utf-8")
    Path("reports/metrics/regression_metrics.json").write_text(json.dumps(regression, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default="results/metrics.csv")
    args = parser.parse_args()
    export_metric_json(args.metrics)
    print("Wrote reports/metrics classification and regression JSON files.")


if __name__ == "__main__":
    main()

