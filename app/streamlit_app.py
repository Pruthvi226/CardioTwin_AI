"""Streamlit product interface for CardioTwin AI."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.data.dataset_loader import load_demo_csv
from src.data.signal_quality import assess_signal_quality
from src.explainability.signal_saliency import signal_saliency
from src.features.extract_features import extract_features
from src.features.spectrogram_builder import window_to_spectrogram
from src.models.classical_models import feature_columns
from src.preprocessing.clean_signal import preprocess_ppg
from src.preprocessing.segment_windows import WindowedDataset, window_dataframe
from src.retrieval.vector_store import DEFAULT_VECTOR_INDEX_PATH, load_vector_index, query_similar_windows
from src.utils.common import DISCLAIMER, assess_prediction_risk


st.set_page_config(page_title="CardioTwin AI", layout="wide", initial_sidebar_state="expanded")


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2rem;
        max-width: 1440px;
    }
    div[data-testid="stSidebar"] {
        background: #f7f8fa;
        border-right: 1px solid #d9dee7;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d9dee7;
        padding: 0.85rem 1rem;
        border-radius: 8px;
    }
    .ct-header {
        border-bottom: 1px solid #d9dee7;
        padding-bottom: 0.85rem;
        margin-bottom: 1rem;
    }
    .ct-header h1 {
        font-size: 1.75rem;
        line-height: 1.15;
        margin: 0;
        letter-spacing: 0;
    }
    .ct-muted {
        color: #526071;
        font-size: 0.92rem;
        margin-top: 0.35rem;
    }
    .ct-section-label {
        color: #526071;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .ct-alert {
        border-left: 4px solid #0f766e;
        background: #f3fbf8;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def _load_metrics() -> pd.DataFrame:
    path = Path("results/metrics.csv")
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=["model", "accuracy", "weighted_f1", "mae", "rmse"])


@st.cache_data
def _load_default_signal() -> pd.DataFrame:
    path = Path("data/raw/demo_ppg.csv")
    if path.exists():
        return load_demo_csv(path)
    return pd.DataFrame()


@st.cache_data
def _load_feature_importance() -> pd.DataFrame:
    path = Path("results/feature_importance.csv")
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=["feature", "importance"])


@st.cache_resource
def _load_model() -> Any | None:
    model_path = Path("models/RandomForest_features.joblib")
    if not model_path.exists():
        return None
    return joblib.load(model_path)


@st.cache_resource
def _load_retrieval_index() -> dict[str, Any] | None:
    try:
        return load_vector_index(DEFAULT_VECTOR_INDEX_PATH)
    except (OSError, ValueError):
        return None


def _normalise_signal_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a usable signal dataframe from demo or uploaded CSV input."""
    result = frame.copy()
    result.columns = [str(column).strip().lower() for column in result.columns]

    if "ppg" not in result.columns:
        numeric_columns = result.select_dtypes(include=["number"]).columns.tolist()
        if numeric_columns:
            result["ppg"] = result[numeric_columns[0]]

    if "ppg" not in result.columns:
        return pd.DataFrame()

    result["ppg"] = pd.to_numeric(result["ppg"], errors="coerce")
    result = result.dropna(subset=["ppg"]).reset_index(drop=True)
    if result.empty:
        return pd.DataFrame()

    if "fs" not in result.columns:
        result["fs"] = 64.0
    result["fs"] = pd.to_numeric(result["fs"], errors="coerce").fillna(64.0)

    if "subject_id" not in result.columns:
        result["subject_id"] = "uploaded"
    result["subject_id"] = result["subject_id"].astype(str)

    if "time" not in result.columns:
        result["time"] = np.arange(len(result), dtype=float) / float(result["fs"].iloc[0])
    result["time"] = pd.to_numeric(result["time"], errors="coerce").ffill().fillna(0.0)

    defaults: dict[str, float | int] = {
        "stress_label": 0,
        "quality_label": 1,
        "sbp": 120.0,
        "dbp": 80.0,
        "heart_rate": 0.0,
        "activity": 0,
    }
    for column, value in defaults.items():
        if column not in result.columns:
            result[column] = value
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(value)

    return result.sort_values(["subject_id", "time"]).reset_index(drop=True)


def _load_signal(uploaded_file: Any | None) -> pd.DataFrame:
    if uploaded_file is not None:
        return _normalise_signal_frame(pd.read_csv(uploaded_file))
    return _normalise_signal_frame(_load_default_signal())


