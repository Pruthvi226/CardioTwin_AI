"""Summarize pipeline logs into recruiter-friendly bullets."""

from __future__ import annotations

from pathlib import Path


def summarize_log(path: str | Path, max_lines: int = 8) -> list[str]:
    """Return the last informative lines from a log file."""
    log_path = Path(path)
    if not log_path.exists():
        return ["No log file was found for this run."]
    lines = [line.strip() for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    return lines[-max_lines:] if lines else ["The log file is empty."]

