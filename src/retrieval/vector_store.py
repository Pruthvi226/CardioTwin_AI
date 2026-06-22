"""Local vector store for PPG feature similarity search.

The project keeps this dependency-light by using Scikit-learn's nearest-neighbor
index and persisting the fitted index with joblib. It behaves like a small local
vector database for demo and recruiter-review workflows.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


DEFAULT_VECTOR_INDEX_PATH = Path("models/ppg_feature_vector_index.joblib")

DEFAULT_METADATA_COLUMNS = [
    "window_id",
    "subject_id",
    "stress_label",
    "quality_label",
    "sbp",
    "dbp",
    "heart_rate",
    "activity",
    "mdi_score",
    "signal_quality_score",
]


def _numeric_matrix(frame: pd.DataFrame, columns: list[str]) -> np.ndarray:
    """Return a dense numeric matrix with stable column order."""
    if not columns:
        raise ValueError("At least one feature column is required to build a vector index.")

    numeric = frame.reindex(columns=columns)
    numeric = numeric.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    return numeric.fillna(0.0).to_numpy(dtype=float)


def _json_safe(value: Any) -> Any:
    """Convert pandas/numpy values into API-friendly primitives."""
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float):
        return None if math.isnan(value) or math.isinf(value) else value
    if pd.isna(value):
        return None
    return value


def build_feature_vector_index(
    features: pd.DataFrame,
    feature_columns: list[str],
    out_path: str | Path = DEFAULT_VECTOR_INDEX_PATH,
    *,
    metadata_columns: list[str] | None = None,
    metric: str = "cosine",
    n_neighbors: int = 5,
) -> Path:
    """Build and persist a local nearest-neighbor index from feature vectors."""
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    vectors = _numeric_matrix(features, feature_columns)
    if len(vectors) == 0:
        raise ValueError("Cannot build a vector index from an empty feature table.")

    scaler = StandardScaler()
    scaled_vectors = scaler.fit_transform(vectors)
    neighbor_count = max(1, min(int(n_neighbors), len(scaled_vectors)))

    index = NearestNeighbors(n_neighbors=neighbor_count, metric=metric)
    index.fit(scaled_vectors)

    metadata_source = metadata_columns or DEFAULT_METADATA_COLUMNS
    available_metadata = [column for column in metadata_source if column in features.columns]
    metadata = features[available_metadata].copy() if available_metadata else pd.DataFrame(index=features.index)
    if "window_id" not in metadata.columns:
        metadata.insert(0, "window_id", np.arange(len(features)))
    metadata = metadata.reset_index(drop=True)

    artifact = {
        "index_type": "sklearn_nearest_neighbors",
        "metric": metric,
        "feature_columns": feature_columns,
        "scaler": scaler,
        "index": index,
        "metadata": metadata,
        "vector_count": int(len(scaled_vectors)),
        "n_neighbors": neighbor_count,
    }
    joblib.dump(artifact, output)
    return output


def load_vector_index(path: str | Path = DEFAULT_VECTOR_INDEX_PATH) -> dict[str, Any] | None:
    """Load a persisted local vector index if it exists."""
    index_path = Path(path)
    if not index_path.exists():
        return None
    artifact = joblib.load(index_path)
    required = {"index", "scaler", "feature_columns", "metadata", "vector_count"}
    if not required.issubset(artifact):
        raise ValueError(f"Invalid vector index artifact: {index_path}")
    return artifact


def query_similar_windows(
    query_features: pd.DataFrame | pd.Series | dict[str, Any],
    vector_index: dict[str, Any],
    *,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """Return nearest indexed PPG windows for one query feature row."""
    if isinstance(query_features, pd.Series):
        query_frame = query_features.to_frame().T
    elif isinstance(query_features, dict):
        query_frame = pd.DataFrame([query_features])
    else:
        query_frame = query_features.head(1).copy()

    feature_columns = list(vector_index["feature_columns"])
    matrix = _numeric_matrix(query_frame, feature_columns)
    scaled = vector_index["scaler"].transform(matrix)

    available = int(vector_index.get("vector_count", 0))
    if available == 0:
        return []
    neighbors = max(1, min(int(top_k), available))
    distances, indices = vector_index["index"].kneighbors(scaled, n_neighbors=neighbors)

    metric = str(vector_index.get("metric", "cosine"))
    metadata = vector_index["metadata"].reset_index(drop=True)
    results: list[dict[str, Any]] = []
    for rank, (distance, index_position) in enumerate(zip(distances[0], indices[0]), start=1):
        row = metadata.iloc[int(index_position)].to_dict()
        if metric == "cosine":
            similarity = 1.0 - float(distance)
        else:
            similarity = 1.0 / (1.0 + float(distance))

        results.append(
            {
                "rank": rank,
                "similarity": round(float(np.clip(similarity, 0.0, 1.0)), 4),
                "distance": round(float(distance), 6),
                "metadata": {key: _json_safe(value) for key, value in row.items()},
            }
        )

    return results
