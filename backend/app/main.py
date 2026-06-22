"""FastAPI entrypoint for the CardioTwin multimodal health risk digital twin."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database.db import init_db
from .routes import (
    alert_routes,
    chatbot_routes,
    fusion_routes,
    image_routes,
    report_routes,
    signal_routes,
    tabular_routes,
    text_routes,
    trend_routes,
)
from .utils.config import get_fusion_weights
from .utils.disclaimer import DISCLAIMER


app = FastAPI(
    title="CardioTwin AI: Multimodal Health Risk Digital Twin API",
    version="3.0.0",
    description=(
        "Educational multimodal AI system for PPG, structured vitals, symptom notes, "
        "medical report images, trends, alerts, and longitudinal health memory."
    ),
)


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "")
    if raw.strip():
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(signal_routes.router)
app.include_router(tabular_routes.router)
app.include_router(text_routes.router)
app.include_router(image_routes.router)
app.include_router(fusion_routes.router)
app.include_router(report_routes.router)
app.include_router(trend_routes.router)
app.include_router(alert_routes.router)
app.include_router(chatbot_routes.router)


@app.get("/")
async def root() -> dict:
    return {
        "project": "CardioTwin AI: Multimodal Health Risk Digital Twin",
        "description": "Fuses PPG signals, patient vitals, symptoms, reports, trends, alerts, and summaries.",
        "status": "running",
        "fusion_weights": get_fusion_weights(),
        "disclaimer": DISCLAIMER,
    }


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "disclaimer": DISCLAIMER}