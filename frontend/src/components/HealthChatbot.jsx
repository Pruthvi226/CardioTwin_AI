import { Send } from "lucide-react";
import { useState } from "react";
import { chatWithTwin } from "../services/api.js";

export default function HealthChatbot({ context }) {
  const [question, setQuestion] = useState("Why is my risk score this level?");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function ask() {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const response = await chatWithTwin(question, context);
      setAnswer(response.answer);
    } catch (error) {
      setAnswer(error.message || "Unable to answer from the current report.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel chatbot-panel">
      <div className="panel-title-row">
        <h3>Health Twin Chat</h3>
        <span>Report-grounded</span>
      </div>
      <div className="chat-row">
        <input value={question} onChange={(event) => setQuestion(event.target.value)} />
        <button className="primary-button icon-only" onClick={ask} disabled={loading} title="Ask">
          <Send size={18} aria-hidden="true" />
        </button>
      </div>
      <p className="chat-answer">{answer || "Ask about the current generated report."}</p>
    </section>
  );
}

