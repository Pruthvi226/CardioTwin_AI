# CardioTwin AI: Multimodal Health Risk Digital Twin - Complete Project Guide

**Medical disclaimer:** This system is for educational and research purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment.

This guide explains the full CardioTwin AI project in simple language, from the problem statement to the AI concepts, backend, frontend, database, Docker deployment, and interview explanation.

---

# 1. Project Overview

## Project Title

**CardioTwin AI: Multimodal Health Risk Digital Twin**

## One-Line Explanation

CardioTwin AI is a multimodal healthcare AI system that combines PPG signals, patient vitals, symptoms, and medical report images to generate explainable cardiovascular risk insights.

## What Are We Building?

We are building an educational healthcare AI prototype that accepts different types of health data and produces:

- A health risk score
- A risk category
- A confidence score
- Alerts for warning patterns
- A doctor-friendly summary
- A patient-friendly explanation
- A downloadable report
- Trend insights from past readings

The goal is not to diagnose disease. The goal is to show how a responsible healthcare AI system can collect multiple inputs, analyze them separately, combine them transparently, and explain the result.

## What Does "Digital Twin" Mean Here?

A digital twin is a software representation of something in the real world.

In this project, the "twin" is not a perfect medical copy of a person. It is a simplified health profile that is updated using available health readings such as heart rate, blood pressure, SpO2, sleep, symptoms, PPG signal quality, and report values.

For example:

- If today's blood pressure is higher than last week, the digital twin can show that trend.
- If sleep is low and heart rate is high, the digital twin can explain that these factors increased the risk score.
- If a PPG signal is noisy, the digital twin can reduce confidence instead of acting overconfident.

So, in this project, a digital twin means a live, data-driven health snapshot that helps users understand risk patterns over time.

## What Does "Multimodal AI" Mean?

Multimodal AI means AI that works with more than one type of data.

In CardioTwin AI, the main modalities are:

- Signal data: PPG waveform CSV
- Tabular data: age, BP, heart rate, BMI, SpO2, sleep, activity, medical history
- Text data: symptoms and notes
- Image data: ECG image, medical report, lab report, or screenshot
- Time-series data: past readings over days or weeks

Healthcare is naturally multimodal. A doctor does not look at only one thing. A doctor may check pulse, blood pressure, symptoms, medical history, report images, lifestyle, and previous readings. CardioTwin AI follows the same idea by combining different sources of information.

---

# 2. Problem Statement

Many health monitoring systems look at only one type of data, such as heart rate or blood pressure. But real health risk depends on multiple signals, including vitals, symptoms, lifestyle, wearable signals, medical reports, and previous readings.

This project solves that limitation by combining:

- PPG signal
- Patient vitals
- Symptoms
- Medical report image or OCR text
- Past health readings

The final goal is to generate a simple, explainable health risk score and summary.

Important: CardioTwin AI is not a diagnosis system. It is a risk-awareness and educational AI assistant. It can help explain patterns, but it cannot confirm whether someone has a disease or medical emergency.

---

# 3. Real-World Motivation

This project matters because health data is becoming common, but understanding it is still difficult.

Examples:

- Smartwatches collect heart rate and optical signals, but users may not understand what the numbers mean.
- Patients may upload lab reports or ECG screenshots but may not understand the values.
- Doctors may benefit from structured summaries instead of raw scattered data.
- Health data comes from many sources, including wearables, forms, notes, reports, and history.
- AI should explain why it gives a risk score, especially in healthcare.

CardioTwin AI is useful for:

- Hackathons
- AI/ML portfolio projects
- Healthcare AI demos
- Digital health research
- Wearable AI system prototypes
- Full-stack ML engineering practice
- Responsible AI demonstrations

It shows more than just model training. It shows system design, data processing, explainability, API development, frontend dashboards, reports, database memory, and Docker deployment.

---

# 4. What Inputs Does the System Take?

CardioTwin AI accepts several types of input because healthcare information does not come in one format.

## 4.1 Signal Data

Input:

- PPG waveform CSV

PPG stands for Photoplethysmography. It is a signal captured by optical sensors in devices like smartwatches or pulse oximeters. It measures blood volume changes in the skin.

PPG is useful for:

- Heart rate estimation
- Signal quality checking
- Peak detection
- Approximate blood pressure trend estimation
- Noise detection
- Motion artifact detection

When to use signal data:

Use signal data when you have wearable or sensor-based health data. For example, a smartwatch, pulse oximeter, or research dataset may provide PPG waveforms.

Important safety note:

PPG-based blood pressure estimation in this project should be treated as an educational approximation unless trained and validated on a real clinical dataset.

## 4.2 Tabular Data

Input examples:

- Age
- Gender
- Height
- Weight
- BMI
- Heart rate
- Systolic BP
- Diastolic BP
- SpO2
- Sleep hours
- Activity level
- Smoking status
- Diabetes history
- Hypertension history

Tabular data is structured data in rows and columns. It is the easiest type of health data to process because each field has a clear meaning.

Tabular data is useful for:

- Rule-based risk scoring
- ML model prediction
- Risk factor detection
- BMI calculation
- Missing input checks
- Confidence scoring

When to use tabular data:

Use tabular data when the health information is numeric or categorical. For example, blood pressure is numeric, and smoking status is categorical.

## 4.3 Text Data

Input examples:

- Symptoms
- Lifestyle notes
- Doctor notes
- Medication notes

Example text:

```text
I feel dizzy and tired.
I have chest pain and shortness of breath.
I slept only 4 hours.
```

Text data is useful for:

- Symptom extraction
- Warning pattern detection
- Risk explanation
- Patient-friendly summaries
- Doctor-style notes

When to use text processing:

Use text processing when the user provides natural language health complaints, lifestyle descriptions, or medical notes.

## 4.4 Image Data

Input examples:

- ECG image
- Medical report image
- Lab report screenshot
- Scanned report

