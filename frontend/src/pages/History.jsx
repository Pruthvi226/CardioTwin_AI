import { useEffect, useState } from "react";
import TrendCharts from "../components/TrendCharts.jsx";
import { analyzeTrends, compareLastReading, getHistory } from "../services/api.js";

export default function History() {
  const [trend, setTrend] = useState(null);
  const [history, setHistory] = useState([]);
  const [comparison, setComparison] = useState(null);

  useEffect(() => {
    async function load() {
      const [trendResult, historyResult, compareResult] = await Promise.all([
        analyzeTrends(),
        getHistory(20),
        compareLastReading(),
      ]);
      setTrend(trendResult);
      setHistory(historyResult.readings || []);
      setComparison(compareResult);
    }
    load().catch(() => {});
  }, []);

  return (
    <main className="results-column">
      <TrendCharts data={trend?.chart_data || []} />
      <section className="panel">
        <div className="panel-title-row">
          <h3>Risk Change</h3>
          <span>{comparison?.risk_delta ?? 0}</span>
        </div>
        <p>{comparison?.explanation || trend?.explanation || "Trend analysis is loading."}</p>
      </section>
      <section className="panel">
        <div className="panel-title-row">
          <h3>Saved Readings</h3>
          <span>{history.length}</span>
        </div>
        <div className="history-list">
          {history.length === 0 ? (
            <p>No saved readings yet.</p>
          ) : (
            history.map((item) => (
              <div className="history-row" key={item.id}>
                <strong>{item.risk_category}</strong>
                <span>{item.final_risk_score}/100</span>
                <small>{item.created_at}</small>
              </div>
            ))
          )}
        </div>
      </section>
    </main>
  );
}

