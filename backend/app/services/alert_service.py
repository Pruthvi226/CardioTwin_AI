"""Emergency alert and health recommendation service."""

from __future__ import annotations

from typing import Any

from ..utils.risk_rules import check_emergency_patterns, generate_recommendations


def check_alerts(payload: dict[str, Any]) -> dict[str, Any]:
    return check_emergency_patterns(payload)


def recommendations(payload: dict[str, Any]) -> dict[str, Any]:
    return generate_recommendations(payload)

