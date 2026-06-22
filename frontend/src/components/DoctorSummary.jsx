export default function DoctorSummary({ summary, assist, disclaimer }) {
  const actions = assist?.recommended_actions || [];
  const questions = assist?.suggested_review_questions || [];
  const findings = assist?.key_findings || [];

  return (
    <section className="panel summary-panel">
      <div className="panel-title-row">
        <h3>Clinical Assist</h3>
        <span>{assist?.triage_priority || "Structured"}</span>
      </div>
      <pre>{summary || "Clinical assist summary will appear after analysis."}</pre>
      {assist?.handoff_note && <p className="patient-text">{assist.handoff_note}</p>}
      {findings.length > 0 && (
        <div className="recommendation-list">
          {findings.slice(0, 4).map((item) => <p key={item}>{item}</p>)}
        </div>
      )}
      {questions.length > 0 && (
        <div className="recommendation-list">
          {questions.slice(0, 4).map((item) => <p key={item}>{item}</p>)}
        </div>
      )}
      {actions.length > 0 && (
        <div className="recommendation-list">
          {actions.slice(0, 4).map((item) => <p key={item}>{item}</p>)}
        </div>
      )}
      <p className="small-muted">{disclaimer}</p>
    </section>
  );
}