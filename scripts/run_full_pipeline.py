"""One-command CardioTwin AI demo pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from scripts.generate_demo_data import generate_demo_frame
from src.config import ensure_project_dirs, load_config
from src.data.data_validation import validate_processed_windows, validate_raw_demo_frame
from src.data.dataset_loader import load_demo_csv, load_processed_npz, save_processed_npz
from src.evaluation.evaluate import (
    classification_metrics,
    plot_confusion_matrix,
    plot_feature_importance,
    plot_model_comparison,
    regression_metrics,
    save_metrics,
)
from src.evaluation.explainability import feature_importance_table
from src.evaluation.model_card import generate_model_card
from src.experiments.tracker import log_experiment
from src.features.extract_features import extract_features
from src.features.spectrogram import save_spectrogram_arrays
from src.features.spectrogram_builder import build_spectrogram_tensor, save_spectrogram_preview
from src.models.classical_models import feature_columns, train_bp_regressor, train_classical_models
from src.nlp.report_generator import generate_report
from src.preprocessing.segment_windows import window_dataframe
from src.training.finetune_predictive import (
    predict_torch_classifier,
    train_cnn_lstm_classifier,
    train_ssl_embedding_classifier,
)
from src.training.train_cv_branch import train_spectrogram_cnn
from src.training.train_ssl import train_ssl_autoencoder


def _paths(config: dict) -> dict[str, Path]:
    raw_path = Path(config["paths"].get("raw_data", "data/raw"))
    processed_path = Path(config["paths"].get("processed_data", "data/processed"))
    results_path = Path(config["paths"].get("results", "results"))
    reports_path = Path(config["paths"].get("reports", "reports"))
    models_path = Path(config["paths"].get("models", "models"))
    return {
        "raw_csv": raw_path / "demo_ppg.csv",
        "real_csv": raw_path / "real_ppg.csv",
        "processed_npz": processed_path / "demo_windows.npz",
        "features_csv": processed_path / "mdi_features.csv",
        "results": results_path,
        "reports": reports_path,
        "models": models_path,
    }


def generate_data(config: dict) -> Path:
    paths = _paths(config)
    demo = config.get("demo", {})
    frame = generate_demo_frame(
        samples=int(demo.get("samples", 3000)),
        fs=float(config["preprocessing"].get("target_fs", 64.0)),
        subjects=int(demo.get("subjects", 8)),
        seed=int(demo.get("seed", 42)),
    )
    paths["raw_csv"].parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(paths["raw_csv"], index=False)
    return paths["raw_csv"]


def _raw_path_for_dataset(config: dict, dataset: str) -> Path:
    paths = _paths(config)
    if dataset == "synthetic":
        return paths["raw_csv"]
    if dataset == "real":
        return paths["real_csv"]
    raise ValueError("dataset must be 'synthetic' or 'real'")


def preprocess(config: dict, dataset: str = "synthetic") -> tuple[np.ndarray, pd.DataFrame, pd.DataFrame]:
    paths = _paths(config)
    raw_path = _raw_path_for_dataset(config, dataset)
    if dataset == "synthetic" and not raw_path.exists():
        generate_data(config)
    if dataset == "real" and not raw_path.exists():
        raise FileNotFoundError(
            "Real dataset mode expects data/raw/real_ppg.csv with subject_id,time,ppg,fs,stress_label,quality_label,sbp,dbp columns. "
            "Download WESAD or another suitable wearable PPG dataset manually and convert it to this schema."
        )

    frame = load_demo_csv(raw_path)
    issues = validate_raw_demo_frame(frame)
    if issues:
        raise ValueError("Raw data validation failed: " + "; ".join(issues))

    preprocessing = config.get("preprocessing", {})
    fs_target = float(preprocessing.get("target_fs", 64.0))
    windowed = window_dataframe(
        frame,
        fs_target=fs_target,
        window_seconds=float(preprocessing.get("window_seconds", 8.0)),
        overlap=float(preprocessing.get("overlap", 0.5)),
    )
    processed_issues = validate_processed_windows(windowed.windows, windowed.labels)
    if processed_issues:
        raise ValueError("Processed data validation failed: " + "; ".join(processed_issues))

    save_processed_npz(paths["processed_npz"], windowed.windows, windowed.labels)
    features = extract_features(windowed.windows, windowed.labels, fs=fs_target)
    paths["features_csv"].parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(paths["features_csv"], index=False)

    preview_dir = paths["results"] / "plots"
    preview_dir.mkdir(parents=True, exist_ok=True)
    save_spectrogram_preview(windowed.windows[0], preview_dir / "spectrogram_preview.png", fs=fs_target)
    save_spectrogram_arrays(windowed.windows[: min(64, len(windowed.windows))], fs=fs_target)
    plt.figure(figsize=(8, 3))
    plt.plot(windowed.windows[0], color="#0f766e", linewidth=1.2)
    plt.title("Cleaned PPG Window")
    plt.xlabel("Sample")
    plt.ylabel("Normalized amplitude")
    plt.tight_layout()
    plt.savefig(preview_dir / "cleaned_signal_preview.png", dpi=160)
    plt.close()

    return windowed.windows, windowed.labels, features


def subject_wise_indices(labels: pd.DataFrame, train_ratio: float = 0.60, val_ratio: float = 0.20) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, list[str]]]:
    """Split by subject to reduce biosignal leakage."""
    rng = np.random.default_rng(42)
    subjects = np.array(sorted(labels["subject_id"].astype(str).unique()))
    rng.shuffle(subjects)
    if len(subjects) < 3:
        indices = np.arange(len(labels))
        train_idx, test_idx = train_test_split(indices, test_size=0.25, random_state=42)
        return train_idx, np.array([], dtype=int), test_idx, {"train": [], "val": [], "test": []}

    n_train = max(1, int(round(len(subjects) * train_ratio)))
    n_val = max(1, int(round(len(subjects) * val_ratio)))
    train_subjects = subjects[:n_train]
    val_subjects = subjects[n_train : n_train + n_val]
    test_subjects = subjects[n_train + n_val :]
    if len(test_subjects) == 0:
        test_subjects = val_subjects[-1:]
        val_subjects = val_subjects[:-1]

    subject_series = labels["subject_id"].astype(str)
    train_idx = labels.index[subject_series.isin(train_subjects)].to_numpy()
    val_idx = labels.index[subject_series.isin(val_subjects)].to_numpy()
    test_idx = labels.index[subject_series.isin(test_subjects)].to_numpy()
    return train_idx, val_idx, test_idx, {
        "train": train_subjects.tolist(),
        "val": val_subjects.tolist(),
        "test": test_subjects.tolist(),
    }


def train_all(config: dict, dataset: str = "synthetic") -> pd.DataFrame:
    paths = _paths(config)
    if not paths["processed_npz"].exists() or not paths["features_csv"].exists():
        windows, labels, features = preprocess(config, dataset=dataset)
    else:
        windows, labels = load_processed_npz(paths["processed_npz"])
        features = pd.read_csv(paths["features_csv"])

    selected_columns = feature_columns(features)
    x_features = features[selected_columns].fillna(0)
    y_stress = features["stress_label"].astype(int).to_numpy()
    y_quality = features["quality_label"].astype(int).to_numpy()
    y_bp = features[["sbp", "dbp"]].to_numpy()

    train_idx, val_idx, test_idx, split_subjects = subject_wise_indices(labels)

    metrics: list[dict[str, float | str]] = []
    x_train = x_features.iloc[train_idx]
    x_test = x_features.iloc[test_idx]
    classical = train_classical_models(x_train, y_stress[train_idx], paths["models"])
    for name, model in classical.items():
        predictions = model.predict(x_test)
        metrics.append(classification_metrics(name, y_stress[test_idx], predictions))

    bp_model = train_bp_regressor(x_train, y_bp[train_idx], paths["models"])
    bp_predictions = bp_model.predict(x_test)
    metrics.append(regression_metrics("RandomForest_BP_regression", y_bp[test_idx], bp_predictions))

    importance = feature_importance_table(classical["RandomForest_features"], selected_columns)
    importance.to_csv(paths["results"] / "feature_importance.csv", index=False)
    plot_feature_importance(importance, paths["reports"] / "figures" / "feature_importance.png")

    training = config.get("training", {})
    device = str(training.get("device", "cpu"))
    epochs = int(training.get("demo_epochs", 3))
    batch_size = int(training.get("batch_size", 64))
    learning_rate = float(training.get("learning_rate", 0.001))

    cnn_model = train_cnn_lstm_classifier(
        windows[train_idx],
        y_stress[train_idx],
        paths["models"],
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        device=device,
    )
    cnn_pred, _ = predict_torch_classifier(cnn_model, windows[test_idx])
    metrics.append(classification_metrics("CNNLSTM_raw_windows", y_stress[test_idx], cnn_pred))

    ssl_model, ssl_losses = train_ssl_autoencoder(
        windows[train_idx],
        paths["models"],
        epochs=max(1, int(training.get("ssl_epochs", 2))),
        batch_size=batch_size,
        learning_rate=learning_rate,
        device=device,
    )
    ssl_classifier, ssl_pred, _ = train_ssl_embedding_classifier(
        ssl_model,
        windows[train_idx],
        y_stress[train_idx],
        windows[test_idx],
    )
    joblib.dump(ssl_classifier, paths["models"] / "SSL_embedding_logistic.joblib")
    metrics.append(classification_metrics("SSL_encoder_finetuned", y_stress[test_idx], ssl_pred))

    spectrograms = build_spectrogram_tensor(
        windows,
        fs=float(config.get("preprocessing", {}).get("target_fs", 64.0)),
        image_size=int(config.get("cv_branch", {}).get("image_size", 64)),
    )
    cv_model = train_spectrogram_cnn(
        spectrograms[train_idx],
        y_stress[train_idx],
        paths["models"],
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        device=device,
    )
    cv_pred, _ = predict_torch_classifier(cv_model, spectrograms[test_idx])
    metrics.append(classification_metrics("SpectrogramCNN_stress", y_stress[test_idx], cv_pred))

    metrics_frame = save_metrics(metrics, paths["results"] / "metrics.csv")
    (paths["reports"] / "metrics").mkdir(parents=True, exist_ok=True)
    metrics_frame.dropna(subset=["f1_score"]).to_json(paths["reports"] / "metrics" / "classification_metrics.json", orient="records", indent=2)
    metrics_frame.dropna(subset=["mae"]).to_json(paths["reports"] / "metrics" / "regression_metrics.json", orient="records", indent=2)
    plot_model_comparison(metrics_frame, paths["results"] / "plots" / "model_comparison.png")
    plot_model_comparison(metrics_frame, paths["reports"] / "figures" / "model_comparison.png")
    plot_confusion_matrix(
        y_stress[test_idx],
        cnn_pred,
        paths["results"] / "plots" / "cnn_lstm_confusion_matrix.png",
        "CNN-LSTM Stress Classification",
    )
    plot_confusion_matrix(
        y_stress[test_idx],
        cnn_pred,
        paths["reports"] / "figures" / "confusion_matrix.png",
        "CNN-LSTM Stress Classification",
    )

    run_summary = {
        "windows": int(len(windows)),
        "dataset_mode": dataset,
        "split_strategy": "subject_wise",
        "split_subjects": split_subjects,
        "features": selected_columns,
        "ssl_losses": ssl_losses,
        "bp_mae": float(mean_absolute_error(y_bp[test_idx], bp_predictions)),
        "synthetic_warning": "Synthetic demo results verify the pipeline only. Real-world performance requires subject-wise evaluation on real wearable datasets.",
    }
    (paths["results"] / "run_summary.json").write_text(json.dumps(run_summary, indent=2), encoding="utf-8")
    log_experiment(
        {
            "dataset_name": "demo_ppg" if dataset == "synthetic" else "real_ppg",
            "dataset_mode": dataset,
            "model_name": "pipeline_all",
            "weighted_f1": float(metrics_frame["weighted_f1"].dropna().max()),
            "mae": float(metrics_frame["mae"].dropna().min()) if metrics_frame["mae"].notna().any() else np.nan,
            "model_artifact_path": str(paths["models"]),
            "confusion_matrix_path": str(paths["reports"] / "figures" / "confusion_matrix.png"),
        }
    )
    return metrics_frame


def evaluate(config: dict, dataset: str = "synthetic") -> None:
    paths = _paths(config)
    metrics_path = paths["results"] / "metrics.csv"
    if not metrics_path.exists():
        metrics = train_all(config, dataset=dataset)
    else:
        metrics = pd.read_csv(metrics_path)
    generate_report(metrics_path, paths["reports"] / "experiment_report.md", dataset=dataset)
    generate_report(metrics_path, paths["reports"] / "generated_reports" / "experiment_summary.md", dataset=dataset)
    generate_model_card(metrics, paths["reports"] / "model_card.md")


def run_stage(stage: str, config: dict, dataset: str = "synthetic") -> None:
    ensure_project_dirs(config)
    if stage == "generate_data":
        output = generate_data(config)
        print(f"Generated demo data: {output}")
    elif stage == "preprocess":
        windows, _, features = preprocess(config, dataset=dataset)
        print(f"Preprocessed {len(windows)} windows and wrote {len(features)} feature rows.")
    elif stage == "train_all":
        metrics = train_all(config, dataset=dataset)
        print(metrics.to_string(index=False))
    elif stage == "evaluate":
        evaluate(config, dataset=dataset)
        print("Generated reports/experiment_report.md and reports/model_card.md")
    elif stage == "all":
        if dataset == "synthetic":
            generate_data(config)
        preprocess(config, dataset=dataset)
        metrics = train_all(config, dataset=dataset)
        evaluate(config, dataset=dataset)
        print(metrics.to_string(index=False))
    else:
        raise ValueError(f"Unknown stage: {stage}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CardioTwin AI demo pipeline.")
    parser.add_argument("--stage", default="all", choices=["generate_data", "preprocess", "train_all", "evaluate", "all"])
    parser.add_argument("--dataset", default="synthetic", choices=["synthetic", "real"])
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    config = load_config(args.config)
    run_stage(args.stage, config, dataset=args.dataset)


if __name__ == "__main__":
    main()
