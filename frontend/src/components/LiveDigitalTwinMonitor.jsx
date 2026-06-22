import { Activity, HeartPulse } from "lucide-react";
import { useEffect, useState } from "react";
import { getLiveSimulation } from "../services/api.js";

export default function LiveDigitalTwinMonitor() {
  const [reading, setReading] = useState(null);

  useEffect(() => {
    let active = true;
    async function tick() {
      try {
        const next = await getLiveSimulation();
        if (active) setReading(next);
      } catch {
        if (active) setReading(null);
      }
    }
    tick();
    const interval = window.setInterval(tick, 4000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  return (
    <section className="panel live-panel">
      <div className="panel-title-row">
        <h3>Live Digital Twin</h3>
        <span>{reading?.risk_level || "Syncing"}</span>
      </div>
      <div className="live-grid">
        <Metric icon={<HeartPulse size={18} />} label="Heart rate" value={`${reading?.heart_rate ?? "--"} bpm`} />
        <Metric icon={<Activity size={18} />} label="SpO2" value={`${reading?.spo2 ?? "--"}%`} />
        <Metric label="Signal quality" value={`${reading?.ppg_signal_quality ?? "--"}%`} />
        <Metric
          label="BP estimate"
          value={
            reading?.estimated_bp
              ? `${reading.estimated_bp.systolic}/${reading.estimated_bp.diastolic}`
              : "--"
          }
        />
      </div>
      <p className="small-muted">{reading?.timestamp ? new Date(reading.timestamp).toLocaleString() : "Waiting for reading"}</p>
    </section>
  );
}

function Metric({ icon, label, value }) {
  return (
    <div className="live-metric">
      <span>{icon}{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

