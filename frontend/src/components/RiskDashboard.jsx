export default function RiskDashboard({ fusion, signal, tabular, alert }) {
  const score = fusion?.final_risk_score ?? "--";
  const category = fusion?.risk_category ?? "Awaiting analysis";
  const bpTrend = fusion?.blood_pressure_trend_prediction || tabular?.bp_trend_prediction || signal?.bp_prediction?.trend || "--";
  const bpEstimate = signal?.bp_prediction ? `${signal.bp_prediction.systolic}/${signal.bp_prediction.diastolic}` : "--";

  return (
    <section className="risk-grid expanded-risk-grid">
      <article className="risk-card primary-risk">
        <span>Final Risk Score</span>
        <strong>{score}</strong>
        <p>{category}</p>
      </article>
      <article className="risk-card">
        <span>Risk Category</span>
        <strong>{category}</strong>
        <p>{fusion?.final_explanation || fusion?.explanation || "Run analysis to generate explanation."}</p>
      </article>
      <article className="risk-card">
        <span>BP Estimate</span>
        <strong>{bpEstimate}</strong>
        <p>{bpTrend}</p>
      </article>
      <article className="risk-card">
        <span>Signal Quality</span>
        <strong>{signal?.quality_score ?? "--"}</strong>
        <p>{signal?.reliability || "Awaiting PPG analysis"}</p>
      </article>
      <article className="risk-card">
        <span>Prediction Confidence</span>
        <strong>{fusion?.confidence_score ?? "--"}</strong>
        <p>{fusion?.confidence_reason || "Confidence depends on completeness and input quality."}</p>
      </article>
      <article className="risk-card">
        <span>Alert Status</span>
        <strong>{alert?.alert_level || "--"}</strong>
        <p>{alert?.recommended_action || "No alert check has been generated yet."}</p>
      </article>
    </section>
  );
}