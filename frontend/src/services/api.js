import axios from "axios";

function defaultApiBaseUrl() {
  if (typeof window === "undefined") {
    return "http://127.0.0.1:8000";
  }

  const { port } = window.location;
  const isViteDev = port === "5173" || port === "5174";
  return isViteDev ? "http://127.0.0.1:8000" : "/api";
}

const API_BASE_URL = import.meta.env.VITE_API_URL || defaultApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

function uploadBody(file, fieldName = "file") {
  if (!file) return undefined;
  const formData = new FormData();
  formData.append(fieldName, file);
  return formData;
}

export async function analyzeSignal(file) {
  const response = await api.post("/analyze-signal", uploadBody(file, "file"));
  return response.data;
}

export async function analyzeTabular(patient) {
  const response = await api.post("/analyze-tabular", patient);
  return response.data;
}

export async function analyzeText(notes) {
  const response = await api.post("/analyze-text", notes);
  return response.data;
}

export async function analyzeImage(file) {
  const response = await api.post("/analyze-image", uploadBody(file, "image"));
  return response.data;
}

export async function calculateFusion(payload) {
  const response = await api.post("/multimodal-risk", payload);
  return response.data;
}

export async function getLiveSimulation() {
  const response = await api.get("/live-simulation");
  return response.data;
}

export async function checkAlerts(payload) {
  const response = await api.post("/check-alerts", payload);
  return response.data;
}

export async function generateSummary(payload) {
  const response = await api.post("/generate-summary", payload);
  return response.data;
}

export async function analyzeTrends(records) {
  const response = await api.post("/analyze-trends", records ? { records } : {});
  return response.data;
}

export async function detectAnomaly(payload) {
  const response = await api.post("/detect-anomaly", payload);
  return response.data;
}

export async function generateRecommendations(payload) {
  const response = await api.post("/generate-recommendations", payload);
  return response.data;
}

export async function getDemoPatients() {
  const response = await api.get("/demo-patients");
  return response.data;
}

export async function saveReading(payload) {
  const response = await api.post("/save-reading", payload);
  return response.data;
}

export async function getHistory(limit = 25) {
  const response = await api.get("/history", { params: { limit } });
  return response.data;
}

export async function compareLastReading() {
  const response = await api.get("/compare-last-reading");
  return response.data;
}

export async function chatWithTwin(question, context) {
  const response = await api.post("/chat", { question, context });
  return response.data;
}

export async function generateReport(payload) {
  const response = await api.post("/generate-report", payload, { responseType: "blob" });
  const disposition = response.headers?.["content-disposition"] || "";
  const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
  return {
    blob: response.data,
    filename: filenameMatch?.[1] || "multimodal_health_risk_report.pdf",
  };
}