# CardioTwin AI Model Card

## Intended Use
Demo-ready PPG signal analytics for representation learning, signal quality review, and predictive modeling experiments.

## Performance Snapshot
Best classifier: RandomForest_features with weighted F1=1.000.

## Data
The default workflow uses synthetic PPG-like signals for reproducible pipeline validation. Real clinical or wearable datasets require separate validation and governance.

## Limitations
- Synthetic data is not a substitute for clinical validation.
- Predictions may be sensitive to subject variability, sensor placement, motion artifacts, and dataset shift.
- Outputs should be interpreted as research signals, not clinical advice.

## Safety Disclaimer
CardioTwin AI is a research and internship-demo analytics tool. It is not a medical diagnosis system and has not been clinically validated.