def _prepare_subject_windows(subject_frame: pd.DataFrame) -> tuple[np.ndarray, WindowedDataset]:
    source_fs = float(subject_frame["fs"].iloc[0])
    cleaned = preprocess_ppg(subject_frame["ppg"].to_numpy(), fs_original=source_fs, fs_target=64.0)
    windowed = window_dataframe(subject_frame, fs_target=64.0, window_seconds=8.0, overlap=0.5)
    return cleaned, windowed


def _model_features(features: pd.DataFrame) -> pd.DataFrame:
    selected = feature_columns(features)
    return features[selected].fillna(0.0).head(1)


def _predict(features: pd.DataFrame) -> tuple[int, float, str]:
    model = _load_model()
    if model is not None:
        try:
            probabilities = model.predict_proba(_model_features(features))[0]
            return int(np.argmax(probabilities)), float(np.max(probabilities)), "RandomForest features"
        except ValueError:
            pass

    score = float(features["mdi_score"].iloc[0])
    return int(score >= 0.5), max(score, 1.0 - score), "MDI fallback"


def _review_status(risk_flag: str, confidence: float, threshold: float, signal_quality: float) -> str:
    if confidence < threshold:
        return "Manual review"
    if signal_quality < 0.65 or risk_flag in {"low_confidence", "poor_signal_quality", "review_required"}:
        return "Review queue"
    return "Ready"


def _artifact_table() -> pd.DataFrame:
    artifacts = [
        ("Raw demo data", "data/raw/demo_ppg.csv"),
        ("Processed windows", "data/processed/demo_windows.npz"),
        ("Feature table", "data/processed/mdi_features.csv"),
        ("Feature model", "models/RandomForest_features.joblib"),
        ("Vector index", str(DEFAULT_VECTOR_INDEX_PATH)),
        ("Metrics", "results/metrics.csv"),
        ("Experiment report", "reports/experiment_report.md"),
        ("API service", "src/api/main.py"),
    ]
    return pd.DataFrame(
        [
            {
                "asset": name,
                "path": path,
                "status": "Ready" if Path(path).exists() else "Missing",
            }
            for name, path in artifacts
        ]
    )


def _download_json(label: str, payload: dict[str, Any], file_name: str) -> None:
    st.download_button(
        label,
        json.dumps(payload, indent=2, default=str),
        file_name=file_name,
        mime="application/json",
    )


with st.sidebar:
    st.markdown("### CardioTwin AI")
    uploaded = st.file_uploader("PPG CSV", type=["csv"])

raw_frame = _load_signal(uploaded)
if raw_frame.empty:
    st.error("No usable PPG signal was found.")
    st.stop()

subject_options = sorted(raw_frame["subject_id"].astype(str).unique())

with st.sidebar:
    st.markdown("### Signal")
    subject = st.selectbox("Subject", subject_options)
    threshold = st.slider("Review threshold", min_value=0.10, max_value=0.95, value=0.60, step=0.05)
    top_k = st.slider("Similar windows", min_value=1, max_value=10, value=3, step=1)
    st.markdown("### Runtime")
    st.caption("Target sampling: 64 Hz")
    st.caption("Window length: 8 seconds")
    st.caption("Mode: research demo")

subject_frame = raw_frame[raw_frame["subject_id"].astype(str) == subject].copy()
cleaned_signal, windowed = _prepare_subject_windows(subject_frame)
if len(windowed.windows) == 0:
    st.error("The selected subject does not have enough samples for an 8-second PPG window.")
    st.stop()

with st.sidebar:
    selected_window = st.number_input(
        "Window",
        min_value=0,
        max_value=len(windowed.windows) - 1,
        value=0,
        step=1,
    )

labels = windowed.labels.reset_index(drop=True)
features = extract_features(windowed.windows, labels, fs=64.0)
selected_features = features.iloc[[int(selected_window)]].reset_index(drop=True)
selected_signal = windowed.windows[int(selected_window)]
quality = assess_signal_quality(selected_signal, fs=64.0)
prediction, confidence, active_model = _predict(selected_features)
prediction_name = "stress_like_pattern" if prediction else "baseline_like_pattern"
risk = assess_prediction_risk(
    prediction=prediction_name,
    confidence=confidence,
    signal_quality=float(quality["signal_quality_score"]),
    explanation=[str(quality["artifact_warning"])],
)
status = _review_status(risk["risk_flag"], confidence, threshold, float(quality["signal_quality_score"]))

