# CardioTwin AI

Modern self-supervised PPG signal intelligence platform for wearable health analytics demos.

CardioTwin AI turns raw photoplethysmography (PPG) signals into a complete AI workflow: preprocessing, morphology and MDI feature extraction, self-supervised representation learning, predictive modeling, spectrogram-based computer vision, automated reporting, API serving, and an interactive Streamlit dashboard.

> Research/demo only. CardioTwin AI is not a medical diagnosis system and does not claim clinical accuracy.

## Project Snapshot

| Area | Implementation |
| --- | --- |
| Signal processing | NaN/outlier repair, bandpass filtering, 64 Hz resampling, z-score normalization, 8-second windows |
| Feature engineering | Peak intervals, pulse amplitude, slope, AUC, HR proxy, variability, signal quality, MDI score |
| ML models | RandomForest, GradientBoosting, CNN-LSTM, masked SSL encoder, spectrogram CNN |
| CV branch | Converts PPG windows into spectrogram images for image-style classification |
| NLP/reporting | Generates structured experiment summaries from metrics |
| Product demo | Streamlit dashboard with signal lab, predictions, CV view, reports, and recruiter demo |
| MLOps | Config-driven pipeline, saved artifacts, Dockerfile, FastAPI endpoint, GitHub Actions smoke test |

## Demo Results

Latest synthetic demo run:

- Best classifier: `RandomForest_features`, weighted F1 `1.000`
- SSL baseline: `SSL_encoder_finetuned`, weighted F1 `1.000`
- BP regression baseline: MAE about `1.37`, RMSE about `1.58`
- Metrics file: `results/metrics.csv`
- Auto report: `reports/experiment_report.md`

These results validate the pipeline on synthetic demo data. Real-world performance requires governed wearable or clinical datasets and subject-wise validation.

## Architecture

```text
app/
  streamlit_app.py          Interactive dashboard
scripts/
  generate_demo_data.py     Synthetic PPG generator
  run_full_pipeline.py      One-command pipeline
  export_results.py         Submission manifest
src/
  preprocessing/            Cleaning, filtering, quality, windowing
  features/                 Morphology, MDI, spectrogram builder
  models/                   Classical, CNN-LSTM, SSL, Transformer, CV CNN
  training/                 SSL, predictive, and CV training
  evaluation/               Metrics, plots, model card, explainability
  nlp/                      Template-based experiment reports
  api/                      FastAPI prediction endpoint
data/
  raw/                      Demo or real input signals
  processed/                Windows and feature tables
models/                     Trained .pt and .joblib models
results/                    Metrics, plots, summaries
reports/                    Experiment report and model card
```

Legacy research scripts from the original repository are preserved for traceability. See `LEGACY_RESEARCH_FILES.md` for the clean demo path.

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_full_pipeline.py --stage all --config config.yaml
streamlit run app/streamlit_app.py
```

Open the dashboard at:

```text
http://localhost:8501
```

## Pipeline Commands

```bash
python scripts/generate_demo_data.py --samples 12000 --out data/raw/demo_ppg.csv
python scripts/run_full_pipeline.py --stage preprocess --config config.yaml
python scripts/run_full_pipeline.py --stage train_all --config config.yaml
python scripts/run_full_pipeline.py --stage evaluate --config config.yaml
python scripts/export_results.py
```

## Dashboard

The Streamlit app includes:

- Signal Lab: raw signal, cleaned signal, feature table
- AI Prediction: predicted class, confidence, threshold review
- CV View: spectrogram image used by the CV branch
- Experiment Report: generated report and metrics table
- Recruiter Demo: problem, solution, tech stack, limitations

## API

Start the API:

```bash
uvicorn src.api.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Prediction request:

```json
{
  "ppg": [0.01, 0.04, 0.08, 0.12, 0.10],
  "fs": 64.0
}
```

The response returns predicted class, confidence, MDI score, signal quality score, feature preview, and a demo-only disclaimer.

## Generated Artifacts

- `data/raw/demo_ppg.csv`
- `data/processed/demo_windows.npz`
- `data/processed/mdi_features.csv`
- `models/*.pt`
- `models/*.joblib`
- `results/metrics.csv`
- `results/feature_importance.csv`
- `results/plots/model_comparison.png`
- `results/plots/spectrogram_preview.png`
- `reports/experiment_report.md`
- `reports/model_card.md`
- `reports/submission_manifest.json`

## Tech Stack

Python, NumPy, SciPy, Pandas, Scikit-learn, PyTorch, Matplotlib, Streamlit, FastAPI, Uvicorn, PyYAML, Joblib, Docker, GitHub Actions.

## Resume Bullets

- Built CardioTwin AI, an end-to-end self-supervised PPG signal intelligence platform using PyTorch, Scikit-learn, Pandas, and Streamlit to preprocess wearable signals, train predictive models, and visualize physiological patterns.
- Implemented signal preprocessing, MDI/morphology feature extraction, CNN/Transformer-ready models, spectrogram-based CV classification, model comparison, FastAPI serving, and automated NLP experiment reporting.

## 60-Second Pitch

CardioTwin AI converts raw wearable PPG signals into AI-ready insights. It cleans and segments the signal, extracts physiological biomarkers, trains classical and deep learning models, compares performance with accuracy, F1, MAE, and RMSE, and adds a computer-vision branch by converting signals into spectrogram images. The final output is a Streamlit dashboard where users can inspect signals, predictions, explanations, and generated experiment reports.

## Limitations

- Default data is synthetic and intended for reproducible pipeline validation.
- The project should not be presented as a clinical diagnostic system.
- Real-world claims require larger datasets, subject-wise validation, sensor-noise analysis, and clinical review.

## Tests

```bash
python -m unittest discover -s tests
```

