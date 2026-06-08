# Dataset Card

## Dataset Source
Synthetic demo data is generated locally. Real mode supports manually prepared public wearable PPG datasets such as WESAD.

## Dataset Mode
- `synthetic`: pipeline validation only.
- `real`: subject-wise evaluation after manual dataset preparation.

## Features
PPG samples, subject id, sampling frequency, stress-like label, signal quality label, SBP/DBP demo targets, heart-rate proxy, activity label.

## Labels
Labels are demo categories and scores. They must not be interpreted as clinical truth.

## Limitations
Synthetic data does not represent real population variability. Real data requires licensing, consent, preprocessing review, and subject-wise splits.

