import { Mic } from "lucide-react";
import { useState } from "react";

export default function VoiceSymptomInput({ onTranscript }) {
  const [status, setStatus] = useState("Ready");

  function startListening() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setStatus("Voice unavailable");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.onstart = () => setStatus("Listening");
    recognition.onerror = () => setStatus("Voice error");
    recognition.onend = () => setStatus("Ready");
    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript || "";
      if (transcript) onTranscript(transcript);
    };
    recognition.start();
  }

  return (
    <button className="ghost-button voice-button" type="button" onClick={startListening} title="Speak symptoms">
      <Mic size={17} aria-hidden="true" />
      {status}
    </button>
  );
}

