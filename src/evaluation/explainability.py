"""Explainability helpers for classical and deep demo models."""

from __future__ import annotations

import numpy as np
import pandas as pd


def feature_importance_table(model, feature_names: list[str], top_n: int = 10) -> pd.DataFrame:
    """Extract feature importances from a sklearn pipeline when available."""
    estimator = getattr(model, "named_steps", {}).get("model", model)
    importances = getattr(estimator, "feature_importances_", None)
    if importances is None:
        return pd.DataFrame({"feature": feature_names[:top_n], "importance": np.nan})

    frame = pd.DataFrame({"feature": feature_names, "importance": importances})
    return frame.sort_values("importance", ascending=False).head(top_n).reset_index(drop=True)


def signal_saliency(window: np.ndarray) -> pd.DataFrame:
    """Simple signal saliency proxy based on local slope magnitude."""
    values = np.asarray(window, dtype=float)
    slope = np.abs(np.gradient(values))
    saliency = slope / (slope.max() + 1e-8)
    return pd.DataFrame({"sample": np.arange(len(values)), "saliency": saliency})

