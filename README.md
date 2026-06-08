# CardioTwin AI

Self-supervised PPG intelligence platform for predictive health signal analytics.

[![Python CI](https://github.com/Pruthvi226/CardioTwin_AI/actions/workflows/python-ci.yml/badge.svg)](https://github.com/Pruthvi226/CardioTwin_AI/actions/workflows/python-ci.yml)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-ee4c2c)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-ff4b4b)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed)

CardioTwin AI is an end-to-end AI engineering project for wearable PPG signal analytics. It cleans raw signal input, extracts statistical, morphology, frequency-domain, and signal-quality features, builds spectrogram images for a Computer Vision branch, trains multiple ML/deep-learning models, adds explainability and uncertainty flags, serves predictions through FastAPI, and presents the workflow in a polished Streamlit dashboard.

**Research demo only. Not for clinical diagnosis or medical decision-making.**

## Demo Screenshots

> Replace placeholder screenshots with real deployed dashboard screenshots before final submission.

| Dashboard | Signal Lab | Explainability |
| --- | --- | --- |
| ![Dashboard](assets/dashboard_home.png) | ![Signal Lab](assets/signal_lab.png) | ![Explainability](assets/explainability.png) |

| Model Comparison | API Docs | Architecture |
| --- | --- | --- |
| ![Model Comparison](assets/model_comparison.png) | ![API Docs](assets/api_docs.png) | ![Architecture](assets/architecture.png) |

## Why This Project

PPG signals are common in wearable devices, but they are noisy, subject-dependent, and difficult to use directly for AI modeling. This project demonstrates the complete AI workflow an internship recruiter expects: dataset preparation, preprocessing, feature engineering, model training, evaluation, visualization, reporting, API serving, and documentation.

## Internship JD Alignment

- Designing and training AI/ML models: Scikit-learn baselines, CNN-LSTM, Transformer-ready encoder, SSL encoder.
- Data preprocessing and feature engineering: filtering, resampling, windowing, signal quality, morphology, frequency features.
- Python AI libraries: PyTorch, Scikit-learn, Pandas, NumPy, SciPy.
- AI automation: one-command pipeline and automated NLP-style report generation.
- Evaluation and optimization: metrics, model comparison, confidence, uncertainty, risk flags.
- Visualizations and reports: Streamlit dashboard, plots, generated experiment report, model card.
- NLP, CV, Predictive Modeling: report generator, spectrogram CV branch, classification/regression-style tasks.

## Key Features

- Synthetic and real dataset modes.
- Subject-wise split support for biosignal leakage control.
- Missing-value handling, smoothing/filtering, normalization, window segmentation.
- Signal quality scoring with noise and artifact warnings.
- Handcrafted statistical, morphology, and frequency-domain features.
- Spectrogram generation under `data/processed/spectrograms/`.
- Classical ML, CNN-LSTM, Transformer-ready, and SSL model families.
- Confidence, uncertainty, and risk-flag prediction payloads.
- Explainability through feature attribution and signal saliency.
- FastAPI endpoints for inference and model metadata.
- Streamlit dashboard with 10 recruiter-ready workflow pages.
- Local CSV experiment tracking under `reports/metrics/experiment_runs.csv`.
- Docker and Docker Compose support.
- CI tests with GitHub Actions.

## System Architecture

```text
Raw PPG CSV
  -> preprocessing
  -> window segmentation
  -> signal quality assessment
  -> feature extraction
  -> spectrogram generation
  -> model training and evaluation
  -> explainability and uncertainty
  -> Streamlit dashboard / FastAPI API
  -> generated reports and model cards
```

See `docs/SYSTEM_ARCHITECTURE.md`.

## Tech Stack

Python, NumPy, SciPy, Pandas, Scikit-learn, PyTorch, Matplotlib, Streamlit, FastAPI, Uvicorn, Docker, GitHub Actions.

## Dataset Modes

### Synthetic Demo Mode

Used only to verify the full pipeline and run the demo without external datasets.

```bash
python scripts/run_full_pipeline.py --dataset synthetic --stage all
```

Synthetic demo results verify the pipeline only. Real-world performance requires subject-wise evaluation on real wearable datasets.

### Real Dataset Mode

Real mode expects a manually prepared CSV:

```text
data/raw/real_ppg.csv
```

Required columns:

```text
subject_id,time,ppg,fs,stress_label,quality_label,sbp,dbp,heart_rate,activity
```

Suggested public dataset: WESAD or another wearable/PPG-style dataset with proper usage rights. Convert it to the schema above, then run:

```bash
python scripts/run_full_pipeline.py --dataset real --stage all
```

## ML Pipeline

1. Generate or load dataset.
2. Validate columns and labels.
3. Clean missing values and outliers.
4. Apply PPG-band filtering and normalization.
5. Segment into 8-second windows.
6. Score signal quality and artifact risk.
7. Extract handcrafted features.
8. Generate spectrogram arrays/images.
9. Split subjects into train/validation/test.
10. Train and compare model families.
11. Save metrics, plots, reports, model card, and experiment tracker rows.

## Models Used

- Logistic Regression
- Random Forest
- Gradient Boosting
- SVM-ready classical baseline
- CNN-LSTM sequence model
- Transformer encoder classifier
- Self-supervised masked reconstruction encoder
- Spectrogram CNN branch

## Evaluation

Classification metrics:

- Accuracy
- Precision
- Recall
- F1-score
- Weighted F1
- Confusion matrix
- ROC-AUC when applicable

Regression/score metrics:

- MAE
- RMSE
- R2 score

Saved outputs:

- `reports/metrics/classification_metrics.json`
- `reports/metrics/regression_metrics.json`
- `reports/figures/confusion_matrix.png`
- `reports/figures/model_comparison.png`
- `reports/figures/feature_importance.png`

## Explainability

Explainability modules live in `src/explainability/`:

- Feature attribution for Scikit-learn models.
- SHAP-compatible fallback interface.
- Signal saliency from important time-region estimates.
- Dashboard page: "Why did the model predict this?"

## Dashboard

Run:

```bash
streamlit run app/streamlit_app.py
```

Dashboard pages:

1. Home / Project Overview
2. Upload PPG Signal
3. Signal Preprocessing Lab
4. Feature Engineering Explorer
5. AI Prediction
6. Spectrogram CV View
7. Explainability
8. Model Comparison
9. Experiment Report Generator
10. Recruiter Demo Mode

## API

Run:

```bash
uvicorn src.api.main:app --reload
```

Endpoints:

- `GET /`
- `GET /health`
- `POST /predict`
- `GET /model-info`
- `GET /sample-response`

Example response:

```json
{
  "project": "CardioTwin AI",
  "prediction": "stress_like_pattern",
  "confidence": 0.78,
  "uncertainty": "medium",
  "signal_quality": 0.62,
  "risk_flag": "acceptable_demo_prediction",
  "top_features": ["peak_interval_std", "spectral_entropy", "signal_energy"],
  "disclaimer": "Research demo only. Not for clinical diagnosis or medical decision-making."
}
```

## How To Run Locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_full_pipeline.py --dataset synthetic --stage all --config config.yaml
streamlit run app/streamlit_app.py
```

API:

```bash
uvicorn src.api.main:app --reload
```

Tests:

```bash
python -m unittest discover -s tests
```

## Docker Setup

```bash
docker compose up --build
```

Services:

- Dashboard: `http://localhost:8501`
- API: `http://localhost:8000`

## Project Structure

```text
app/                         Streamlit dashboard
src/data/                    synthetic/real loading, preprocessing, signal quality
src/features/                handcrafted features, frequency features, spectrograms
src/models/                  sklearn, CNN-LSTM, Transformer, SSL models
src/explainability/          feature attribution and signal saliency
src/experiments/             local experiment tracking
src/nlp/                     generated experiment summaries
src/api/                     FastAPI service
src/utils/                   config, logger, common safety helpers
scripts/                     pipeline, train, evaluate, report, assets
docs/                        report, architecture, cards, API docs, demo script
assets/                      screenshot placeholders
tests/                       unit and API tests
reports/                     generated metrics, figures, model/report docs
results/                     demo run outputs
```

## Results

The included results are synthetic demo outputs. They prove that the pipeline runs end-to-end; they do not prove real-world medical performance.

```text
Synthetic demo results verify the pipeline only. Real-world performance requires subject-wise evaluation on real wearable datasets.
```

## Limitations And Ethics

- Research demo only. Not for clinical diagnosis or medical decision-making.
- Synthetic data cannot prove real-world generalization.
- Real validation needs subject-wise splits, larger wearable datasets, bias checks, and clinical review.
- Low-confidence or low-quality predictions should be treated as review-required.

See `docs/LIMITATIONS_AND_ETHICS.md`.

## Future Improvements

- Add a WESAD conversion script.
- Add MLflow as an optional experiment tracker.
- Deploy Streamlit and FastAPI publicly.
- Replace placeholder screenshots with real deployed screenshots.
- Add real dataset benchmark results with subject-wise validation.

## Resume Bullets

- Built CardioTwin AI, an end-to-end AI platform for wearable PPG signal analytics using PyTorch, Scikit-learn, Pandas, FastAPI, and Streamlit, covering preprocessing, feature engineering, predictive modeling, spectrogram-based CV analysis, and automated report generation.
- Implemented model comparison, explainability, uncertainty scoring, signal quality assessment, and experiment tracking to evaluate AI models and present results through a recruiter-ready dashboard and API.
- Designed a modular ML pipeline with synthetic/real dataset modes, subject-wise validation support, Dockerized deployment, CI testing, and clear model/dataset documentation.

## Final Checklist

- README has screenshots
- Dashboard runs locally
- API runs locally
- Synthetic demo pipeline works
- Real dataset mode documented
- Model metrics are saved
- Explainability page works
- Report generator works
- Tests pass
- Docker compose works
- CI badge visible
- Demo script added
- Disclaimer included
- GitHub repo has description and topics
- Optional: deployed Streamlit link added
- Optional: demo video/GIF added

## GitHub About Section

Description:

```text
End-to-end self-supervised PPG signal intelligence platform using PyTorch, Scikit-learn, FastAPI, Streamlit, and local experiment tracking.
```

Topics:

```text
artificial-intelligence, machine-learning, deep-learning, pytorch, scikit-learn, streamlit, fastapi, healthcare-ai, signal-processing, self-supervised-learning, computer-vision, nlp, mlops
```

## Author

Pruthvi226

