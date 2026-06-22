# Data Folder

This folder contains a small synthetic PPG dataset for demonstrating the Databricks Lakehouse workflow.

## File

- `sample_ppg_data.csv`: Window-level PPG examples with labels and blood pressure targets.

## Columns

- `patient_id`: Synthetic patient identifier.
- `window_id`: Unique signal window identifier.
- `timestamp`: Window start time.
- `sampling_rate`: Signal frequency in Hz.
- `ppg_values`: Semicolon-separated PPG samples for one window.
- `cardiovascular_status`: Educational class label. `0` = normal, `1` = elevated risk, `2` = higher risk pattern.
- `systolic_bp`: Synthetic systolic blood pressure target.
- `diastolic_bp`: Synthetic diastolic blood pressure target.

The values are not clinical measurements. They are intentionally small and simple so the notebooks can run quickly on Databricks Free Edition.
