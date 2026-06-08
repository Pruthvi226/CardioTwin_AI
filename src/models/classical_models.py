"""Classical ML baselines for morphology features."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


NON_FEATURE_COLUMNS = {
    "window_id",
    "subject_id",
    "stress_label",
    "quality_label",
    "sbp",
    "dbp",
    "heart_rate",
    "activity",
}


def feature_columns(frame: pd.DataFrame) -> list[str]:
    """Return numeric feature columns used by classical models."""
    return [
        column
        for column in frame.columns
        if column not in NON_FEATURE_COLUMNS and pd.api.types.is_numeric_dtype(frame[column])
    ]


def train_classical_models(
    x_train: pd.DataFrame,
    y_train: np.ndarray,
    output_dir: str | Path,
) -> dict[str, Pipeline]:
    """Train RandomForest and GradientBoosting stress classifiers."""
    models: dict[str, Pipeline] = {
        "RandomForest_features": Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=120,
                        max_depth=8,
                        min_samples_leaf=2,
                        random_state=42,
                        class_weight="balanced",
                    ),
                ),
            ]
        ),
        "GradientBoosting_features": Pipeline(
            [
                ("scale", StandardScaler()),
                ("model", GradientBoostingClassifier(random_state=42)),
            ]
        ),
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for name, model in models.items():
        model.fit(x_train, y_train)
        joblib.dump(model, output / f"{name}.joblib")

    return models


def train_bp_regressor(x_train: pd.DataFrame, y_train: np.ndarray, output_dir: str | Path) -> Pipeline:
    """Train a lightweight BP regression baseline for the dashboard/API."""
    model = Pipeline(
        [
            ("scale", StandardScaler()),
            ("model", RandomForestRegressor(n_estimators=120, max_depth=8, random_state=42)),
        ]
    )
    model.fit(x_train, y_train)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output / "RandomForest_bp_regressor.joblib")
    return model