Image data is useful for:

- OCR
- Extracting values from reports
- Reading doctor remarks
- Summarizing report text
- Detecting whether the image is clear enough to trust

When to use image or OCR:

Use image/OCR when important health information is present in scanned images or screenshots.

## 4.5 Time-Series Data

Input:

- Past readings over multiple days

Time-series data is useful for:

- Trend prediction
- Risk change analysis
- Longitudinal health memory
- Comparing current reading with previous readings

When to use time-series data:

Use time-series data when readings are collected over time. A single reading is useful, but trends are often more informative.

---

# 5. Nature of Dataset

This project can use multiple datasets. Each dataset type supports a different part of the system.

## 5.1 PPG Signal Dataset

Format:

CSV file containing time and signal amplitude.

Example:

```csv
time,ppg_signal
0.00,0.51
0.01,0.53
0.02,0.56
0.03,0.55
```

Nature:

- Time-series signal data
- Continuous numeric values
- May contain noise
- May contain motion artifacts
- Needs preprocessing before analysis

Possible sources:

- Public PPG datasets
- Synthetic generated PPG data
- Wearable sensor data
- Pulse oximeter data

Use in this project:

- Signal quality scoring
- Heart rate estimation
- BP trend approximation
- Peak detection
- Anomaly detection

## 5.2 Patient Vitals Dataset

Format:

CSV or JSON.

Example:

```json
{
  "age": 25,
  "gender": "male",
  "heart_rate": 88,
  "systolic_bp": 130,
  "diastolic_bp": 85,
  "spo2": 97,
  "sleep_hours": 5,
  "activity_level": "low"
}
```

Nature:

- Structured/tabular data
- Numeric plus categorical values
- Easy to process with rules or ML models
- Useful for both current risk and historical trends

Use in this project:

- Risk scoring
- Risk factor detection
- BMI calculation
- Confidence scoring
- Health summary generation

## 5.3 Symptoms Text Dataset

Format:

Plain text.

Example:

```text
I feel dizzy and tired since morning. I also have mild chest discomfort.
```

Nature:

- Unstructured text
- May contain spelling mistakes
- May contain vague symptoms
- May include urgent warning phrases

Use in this project:

- Symptom extraction
- Emergency warning detection
- Patient-friendly explanation
- Doctor-friendly summary

## 5.4 Medical Report Image Dataset

Format:

- PNG
- JPG
- PDF
- Screenshot

Nature:

- Image data
- May be clear or blurry
- May contain text, numbers, tables, or ECG graph images
- Needs OCR to convert visible text into machine-readable text

Use in this project:

- OCR
- Extract BP, HR, SpO2, glucose, cholesterol, ECG notes, or doctor remarks
- Generate a report summary
- Increase or decrease confidence depending on image clarity

## 5.5 Historical Health Dataset

Format:

CSV with timestamped readings.

Example:

```csv
date,heart_rate,systolic_bp,diastolic_bp,spo2,sleep_hours,risk_score
2026-06-01,82,124,80,98,7,25
2026-06-02,88,130,84,97,6,38
2026-06-03,95,138,90,96,5,55
```

Nature:

- Time-series tabular data
- Useful for trend analysis
- Useful for comparing present values with previous values

Use in this project:

- Health trend prediction
- Current vs previous reading comparison
- Risk increase/decrease explanation
- Longitudinal health memory

---

# 6. Dataset Strategy If Real Dataset Is Not Available

If a real clinical dataset is not available, do not fake medical accuracy.

For a student project, portfolio project, or hackathon demo, it is acceptable to use:

- Synthetic PPG signals
- Rule-based vitals scoring
- Demo patient profiles
- OCR demo images
- Simulated historical readings

Why this is acceptable:

The goal is to demonstrate system design, multimodal AI pipeline architecture, explainability, frontend/backend integration, and responsible AI behavior.

What you must not claim:

- Do not claim the model is clinically validated.
- Do not claim the system diagnoses heart disease.
- Do not claim the BP approximation is medically accurate.
- Do not claim emergency alerts are doctor-confirmed.

Real clinical model training requires verified medical datasets, expert validation, ethics approval, privacy controls, and careful testing across diverse patient groups.

---

# 7. AI/ML Concepts Used

This section explains the main AI/ML ideas used in CardioTwin AI.

## 7.1 Signal Processing

What it is:

Signal processing cleans and analyzes sensor signals.

Why we use it:

PPG signals may contain noise due to hand movement, poor sensor contact, lighting changes, or device issues. If the signal is noisy, the system should know that before estimating heart rate or risk.

When to use it:

Use signal processing before extracting features from PPG signals.

Common concepts:

- Normalization
- Filtering
- Peak detection
- Noise detection
- Signal quality scoring
- Motion artifact estimation

Example:

If the PPG waveform has clear repeated peaks, the signal quality is better. If the waveform is flat, chaotic, or broken, the signal quality is lower.

## 7.2 Feature Extraction

What it is:

Feature extraction converts raw data into useful numbers.

Example features from PPG:

- Number of peaks
- Average distance between peaks
- Estimated heart rate
- Signal quality
- Noise level
- Peak regularity

Why we use it:

ML models and scoring rules work better with clean, meaningful numbers than with messy raw data.

When to use it:

Use feature extraction after preprocessing and before risk scoring or ML prediction.

## 7.3 Rule-Based Scoring

What it is:

Rule-based scoring uses human-written rules.

Example:

```text
If systolic BP > 140, increase the risk score.
If SpO2 < 90, create an urgent warning.
If sleep hours are very low, add a small risk contribution.
```

Why we use it:

Rule-based scoring is useful when real labeled clinical training data is limited. It is also easy to explain, which is important in healthcare demos.

When to use it:

Use it in early project versions, hackathon demos, and educational prototypes where transparency matters more than clinical performance claims.

## 7.4 Machine Learning Model

