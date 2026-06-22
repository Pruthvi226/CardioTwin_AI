import { FlaskConical } from "lucide-react";

export default function SyntheticPatientSelector({ patients, onSelect }) {
  return (
    <section className="panel">
      <div className="panel-title-row">
        <h3>Demo Cases</h3>
        <span>{patients.length}</span>
      </div>
      <div className="demo-case-grid">
        {patients.map((patient) => (
          <button className="case-button" key={patient.id} onClick={() => onSelect(patient)} title={patient.expected_output}>
            <FlaskConical size={16} aria-hidden="true" />
            <span>{patient.name}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

