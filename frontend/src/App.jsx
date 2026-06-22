import { useState } from "react";
import Dashboard from "./pages/Dashboard.jsx";
import History from "./pages/History.jsx";
import Home from "./pages/Home.jsx";
import Report from "./pages/Report.jsx";
import { generateReport } from "./services/api.js";

const DISCLAIMER =
  "This system is for educational and research purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment.";

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [latestResults, setLatestResults] = useState(null);

  async function downloadLatestReport() {
    if (!latestResults?.fusion) return;
    const { blob, filename } = await generateReport({ fusion_result: latestResults.fusion, component_results: latestResults });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">CardioTwin AI</p>
          <h1>Multimodal Health Risk Digital Twin</h1>
        </div>
        <nav className="app-nav" aria-label="Main navigation">
          {[
            ["home", "Home"],
            ["dashboard", "Dashboard"],
            ["history", "History"],
            ["report", "Report"],
          ].map(([id, label]) => (
            <button className={page === id ? "nav-button active" : "nav-button"} onClick={() => setPage(id)} key={id}>
              {label}
            </button>
          ))}
        </nav>
        <div className="status-pill">Research demo</div>
      </header>
      <div className="disclaimer-strip">{DISCLAIMER}</div>
      {page === "home" && <Home onStart={() => setPage("dashboard")} disclaimer={DISCLAIMER} />}
      {page === "dashboard" && <Dashboard disclaimer={DISCLAIMER} onResultsChange={setLatestResults} />}
      {page === "history" && <History />}
      {page === "report" && <Report results={latestResults} onDownload={downloadLatestReport} disclaimer={DISCLAIMER} />}
    </div>
  );
}