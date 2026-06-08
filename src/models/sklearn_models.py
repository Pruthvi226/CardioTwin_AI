"""Scikit-learn baselines for CardioTwin AI."""

from __future__ import annotations

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def build_sklearn_classifiers(random_state: int = 42) -> dict[str, Pipeline]:
    """Return all requested classical baseline models."""
    return {
        "logistic_regression": Pipeline(
            [("scale", StandardScaler()), ("model", LogisticRegression(max_iter=1000, class_weight="balanced"))]
        ),
        "random_forest": Pipeline(
            [("scale", StandardScaler()), ("model", RandomForestClassifier(n_estimators=160, random_state=random_state, class_weight="balanced"))]
        ),
        "gradient_boosting": Pipeline(
            [("scale", StandardScaler()), ("model", GradientBoostingClassifier(random_state=random_state))]
        ),
        "svm": Pipeline(
            [("scale", StandardScaler()), ("model", SVC(probability=True, class_weight="balanced", random_state=random_state))]
        ),
    }

