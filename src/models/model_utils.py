"""Model utility helpers."""

from __future__ import annotations

import numpy as np


def softmax_confidence(logits: np.ndarray) -> tuple[int, float]:
    """Return predicted class and max softmax confidence."""
    values = np.asarray(logits, dtype=float)
    values = values - values.max()
    probs = np.exp(values) / np.sum(np.exp(values))
    return int(np.argmax(probs)), float(np.max(probs))

