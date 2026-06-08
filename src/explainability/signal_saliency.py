"""Signal saliency helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd


def signal_saliency(window: np.ndarray) -> pd.DataFrame:
    """Estimate important time regions from normalized slope magnitude."""
    values = np.asarray(window, dtype=float)
    slope = np.abs(np.gradient(values))
    saliency = slope / (slope.max() + 1e-8)
    return pd.DataFrame({"sample": np.arange(len(values)), "saliency": saliency})

