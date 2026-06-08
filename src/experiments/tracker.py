"""CSV experiment tracker for CardioTwin AI."""

from __future__ import annotations

from pathlib import Path
from time import time
from typing import Any

import pandas as pd


def log_experiment(run: dict[str, Any], out_path: str | Path = "reports/metrics/experiment_runs.csv") -> Path:
    """Append one experiment run to a local CSV tracker."""
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": int(time()), **run}
    if output.exists():
        frame = pd.read_csv(output)
        frame = pd.concat([frame, pd.DataFrame([row])], ignore_index=True)
    else:
        frame = pd.DataFrame([row])
    frame.to_csv(output, index=False)
    return output

