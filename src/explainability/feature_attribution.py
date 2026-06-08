"""Feature attribution utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def top_feature_attributions(model, feature_names: list[str], top_n: int = 8) -> pd.DataFrame:
    """Return feature importances or neutral placeholders."""
    estimator = getattr(model, "named_steps", {}).get("model", model)
    importances = getattr(estimator, "feature_importances_", None)
    if importances is None:
        importances = np.ones(len(feature_names), dtype=float) / max(1, len(feature_names))
    frame = pd.DataFrame({"feature": feature_names, "importance": importances})
    return frame.sort_values("importance", ascending=False).head(top_n).reset_index(drop=True)

