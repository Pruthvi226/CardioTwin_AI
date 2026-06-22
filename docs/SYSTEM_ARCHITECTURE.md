# System Architecture

## Data Flow
Raw CSV signal input moves through missing-value handling, filtering, normalization, windowing, quality scoring, feature extraction, spectrogram generation, and local vector index creation.

## Training Flow
Subject-wise splits create train, validation, and test subjects. Classical ML uses handcrafted features; deep models use raw windows or spectrogram tensors.

## Inference Flow
The API and dashboard clean incoming signals, create windows, extract features, query the local vector index for similar historical/demo windows, estimate confidence and uncertainty, then return a safe demo prediction.

## Dashboard Flow
Users upload or select a sample signal, inspect preprocessing, review features, run prediction, inspect explainability, and generate reports.

## API Flow
FastAPI exposes health, project metadata, prediction, model info, and sample-response endpoints.
