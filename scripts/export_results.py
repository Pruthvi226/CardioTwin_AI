"""Export a compact submission manifest for CardioTwin AI."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    artifacts = {
        "metrics": "results/metrics.csv",
        "experiment_report": "reports/experiment_report.md",
        "model_card": "reports/model_card.md",
        "dashboard": "app/streamlit_app.py",
        "api": "src/api/main.py",
        "disclaimer": "Research/demo only. Not a medical diagnosis system.",
    }
    output = Path("reports/submission_manifest.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifacts, indent=2), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

