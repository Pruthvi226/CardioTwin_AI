"""Configuration loading for model fusion and risk categories."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULT_FUSION_WEIGHTS = {
    "signal": 0.35,
    "tabular": 0.30,
    "text": 0.20,
    "image": 0.15,
}

RISK_BANDS = [
    (0, 25, "Low Risk"),
    (26, 50, "Mild Risk"),
    (51, 75, "Moderate Risk"),
    (76, 100, "High Risk"),
]


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, float(value)))


def app_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config() -> dict[str, Any]:
    config_path = Path(os.getenv("CARDIOTWIN_CONFIG", app_root() / "config.json"))
    if not config_path.exists():
        return {"fusion_weights": DEFAULT_FUSION_WEIGHTS}

    try:
        with config_path.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {"fusion_weights": DEFAULT_FUSION_WEIGHTS}

    weights = loaded.get("fusion_weights", DEFAULT_FUSION_WEIGHTS)
    merged = {**DEFAULT_FUSION_WEIGHTS, **weights}
    return {**loaded, "fusion_weights": normalize_weights(merged)}


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    numeric = {name: max(0.0, float(value)) for name, value in weights.items()}
    total = sum(numeric.values())
    if total <= 0:
        return DEFAULT_FUSION_WEIGHTS.copy()
    return {name: value / total for name, value in numeric.items()}


def get_fusion_weights() -> dict[str, float]:
    return load_config().get("fusion_weights", DEFAULT_FUSION_WEIGHTS.copy())


def risk_category(score: float) -> str:
    rounded = int(round(clamp(score)))
    for lower, upper, label in RISK_BANDS:
        if lower <= rounded <= upper:
            return label
    return "High Risk"

