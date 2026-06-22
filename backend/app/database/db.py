"""SQLite connection utilities for local longitudinal health memory."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path


DEFAULT_DB_PATH = Path(os.getenv("CARDIOTWIN_DB_PATH", Path(tempfile.gettempdir()) / "cardiotwin_health_memory.sqlite3"))


def get_connection() -> sqlite3.Connection:
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DEFAULT_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                patient_id TEXT DEFAULT 'demo',
                final_risk_score REAL,
                risk_category TEXT,
                systolic_bp REAL,
                diastolic_bp REAL,
                heart_rate REAL,
                spo2 REAL,
                sleep_hours REAL,
                signal_quality REAL,
                payload_json TEXT NOT NULL
            )
            """
        )
        connection.commit()