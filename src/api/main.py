"""FastAPI endpoints for CardioTwin AI demo predictions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.data.signal_quality import assess_signal_quality
from src.features.extract_features import extract_features
from src.preprocessing.clean_signal import preprocess_ppg
from src.preprocessing.segment_windows import create_windows
from src.retrieval.vector_store import DEFAULT_VECTOR_INDEX_PATH, load_vector_index, query_similar_windows
from src.utils.common import DISCLAIMER, assess_prediction_risk


app = FastAPI(title="CardioTwin AI API", version="1.0.0")


class PredictionRequest(BaseModel):
    ppg: list[float] = Field(..., description="Raw PPG samples")
    fs: float = Field(64.0, description="Original sampling frequency")
    top_k: int = Field(3, ge=1, le=10, description="Number of similar indexed windows to return")


def _load_model() -> Any | None:
    model_path = Path("models/RandomForest_features.joblib")
    if not model_path.exists():
        return None
    return joblib.load(model_path)


def _load_retrieval_index() -> dict[str, Any] | None:
    try:
        return load_vector_index(DEFAULT_VECTOR_INDEX_PATH)
    except (OSError, ValueError):
        return None


@app.get("/")
def root() -> dict[str, str]:
    return {"project": "CardioTwin AI", "status": "running", "disclaimer": DISCLAIMER}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "disclaimer": DISCLAIMER}


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
    features = extract_features(windows, labels, fs=target_fs)
    quality = assess_signal_quality(windows[0], fs=target_fs)
    model = _load_model()
    feature_row = features.drop(columns=[column for column in features.columns if column in {"stress_label", "quality_label"}])
    feature_row = feature_row.select_dtypes(include=["number"]).drop(columns=["window_id"], errors="ignore").head(1)
    vector_index = _load_retrieval_index()
    similar_windows = (
        query_similar_windows(feature_row, vector_index, top_k=request.top_k)
        if vector_index is not None
        else []
    )

    if model is None:
        score = float(features["mdi_score"].iloc[0])
        prediction = int(score >= 0.5)
        confidence = max(score, 1.0 - score)
    else:
        try:
            probabilities = model.predict_proba(feature_row)[0]
            prediction = int(np.argmax(probabilities))
            confidence = float(np.max(probabilities))
        except ValueError:
            score = float(features["mdi_score"].iloc[0])
            prediction = int(score >= 0.5)
            confidence = max(score, 1.0 - score)

    prediction_name = "stress_like_pattern" if prediction else "baseline_like_pattern"
    top_features = ["mdi_score", "heart_rate_proxy", "spectral_entropy", "signal_quality_score"]
    payload = assess_prediction_risk(
        prediction=prediction_name,
        confidence=confidence,
        signal_quality=float(quality["signal_quality_score"]),
        explanation=[str(quality["artifact_warning"])],
    )
    payload.update(
        {
            "project": "CardioTwin AI",
            "mdi_score": round(float(features["mdi_score"].iloc[0]), 4),
            "top_features": top_features,
            "similar_windows": similar_windows,
            "retrieval": {
                "enabled": vector_index is not None,
                "backend": "sklearn_nearest_neighbors",
                "index_path": str(DEFAULT_VECTOR_INDEX_PATH),
            },
            "extracted_features": features.head(1).to_dict(orient="records")[0],
        }
    )
    return payload


@app.get("/model-info")
def model_info() -> dict[str, Any]:
    return {
        "model_name": "RandomForest_features fallback with PyTorch demo baselines",
        "version": "1.1.0",
        "training_dataset_mode": "synthetic by default; real mode documented",
        "metrics_path": "results/metrics.csv",
        "vector_database": {
            "enabled": DEFAULT_VECTOR_INDEX_PATH.exists(),
            "backend": "sklearn_nearest_neighbors",
            "index_path": str(DEFAULT_VECTOR_INDEX_PATH),
            "purpose": "nearest-window retrieval for similarity evidence during demo inference",
        },
        "limitations": [
            "Synthetic demo results verify the pipeline only.",
            "Real-world performance requires subject-wise evaluation on governed wearable datasets.",
        ],
        "disclaimer": DISCLAIMER,
    }


@app.get("/sample-response")
def sample_response() -> dict[str, Any]:
    return {
        "project": "CardioTwin AI",
        "prediction": "stress_like_pattern",
        "confidence": 0.78,
        "uncertainty": "medium",
        "signal_quality": 0.62,
        "risk_flag": "acceptable_demo_prediction",
        "top_features": ["peak_interval_std", "spectral_entropy", "signal_energy"],
        "similar_windows": [
            {
                "rank": 1,
                "similarity": 0.94,
                "metadata": {"window_id": 12, "stress_label": 1, "signal_quality_score": 0.88},
            }
        ],
        "explanation": ["demo response", "confidence and signal quality are review aids"],
        "disclaimer": DISCLAIMER,
    }