What it is:

A machine learning model learns patterns from data.

Possible models:

- Logistic Regression
- Random Forest
- XGBoost
- LightGBM
- Neural networks

Why we use it:

ML is useful when we have enough validated labeled data. For example, if we have many patient records with known risk labels, a model can learn relationships between inputs and outcomes.

When to use it in this project:

Use ML for tabular risk prediction, BP estimation, signal classification, or anomaly detection when a reliable dataset is available.

Important:

In healthcare, ML models need validation. A high score on a demo dataset is not enough to use the model in real medical decisions.

## 7.5 OCR

What it is:

OCR means Optical Character Recognition. It extracts text from images.

Why we use it:

Medical reports are often uploaded as scanned images, screenshots, or photos. OCR helps convert those images into text that the backend can analyze.

When to use it:

Use OCR when a user uploads an ECG image, report image, lab report screenshot, or scanned document.

Possible tools:

- pytesseract
- easyocr

Example:

An uploaded report image may contain:

```text
BP: 150/95
Heart Rate: 102 bpm
SpO2: 93%
```

OCR extracts this text so the system can detect abnormal values.

## 7.6 NLP / Text Understanding

What it is:

NLP means Natural Language Processing. It helps computers understand text.

Why we use it:

Symptoms are written in normal human language. The system needs to identify important phrases like chest pain, dizziness, fatigue, palpitations, or shortness of breath.

When to use it:

Use NLP for symptom extraction, severity detection, warning pattern detection, and explanation generation.

Example symptoms:

- Chest pain
- Dizziness
- Fatigue
- Shortness of breath
- Palpitations
- Headache

## 7.7 Multimodal Fusion

What it is:

Multimodal fusion combines different types of data into one final result.

In this project, the system combines:

- Signal risk score
- Tabular risk score
- Symptom risk score
- Image/report risk score

Why we use it:

One input alone is not enough for a reliable risk overview. A user may have normal heart rate but worrying symptoms, or a high blood pressure reading but no symptom text. Fusion gives a more complete view.

When to use it:

Use fusion after each individual modality has been analyzed separately.

Example fusion formula:

```text
Final Risk Score =
0.35 x Signal Risk Score +
0.30 x Tabular Risk Score +
0.20 x Symptom Risk Score +
0.15 x Image/Report Risk Score
```

Why this is called late fusion:

Each modality is analyzed separately first. Then the final scores are combined at the end. This makes the system easier to debug and explain.

## 7.8 Explainable AI

What it is:

Explainable AI tells the user why the system gave an output.

Why we use it:

Healthcare AI must not feel like a black box. Users should know which factors increased the risk score.

When to use it:

Use explainability after risk scoring or prediction.

Example:

```text
Risk is elevated mainly because of high blood pressure, low sleep, and dizziness.
```

In this project, explanations are generated from modality contributions, rules triggered, missing inputs, and warning factors.

## 7.9 Confidence Score

What it is:

A confidence score shows how reliable the output is.

Why we use it:

If the PPG signal is noisy or the report image is unclear, the system should not act overconfident.

When to use it:

Use confidence scoring after checking signal quality, missing fields, image clarity, and available modalities.

Important:

The confidence score is not a medical probability. It is a system reliability indicator.

## 7.10 Anomaly Detection

What it is:

Anomaly detection finds unusual patterns.

Examples:

- Sudden heart rate spike
- Very low SpO2
- Unusual BP jump
- Noisy PPG segment
- Risk score suddenly increasing

When to use it:

Use anomaly detection for live monitoring or historical health readings.

## 7.11 Time-Series Trend Analysis

What it is:

Time-series analysis studies data over time.

Why we use it:

Health risk is not only about one reading. Trends matter.

When to use it:

Use it when previous readings are available.

Example:

```text
Blood pressure increased over the last 7 days.
```

Trend analysis makes the digital twin feel more realistic because it remembers change over time.

---

# 8. System Architecture

The architecture is designed as a full-stack multimodal AI system.

High-level flow:

```text
User Input
  |
  |-- PPG Signal CSV
  |-- Patient Vitals
  |-- Symptoms Text
  |-- Medical Report Image
  |-- Past Readings
  |
Frontend React Dashboard
  |
FastAPI Backend
  |
Separate AI Modules
  |-- Signal Model
  |-- Tabular Model
  |-- Text Model
  |-- Image/OCR Model
  |-- Trend Model
  |-- Anomaly Model
  |
Fusion Engine
  |
Explanation Engine
  |
Final Output
  |-- Risk Score
  |-- Risk Category
  |-- Confidence Score
  |-- Doctor Summary
  |-- Patient Summary
  |-- Alerts
  |-- Trend Insights
  |-- PDF Report
```

## Frontend Layer

The frontend is the user interface. It lets users upload data, fill forms, view charts, see risk scores, read summaries, and download reports.

## Backend Layer

The backend receives requests from the frontend and calls the correct AI modules. It also validates data, combines results, saves history, and generates reports.

## ML Modules Layer

Each modality has its own analysis module:

- Signal model analyzes PPG.
- Tabular model analyzes vitals.
- Text model analyzes symptoms.
- Image model analyzes report images or OCR text.
- Trend model analyzes history.
- Anomaly model detects unusual patterns.

## Fusion Engine

The fusion engine combines the separate modality scores into one final risk score.

## Database Layer

The database stores readings, timestamps, summaries, and history. SQLite is used first because it is simple for local development and demos.

## Report Generator

The report generator creates a professional-looking summary that can be downloaded and shared for demos.

## Docker Layer

Docker packages the backend and frontend so the project can run consistently on different machines.

---

# 9. Backend Explanation

Backend framework:

**FastAPI**

FastAPI is a Python framework for building APIs. It is popular for AI/ML projects because it is fast, simple, and automatically generates API documentation.

## Why FastAPI?

