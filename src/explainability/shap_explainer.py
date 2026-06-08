"""SHAP/permutation-style explainability fallback."""

from __future__ import annotations

import pandas as pd

from src.explainability.feature_attribution import top_feature_attributions


def explain_sklearn_model(model, feature_frame: pd.DataFrame, top_n: int = 8) -> pd.DataFrame:
    """Return top features without requiring SHAP as a hard dependency."""
    return top_feature_attributions(model, list(feature_frame.columns), top_n=top_n)

