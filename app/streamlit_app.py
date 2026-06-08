"""Streamlit dashboard for CardioTwin AI."""

from __future__ import annotations

import sys
from pathlib import Path

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
from src.preprocessing.clean_signal import preprocess_ppg
from src.preprocessing.segment_windows import create_windows
from src.utils.common import DISCLAIMER, assess_prediction_risk


st.set_page_config(page_title="CardioTwin AI", layout="wide")


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


def _predict(features: pd.DataFrame) -> tuple[int, float]:
    model_path = Path("models/RandomForest_features.joblib")
    if model_path.exists():
        model = joblib.load(model_path)
        excluded = {"stress_label", "quality_label", "subject_id", "sbp", "dbp", "heart_rate", "activity"}
        row = features.drop(columns=[column for column in features.columns if column in excluded], errors="ignore")
        row = row.select_dtypes(include=["number"]).drop(columns=["window_id"], errors="ignore").head(1)
        try:
            probabilities = model.predict_proba(row)[0]
            return int(np.argmax(probabilities)), float(np.max(probabilities))
        except ValueError:
            pass
    score = float(features["mdi_score"].iloc[0])
    return int(score >= 0.5), max(score, 1.0 - score)


with st.sidebar:
    st.header("Workflow")
    st.write("Step 1: Upload signal")
    st.write("Step 2: Clean signal")
    st.write("Step 3: Extract features")
    st.write("Step 4: Predict")
    st.write("Step 5: Explain")
    st.write("Step 6: Generate report")
    st.divider()
    uploaded = st.file_uploader("Upload PPG CSV", type=["csv"])
    model_choice = st.selectbox("Model", ["RandomForest features", "CNN-LSTM", "SSL embeddings", "Spectrogram CNN"])
    threshold = st.slider("Confidence threshold", min_value=0.1, max_value=0.95, value=0.5, step=0.05)
    run_prediction = st.button("Run prediction", type="primary")

st.title("CardioTwin AI")
st.caption("Self-supervised PPG intelligence platform for predictive health signal analytics")
st.warning(DISCLAIMER)

metrics = _load_metrics()
best_f1 = metrics["weighted_f1"].dropna().max() if "weighted_f1" in metrics else metrics.get("f1_score", pd.Series(dtype=float)).dropna().max()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Best weighted F1", "N/A" if pd.isna(best_f1) else f"{best_f1:.3f}")
col2.metric("Models compared", len(metrics))
col3.metric("Threshold", f"{threshold:.2f}")
col4.metric("Dataset mode", "Synthetic demo")

raw_frame = pd.read_csv(uploaded) if uploaded is not None else _load_default_signal()
if raw_frame.empty:
    st.info("Run `python scripts/run_full_pipeline.py --dataset synthetic --stage all --config config.yaml` to generate demo data and models.")
    st.stop()

subject = st.selectbox("Subject", sorted(raw_frame["subject_id"].astype(str).unique()))
subject_frame = raw_frame[raw_frame["subject_id"].astype(str) == subject].copy()
fs = float(subject_frame["fs"].iloc[0])
cleaned = preprocess_ppg(subject_frame["ppg"].to_numpy(), fs_original=fs, fs_target=64.0)
windows = create_windows(cleaned, window_size=512, overlap=0.5)
if len(windows) == 0:
    st.warning("The selected signal is too short for an 8-second window.")
    st.stop()

labels = pd.DataFrame({"stress_label": [0] * len(windows), "quality_label": [1] * len(windows)})
features = extract_features(windows[:1], labels.head(1), fs=64.0)
prediction, confidence = _predict(features)
quality = assess_signal_quality(windows[0], fs=64.0)
risk = assess_prediction_risk(
    prediction="stress_like_pattern" if prediction else "baseline_like_pattern",
    confidence=confidence,
    signal_quality=float(quality["signal_quality_score"]),
    explanation=[str(quality["artifact_warning"])],
)

tabs = st.tabs(
    [
        "Home",
        "Upload PPG Signal",
        "Signal Preprocessing Lab",
        "Feature Engineering Explorer",
        "AI Prediction",
        "Spectrogram CV View",
        "Explainability",
        "Model Comparison",
        "Experiment Report Generator",
        "Recruiter Demo Mode",
    ]
)