- Fast and lightweight
- Easy to write
- Good for ML projects
- Automatic API docs at `/docs`
- Works well with React frontend
- Supports file uploads and JSON APIs
- Uses Pydantic for data validation

## Backend Responsibilities

The backend is responsible for:

- Receiving files and form data
- Processing PPG signal CSV files
- Analyzing patient vitals
- Analyzing symptoms
- Running OCR or fallback text extraction on report images
- Combining risk scores
- Generating explanations
- Checking alert rules
- Saving history
- Comparing current readings with past readings
- Generating PDF reports
- Serving demo patient profiles

## Major API Endpoints

Common endpoints:

```text
GET /health
Checks if the backend is running.

POST /analyze-signal
Analyzes a PPG signal.

POST /analyze-tabular
Analyzes patient vitals.

POST /analyze-text
Analyzes symptoms.

POST /analyze-image
Analyzes a medical report image or OCR text.

POST /multimodal-risk
Combines all modality scores into the final risk result.

POST /check-alerts
Checks emergency warning rules.

POST /generate-summary
Creates doctor and patient summaries.

POST /generate-report
Creates a downloadable PDF or text report.

GET /demo-patients
Returns sample demo patients.
```

Additional endpoints in this repo may include:

```text
POST /upload-signal
Uploads and previews a signal file.

POST /analyze-trends
Analyzes historical readings.

POST /detect-anomaly
Checks for unusual physiological patterns.

POST /generate-recommendations
Creates educational health recommendations.

GET /live-simulation
Returns simulated live readings.

POST /save-reading
Saves a reading to SQLite history.

GET /history
Returns saved historical readings.

GET /compare-last-reading
Compares the current reading with the previous one.

POST /chat
Answers questions using the current report context.
```

## Backend Folder Ideas

The backend is usually organized like this:

```text
backend/
  app/
    main.py
    routes/
    models/
    services/
    database/
    utils/
    data/
  requirements.txt
  Dockerfile
```

Simple explanation:

- `main.py`: starts the FastAPI app and connects routes.
- `routes/`: defines API endpoints.
- `models/`: contains scoring and model logic.
- `services/`: contains reusable processing services.
- `database/`: handles SQLite storage.
- `utils/`: contains helpers, validators, config, and disclaimers.
- `data/`: stores sample demo files.

---

# 10. Frontend Explanation

Frontend framework:

**React**

React is used to build the user interface. It helps split the dashboard into reusable components.

## Frontend Responsibilities

The frontend should allow users to:

- Upload a PPG CSV
- Enter patient vitals
- Type or speak symptoms
- Upload a report image
- View signal charts
- View trend charts
- See the final risk score
- See modality contribution
- Read alerts
- Read doctor summary
- Read patient summary
- Download a report

## Main Components

Expected components:

- `SignalUpload`
- `PatientForm`
- `SymptomInput`
- `ImageUpload`
- `RiskDashboard`
- `SignalChart`
- `TrendCharts`
- `ModalityContribution`
- `AlertBox`
- `DoctorSummary`
- `PatientSummary`
- `ReportDownload`

This repo also includes components such as:

- `VoiceSymptomInput`
- `HealthChatbot`
- `SyntheticPatientSelector`
- `LiveDigitalTwinMonitor`

## Why Dashboard UI Matters

Healthcare AI should be understandable. A system that only returns raw JSON is difficult for users to trust or explain.

A good dashboard helps show:

- Which data was used
- Which risk factors were found
- Which modality contributed most
- Whether the signal was reliable
- Whether any warning pattern was detected
- What the patient should understand in plain language
- What a doctor might want to review

---

# 11. Database Explanation

Use SQLite first.

## Why SQLite?

SQLite is a good first database because:

- It is simple
- It needs no separate server setup
- It is good for local demos
- It is beginner-friendly
- It works well for hackathons
- It can store patient reading history in one local file

## What To Store

The database can store:

- Patient readings
- Risk scores
- Timestamps
- Summaries
- Trend history
- Report metadata
- Confidence scores

## Tables

Possible tables:

```text
patients
readings
reports
risk_history
```

Example:

- `patients`: stores basic demo patient profile data.
- `readings`: stores vitals, symptoms, signal results, and report results.
- `reports`: stores generated report metadata.
- `risk_history`: stores risk score changes over time.

## When To Upgrade To MongoDB

Use MongoDB later if the data becomes more flexible or document-like.

MongoDB can be useful for:

- Many different report formats
- Chatbot history
- Nested patient timelines
- Flexible JSON-style health records
- Rapid prototyping with changing schemas

For this project, SQLite is enough for the first full-stack version.

---

# 12. Docker Explanation

## What Is Docker?

Docker packages an application with its dependencies so it runs the same way on different computers.

Without Docker:

- One person may have Python 3.10.
- Another may have Python 3.12.
- One system may be missing OCR dependencies.
- One system may have a different Node.js version.
- Backend and frontend setup can become confusing.

With Docker:

- Backend runs in one container.
- Frontend runs in one container.
- Database storage can be mounted as a volume.
- The whole project can start with one command.

## When To Use Docker

Use Docker for:

- Deployment
- Hackathon submission
- Team collaboration
- Reproducible demos
- Running backend and frontend together

## Backend Dockerfile

Purpose:

Builds the backend container.

It should:

- Start from a Python image
- Install Python dependencies
- Copy backend code
- Expose port `8000`
- Run the FastAPI server with Uvicorn

Example idea:

```Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Frontend Dockerfile

Purpose:

Builds the frontend container.

It should:

- Start from a Node image
- Install frontend dependencies
- Build the React app
- Serve the built files using Nginx or another static server

## docker-compose.yml

Purpose:

Runs backend and frontend together.

Example services:

- `backend`
- `frontend`

Command:

```bash
docker-compose up --build
```

Meaning:

Build all containers and start the full project.

Note for this repo:

The full multimodal React plus FastAPI setup is defined in `docker-compose.multimodal.yml`. You can run it with:

```bash
docker compose -f docker-compose.multimodal.yml up --build
```

In that setup:

- Backend runs at `http://localhost:8000`
- Frontend runs at `http://localhost:8080`
- API docs run at `http://localhost:8000/docs`

