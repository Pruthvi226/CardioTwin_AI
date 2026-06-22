import { AlertTriangle } from "lucide-react";

export default function AlertBox({ alert }) {
  const level = alert?.alert_level || "Routine";
  return (
    <section className={`panel alert-box alert-${level.toLowerCase().replaceAll(" ", "-")}`}>
      <div className="panel-title-row">
        <h3>Alert Status</h3>
        <span>{level}</span>
      </div>
      <div className="alert-content">
        <AlertTriangle size={22} aria-hidden="true" />
        <p>{alert?.alert_message || "No alert analysis has been generated yet."}</p>
      </div>
      <div className="flag-list">
        {(alert?.emergency_flags || []).map((flag, index) => (
          <div className={`flag flag-${flag.severity}`} key={`${flag.label}-${index}`}>
            <strong>{flag.label}</strong>
            <span>{flag.severity}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

