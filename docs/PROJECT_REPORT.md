# Project Report

## Problem Statement
Wearable PPG signals are noisy, subject-dependent, and difficult to convert into reliable AI-ready patterns.

## Objective
Build a demo-ready AI analytics platform that preprocesses PPG, extracts signal features, trains multiple model families, explains predictions, and reports results clearly.

## Methodology
The pipeline supports synthetic demo mode and documented real dataset mode. Signals are cleaned, segmented, scored for quality, transformed into morphology/frequency features, and converted into spectrograms for the CV branch.

## Dataset
Synthetic mode is included for reproducible pipeline validation. Real mode expects a manually prepared wearable PPG CSV such as WESAD converted into the documented schema.

## Models
Classical ML, CNN-LSTM, Transformer-ready encoder, and SSL masked reconstruction are included for comparison.

## Evaluation
Classification uses accuracy, precision, recall, and weighted F1. Regression-style scores use MAE, RMSE, and R2 where applicable.

## Results
Synthetic demo results verify the pipeline only. Real-world performance requires subject-wise evaluation on real wearable datasets.

## Limitations
Research demo only. Not for clinical diagnosis or medical decision-making.

## Future Work
Add real WESAD conversion scripts, MLflow tracking, deployed dashboard screenshots, and stronger subject-wise validation.

