import DoctorSummary from "../components/DoctorSummary.jsx";
import PatientSummary from "../components/PatientSummary.jsx";
import ReportDownload from "../components/ReportDownload.jsx";

export default function Report({ results, onDownload, disclaimer }) {
  return (
    <main className="results-column">
      <section className="risk-grid">
        <article className="risk-card primary-risk">
          <span>Final Risk Score</span>
          <strong>{results?.fusion?.final_risk_score ?? "--"}</strong>
          <p>{results?.fusion?.risk_category || "No report generated yet"}</p>
        </article>
        <article className="risk-card">
          <span>Confidence</span>
          <strong>{results?.fusion?.confidence_score ?? "--"}</strong>
          <p>{results?.fusion?.confidence_reason || "Awaiting analysis"}</p>
        </article>
      </section>
      <DoctorSummary summary={results?.fusion?.doctor_summary} assist={results?.fusion?.clinician_assist} disclaimer={disclaimer} />
      <PatientSummary summary={results?.fusion?.patient_summary} guidance={results?.fusion?.patient_guidance} flags={results?.fusion?.warning_flags || []} disclaimer={disclaimer} />
      <div className="report-row">
        <ReportDownload disabled={!results?.fusion} onDownload={onDownload} />
      </div>
    </main>
  );
}

