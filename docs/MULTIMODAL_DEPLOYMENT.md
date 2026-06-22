# Multimodal Deployment Guide

This guide deploys the React + FastAPI Multimodal Health Risk Twin. The legacy Streamlit/PPG compose file is kept separate.

## Local Development

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Production Compose

```bash
docker compose -f docker-compose.multimodal.yml up --build
```

Open:

- Frontend: `http://127.0.0.1:8080`
- Backend API: `http://127.0.0.1:8000`
- Backend docs: `http://127.0.0.1:8000/docs`

The production frontend uses Nginx and proxies `/api/*` to the backend container.

## Environment

Backend:

- `CORS_ORIGINS`: comma-separated allowed origins for direct browser calls to FastAPI.
- `CARDIOTWIN_CONFIG`: path to the JSON config file containing fusion weights.

Frontend:

- `VITE_API_URL`: API base URL baked into the frontend build. Use `/api` when deploying with the included Nginx reverse proxy.

## Health Checks

- Backend: `GET /health`
- Frontend container: `GET /healthz`

## E2E Test

Start backend and frontend locally, then run:

```bash
cd frontend
npm run test:e2e
```

The test uploads bundled demo files, runs analysis, verifies dashboard output, and exports a report.

## Medical Disclaimer

This system is for educational and research purposes only and should not be used as a substitute for professional medical advice.

