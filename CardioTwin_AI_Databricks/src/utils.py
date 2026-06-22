"""Shared plotting, metric, and file helpers for CardioTwin AI."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.model_selection import train_test_split


DEFAULT_FEATURE_COLUMNS = [
    "mean_amplitude",
    "std_amplitude",
    "min_amplitude",
    "max_amplitude",
    "amplitude_range",
    "peak_count",
    "heart_rate_approx",
    "signal_energy",
    "mean_abs_change",
    "systolic_proxy",
    "diastolic_proxy",
    "pulse_pressure_proxy",
    "signal_quality_score",
]


def ensure_parent_dir(path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def write_markdown(path: str | Path, content: str) -> Path:
    output_path = ensure_parent_dir(path)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def available_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return known numeric feature columns that are present in a dataframe."""

    return [col for col in DEFAULT_FEATURE_COLUMNS if col in df.columns]


def safe_train_test_split(
    X: pd.DataFrame,
    y: pd.Series | pd.DataFrame,
    test_size: float = 0.30,
    random_state: int = 42,
    stratify: pd.Series | None = None,
):
    """Train/test split that falls back gracefully for tiny demo datasets."""

    try:
        return train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify,
        )
    except ValueError:
        return train_test_split(X, y, test_size=test_size, random_state=random_state)


def save_confusion_matrix_plot(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    labels: Iterable[int],
    output_path: str | Path,
    title: str = "Confusion Matrix",
) -> Path:
    """Save a confusion matrix artifact for MLflow."""

    output_path = ensure_parent_dir(output_path)
    matrix = confusion_matrix(y_true, y_pred, labels=list(labels))
    display = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=list(labels))
    display.plot(cmap="Blues", values_format="d")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return output_path


def save_feature_importance_plot(
    feature_names: Sequence[str],
    importances: Sequence[float],
    output_path: str | Path,
    title: str = "Feature Importance",
) -> Path:
    """Save a horizontal feature-importance chart."""

    output_path = ensure_parent_dir(output_path)
    order = np.argsort(importances)
    ordered_names = np.asarray(feature_names)[order]
    ordered_values = np.asarray(importances)[order]

    plt.figure(figsize=(8, max(4, len(feature_names) * 0.35)))
    plt.barh(ordered_names, ordered_values, color="#2b8cbe")
    plt.title(title)
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return output_path


def save_regression_prediction_plot(
    y_true: pd.DataFrame | np.ndarray,
    y_pred: np.ndarray,
    target_names: Sequence[str],
    output_path: str | Path,
) -> Path:
    """Save predicted-vs-actual scatter plots for regression targets."""

    output_path = ensure_parent_dir(output_path)
    true_values = np.asarray(y_true)
    pred_values = np.asarray(y_pred)
    n_targets = len(target_names)

    fig, axes = plt.subplots(1, n_targets, figsize=(5 * n_targets, 4))
    if n_targets == 1:
        axes = [axes]

    for index, target in enumerate(target_names):
        ax = axes[index]
        ax.scatter(true_values[:, index], pred_values[:, index], color="#2b8cbe", alpha=0.85)
        min_value = min(true_values[:, index].min(), pred_values[:, index].min())
        max_value = max(true_values[:, index].max(), pred_values[:, index].max())
        ax.plot([min_value, max_value], [min_value, max_value], color="#333333", linestyle="--")
        ax.set_title(target)
        ax.set_xlabel("Actual")
        ax.set_ylabel("Predicted")

    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return output_path
