import { FileText } from "lucide-react";
import VoiceSymptomInput from "./VoiceSymptomInput.jsx";

export default function SymptomInput({ notes, onChange, result }) {
  function update(name, value) {
    onChange({ ...notes, [name]: value });
  }

  function appendTranscript(transcript) {
    const trimmed = transcript.trim();
    if (!trimmed) return;
    const current = notes.symptoms?.trim() || "";
    update("symptoms", current ? `${current} ${trimmed}` : trimmed);
  }

  return (
    <section className="panel">
      <div className="panel-title-row">
        <h3>Symptoms & Notes</h3>
        <span>{result?.symptom_severity || "Not run"}</span>
      </div>
      <label className="textarea-field">
        <span>Symptoms</span>
        <textarea value={notes.symptoms} onChange={(event) => update("symptoms", event.target.value)} />
      </label>
      <label className="textarea-field">
        <span>Lifestyle notes</span>
        <textarea value={notes.lifestyle_notes} onChange={(event) => update("lifestyle_notes", event.target.value)} />
      </label>
      <div className="symptom-tools">
        <VoiceSymptomInput onTranscript={appendTranscript} />
      </div>
      <div className="note-chip">
        <FileText size={16} aria-hidden="true" />
        <span>{result?.matched_symptoms?.join(", ") || "No symptom analysis yet"}</span>
      </div>
    </section>
  );
}

