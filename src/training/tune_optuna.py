"""Optional hyperparameter-tuning placeholder.

Optuna is intentionally not required for the default demo path.  This module
keeps a stable place for future tuning work without adding a heavy dependency.
"""


def describe_tuning_space() -> dict[str, list[float | int]]:
    """Return the tuning knobs recommended for the internship roadmap."""
    return {
        "learning_rate": [0.0003, 0.001, 0.003],
        "window_seconds": [6, 8, 10],
        "augmentation_strength": [0.05, 0.1, 0.2],
        "batch_size": [32, 64, 128],
    }

