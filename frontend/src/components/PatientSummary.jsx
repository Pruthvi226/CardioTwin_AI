export default function PatientSummary({ summary, guidance, flags, disclaimer }) {
  const steps = guidance?.what_to_do_now || [];
  const seekHelp = guidance?.when_to_seek_help || [];

  return (
    <section className="panel summary-panel patient-panel">
      <div className="panel-title-row">
        <h3>Plain-Language Guidance</h3>
        <span>{flags?.length || 0} flags</span>
      </div>
      <p className="patient-text">{summary || "Patient-friendly warning insights will appear after analysis."}</p>
      {guidance?.what_it_means && <p className="patient-text">{guidance.what_it_means}</p>}
      {steps.length > 0 && (
        <div className="recommendation-list">
          {steps.map((item) => <p key={item}>{item}</p>)}
        </div>
      )}
      {seekHelp.length > 0 && (
        <div className="recommendation-list">
          {seekHelp.slice(0, 4).map((item) => <p key={item}>{item}</p>)}
        </div>
      )}
      <p className="small-muted">{disclaimer}</p>
    </section>
  );
}