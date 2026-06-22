import { useEffect, useMemo, useState } from "react";
import { Activity, Play, RotateCcw, Save } from "lucide-react";
import AlertBox from "../components/AlertBox.jsx";
import DoctorSummary from "../components/DoctorSummary.jsx";
import HealthChatbot from "../components/HealthChatbot.jsx";
import ImageUpload from "../components/ImageUpload.jsx";
import LiveDigitalTwinMonitor from "../components/LiveDigitalTwinMonitor.jsx";
import ModalityContribution from "../components/ModalityContribution.jsx";
import PatientForm from "../components/PatientForm.jsx";
import PatientSummary from "../components/PatientSummary.jsx";
import ReportDownload from "../components/ReportDownload.jsx";
import RiskDashboard from "../components/RiskDashboard.jsx";
import SignalChart from "../components/SignalChart.jsx";
import SignalUpload from "../components/SignalUpload.jsx";
import SymptomInput from "../components/SymptomInput.jsx";
import SyntheticPatientSelector from "../components/SyntheticPatientSelector.jsx";
import TrendCharts from "../components/TrendCharts.jsx";
import {
  analyzeImage,
  analyzeSignal,
  analyzeTabular,
  analyzeText,
  analyzeTrends,
  calculateFusion,
  checkAlerts,
  detectAnomaly,
  generateRecommendations,
  generateReport,
  getDemoPatients,
  saveReading,
} from "../services/api.js";

const DEFAULT_PATIENT = {
  age: 48,
  gender: "Female",
  height: 168,
  weight: 78,
  heart_rate: 88,
  systolic_bp: 138,
  diastolic_bp: 86,
  spo2: 96,
  sleep_hours: 5.8,
  activity_level: "low",
  smoking_status: false,
  diabetes_history: false,
  hypertension_history: true,
  medication_status: "none",
  existing_risk_factors: "family_history",
};

const DEFAULT_NOTES = {
  symptoms: "Dizziness, fatigue, occasional palpitations",
  lifestyle_notes: "Low activity and poor sleep during the last week",
  medication_notes: "",
  doctor_notes: "",
};

