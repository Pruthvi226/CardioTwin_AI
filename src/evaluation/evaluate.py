"""Evaluation metrics and plots for CardioTwin AI."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)


def classification_metrics(model_name: str, y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float | str]:
    """Return a metrics row for a classifier."""
    roc_auc = np.nan
    try:
        roc_auc = float(roc_auc_score(y_true, y_pred))
    except ValueError:
        pass
    return {
        "model": model_name,
        "task": "stress_or_quality_classification",
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "roc_auc": roc_auc,
        "mae": np.nan,
        "rmse": np.nan,
        "r2": np.nan,
    }


def regression_metrics(model_name: str, y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float | str]:
    """Return a metrics row for a regressor."""
    return {
        "model": model_name,
        "task": "bp_regression",
        "accuracy": np.nan,
        "precision": np.nan,
        "recall": np.nan,
        "f1_score": np.nan,
        "weighted_f1": np.nan,
        "roc_auc": np.nan,
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def save_metrics(metrics: list[dict[str, float | str]], out_path: str | Path) -> pd.DataFrame:
    """Save metrics to CSV and return the dataframe."""
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(metrics)
    frame.to_csv(output, index=False)
    return frame


def plot_model_comparison(metrics: pd.DataFrame, out_path: str | Path) -> None:
    """Plot classification F1 scores for recruiter/demo review."""
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    classified = metrics.dropna(subset=["f1_score"]).sort_values("f1_score", ascending=True)
    if classified.empty:
        return
    plt.figure(figsize=(8, 4.5))
    plt.barh(classified["model"], classified["f1_score"], color="#0f766e")
    plt.xlabel("Weighted F1")
    plt.xlim(0, 1)
    plt.title("CardioTwin Model Comparison")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def plot_feature_importance(importance: pd.DataFrame, out_path: str | Path) -> None:
    """Save a feature importance bar chart."""
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if importance.empty or "importance" not in importance:
        return
    frame = importance.sort_values("importance").tail(10)
    plt.figure(figsize=(8, 4.5))
    plt.barh(frame["feature"], frame["importance"], color="#2563eb")
    plt.title("Top Feature Attributions")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, out_path: str | Path, title: str) -> None:
    """Save a confusion matrix image."""
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    display = ConfusionMatrixDisplay.from_predictions(y_true, y_pred, cmap="Blues", colorbar=False)
    display.ax_.set_title(title)
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()

