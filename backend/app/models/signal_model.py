"""PPG signal analysis, feature extraction, and BP trend estimation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from ..services.explanation_service import signal_quality_explanation
from ..services.preprocessing import chart_points, clean_ppg_signal, dataframe_to_signal, demo_ppg_signal, read_csv_bytes
from ..utils.config import clamp, risk_category
from ..utils.validators import percentage

try:
    from scipy.signal import find_peaks
except Exception:  # pragma: no cover - scipy is preferred but not mandatory for demo mode
    find_peaks = None


def _detect_peaks(cleaned: np.ndarray, fs: float) -> np.ndarray:
    if cleaned.size < 5:
        return np.array([], dtype=int)
    if find_peaks is not None:
        distance = max(1, int(fs * 0.42))
        prominence = max(0.05, float(np.std(cleaned)) * 0.25)
        peaks, _ = find_peaks(cleaned, distance=distance, prominence=prominence)
        return peaks.astype(int)

    peaks = []
    for index in range(1, len(cleaned) - 1):
        if cleaned[index] > cleaned[index - 1] and cleaned[index] > cleaned[index + 1]:
            peaks.append(index)
    return np.asarray(peaks, dtype=int)


def _artifact_ratio(raw: np.ndarray) -> float:
    if raw.size < 3:
        return 1.0
    diffs = np.diff(raw)
    threshold = max(float(np.std(diffs)) * 3.0, 1e-6)
    abrupt = np.abs(diffs) > threshold
    flat = np.abs(diffs) < max(float(np.std(raw)) * 0.005, 1e-6)
    return float(np.clip(abrupt.mean() + flat.mean() * 0.3, 0, 1))


def _valid_intervals(intervals: np.ndarray) -> tuple[np.ndarray, float]:
    if intervals.size == 0:
        return intervals, 0.0
    plausible = intervals[(intervals >= 0.35) & (intervals <= 1.65)]
    rejected_ratio = 1.0 - (len(plausible) / len(intervals))
    return plausible, float(np.clip(rejected_ratio, 0, 1))


def _heart_rate_penalty(heart_rate: float) -> float:
    if heart_rate < 40 or heart_rate > 170:
        return 28.0
    if heart_rate < 50 or heart_rate > 125:
        return 14.0
    return 0.0


def _estimate_bp(heart_rate: float, quality_score: float, hrv_sdnn: float) -> dict[str, Any]:
    stress_term = max(0.0, heart_rate - 72.0) * 0.32
    quality_term = max(0.0, 70.0 - quality_score) * 0.18
    hrv_term = max(0.0, hrv_sdnn - 80.0) * 0.04
    systolic = clamp(116.0 + stress_term + quality_term + hrv_term, 90, 190)
    diastolic = clamp(74.0 + stress_term * 0.45 + quality_term * 0.35 + hrv_term * 0.2, 55, 120)
    if systolic >= 140 or diastolic >= 90:
        trend = "Elevated BP trend predicted"
    elif systolic >= 130 or diastolic >= 80:
        trend = "Borderline BP trend predicted"
    else:
        trend = "Stable BP trend predicted"
    if quality_score >= 80:
        confidence = "higher"
    elif quality_score >= 55:
        confidence = "moderate"
    else:
        confidence = "low"
    return {
        "systolic": round(systolic, 1),
        "diastolic": round(diastolic, 1),
        "trend": trend,
        "method": "rule_based_regression_fallback",
        "confidence": confidence,
        "note": "Educational approximation; not a clinical BP measurement.",
    }


def analyze_ppg_signal(signal: np.ndarray, fs: float = 64.0, timestamps: np.ndarray | None = None) -> dict[str, Any]:
    raw = np.asarray(signal, dtype=float)
    if raw.size < 5:
        raise ValueError("At least five PPG samples are required for signal analysis.")
    if timestamps is None:
        timestamps = np.arange(raw.size, dtype=float) / fs

    cleaned = clean_ppg_signal(raw, window=max(5, int(fs * 0.12)))
    peaks = _detect_peaks(cleaned, fs)
    peak_times = timestamps[peaks] if len(peaks) else np.array([], dtype=float)
    raw_intervals = np.diff(peak_times) if len(peak_times) > 1 else np.array([], dtype=float)
    intervals, rejected_interval_ratio = _valid_intervals(raw_intervals)
    duration_seconds = max(float(timestamps[-1] - timestamps[0]), raw.size / fs)

    if len(intervals) > 0:
        heart_rate = float(60.0 / np.mean(intervals))
        hrv_sdnn = float(np.std(intervals) * 1000.0)
        peak_interval_mean = float(np.mean(intervals))
        interval_cv = float(np.std(intervals) / (np.mean(intervals) + 1e-6))
    elif len(raw_intervals) > 0:
        heart_rate = float(60.0 / np.mean(raw_intervals))
        hrv_sdnn = float(np.std(raw_intervals) * 1000.0)
        peak_interval_mean = float(np.mean(raw_intervals))
        interval_cv = float(np.std(raw_intervals) / (np.mean(raw_intervals) + 1e-6))
    else:
        heart_rate = float(len(peaks) / max(duration_seconds, 1.0) * 60.0)
        hrv_sdnn = 0.0
        peak_interval_mean = 0.0
        interval_cv = 0.0

    artifact_ratio = _artifact_ratio(raw)
    noise_level = float(np.std(raw - np.median(raw)) / (np.ptp(raw) + 1e-6))
    peak_density_penalty = _heart_rate_penalty(heart_rate)
    interval_penalty = min(22.0, rejected_interval_ratio * 22.0)
    rhythm_penalty = min(18.0, max(0.0, interval_cv - 0.12) * 70.0)
    quality_score = clamp(
        100.0
        - artifact_ratio * 42.0
        - noise_level * 22.0
        - peak_density_penalty
        - interval_penalty
        - rhythm_penalty
    )
    reliability = "Reliable" if quality_score >= 80 else "Review Needed" if quality_score >= 55 else "Noisy"
    bp_prediction = _estimate_bp(heart_rate, quality_score, hrv_sdnn)
    bp_quality_scale = clamp(quality_score, 35.0, 100.0) / 100.0

    risk_parts = {
        "signal_quality": max(0.0, 100.0 - quality_score) * 0.45,
        "heart_rate": max(0.0, abs(heart_rate - 75.0) - 18.0) * 0.8,
        "rhythm_irregularity": max(0.0, interval_cv - 0.12) * 38.0,
        "interval_rejections": rejected_interval_ratio * 18.0,
        "predicted_bp": (max(0.0, bp_prediction["systolic"] - 125.0) * 0.7) * bp_quality_scale,
    }
    signal_risk = clamp(sum(risk_parts.values()))
    warnings = []
    if quality_score < 55:
        warnings.append({"label": "Noisy PPG signal", "severity": "medium", "detail": "Motion artifacts may reduce reliability."})
    if rejected_interval_ratio > 0.35:
        warnings.append({"label": "Unstable PPG peak pattern", "severity": "medium", "detail": "Many detected peak intervals were physiologically implausible."})
    if heart_rate > 120 or heart_rate < 45:
        warnings.append({"label": "Heart rate outlier", "severity": "high", "detail": f"Estimated heart rate is {heart_rate:.1f} bpm."})

    return {
        "risk_score": percentage(signal_risk),
        "risk_category": risk_category(signal_risk),
        "quality_score": percentage(quality_score),
        "reliability": reliability,
        "artifact_ratio": round(artifact_ratio, 4),
        "heart_rate_estimate": round(heart_rate, 1),
        "bp_prediction": bp_prediction,
        "features": {
            "sample_count": int(raw.size),
            "sampling_rate": round(float(fs), 2),
            "duration_seconds": round(duration_seconds, 2),
            "peak_count": int(len(peaks)),
            "peak_interval_mean": round(peak_interval_mean, 4),
            "hrv_sdnn_ms": round(hrv_sdnn, 2),
            "interval_cv": round(interval_cv, 4),
            "rejected_interval_ratio": round(rejected_interval_ratio, 4),
            "noise_level": round(noise_level, 4),
        },
        "peaks": [{"time": round(float(time), 3), "index": int(index)} for time, index in zip(peak_times[:60], peaks[:60])],
        "chart": chart_points(raw, cleaned, timestamps),
        "explanation": signal_quality_explanation(quality_score, artifact_ratio),
        "warning_flags": warnings,
        "heart_rate": round(heart_rate, 1),
        "signal_quality": percentage(quality_score),
        "peak_count": int(len(peaks)),
        "noise_level": round(noise_level, 4),
        "estimated_systolic_bp": bp_prediction["systolic"],
        "estimated_diastolic_bp": bp_prediction["diastolic"],
        "signal_risk_score": percentage(signal_risk),
        "confidence_score": percentage(max(30.0, min(92.0, quality_score - rejected_interval_ratio * 12.0))),
    }


def analyze_signal_csv(raw: bytes | None = None) -> dict[str, Any]:
    if raw:
        parsed = dataframe_to_signal(read_csv_bytes(raw))
    else:
        sample_path = Path(__file__).resolve().parents[1] / "data" / "sample_ppg.csv"
        if sample_path.exists():
            parsed = dataframe_to_signal(read_csv_bytes(sample_path.read_bytes()))
        else:
            parsed = demo_ppg_signal()
    result = analyze_ppg_signal(parsed["signal"], parsed["sampling_rate"], parsed["timestamps"])
    result["source"] = {
        "signal_column": parsed.get("signal_column", "demo_ppg"),
        "time_column": parsed.get("time_column", "generated_time"),
        "columns": parsed.get("columns", []),
        "demo_mode": raw is None,
    }
    return result


def summarize_signal_upload(raw: bytes) -> dict[str, Any]:
    parsed = dataframe_to_signal(read_csv_bytes(raw))
    return {
        "sample_count": int(len(parsed["signal"])),
        "sampling_rate": round(float(parsed["sampling_rate"]), 2),
        "signal_column": parsed["signal_column"],
        "time_column": parsed["time_column"],
        "columns": parsed["columns"],
        "preview": [round(float(value), 5) for value in parsed["signal"][:12]],
    }