For local non-Docker Vite development, the frontend usually runs at `http://localhost:5173`.

---

# 13. Complete Folder Structure

Recommended structure:

```text
CardioTwin-AI/
|
|-- backend/
|   |-- app/
|   |   |-- main.py
|   |   |-- routes/
|   |   |-- models/
|   |   |-- services/
|   |   |-- database/
|   |   |-- utils/
|   |   |-- data/
|   |-- requirements.txt
|   |-- Dockerfile
|
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- pages/
|   |   |-- services/
|   |   |-- App.jsx
|   |-- package.json
|   |-- Dockerfile
|
|-- docker-compose.yml
|-- docker-compose.multimodal.yml
|-- README.md
|-- CARDIOTWIN_PROJECT_GUIDE.md
```

What each folder does:

- `backend/`: FastAPI backend for APIs, scoring, fusion, reports, and database.
- `backend/app/routes/`: API endpoints such as signal, tabular, text, image, fusion, alerts, trends, and reports.
- `backend/app/models/`: modality-specific model or scoring logic.
- `backend/app/services/`: reusable business logic such as preprocessing, feature extraction, explanation, report generation, and health memory.
- `backend/app/database/`: SQLite setup and database operations.
- `backend/app/utils/`: validators, config helpers, risk rules, and safety disclaimer.
- `backend/app/data/`: sample PPG, sample patient data, sample report image, and demo history.
- `frontend/`: React dashboard.
- `frontend/src/components/`: reusable UI components.
- `frontend/src/pages/`: app pages such as dashboard, history, report, and home.
- `frontend/src/services/`: API calling logic.
- `docs/`: supporting documentation.
- `reports/`: generated project reports, metrics, and demo outputs.
- `src/`: older or research-focused PPG pipeline modules.
- `tests/`: automated tests.
- `docker-compose.yml`: root-level compose file for services.
- `docker-compose.multimodal.yml`: full multimodal backend/frontend Docker setup in this repo.

---

# 14. Step-by-Step Development Plan

## Phase 1: Build Backend FastAPI Skeleton

Create the FastAPI app, health endpoint, CORS setup, and route structure.

Goal:

```text
GET /health returns status ok.
```

## Phase 2: Add Signal Upload and PPG Analysis

Add CSV upload, parse the PPG signal, clean the waveform, detect peaks, estimate heart rate, and calculate signal quality.

Goal:

```text
POST /analyze-signal returns signal risk score and signal quality.
```

## Phase 3: Add Patient Vitals Form and Tabular Scoring

Accept vitals such as age, BP, heart rate, BMI, SpO2, sleep, activity, smoking, diabetes, and hypertension.

Goal:

```text
POST /analyze-tabular returns risk factors and tabular risk score.
```

## Phase 4: Add Symptom Analysis

Analyze symptom text for keywords and warning combinations.

Goal:

```text
POST /analyze-text returns symptoms found, severity, and warning flags.
```

## Phase 5: Add Report Image OCR

Allow image upload and extract useful text using OCR.

Goal:

```text
POST /analyze-image returns OCR text, extracted values, and image risk score.
```

## Phase 6: Add Multimodal Fusion Score

Combine signal, tabular, text, and image scores using transparent weights.

Goal:

```text
POST /multimodal-risk returns final score and category.
```

## Phase 7: Add Explanations and Alerts

Generate doctor-friendly and patient-friendly summaries. Add emergency warning pattern detection.

Goal:

```text
System explains why the score changed and warns safely when urgent patterns appear.
```

## Phase 8: Add React Dashboard

Build the UI for uploads, forms, charts, risk cards, summaries, and reports.

Goal:

```text
User can run the full analysis from a browser.
```

## Phase 9: Add History and Trend Analysis

Store readings in SQLite and compare current values with previous readings.

Goal:

```text
System can say whether risk, BP, HR, or sleep is increasing or decreasing.
```

## Phase 10: Add PDF Report Generation

Create a report that includes risk score, inputs, explanations, summaries, and limitations.

Goal:

```text
User can download a professional demo report.
```

## Phase 11: Add Docker

Create backend and frontend Dockerfiles and a compose file.

Goal:

```text
The full project starts with one Docker command.
```

## Phase 12: Write README and Final Documentation

Document the project clearly for GitHub, interviews, and hackathons.

Goal:

```text
Anyone can understand, run, and explain the project.
```

---

# 15. Risk Scoring Logic

Risk scoring should be simple, transparent, and educational.

## Signal Risk

Signal risk can increase when:

- Signal quality is low
- Heart rate estimate is high
- Peak pattern is irregular
- Noise level is high
- PPG waveform is too flat or unstable

Important:

Low signal quality should increase uncertainty. It should not automatically mean the patient is medically high risk.

## Tabular Risk

Tabular risk can increase when:

- Systolic BP is high
- Diastolic BP is high
- SpO2 is low
- Sleep is low
- BMI is high
- Heart rate is very high or very low
- Smoking history is present
- Diabetes history is present
- Hypertension history is present

## Text Risk

Text risk can increase based on symptom severity.

Examples:

- Mild fatigue gives a low score.
- Dizziness gives a medium score.
- Chest pain plus shortness of breath gives an emergency warning pattern.

## Image Risk

Image/report risk can increase when:

- OCR extracts abnormal values
- Report text contains warning phrases
- ECG/report notes mention concerning findings
- Extracted BP, HR, or SpO2 values are outside expected ranges

Image confidence can decrease when:

- The image is blurry
- OCR fails
- Important values are missing
- The report is unclear