with tabs[0]:
    st.subheader("Project Overview")
    st.write("CardioTwin AI is a product-style AI engineering workflow for PPG signal analytics. It combines preprocessing, feature engineering, predictive modeling, computer vision-style spectrograms, explainability, API serving, and automated reporting.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Signal quality", f"{quality['signal_quality_score']:.3f}")
    c2.metric("Uncertainty", risk["uncertainty"])
    c3.metric("Risk flag", risk["risk_flag"])
    if Path("assets/architecture.png").exists():
        st.image("assets/architecture.png", caption="System architecture placeholder", use_container_width=True)

with tabs[1]:
    st.subheader("Upload or sample signal")
    st.write("Use the sidebar uploader or inspect the generated synthetic sample below.")
    st.dataframe(subject_frame.head(25), use_container_width=True)

with tabs[2]:
    left, right = st.columns(2)
    with left:
        st.subheader("Raw signal")
        st.line_chart(subject_frame.set_index("time")["ppg"])
    with right:
        st.subheader("Cleaned signal window")
        st.line_chart(pd.DataFrame({"cleaned_ppg": windows[0]}))
    st.metric("Signal quality score", f"{quality['signal_quality_score']:.3f}")
    st.write("Artifact warning:", quality["artifact_warning"])

with tabs[3]:
    st.subheader("Feature table")
    st.dataframe(features.T.rename(columns={0: "value"}), use_container_width=True)

with tabs[4]:
    st.subheader("Prediction")
    st.metric("Predicted class", risk["prediction"])
    st.metric("Confidence", f"{risk['confidence']:.3f}")
    st.metric("Uncertainty", risk["uncertainty"])
    st.metric("Risk flag", risk["risk_flag"])
    st.progress(min(confidence, 1.0))
    if confidence < threshold:
        st.warning("Confidence is below the selected review threshold.")
    st.bar_chart(pd.DataFrame({"score": [1.0 - confidence, confidence]}, index=["alternative", "predicted"]))

with tabs[5]:
    image = window_to_spectrogram(windows[0], fs=64.0, image_size=128)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.imshow(image, aspect="auto", origin="lower", cmap="magma")
    ax.set_xlabel("Time bins")
    ax.set_ylabel("Frequency bins")
    ax.set_title(f"Spectrogram branch input: {model_choice}")
    st.pyplot(fig)

with tabs[6]:
    st.subheader("Why did the model predict this?")
    top_features = features[["mdi_score", "heart_rate_proxy", "spectral_entropy", "signal_quality_score"]].T.rename(columns={0: "value"})
    st.dataframe(top_features, use_container_width=True)
    saliency = signal_saliency(windows[0])
    st.line_chart(saliency.set_index("sample")["saliency"])
    st.write("Explanation:", ", ".join(risk["explanation"]))
    st.warning(DISCLAIMER)

with tabs[7]:
    st.subheader("Model Comparison")
    comparison_path = Path("results/plots/model_comparison.png")
    if comparison_path.exists():
        st.image(str(comparison_path), use_container_width=True)
    if not metrics.empty:
        st.dataframe(metrics, use_container_width=True)

with tabs[8]:
    report_path = Path("reports/generated_reports/experiment_summary.md")
    fallback_report = Path("reports/experiment_report.md")
    active_report = report_path if report_path.exists() else fallback_report
    if active_report.exists():
        report_text = active_report.read_text(encoding="utf-8")
        st.markdown(report_text)
        st.download_button("Download report", report_text, file_name="cardiotwin_experiment_summary.md")
    else:
        st.info("Run the evaluate stage to generate the NLP experiment report.")

with tabs[9]:
    st.subheader("Problem")
    st.write("Wearable PPG signals are noisy, subject-dependent, and hard to convert into reliable AI features.")
    st.subheader("Solution")
    st.write("CardioTwin AI cleans raw PPG, extracts morphology/frequency biomarkers, trains classical and deep models, adds a spectrogram CV branch, explains uncertainty, and generates reports.")
    st.subheader("Tech Stack")
    st.write("Python, NumPy, SciPy, Pandas, Scikit-learn, PyTorch, Streamlit, FastAPI, Matplotlib.")
    st.subheader("Limitations")
    st.write("Synthetic demo data validates the pipeline only. Real-world claims require governed datasets, subject-wise validation, and clinical review.")
    st.warning(DISCLAIMER)
