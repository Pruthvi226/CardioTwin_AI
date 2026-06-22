export default function Home({ onStart, disclaimer }) {
  return (
    <main className="home-page">
      <section className="home-hero">
        <p className="eyebrow">Educational multimodal healthcare AI</p>
        <h2>CardioTwin AI: Multimodal Health Risk Digital Twin</h2>
        <p>
          CardioTwin AI fuses PPG signals, patient vitals, symptoms, medical report OCR, alerts,
          trends, and summaries into explainable cardiovascular risk insights.
        </p>
        <button className="primary-button" onClick={onStart}>Start Analysis</button>
      </section>
      <section className="disclaimer-strip">{disclaimer}</section>
    </main>
  );
}