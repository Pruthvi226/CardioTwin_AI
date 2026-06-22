# Databricks Workflow Summary

CardioTwin AI Databricks follows a simple Bronze, Silver, Gold style Lakehouse workflow.

## 1. Bronze: Raw PPG Data

- Notebook: `01_data_ingestion.ipynb`
- Input: `data/sample_ppg_data.csv`
- Delta table: `cardio_ppg_raw`
- Purpose: Preserve raw signal windows with schema validation and missing-value checks.

## 2. Silver: Clean PPG Windows

- Notebook: `02_ppg_preprocessing.ipynb`
- Delta table: `cardio_ppg_clean`
- Purpose: Impute missing samples, smooth signals, normalize windows, and remove unusable windows.

## 3. Gold: Features and Quality Scores

- Notebooks: `03_feature_engineering.ipynb`, `04_signal_quality_scoring.ipynb`
- Delta tables: `cardio_ppg_features`, `cardio_signal_quality`
- Purpose: Create ML-ready window-level features and a 0-1 signal quality score.

## 4. MLflow Experiments

- Notebook: `05_classification_mlflow.ipynb`
- Notebook: `06_bp_regression_mlflow.ipynb`
- Optional notebook: `07_cnn_lstm_experiment.ipynb`
- Purpose: Track model parameters, metrics, artifacts, and saved models.

## 5. Model Comparison

- Notebook: `08_model_comparison_report.ipynb`
- Output: `reports/model_metrics_summary.md`
- Purpose: Compare MLflow runs and summarize the selected best models.
