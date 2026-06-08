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
from src.features.mdi_features import build_feature_table
from src.features.spectrogram_builder import window_to_spectrogram
from src.preprocessing.clean_signal import preprocess_ppg
from src.preprocessing.segment_windows import create_windows


st.set_page_config(page_title="CardioTwin AI", layout="wide")


@st.cache_data
def _load_metrics() -> pd.DataFrame:
    path = Path("results/metrics.csv")
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=["model", "accuracy", "f1_score", "mae", "rmse"])


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
        probabilities = model.predict_proba(row)[0]
        return int(np.argmax(probabilities)), float(np.max(probabilities))
    score = float(features["mdi_score"].iloc[0])
    return int(score >= 0.5), max(score, 1.0 - score)


with st.sidebar:
    st.header("Controls")
    uploaded = st.file_uploader("Upload PPG CSV", type=["csv"])
    model_choice = st.selectbox("Model", ["RandomForest features", "CNN-LSTM", "SSL embeddings", "Spectrogram CNN"])
    threshold = st.slider("Confidence threshold", min_value=0.1, max_value=0.95, value=0.5, step=0.05)
    run_prediction = st.button("Run prediction", type="primary")

st.title("CardioTwin AI")
st.caption("Self-supervised PPG intelligence and predictive health analytics platform")

metrics = _load_metrics()
col1, col2, col3, col4 = st.columns(4)
best_f1 = metrics["f1_score"].dropna().max() if "f1_score" in metrics else np.nan
col1.metric("Best weighted F1", "N/A" if pd.isna(best_f1) else f"{best_f1:.3f}")
col2.metric("Models compared", len(metrics))
col3.metric("Latest threshold", f"{threshold:.2f}")
col4.metric("Demo mode", "Synthetic")

if uploaded is not None:
    raw_frame = pd.read_csv(uploaded)
else:
    raw_frame = _load_default_signal()

if raw_frame.empty:
    st.info("Run `python scripts/run_full_pipeline.py --stage all --config config.yaml` to generate demo data and models.")
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
features = build_feature_table(windows[:1], labels.head(1), fs=64.0)
prediction, confidence = _predict(features)

tab_signal, tab_prediction, tab_cv, tab_report, tab_recruiter = st.tabs(
    ["Signal Lab", "AI Prediction", "CV View", "Experiment Report", "Recruiter Demo"]
)

with tab_signal:
    left, right = st.columns(2)
    with left:
        st.subheader("Raw signal")
        st.line_chart(subject_frame.set_index("time")["ppg"])
    with right:
        st.subheader("Cleaned window")
        st.line_chart(pd.DataFrame({"cleaned_ppg": windows[0]}))
    st.dataframe(features.T.rename(columns={0: "value"}), use_container_width=True)

with tab_prediction:
    status = "Stress-like" if prediction else "Baseline-like"
    st.metric("Predicted class", status)
    st.metric("Confidence", f"{confidence:.3f}")
    st.progress(min(confidence, 1.0))
    if confidence < threshold:
        st.warning("Confidence is below the selected review threshold.")
    st.bar_chart(pd.DataFrame({"score": [1.0 - confidence, confidence]}, index=["alternative", "predicted"]))

with tab_cv:
    image = window_to_spectrogram(windows[0], fs=64.0, image_size=128)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.imshow(image, aspect="auto", origin="lower", cmap="magma")
    ax.set_xlabel("Time bins")
    ax.set_ylabel("Frequency bins")
    ax.set_title(f"Spectrogram branch input: {model_choice}")
    st.pyplot(fig)

with tab_report:
    report_path = Path("reports/experiment_report.md")
    if report_path.exists():
        st.markdown(report_path.read_text(encoding="utf-8"))
    else:
        st.info("Run the evaluate stage to generate the NLP experiment report.")
    if not metrics.empty:
        st.dataframe(metrics, use_container_width=True)

with tab_recruiter:
    st.subheader("Problem")
    st.write("Wearable PPG signals are noisy, subject-dependent, and hard to convert into reliable AI features.")
    st.subheader("Solution")
    st.write("CardioTwin AI cleans raw PPG, extracts MDI/morphology biomarkers, trains classical and deep models, adds a spectrogram CV branch, and generates experiment reports.")
    st.subheader("Tech Stack")
    st.write("Python, NumPy, SciPy, Pandas, Scikit-learn, PyTorch, Streamlit, FastAPI, Matplotlib.")
    st.subheader("Limitations")
    st.write("Synthetic demo data validates the pipeline only. Real clinical claims require governed datasets, subject-wise validation, and clinical review.")
