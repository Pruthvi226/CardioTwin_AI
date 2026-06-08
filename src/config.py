"""Configuration helpers for CardioTwin AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_PATH = Path("config.yaml")


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load a YAML configuration file and return a plain dictionary."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    return data


def ensure_project_dirs(config: dict[str, Any]) -> None:
    """Create the directories referenced by the active config."""
    for path in (config.get("paths") or {}).values():
        if isinstance(path, str) and path:
            Path(path).mkdir(parents=True, exist_ok=True)

