import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function TrendCharts({ data }) {
  const chartData = data?.length ? data : [];
  return (
    <section className="panel trend-panel">
      <div className="panel-title-row">
        <h3>Health Trends</h3>
        <span>{chartData.length} readings</span>
      </div>
      <div className="trend-chart">
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#dbe4df" />
            <XAxis dataKey="timestamp" hide />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="systolic_bp" stroke="#0f766e" strokeWidth={2} dot={false} name="Systolic BP" />
            <Line type="monotone" dataKey="heart_rate" stroke="#ad5c35" strokeWidth={2} dot={false} name="HR" />
            <Line type="monotone" dataKey="spo2" stroke="#3b70b2" strokeWidth={2} dot={false} name="SpO2" />
            <Line type="monotone" dataKey="risk_score" stroke="#7b679e" strokeWidth={2} dot={false} name="Risk" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

