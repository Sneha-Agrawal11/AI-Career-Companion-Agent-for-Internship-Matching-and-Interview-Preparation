const ScoreBar = ({ label, value }) => {
  const normalized = Number.isFinite(value) ? Math.max(0, Math.min(100, value)) : 0;
  return (
    <div className="score-row">
      <div className="score-head">
        <span>{label}</span>
        <span>{normalized.toFixed(1)}%</span>
      </div>
      <div className="score-track" aria-hidden="true">
        <div className="score-fill" style={{ width: `${normalized}%` }} />
      </div>
    </div>
  );
};

export default ScoreBar;