## Final Score

Use weighted late fusion:

```text
Final Risk Score =
0.35 x Signal Risk Score +
0.30 x Tabular Risk Score +
0.20 x Symptom Risk Score +
0.15 x Image/Report Risk Score
```

## Risk Categories

```text
0-25: Low Risk
26-50: Mild Risk
51-75: Moderate Risk
76-100: High Risk
```

These categories are educational risk bands. They are not medical diagnoses.

---

# 16. Alert Logic

Alert logic detects warning patterns that should be handled carefully.

Trigger an emergency warning if:

- Chest pain plus shortness of breath
- Systolic BP greater than 180
- Diastolic BP greater than 120
- SpO2 less than 90
- Fainting plus palpitations
- Severe dizziness plus very high BP

Important wording:

Do not say:

```text
You have a heart attack.
```

Say:

```text
Emergency warning pattern detected. Please seek immediate medical attention.
```

Why this matters:

The system can detect patterns, but it cannot confirm a diagnosis. Safe language protects users and keeps the project medically responsible.

---

# 17. Confidence Score Logic

Confidence depends on data quality and completeness.

Factors that increase confidence:

- PPG signal is clean
- Vitals are complete
- Symptom description is clear
- Report image is readable
- Multiple modalities are available
- Historical readings are present

Factors that reduce confidence:

- PPG signal is noisy
- Important vitals are missing
- Symptom text is too vague
- Report image is blurry
- OCR fails
- Only one modality is available

Example:

If all inputs are present and signal quality is high, confidence is high.

If PPG is missing and the image is blurry, confidence is lower.

Important:

Confidence means the system has enough usable data to explain its result. It does not mean the medical result is guaranteed correct.

---

# 18. PDF Report Explanation

The PDF report should contain:

- Patient details
- Medical disclaimer
- PPG signal chart
- Vitals summary
- Symptom analysis
- OCR findings
- Risk score
- Risk category
- Confidence score
- Modality contribution
- Doctor summary
- Patient summary
- Recommendations
- Limitations

Why PDF reports are useful:

- Easy to share
- Good for demos
- Looks professional
- Shows the complete AI pipeline
- Helps hackathon judges understand the system quickly
- Helps interviewers see full-stack thinking

The report must include the safety disclaimer:

```text
This system is for educational and research purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment.
```

---

# 19. How to Run Without Docker

## Backend

Open a terminal:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

OCR note:

For real OCR with `pytesseract`, the Tesseract OCR executable must also be installed on the computer. If it is missing, the project can still run with demo or fallback behavior depending on implementation.

## Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

If the backend URL changes, configure the frontend API URL using an environment variable such as:

```text
VITE_API_URL=http://localhost:8000
```

---

# 20. How to Run With Docker

## General Command

```bash
docker-compose up --build
```

or, with newer Docker:

```bash
docker compose up --build
```

This builds and starts the configured services.

## Full Multimodal Docker Command For This Repo

This repo includes a full multimodal compose file:

```bash
docker compose -f docker-compose.multimodal.yml up --build
```

Backend:

```text
http://localhost:8000
```

Frontend in Docker:

```text
http://localhost:8080
```

API docs:

```text
http://localhost:8000/docs
```

Local development frontend without Docker:

```text
http://localhost:5173
```

## Stopping Docker

Press `Ctrl+C` in the terminal, then run:

```bash
docker compose -f docker-compose.multimodal.yml down
```

The compose file can also use a Docker volume to store SQLite history so readings can persist across container restarts.

---

# 21. How to Explain This Project in Interviews

## Question: "Tell me about your project."

Answer:

CardioTwin AI is a multimodal healthcare AI project where I combine different types of health data such as PPG signals, patient vitals, symptoms, and medical report images. The goal is to generate an explainable cardiovascular risk score. I built separate modules for signal processing, tabular risk scoring, symptom analysis, OCR-based report reading, and multimodal fusion. Instead of relying on only one input, the system combines all available inputs and explains which factors influenced the final score. I also added safety disclaimers because this is not a medical diagnosis tool.

## Question: "Why multimodal AI?"

Answer:

Healthcare decisions are not based on one data type. A doctor checks vitals, symptoms, reports, history, and sometimes wearable signals. Multimodal AI follows the same idea by combining multiple sources of information for a better and more explainable risk overview.

## Question: "Why rule-based plus ML hybrid?"

Answer:

In healthcare, real clinical datasets are hard to access and require validation. So I used rule-based scoring for safety and explainability, and kept the architecture ready for ML models like Random Forest or XGBoost when real labeled data is available.

## Question: "Why Docker?"

Answer:

Docker makes the project easy to run on any system. It packages backend, frontend, and dependencies so the project works consistently for demos, deployment, and team collaboration.

## Question: "What makes this project responsible?"

Answer:

The system clearly says it is educational and not a diagnosis tool. It uses explainable scoring, confidence indicators, warning language instead of diagnosis language, and limitations in the report. It avoids claiming clinical accuracy without validated medical datasets.

## Question: "What was the hardest part?"

Answer:

The hardest part was designing the fusion pipeline so that each data type could be analyzed separately but still contribute to one final result. This required thinking about signal quality, missing inputs, explainability, and confidence instead of only producing a score.

---

# 22. Limitations

CardioTwin AI has important limitations:

- It is not a medical diagnosis system.
- It should not be used to treat or replace doctors.
- It uses synthetic or demo data if a real dataset is unavailable.
- Risk scores are educational.
- OCR may fail on blurry reports.
- PPG signals can be noisy.
- BP estimation from PPG is only an approximation unless clinically validated.
- Rule-based alerts are not doctor-confirmed diagnoses.
- Real-world use requires clinical validation.
- Real-world use requires privacy, security, ethics approval, and regulatory review.
- The model may not generalize across age groups, devices, skin tones, sensor types, or clinical conditions without proper validation.