export default function Dashboard({ disclaimer, onResultsChange }) {
  const [patient, setPatient] = useState(DEFAULT_PATIENT);
  const [notes, setNotes] = useState(DEFAULT_NOTES);
  const [signalFile, setSignalFile] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [demoPatients, setDemoPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState({
    signal: null,
    tabular: null,
    text: null,
    image: null,
    fusion: null,
    alert: null,
    recommendations: null,
    trend: null,
    anomaly: null,
  });

  function publish(next) {
    setResults(next);
    onResultsChange?.(next);
  }

  async function runAnalysis({ demo = false } = {}) {
    setLoading(true);
    setError("");
    try {
      const [signal, tabular, text, image] = await Promise.all([
        analyzeSignal(demo ? null : signalFile),
        analyzeTabular(patient),
        analyzeText(notes),
        analyzeImage(demo ? null : imageFile),
      ]);

      const fusion = await calculateFusion({
        signal_result: signal,
        tabular_result: tabular,
        text_result: text,
        image_result: image,
        patient,
      });

      const sharedPayload = { signal_result: signal, tabular_result: tabular, text_result: text, image_result: image, fusion_result: fusion, patient, symptoms: notes.symptoms };
      const [alert, recommendations, trend, anomaly] = await Promise.all([
        checkAlerts(sharedPayload),
        generateRecommendations(sharedPayload),
        analyzeTrends(),
        detectAnomaly({ current: { ...patient, signal_quality: signal.quality_score }, records: [] }),
      ]);

      const next = { signal, tabular, text, image, fusion, alert, recommendations, trend, anomaly };
      publish(next);
    } catch (analysisError) {
      setError(analysisError.message || "Analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  async function downloadReport() {
    if (!results.fusion) return;
    try {
      const { blob, filename } = await generateReport({
        fusion_result: results.fusion,
        component_results: {
          signal: results.signal,
          tabular: results.tabular,
          text: results.text,
          image: results.image,
          alert: results.alert,
          recommendations: results.recommendations,
          anomaly: results.anomaly,
        },
        patient,
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
    } catch (reportError) {
      setError(reportError.message || "Report export failed.");
    }
  }

  async function saveCurrentReading() {
    if (!results.fusion) return;
    try {
      await saveReading({ patient, signal_result: results.signal, fusion_result: results.fusion });
    } catch (saveError) {
      setError(saveError.message || "Unable to save reading.");
    }
  }

  function selectDemoPatient(demo) {
    setPatient({ ...DEFAULT_PATIENT, ...demo.vitals });
    setNotes({ ...DEFAULT_NOTES, symptoms: demo.symptoms, lifestyle_notes: demo.expected_output });
  }

  function resetDemo() {
    setPatient(DEFAULT_PATIENT);
    setNotes(DEFAULT_NOTES);
    setSignalFile(null);
    setImageFile(null);
    publish({ signal: null, tabular: null, text: null, image: null, fusion: null, alert: null, recommendations: null, trend: null, anomaly: null });
    setError("");
  }

  useEffect(() => {
    getDemoPatients().then((payload) => setDemoPatients(payload.demo_patients || [])).catch(() => setDemoPatients([]));
    runAnalysis({ demo: true });
  }, []);

  const warningFlags = useMemo(() => results.fusion?.warning_flags || [], [results.fusion]);
  const chatContext = useMemo(() => ({ ...results, patient }), [results, patient]);

  return (
    <main className="dashboard">
      <section className="input-column" aria-label="Health inputs">
        <div className="section-heading">
          <Activity size={20} aria-hidden="true" />
          <h2>Inputs</h2>
        </div>
        <LiveDigitalTwinMonitor />
        <SyntheticPatientSelector patients={demoPatients} onSelect={selectDemoPatient} />
        <SignalUpload file={signalFile} onFileChange={setSignalFile} result={results.signal} />
        <PatientForm patient={patient} onChange={setPatient} />
        <SymptomInput notes={notes} onChange={setNotes} result={results.text} />
        <ImageUpload file={imageFile} onFileChange={setImageFile} result={results.image} />
        <div className="action-row">
          <button className="primary-button" onClick={() => runAnalysis()} disabled={loading} title="Run multimodal analysis">
            <Play size={18} aria-hidden="true" />
            {loading ? "Analyzing" : "Run Analysis"}
          </button>
          <button className="ghost-button" onClick={() => runAnalysis({ demo: true })} disabled={loading} title="Run with demo inputs">
            <RotateCcw size={18} aria-hidden="true" />
            Demo
          </button>
          <button className="ghost-button" onClick={saveCurrentReading} disabled={!results.fusion || loading} title="Save reading">
            <Save size={18} aria-hidden="true" />
            Save
          </button>
          <button className="ghost-button" onClick={resetDemo} disabled={loading} title="Reset form values">
            <RotateCcw size={18} aria-hidden="true" />
            Reset
          </button>
        </div>
        {error && <div className="error-banner">{error}</div>}
      </section>

      <section className="results-column" aria-label="Health risk results">
        <RiskDashboard fusion={results.fusion} signal={results.signal} tabular={results.tabular} alert={results.alert} />
        <AlertBox alert={results.alert} />
        <div className="split-grid">
          <SignalChart data={results.signal?.chart || []} peaks={results.signal?.peaks || []} />
          <ModalityContribution contributions={results.fusion?.modality_contributions || {}} />
        </div>
        <TrendCharts data={results.trend?.chart_data || []} />
        <section className="panel recommendation-panel">
          <div className="panel-title-row">
            <h3>Personalized Health Coach</h3>
            <span>{results.anomaly?.severity || "ready"}</span>
          </div>
          <div className="recommendation-list">
            {(results.recommendations?.lifestyle_recommendations || ["Run analysis to generate recommendations."]).map((item) => <p key={item}>{item}</p>)}
            {(results.recommendations?.monitoring_recommendations || []).map((item) => <p key={item}>{item}</p>)}
          </div>
          <p className="small-muted">{results.anomaly?.explanation}</p>
        </section>
        <PatientSummary summary={results.fusion?.patient_summary} guidance={results.fusion?.patient_guidance} flags={warningFlags} disclaimer={disclaimer} />
        <DoctorSummary summary={results.fusion?.doctor_summary} assist={results.fusion?.clinician_assist} disclaimer={disclaimer} />
        <HealthChatbot context={chatContext} />
        <section className="panel warning-panel">
          <div className="panel-title-row">
            <h3>Warning Flags</h3>
            <span>{warningFlags.length}</span>
          </div>
          <div className="flag-list">
            {warningFlags.length === 0 ? (
              <p>No warning flags generated.</p>
            ) : (
              warningFlags.map((flag, index) => (
                <div className={`flag flag-${flag.severity || "info"}`} key={`${flag.label}-${index}`}>
                  <strong>{flag.label}</strong>
                  <span>{flag.detail}</span>
                </div>
              ))
            )}
          </div>
        </section>
        <div className="report-row">
          <ReportDownload disabled={!results.fusion} onDownload={downloadReport} />
        </div>
      </section>
    </main>
  );
}