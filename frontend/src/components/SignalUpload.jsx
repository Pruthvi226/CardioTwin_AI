import { Upload } from "lucide-react";

export default function SignalUpload({ file, onFileChange, result }) {
  return (
    <section className="panel">
      <div className="panel-title-row">
        <h3>PPG Signal CSV</h3>
        <span>{result?.reliability || "Demo ready"}</span>
      </div>
      <label className="file-control">
        <Upload size={18} aria-hidden="true" />
        <input
          type="file"
          accept=".csv,.txt"
          onChange={(event) => onFileChange(event.target.files?.[0] || null)}
        />
        <span>{file?.name || "Choose signal file"}</span>
      </label>
      <div className="metric-row compact">
        <span>Quality</span>
        <strong>{result?.quality_score ?? "--"}</strong>
        <span>Estimated HR</span>
        <strong>{result?.heart_rate_estimate ?? "--"} bpm</strong>
      </div>
    </section>
  );
}

