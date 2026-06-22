const LABELS = {
  signal: "Signal",
  tabular: "Vitals",
  text: "Symptoms",
  image: "Report",
};

export default function ModalityContribution({ contributions }) {
  const entries = Object.entries(contributions);
  return (
    <section className="panel contribution-panel">
      <div className="panel-title-row">
        <h3>Modality Contribution</h3>
        <span>Late fusion</span>
      </div>
      <div className="bar-list">
        {entries.length === 0 ? (
          <p>No contribution data yet.</p>
        ) : (
          entries.map(([name, item]) => (
            <div className="bar-row" key={name}>
              <div className="bar-label">
                <span>{LABELS[name] || name}</span>
                <strong>{item.influence_percent}%</strong>
              </div>
              <div className="bar-track">
                <div className={`bar-fill bar-${name}`} style={{ width: `${Math.min(100, item.influence_percent)}%` }} />
              </div>
              <small>score {item.risk_score} x weight {item.weight}</small>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

