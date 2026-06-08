"""FastAPI endpoints for CardioTwin AI demo predictions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.features.mdi_features import build_feature_table
from src.preprocessing.clean_signal import preprocess_ppg
from src.preprocessing.segment_windows import create_windows


app = FastAPI(title="CardioTwin AI API", version="1.0.0")


class PredictionRequest(BaseModel):
    ppg: list[float] = Field(..., description="Raw PPG samples")
    fs: float = Field(64.0, description="Original sampling frequency")


def _load_model() -> Any | None:
    model_path = Path("models/RandomForest_features.joblib")
    if not model_path.exists():
        return None
    return joblib.load(model_path)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictionRequest) -> dict[str, Any]:
    target_fs = 64.0
    cleaned = preprocess_ppg(np.asarray(request.ppg, dtype=float), request.fs, target_fs)
    windows = create_windows(cleaned, window_size=int(8 * target_fs), overlap=0.5)
    if len(windows) == 0:
        windows = cleaned[: int(8 * target_fs)]
        if windows.size < int(8 * target_fs):
            windows = np.pad(windows, (0, int(8 * target_fs) - windows.size))
        windows = windows.reshape(1, -1)

    labels = pd.DataFrame({"stress_label": [0] * len(windows), "quality_label": [1] * len(windows)})
    features = build_feature_table(windows, labels, fs=target_fs)
    model = _load_model()
    feature_row = features.drop(columns=[column for column in features.columns if column in {"stress_label", "quality_label"}])
    feature_row = feature_row.select_dtypes(include=["number"]).drop(columns=["window_id"], errors="ignore").head(1)

    if model is None:
        score = float(features["mdi_score"].iloc[0])
        prediction = int(score >= 0.5)
        confidence = max(score, 1.0 - score)
    else:
        probabilities = model.predict_proba(feature_row)[0]
        prediction = int(np.argmax(probabilities))
        confidence = float(np.max(probabilities))

    return {
        "predicted_stress_class": prediction,
        "confidence": round(confidence, 4),
        "mdi_score": round(float(features["mdi_score"].iloc[0]), 4),
        "signal_quality_score": round(float(features["signal_quality_score"].iloc[0]), 4),
        "feature_preview": features.head(1).to_dict(orient="records")[0],
        "disclaimer": "Research/demo output only; not a medical diagnosis.",
    }

