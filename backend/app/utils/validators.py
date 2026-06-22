"""Input validation helpers used by API routes and model modules."""

from __future__ import annotations

from typing import Iterable

from .config import clamp


SIGNAL_EXTENSIONS = {".csv", ".txt"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".pdf"}


def extension_of(filename: str | None) -> str:
    if not filename or "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()


def validate_extension(filename: str | None, allowed: Iterable[str]) -> None:
    extension = extension_of(filename)
    if extension not in set(allowed):
        expected = ", ".join(sorted(allowed))
        raise ValueError(f"Unsupported file type '{extension or 'unknown'}'. Expected one of: {expected}.")


def as_float(value: object, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "y", "1", "smoker", "positive"}
    return bool(value)


def percentage(value: float) -> float:
    return round(clamp(value), 2)

