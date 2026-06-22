function buildPath(data, key, width, height, padding) {
  if (!data.length) return "";
  const xs = data.map((point) => point.time);
  const ys = data.map((point) => point[key]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const xSpan = maxX - minX || 1;
  const ySpan = maxY - minY || 1;
  return data
    .map((point, index) => {
      const x = padding + ((point.time - minX) / xSpan) * (width - padding * 2);
      const y = height - padding - ((point[key] - minY) / ySpan) * (height - padding * 2);
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

export default function SignalChart({ data }) {
  const width = 640;
  const height = 260;
  const rawPath = buildPath(data, "raw", width, height, 28);
  const cleanPath = buildPath(data, "cleaned", width, height, 28);

  return (
    <section className="panel chart-panel">
      <div className="panel-title-row">
        <h3>Signal Quality Graph</h3>
        <span>{data.length ? `${data.length} pts` : "No data"}</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="PPG waveform">
        <rect x="0" y="0" width={width} height={height} rx="8" className="chart-bg" />
        <path d="M 28 210 L 612 210" className="axis-line" />
        <path d={rawPath} className="raw-line" />
        <path d={cleanPath} className="clean-line" />
      </svg>
      <div className="legend-row">
        <span><i className="legend raw" />Raw</span>
        <span><i className="legend clean" />Cleaned</span>
      </div>
    </section>
  );
}

