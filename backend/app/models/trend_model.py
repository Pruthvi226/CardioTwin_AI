"""Time-series health trend analysis."""

from __future__ import annotations

from io import BytesIO
from typing import Any

import numpy as np
import pandas as pd

from ..utils.disclaimer import DISCLAIMER
from ..utils.validators import as_float


def _load_history(raw: bytes | None, records: list[dict[str, Any]] | None) -> pd.DataFrame:
    if records:
        return pd.DataFrame(records)
    if raw:
        return pd.read_csv(BytesIO(raw))
    sample = __import__("pathlib").Path(__file__).resolve().parents[1] / "data" / "sample_history.csv"
    return pd.read_csv(sample)


def _direction(values: pd.Series) -> str:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if len(clean) < 2:
        return "insufficient_data"
    x = np.arange(len(clean))
    slope = float(np.polyfit(x, clean.to_numpy(dtype=float), 1)[0])
    tolerance = max(abs(float(clean.mean())) * 0.01, 0.5)
    if slope > tolerance:
        return "increasing"
    if slope < -tolerance:
        return "decreasing"
    return "stable"


def analyze_trends(raw: bytes | None = None, records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    dataframe = _load_history(raw, records)
    metric_map = {
        "systolic_bp": "bp_trend",
        "heart_rate": "heart_rate_trend",
        "spo2": "spo2_trend",
        "sleep_hours": "sleep_trend",
        "risk_score": "risk_score_trend",
        "signal_quality": "signal_quality_trend",
    }
    trends = {label: _direction(dataframe[column]) for column, label in metric_map.items() if column in dataframe}
    flags = []
    if trends.get("bp_trend") == "increasing":
        flags.append("Blood pressure is increasing.")
    if trends.get("spo2_trend") == "decreasing":
        flags.append("SpO2 is decreasing.")
    if trends.get("risk_score_trend") == "increasing":
        flags.append("Overall risk score is increasing.")
    if trends.get("sleep_trend") == "decreasing":
        flags.append("Sleep duration is decreasing.")

    risk_change = 0.0
    if "risk_score" in dataframe and len(dataframe["risk_score"].dropna()) >= 2:
        first = as_float(dataframe["risk_score"].dropna().iloc[0], 0)
        last = as_float(dataframe["risk_score"].dropna().iloc[-1], 0)
        risk_change = 0 if first == 0 else (last - first) / first * 100

    explanation = (
        "Blood pressure or risk is increasing across recent readings. Sleep and heart rate may be contributing."
        if flags
        else "Recent readings appear broadly stable based on the available history."
    )
    return {
        "trend_direction": trends,
        "risk_change_percentage": round(risk_change, 2),
        "abnormal_trend_flags": flags,
        "chart_data": dataframe.fillna("").to_dict(orient="records"),
        "explanation": explanation,
        "disclaimer": DISCLAIMER,
    }


def live_simulation() -> dict[str, Any]:
    import math
    import time

    now = time.time()
    heart_rate = 84 + 8 * math.sin(now / 12)
    spo2 = 96 + 1.5 * math.sin(now / 18)
    signal_quality = 86 + 6 * math.sin(now / 15)
    systolic = 120 + (heart_rate - 80) * 0.45
    diastolic = 78 + (heart_rate - 80) * 0.18
    risk_level = "Mild" if systolic < 130 and heart_rate < 96 else "Moderate"
    return {
        "heart_rate": round(heart_rate),
        "spo2": round(spo2, 1),
        "ppg_signal_quality": round(signal_quality, 1),
        "estimated_bp": {"systolic": round(systolic), "diastolic": round(diastolic)},
        "risk_level": risk_level,
        "timestamp": pd.Timestamp.utcnow().isoformat(),
        "disclaimer": DISCLAIMER,
    }

