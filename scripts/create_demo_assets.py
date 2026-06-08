"""Create placeholder demo screenshots/assets."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ASSETS = {
    "dashboard_home.png": "Dashboard Home",
    "signal_lab.png": "Signal Preprocessing Lab",
    "model_comparison.png": "Model Comparison",
    "explainability.png": "Explainability View",
    "api_docs.png": "FastAPI Swagger Docs",
    "architecture.png": "System Architecture",
}


def create_demo_assets(out_dir: str | Path = "assets") -> None:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    for filename, title in ASSETS.items():
        fig, ax = plt.subplots(figsize=(10, 5.5))
        ax.set_facecolor("#f8fafc")
        ax.text(0.5, 0.62, "CardioTwin AI", ha="center", va="center", fontsize=28, weight="bold", color="#0f766e")
        ax.text(0.5, 0.47, title, ha="center", va="center", fontsize=20, color="#111827")
        ax.text(0.5, 0.32, "Replace with real deployed screenshot before final submission.", ha="center", va="center", fontsize=12, color="#64748b")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.tight_layout()
        fig.savefig(output / filename, dpi=150)
        plt.close(fig)


if __name__ == "__main__":
    create_demo_assets()