The safest way to describe the project is:

```text
This is an educational multimodal health risk awareness system, not a diagnosis tool.
```

---

# 23. Future Scope

Future improvements can include:

- Real clinical dataset training
- ECG deep learning model
- Smartwatch integration
- Mobile app
- Doctor dashboard
- SHAP/LIME explainability
- Federated learning for privacy
- Cloud deployment
- Real-time monitoring
- Hospital EHR integration
- Better OCR layout understanding
- Personal baseline modeling
- Secure user authentication
- Data encryption
- Model monitoring dashboard
- Human-in-the-loop doctor review

These features would make the project more advanced, but clinical use would still require expert validation and compliance review.

---

# 24. Final Deliverable

The final deliverable is this file:

```text
CARDIOTWIN_PROJECT_GUIDE.md
```

This guide is designed to be:

- Beginner-friendly
- Detailed
- Written in simple language
- Properly structured
- Useful for GitHub
- Useful for interview preparation
- Useful for hackathon explanation
- Complete from problem statement to Docker deployment

The project should always display or include this disclaimer:

```text
This system is for educational and research purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment.
```

## Short Hackathon Pitch

CardioTwin AI is a multimodal health risk digital twin that combines wearable PPG signals, patient vitals, symptoms, report images, and historical readings. It analyzes each modality separately, fuses the results into an explainable cardiovascular risk score, shows confidence and warning patterns, and generates doctor-friendly and patient-friendly summaries. The system is built with FastAPI, React, SQLite, and Docker, and it is designed as an educational healthcare AI prototype, not a diagnosis system.

## Final Safety Reminder

This system is for educational and research purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment.

---

# 25. Drawbacks of the Previous Algorithm

The first version of the algorithm was useful for a demo because it was simple, transparent, and beginner-friendly. However, it had several drawbacks.

## 25.1 Fixed Fusion Weights Could Dilute Risk

The previous fusion formula used fixed weights:

```text
0.35 signal + 0.30 tabular + 0.20 text + 0.15 image
```

This is easy to explain, but it can be unfair when some inputs are missing. For example, if only vitals are available, the old algorithm could multiply the vitals score by only `0.30`, making the final score look lower than it should.

## 25.2 Missing Data Was Treated Too Simply

Missing data should reduce confidence, not automatically reduce risk. A missing report image does not mean the patient is safer. It only means the system has less evidence.

## 25.3 Noisy PPG Could Affect Risk Too Strongly

The old PPG logic used signal quality, heart rate, and peak detection, but it did not strongly separate clean peak intervals from implausible peak intervals. A noisy signal could produce unstable heart-rate or BP-like estimates.

## 25.4 Symptom Matching Was Keyword-Based

The earlier text model matched words directly. This can create false positives.

Example:

```text
No chest pain or shortness of breath.
```

A simple keyword model may still detect `chest pain` and `shortness of breath`, even though the user denied those symptoms.

## 25.5 Emergency Combinations Needed Stronger Handling

Some symptom combinations matter more than individual symptoms. For example, `chest pain + shortness of breath` should trigger a stronger warning pattern than either phrase alone.

## 25.6 Demo OCR Could Look Too Confident

If no image was uploaded, the image model could fall back to demo report text. This is useful for demos, but it should not be treated with the same confidence as a real uploaded report.

---

# 26. Improved Algorithm Used Now

The improved algorithm is still transparent and rule-based, but it is more reliable and safer for an educational healthcare AI demo.

## 26.1 Reliability-Adjusted Late Fusion

Instead of using fixed weights directly, the new fusion algorithm calculates effective weights based on available evidence and confidence.

Concept:

```text
configured_weight = original modality weight
quality_factor = modality confidence and evidence quality
effective_weight = configured_weight x quality_factor
normalized_effective_weight = effective_weight / sum(all available effective weights)
```

This means:

- Missing modalities do not falsely lower the risk score.
- Low-quality modalities contribute less.
- Confidence explains when evidence is incomplete.
- The final score is based on available usable evidence.

Example:

If only vitals are available, tabular data can receive close to `100%` of the effective fusion weight, while missing signal/text/image inputs reduce confidence instead of reducing risk.

## 26.2 Safety Escalation Floor

The fusion engine now applies a safety floor when emergency warning patterns are detected.

Example:

```text
Chest pain + shortness of breath -> emergency warning pattern
```

The system does not diagnose the condition. It only says:

```text
Emergency warning pattern detected. Please seek immediate medical attention.
```

This makes the algorithm safer because urgent warning patterns are not hidden inside an average score.

## 26.3 Better PPG Signal Reliability

The PPG model now checks:

- Physiologically plausible peak intervals
- Rejected interval ratio
- Rhythm irregularity from interval variation
- Heart-rate plausibility
- Signal quality before trusting BP approximation

The BP estimate now clearly states that it is an educational approximation, not a clinical BP measurement.

## 26.4 Improved Text Understanding

The symptom model now supports simple negation detection.

Example:

```text
No chest pain or shortness of breath.
```

The model can now store these as negated symptoms instead of active warning symptoms.

It also detects important symptom combinations such as:

- Chest pain + breathing difficulty
- Fainting + palpitations

## 26.5 Better Tabular Safety Rules

The vitals model now includes safety floors for:

- Very high blood pressure
- Low oxygen saturation
- Stage 2 hypertension range

It also reports:

- Raw risk score
- Final risk score after safety floor
- Input completeness
- Missing critical fields
- Whether a safety floor was applied

## 26.6 More Honest OCR Confidence

The image model now reduces confidence when demo/fallback report text is used. It also gives stronger attention to OCR terms such as ischemia, STEMI, myocardial infarction, or acute coronary phrases, while still avoiding diagnosis claims.

---

# 27. Differentiation of CardioTwin AI

CardioTwin AI is different from a normal health-risk calculator because it is multimodal, explainable, reliability-aware, and full-stack.

