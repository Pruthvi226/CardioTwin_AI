# CardioTwin AI Experiment Report

## Executive Summary
CardioTwin AI converts PPG windows into cleaned signals, morphology/MDI features, spectrogram images, predictive models, and an automated experiment narrative.

## Best Classification Result
Best model: RandomForest_features
Weighted F1-score: 1.000
Accuracy: 1.000

## Regression Snapshot
Best BP regressor: RandomForest_BP_regression with MAE=1.37 and RMSE=1.58.

## Key Insight
Deep raw-window and spectrogram models test whether learned waveform or image representations beat interpretable morphology features. Classical models remain useful for feature-level explanations.

## Failure Cases To Inspect
- Low signal-quality windows with motion-like noise.
- Subject-level shifts in heart-rate proxy and pulse amplitude.
- Synthetic-to-real dataset gap when moving beyond the demo dataset.

## Recommended Next Experiments
- Tune window length, augmentation strength, and learning rate.
- Add subject-wise splits for stronger leakage control.
- Validate on WESAD/BIDMC/VitalDB or another governed dataset before making clinical claims.

## Safety Note
This is a research/demo AI analytics tool, not a medical diagnosis system.
