# CardioTwin AI Databricks Lakehouse

CardioTwin AI Databricks Lakehouse is an educational healthcare AI project that demonstrates how PPG signal data can be processed with PySpark, stored in Delta Lake, and used for MLflow-tracked cardiovascular status classification and blood pressure regression.

This project is designed for Databricks Free Edition and a B.Tech CSE student portfolio.

## Healthcare Disclaimer

This project is for educational and research purposes only and is not intended for medical diagnosis or clinical use.

## Problem Statement

Photoplethysmography, or PPG, is a low-cost optical signal used in wearable devices to capture pulse-related changes in blood volume. This project builds a Databricks Lakehouse workflow that:

- Ingests PPG signal windows from CSV.
- Cleans and normalizes noisy time-series windows.
- Extracts signal features such as amplitude, peak count, approximate heart rate, energy, and BP proxy features.
- Scores signal quality from 0 to 1.
- Trains classification models for cardiovascular status prediction.
- Trains regression models for systolic and diastolic blood pressure prediction.
- Tracks experiments, metrics, and artifacts using MLflow.

## Folder Structure

```text
CardioTwin_AI_Databricks/
|-- notebooks/
|   |-- 01_data_ingestion.ipynb
|   |-- 02_ppg_preprocessing.ipynb
|   |-- 03_feature_engineering.ipynb
|   |-- 04_signal_quality_scoring.ipynb
|   |-- 05_classification_mlflow.ipynb
|   |-- 06_bp_regression_mlflow.ipynb
|   |-- 07_cnn_lstm_experiment.ipynb
|   `-- 08_model_comparison_report.ipynb
|-- data/
|   |-- sample_ppg_data.csv
|   `-- README.md
|-- src/
|   |-- preprocessing.py
|   |-- feature_engineering.py
|   |-- signal_quality.py
|   |-- train_classification.py
|   |-- train_regression.py
|   `-- utils.py
|-- reports/
|   |-- model_metrics_summary.md
|   `-- databricks_workflow_summary.md
|-- requirements.txt
`-- README.md
```

## Lakehouse Architecture

```text
CSV PPG Data
    |
    v
Bronze Delta Table
cardio_ppg_raw
    |
    v
Silver Delta Table
cardio_ppg_clean
    |
    +--------------------+
    |                    |
    v                    v
Gold Feature Table       Signal Quality Table
cardio_ppg_features      cardio_signal_quality
    |                    |
    +---------+----------+
              |
              v
MLflow Experiments
classification, BP regression, optional CNN-LSTM
              |
              v
Model Comparison Report
reports/model_metrics_summary.md
```

## Delta Lake Tables

| Table | Created By | Purpose |
|---|---|---|
| `cardio_ppg_raw` | `01_data_ingestion.ipynb` | Raw PPG rows loaded from CSV with schema |
| `cardio_ppg_clean` | `02_ppg_preprocessing.ipynb` | Cleaned, smoothed, normalized PPG windows |
| `cardio_ppg_features` | `03_feature_engineering.ipynb` | Window-level ML features |
| `cardio_signal_quality` | `04_signal_quality_scoring.ipynb` | Rule-based signal quality scores |

## Models Trained

Classification models:

- Logistic Regression
- Random Forest Classifier
- Gradient Boosting Classifier

Blood pressure regression models:

- Linear Regression
- Random Forest Regressor
- Gradient Boosting Regressor

Optional deep learning experiment:

- CNN-LSTM model using normalized PPG windows

## Metrics Tracked

Classification:

- Accuracy
- Weighted precision
- Weighted recall
- Weighted F1 score
- Confusion matrix artifact
- Feature importance artifact for tree-based models

Regression:

- MAE
- RMSE
- R2 score
- Systolic MAE
- Diastolic MAE
- Prediction plot artifact

Signal quality:

- Missing score
- Variance score
- Peak consistency score
- Noise score
- Amplitude stability score
- Final signal quality score

## How To Run On Databricks Free Edition

1. Create or open a Databricks Free Edition workspace.
2. Upload or clone this folder into your Databricks Workspace.
3. Create a notebook environment or serverless compute.
4. Install dependencies from `requirements.txt` if they are not already available:

```python
%pip install -r ../requirements.txt
dbutils.library.restartPython()
```

5. Open `notebooks/01_data_ingestion.ipynb`.
6. Set the `input_csv_path` widget to the location of `sample_ppg_data.csv`.

Example Workspace file path:

```text
file:/Workspace/Users/<your-email>/CardioTwin_AI_Databricks/data/sample_ppg_data.csv
```

7. Run notebooks in order:

```text
01_data_ingestion
02_ppg_preprocessing
03_feature_engineering
04_signal_quality_scoring
05_classification_mlflow
06_bp_regression_mlflow
07_cnn_lstm_experiment
08_model_comparison_report
```

8. Open MLflow Experiments in Databricks to inspect metrics, artifacts, and saved models.
9. Review `reports/model_metrics_summary.md` after running notebook 08.

If `/Shared/...` MLflow experiment paths are not writable in your workspace, change the experiment widgets to:

```text
/Users/<your-email>/CardioTwin_AI_Classification
/Users/<your-email>/CardioTwin_AI_BP_Regression
/Users/<your-email>/CardioTwin_AI_CNN_LSTM
```

## Notebook Guide

- `01_data_ingestion.ipynb`: Loads CSV data, applies a Spark schema, writes `cardio_ppg_raw`, and checks missing values.
- `02_ppg_preprocessing.ipynb`: Parses PPG samples, imputes missing points, smooths, normalizes, removes noisy windows, and writes `cardio_ppg_clean`.
- `03_feature_engineering.ipynb`: Extracts mean, standard deviation, min, max, peak count, approximate heart rate, energy, and BP proxy features.
- `04_signal_quality_scoring.ipynb`: Computes a rule-based signal quality score between 0 and 1.
- `05_classification_mlflow.ipynb`: Trains cardiovascular status classifiers and logs MLflow metrics/artifacts.
- `06_bp_regression_mlflow.ipynb`: Trains systolic and diastolic BP regressors and logs MLflow metrics/artifacts.
- `07_cnn_lstm_experiment.ipynb`: Optional TensorFlow CNN-LSTM experiment for raw time-series windows.
- `08_model_comparison_report.ipynb`: Reads MLflow results, selects best models, and writes the final Markdown summary.

## Resume Bullets

- Built a Databricks Lakehouse pipeline for healthcare PPG time-series analysis using PySpark and Delta Lake tables for raw ingestion, cleaned signals, engineered features, and signal quality scores.
- Trained and compared cardiovascular classification and blood pressure regression models with MLflow experiment tracking, logging accuracy, precision, recall, F1, MAE, RMSE, R2, confusion matrices, and prediction artifacts.
- Developed an end-to-end educational Healthcare AI workflow combining PPG preprocessing, signal quality scoring, feature engineering, and optional CNN-LSTM deep learning experiments on Databricks Free Edition.

## Future Improvements

- Replace the synthetic sample data with a real public PPG dataset.
- Add patient-level train/test splitting to avoid leakage across windows.
- Add hyperparameter tuning with Spark MLlib or Optuna.
- Add model registry promotion stages for dev, staging, and production.
- Add explainability using SHAP for tabular models.
- Build a Databricks workflow job to run all notebooks automatically.
- Add dashboard visualizations for signal quality and model performance.

## Notes

The included data is synthetic and intentionally small. It is suitable for validating the workflow and demonstrating engineering skills, but it is not suitable for medical conclusions.
