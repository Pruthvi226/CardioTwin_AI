"""Train one requested CardioTwin model family."""

from __future__ import annotations

import argparse

from scripts.run_full_pipeline import run_stage
from src.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="random_forest", choices=["random_forest", "cnn_lstm", "transformer", "ssl_encoder"])
    parser.add_argument("--dataset", default="synthetic", choices=["synthetic", "real"])
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    config = load_config(args.config)
    config["active_model"] = args.model
    run_stage("train_all", config, dataset=args.dataset)


if __name__ == "__main__":
    main()

