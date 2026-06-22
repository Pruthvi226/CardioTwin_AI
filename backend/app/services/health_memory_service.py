"""High-level longitudinal memory service."""

from __future__ import annotations

from typing import Any

from ..database.crud import compare_last_reading, list_readings, save_reading
from ..utils.disclaimer import DISCLAIMER


def save(payload: dict[str, Any]) -> dict[str, Any]:
    result = save_reading(payload)
    result["disclaimer"] = DISCLAIMER
    return result


def history(limit: int = 25) -> dict[str, Any]:
    return {"readings": list_readings(limit), "disclaimer": DISCLAIMER}


def compare_last() -> dict[str, Any]:
    result = compare_last_reading()
    result["disclaimer"] = DISCLAIMER
    return result