vector_index = _load_retrieval_index()
similar_windows = (
    query_similar_windows(_model_features(selected_features), vector_index, top_k=top_k)
    if vector_index is not None
    else []
)

metrics = _load_metrics()
feature_importance = _load_feature_importance()
best_f1 = (
    metrics["weighted_f1"].dropna().max()
    if "weighted_f1" in metrics
    else metrics.get("f1_score", pd.Series(dtype=float)).dropna().max()
)
regression_row = metrics.dropna(subset=["mae"]).head(1) if "mae" in metrics else pd.DataFrame()
best_mae = None if regression_row.empty else float(regression_row["mae"].iloc[0])

st.markdown(
    """
    <div class="ct-header">
        <h1>CardioTwin AI</h1>
        <div class="ct-muted">PPG signal review workspace</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(f"<div class='ct-alert'>{DISCLAIMER}</div>", unsafe_allow_html=True)

summary_cols = st.columns(5)
summary_cols[0].metric("Review status", status)
summary_cols[1].metric("Prediction", risk["prediction"])
summary_cols[2].metric("Confidence", f"{confidence:.3f}")
summary_cols[3].metric("Signal quality", f"{quality['signal_quality_score']:.3f}")
summary_cols[4].metric("Indexed matches", len(similar_windows))

tabs = st.tabs(["Workbench", "Signal", "Evidence", "Models", "Records"])

with tabs[0]:
    left, right = st.columns([1.45, 1.0])
    with left:
        st.markdown("<div class='ct-section-label'>Selected window</div>", unsafe_allow_html=True)
        window_axis = np.arange(len(selected_signal), dtype=float) / 64.0
        st.line_chart(pd.DataFrame({"seconds": window_axis, "cleaned_ppg": selected_signal}).set_index("seconds"))

        action_cols = st.columns(3)
        action_cols[0].metric("Subject", subject)
        action_cols[1].metric("Window", int(selected_window))
        action_cols[2].metric("Model", active_model)

    with right:
        st.markdown("<div class='ct-section-label'>Decision payload</div>", unsafe_allow_html=True)
        decision = pd.DataFrame(
            [
                {"field": "uncertainty", "value": risk["uncertainty"]},
                {"field": "risk_flag", "value": risk["risk_flag"]},
                {"field": "artifact_warning", "value": quality["artifact_warning"]},
                {"field": "noise_flag", "value": str(quality["noise_flag"])},
                {"field": "amplitude_stability", "value": str(quality["amplitude_stability"])},
            ]
        )
        st.dataframe(decision, hide_index=True, width="stretch")
        if confidence < threshold:
            st.warning("Confidence is below the selected review threshold.")
        if quality["noise_flag"]:
            st.warning("Signal quality is flagged for review.")

        payload = {
            "project": "CardioTwin AI",
            "subject_id": subject,
            "window": int(selected_window),
            "model": active_model,
            "prediction": risk,
            "similar_windows": similar_windows,
            "features": selected_features.head(1).to_dict(orient="records")[0],
        }
        _download_json("Download decision JSON", payload, "cardiotwin_decision.json")

    st.markdown("<div class='ct-section-label'>Similar indexed windows</div>", unsafe_allow_html=True)
    if similar_windows:
        st.dataframe(
            pd.json_normalize(similar_windows),
            hide_index=True,
            width="stretch",
        )
    else:
        st.info("No vector index is available for similar-window retrieval.")

with tabs[1]:
    signal_left, signal_right = st.columns(2)
    with signal_left:
        st.markdown("<div class='ct-section-label'>Raw subject signal</div>", unsafe_allow_html=True)
        raw_chart = subject_frame[["time", "ppg"]].set_index("time")
        st.line_chart(raw_chart)
    with signal_right:
        st.markdown("<div class='ct-section-label'>Cleaned subject signal</div>", unsafe_allow_html=True)
        clean_axis = np.arange(len(cleaned_signal), dtype=float) / 64.0
        st.line_chart(pd.DataFrame({"seconds": clean_axis, "cleaned_ppg": cleaned_signal}).set_index("seconds"))

    spec_left, spec_right = st.columns([1.0, 1.0])
    with spec_left:
        st.markdown("<div class='ct-section-label'>Window quality</div>", unsafe_allow_html=True)
        quality_table = pd.DataFrame([quality])
        st.dataframe(quality_table, hide_index=True, width="stretch")
    with spec_right:
        st.markdown("<div class='ct-section-label'>Spectrogram input</div>", unsafe_allow_html=True)
        spectrogram = window_to_spectrogram(selected_signal, fs=64.0, image_size=128)
        fig, ax = plt.subplots(figsize=(6.5, 3.2))
        ax.imshow(spectrogram, aspect="auto", origin="lower", cmap="viridis")
        ax.set_xlabel("Time bins")
        ax.set_ylabel("Frequency bins")
        fig.tight_layout()
        st.pyplot(fig)

with tabs[2]:
    evidence_left, evidence_right = st.columns([1.0, 1.0])
    with evidence_left:
        st.markdown("<div class='ct-section-label'>Top features</div>", unsafe_allow_html=True)
        feature_view = (
            selected_features[
                ["mdi_score", "heart_rate_proxy", "spectral_entropy", "signal_quality_score", "signal_energy"]
            ]
            .T.reset_index()
            .rename(columns={"index": "feature", 0: "value"})
        )
        st.dataframe(feature_view, hide_index=True, width="stretch")

        if not feature_importance.empty:
            st.markdown("<div class='ct-section-label'>Model feature importance</div>", unsafe_allow_html=True)
            st.bar_chart(feature_importance.head(10).set_index("feature")["importance"])

    with evidence_right:
        st.markdown("<div class='ct-section-label'>Signal saliency</div>", unsafe_allow_html=True)
        saliency = signal_saliency(selected_signal)
        st.line_chart(saliency.set_index("sample")["saliency"])

        st.markdown("<div class='ct-section-label'>Explanation notes</div>", unsafe_allow_html=True)
        st.dataframe(
            pd.DataFrame({"note": risk["explanation"]}),
            hide_index=True,
            width="stretch",
        )

    st.markdown("<div class='ct-section-label'>Feature table for selected subject</div>", unsafe_allow_html=True)
    st.dataframe(features, width="stretch", height=320)
    st.download_button(
        "Download feature CSV",
        features.to_csv(index=False),
        file_name="cardiotwin_window_features.csv",
        mime="text/csv",
    )

with tabs[3]:
    model_cols = st.columns(4)
    model_cols[0].metric("Best weighted F1", "N/A" if pd.isna(best_f1) else f"{best_f1:.3f}")
    model_cols[1].metric("Models compared", len(metrics))
    model_cols[2].metric("BP MAE", "N/A" if best_mae is None else f"{best_mae:.3f}")
    model_cols[3].metric("Vector index", "Ready" if vector_index is not None else "Missing")

    model_left, model_right = st.columns([1.05, 1.0])
    with model_left:
        st.markdown("<div class='ct-section-label'>Model metrics</div>", unsafe_allow_html=True)
        st.dataframe(metrics, width="stretch", hide_index=True)
    with model_right:
        comparison_path = Path("results/plots/model_comparison.png")
        if comparison_path.exists():
            st.image(str(comparison_path), width="stretch")
        elif not metrics.empty and "f1_score" in metrics:
            st.bar_chart(metrics.dropna(subset=["f1_score"]).set_index("model")["f1_score"])

    importance_path = Path("reports/figures/feature_importance.png")
    if importance_path.exists():
        st.image(str(importance_path), width="stretch")

with tabs[4]:
    records_left, records_right = st.columns([1.1, 1.0])
    with records_left:
        st.markdown("<div class='ct-section-label'>Source records</div>", unsafe_allow_html=True)
        st.dataframe(subject_frame.head(500), width="stretch", height=330)

        st.markdown("<div class='ct-section-label'>Project assets</div>", unsafe_allow_html=True)
        st.dataframe(_artifact_table(), hide_index=True, width="stretch")

    with records_right:
        st.markdown("<div class='ct-section-label'>Experiment report</div>", unsafe_allow_html=True)
        report_path = Path("reports/generated_reports/experiment_summary.md")
        fallback_report = Path("reports/experiment_report.md")
        active_report = report_path if report_path.exists() else fallback_report
        if active_report.exists():
            report_text = active_report.read_text(encoding="utf-8")
            st.markdown(report_text)
            st.download_button(
                "Download report",
                report_text,
                file_name="cardiotwin_experiment_summary.md",
                mime="text/markdown",
            )
        else:
            st.info("Experiment report is not available.")

        manifest_path = Path("reports/submission_manifest.json")
        if manifest_path.exists():
            manifest_text = manifest_path.read_text(encoding="utf-8")
            st.download_button(
                "Download submission manifest",
                manifest_text,
                file_name="submission_manifest.json",
                mime="application/json",
            )