## 27.1 Compared With a Basic BMI/BP Calculator

A normal calculator may only use BMI or blood pressure.

CardioTwin AI uses:

- PPG signal
- Vitals
- Symptoms
- Report image/OCR
- Historical readings
- Confidence scoring
- Explainable fusion

## 27.2 Compared With a Single ML Model

A single ML model often gives one prediction without clearly showing why.

CardioTwin AI separates the pipeline:

```text
Signal model -> Tabular model -> Text model -> Image model -> Fusion model -> Explanation
```

This makes the system easier to debug, explain, and improve.

## 27.3 Compared With a Chatbot-Only Health Assistant

A chatbot mainly understands text.

CardioTwin AI combines text with structured vitals, sensor signals, reports, charts, alerts, and PDF generation.

## 27.4 Compared With a Wearable-Only App

A wearable app may focus on heart rate or activity.

CardioTwin AI adds:

- Symptoms
- BP and SpO2
- Medical report OCR
- Doctor summary
- Patient summary
- Modality contribution
- Risk confidence

## 27.5 Key Technical Differentiators

The project demonstrates:

- Reliability-adjusted late fusion
- Safety-aware emergency pattern handling
- Signal quality-aware PPG analysis
- Negation-aware symptom matching
- OCR-based report extraction
- SQLite longitudinal health memory
- React dashboard
- FastAPI ML backend
- Docker deployment
- Responsible AI disclaimers

## 27.6 Best Interview Differentiation Statement

A strong way to explain the differentiation is:

```text
Most beginner healthcare AI projects use one dataset and one prediction model. CardioTwin AI is different because it behaves like a small healthcare AI system. It accepts multiple data types, analyzes each one separately, adjusts fusion weights based on reliability, explains the top risk drivers, detects emergency warning patterns safely, stores history, and generates doctor-friendly and patient-friendly summaries. It is not a diagnosis tool; it is an educational multimodal risk-awareness digital twin.
```
---

# 28. Making CardioTwin Useful for Medical Practitioners and Common People

CardioTwin AI should support two very different audiences:

- Medical practitioners who need structured, reviewable decision-support information.
- Common people who need simple, safe, non-alarming explanations.

The system must not use the same language for both audiences. A clinician can understand terms like triage, SpO2, modality confidence, OCR limitation, and risk drivers. A common user needs plain language such as what the result means, what to do next, and when to seek urgent help.

## 28.1 Medical Practitioner Mode

Practitioner mode is called `Clinical Assist` in the app.

It is designed to help with:

- Triage support
- Quick patient review
- Summarizing multimodal inputs
- Highlighting abnormal vitals and symptoms
- Showing data quality limitations
- Creating a handoff note
- Preparing questions for clinical review

It should show:

- Risk score and risk category
- Confidence score and confidence reason
- BP, HR, SpO2, BMI, age, and gender snapshot
- PPG reliability and signal quality
- Matched symptoms and warning patterns
- OCR/report extracted values
- Top risk drivers
- Missing modalities
- Suggested review questions
- Recommended practitioner actions

Example practitioner output:

```text
Clinical assist priority: Prompt clinical review suggested.
Patient snapshot: BP 162/104, HR 94, SpO2 95, BMI 29.8.
Risk result: 72/100, Moderate Risk, confidence 76/100.
Top drivers: elevated BP, low sleep, hypertension history, dizziness.
Suggested review: confirm current symptoms, repeat BP with validated device, review medications and history, inspect original report if OCR drove risk.
```

Important boundary:

This mode assists review. It does not diagnose, prescribe, or replace clinical judgment.

## 28.2 Common User Mode

Common user mode is called `Plain-Language Guidance` in the app.

It is designed to help users understand:

- What the score roughly means
- Whether there are warning signs
- What practical next step to take
- When to seek urgent medical help
- Why confidence may be low

It should avoid:

- Complex medical jargon
- Diagnosis claims
- Fear-based wording
- Treatment instructions
- False reassurance

Example common-user output:

```text
Your current educational risk score is 72/100. This means your submitted readings show some higher-attention signals. This does not mean you have a disease. Repeat unusual readings if possible and speak with a healthcare professional, especially if symptoms continue or worsen.
```

Emergency wording should be safe and direct:

```text
Emergency warning pattern detected. Please seek immediate medical attention.
```

It should not say:

```text
You are having a heart attack.
```

## 28.3 How the Improved Algorithm Supports Both Audiences

The improved backend now returns two audience-specific objects:

```text
clinician_assist
patient_guidance
```

It also returns:

```text
audience_modes.medical_practitioner
audience_modes.common_user
```

`clinician_assist` contains structured practitioner support:

- `triage_priority`
- `clinical_snapshot`
- `key_findings`
- `top_modalities`
- `data_quality`
- `suggested_review_questions`
- `recommended_actions`
- `handoff_note`

`patient_guidance` contains plain-language support:

- `simple_status`
- `what_it_means`
- `what_to_do_now`
- `when_to_seek_help`
- `confidence_note`
- `not_a_diagnosis`

## 28.4 Why This Differentiates the Project

Many healthcare AI demos produce only one score. CardioTwin AI now produces audience-aware outputs.

For practitioners, it behaves like a structured clinical review assistant.

For common users, it behaves like a plain-language risk-awareness guide.

This makes the project stronger for:

- Hackathon judging
- Healthcare AI portfolio demos
- Interview explanations
- Patient education demos
- Clinical workflow discussions

## 28.5 Best Interview Explanation

```text
I improved CardioTwin AI so it supports two audiences. For medical practitioners, it generates a structured clinical-assist summary with triage priority, vitals snapshot, warning flags, data quality, and review questions. For common users, it generates plain-language guidance explaining what the score means, what to do next, and when to seek urgent help. The system still clearly states that it is not a diagnosis tool and must not replace professional medical care.
```