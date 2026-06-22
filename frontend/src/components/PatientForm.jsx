const FIELD_GROUPS = [
  ["age", "Age", "number"],
  ["gender", "Gender", "select"],
  ["height", "Height cm", "number"],
  ["weight", "Weight kg", "number"],
  ["heart_rate", "Heart rate", "number"],
  ["systolic_bp", "Systolic BP", "number"],
  ["diastolic_bp", "Diastolic BP", "number"],
  ["spo2", "SpO2", "number"],
  ["sleep_hours", "Sleep hours", "number"],
  ["activity_level", "Activity", "select"],
];

export default function PatientForm({ patient, onChange }) {
  function updateField(name, value) {
    onChange({ ...patient, [name]: value });
  }

  function updateCheckbox(name, checked) {
    onChange({ ...patient, [name]: checked });
  }

  return (
    <section className="panel">
      <div className="panel-title-row">
        <h3>Patient Details</h3>
        <span>Vitals</span>
      </div>
      <div className="form-grid">
        {FIELD_GROUPS.map(([name, label, type]) => (
          <label key={name}>
            <span>{label}</span>
            {name === "gender" ? (
              <select value={patient[name]} onChange={(event) => updateField(name, event.target.value)}>
                <option>Female</option>
                <option>Male</option>
                <option>Other</option>
                <option>Prefer not to say</option>
              </select>
            ) : name === "activity_level" ? (
              <select value={patient[name]} onChange={(event) => updateField(name, event.target.value)}>
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
              </select>
            ) : (
              <input
                type={type}
                value={patient[name]}
                onChange={(event) => updateField(name, Number(event.target.value))}
              />
            )}
          </label>
        ))}
      </div>
      <div className="toggle-row">
        <label>
          <input
            type="checkbox"
            checked={Boolean(patient.smoking_status)}
            onChange={(event) => updateCheckbox("smoking_status", event.target.checked)}
          />
          Smoking
        </label>
        <label>
          <input
            type="checkbox"
            checked={Boolean(patient.diabetes_history)}
            onChange={(event) => updateCheckbox("diabetes_history", event.target.checked)}
          />
          Diabetes
        </label>
        <label>
          <input
            type="checkbox"
            checked={Boolean(patient.hypertension_history)}
            onChange={(event) => updateCheckbox("hypertension_history", event.target.checked)}
          />
          Hypertension
        </label>
      </div>
      <label className="full-field">
        <span>Existing risk factors</span>
        <input
          value={patient.existing_risk_factors}
          onChange={(event) => updateField("existing_risk_factors", event.target.value)}
        />
      </label>
    </section>
  );
}

