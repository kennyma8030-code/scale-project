import { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";

const API = "http://localhost:8000";

const SCALES = [
  "C major","G major","D major","A major","E major","B major",
  "F# major","C# major","F major","Bb major","Eb major",
  "Ab major","Db major","Gb major","Cb major",
];

function ScoreRing({ score, max = 7, size = 120 }) {
  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / max) * circumference;
  const color = score === max ? "#34d399" : score >= 5 ? "#fbbf24" : "#f87171";

  return (
    <svg width={size} height={size} className="score-ring">
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="rgba(255,255,255,0.06)"
        strokeWidth="6"
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth="6"
        strokeDasharray={circumference}
        strokeDashoffset={circumference - progress}
        strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        className="ring-progress"
      />
      <text
        x={size / 2}
        y={size / 2 - 6}
        textAnchor="middle"
        dominantBaseline="central"
        className="ring-score"
      >
        {score}/{max}
      </text>
      <text
        x={size / 2}
        y={size / 2 + 16}
        textAnchor="middle"
        dominantBaseline="central"
        className="ring-label"
      >
        intonation
      </text>
    </svg>
  );
}

function StatCard({ label, value, unit, description }) {
  return (
    <div className="stat-card">
      <span className="stat-label">{label}</span>
      <span className="stat-value">
        {typeof value === "number" ? value.toFixed(1) : value}
        {unit && <span className="stat-unit">{unit}</span>}
      </span>
      {description && <span className="stat-desc">{description}</span>}
    </div>
  );
}

function TrendArrow({ slope }) {
  if (slope === null || slope === undefined) return null;
  const improving = slope > 0.01;
  const declining = slope < -0.01;
  return (
    <span className={`trend ${improving ? "trend-up" : declining ? "trend-down" : "trend-flat"}`}>
      {improving ? "↑" : declining ? "↓" : "→"}
    </span>
  );
}

function HistoryRow({ record }) {
  const date = new Date(record.date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });

  const cvLabel =
    record.cv_evenness < 3
      ? "very even"
      : record.cv_evenness < 5
      ? "even"
      : record.cv_evenness < 10
      ? "moderate"
      : "uneven";

  return (
    <div className="history-row">
      <span className="history-date">{date}</span>
      <span className="history-scale">{record.scale}</span>
      <span className="history-intonation">{record.intonation}/7</span>
      <span className={`history-cv cv-${cvLabel.replace(" ", "-")}`}>{cvLabel}</span>
      <span className="history-tempo">{record.mean_tempo?.toFixed(0)} bpm</span>
    </div>
  );
}

export default function App() {
  const [view, setView] = useState("record"); // record | history | trends
  const [scale, setScale] = useState("C major");
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [trends, setTrends] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (view === "history") fetchHistory();
    if (view === "trends") fetchTrends();
  }, [view]);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API}/scales`);
      setHistory(res.data);
    } catch (e) {
      setError("Failed to load history");
    }
  };

  const fetchTrends = async () => {
    try {
      const res = await axios.get(`${API}/trends/all`);
      setTrends(res.data);
    } catch (e) {
      setError("Failed to load trends");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("filepath", file);

    try {
      const res = await axios.post(`${API}/analyze?scale=${encodeURIComponent(scale)}`, formData);
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      setFileName(droppedFile.name);
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
    }
  };

  const cvDescription = (cv) => {
    if (cv < 3) return "Very even — excellent control";
    if (cv < 5) return "Even — solid consistency";
    if (cv < 10) return "Moderate — some unevenness";
    return "Uneven — focus on steady rhythm";
  };

  const tempoDescription = (slope) => {
    if (Math.abs(slope) < 0.5) return "Steady tempo throughout";
    if (slope > 0) return "Speeding up through the scale";
    return "Slowing down through the scale";
  };

  return (
    <div className="app">
      <div className="grain-overlay" />

      <header className="header">
        <div className="logo">
          <span className="logo-icon">♩</span>
          <h1>Scale Tracker</h1>
        </div>
        <nav className="nav">
          {["record", "history", "trends"].map((v) => (
            <button
              key={v}
              className={`nav-btn ${view === v ? "nav-active" : ""}`}
              onClick={() => {
                setView(v);
                setError(null);
              }}
            >
              {v}
            </button>
          ))}
        </nav>
      </header>

      <main className="main">
        {/* RECORD VIEW */}
        {view === "record" && (
          <div className="record-view fade-in">
            <div className="upload-section">
              <h2>Record a scale</h2>
              <p className="subtitle">
                Upload your recording and select the scale to analyze your
                intonation, evenness, and tempo.
              </p>

              <div className="scale-select-wrapper">
                <label>Scale</label>
                <select
                  value={scale}
                  onChange={(e) => setScale(e.target.value)}
                  className="scale-select"
                >
                  {SCALES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>

              <div
                className={`dropzone ${dragActive ? "dropzone-active" : ""} ${
                  fileName ? "dropzone-has-file" : ""
                }`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragActive(true);
                }}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="audio/*"
                  onChange={handleFileSelect}
                  hidden
                />
                {fileName ? (
                  <div className="dropzone-file">
                    <span className="file-icon">♪</span>
                    <span className="file-name">{fileName}</span>
                    <span className="file-change">click to change</span>
                  </div>
                ) : (
                  <div className="dropzone-empty">
                    <span className="dropzone-icon">⎗</span>
                    <span>Drop audio file here or click to browse</span>
                  </div>
                )}
              </div>

              <button
                className="analyze-btn"
                onClick={handleUpload}
                disabled={!file || loading}
              >
                {loading ? (
                  <span className="spinner" />
                ) : (
                  "Analyze"
                )}
              </button>
            </div>

            {error && <div className="error-msg">{error}</div>}

            {result && (
              <div className="results fade-in">
                <div className="results-header">
                  <h3>Results</h3>
                  <span className="results-id">#{result.id}</span>
                </div>

                <div className="results-grid">
                  <div className="results-score">
                    <ScoreRing score={result.analytics.intonation} />
                  </div>

                  <div className="results-stats">
                    <StatCard
                      label="Evenness"
                      value={result.analytics.cv_evenness}
                      unit="cv"
                      description={cvDescription(result.analytics.cv_evenness)}
                    />
                    <StatCard
                      label="Mean Tempo"
                      value={result.analytics.mean_tempo}
                      unit="bpm"
                    />
                    <StatCard
                      label="Tempo Drift"
                      value={result.analytics.tempo_slope}
                      unit="slope"
                      description={tempoDescription(result.analytics.tempo_slope)}
                    />
                    <StatCard
                      label="Tempo Consistency"
                      value={result.analytics.tempo_r}
                      unit="r"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* HISTORY VIEW */}
        {view === "history" && (
          <div className="history-view fade-in">
            <div className="history-header">
              <h2>Practice History</h2>
              {history.length > 0 && (
                <button
                  className="clear-btn"
                  onClick={async () => {
                    await axios.delete(`${API}/delete`);
                    setHistory([]);
                  }}
                >
                  Clear All
                </button>
              )}
            </div>

            {history.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">𝄞</span>
                <p>No recordings yet. Go record a scale!</p>
              </div>
            ) : (
              <div className="history-list">
                <div className="history-row history-row-header">
                  <span>Date</span>
                  <span>Scale</span>
                  <span>Intonation</span>
                  <span>Evenness</span>
                  <span>Tempo</span>
                </div>
                {history
                  .slice()
                  .reverse()
                  .map((record) => (
                    <HistoryRow key={record.id} record={record} />
                  ))}
              </div>
            )}
          </div>
        )}

        {/* TRENDS VIEW */}
        {view === "trends" && (
          <div className="trends-view fade-in">
            <h2>Trends</h2>

            {trends?.error ? (
              <div className="empty-state">
                <span className="empty-icon">📊</span>
                <p>{trends.error}</p>
              </div>
            ) : trends ? (
              <div className="trends-grid">
                {Object.entries(trends).map(([field, data]) => (
                  <div key={field} className="trend-card">
                    <div className="trend-card-header">
                      <span className="trend-field">
                        {field.replace(/_/g, " ")}
                      </span>
                      <TrendArrow slope={data.slope} />
                    </div>
                    <div className="trend-stats">
                      <div className="trend-stat">
                        <span className="trend-stat-label">slope</span>
                        <span className="trend-stat-value">
                          {data.slope?.toFixed(3) ?? "—"}
                        </span>
                      </div>
                      <div className="trend-stat">
                        <span className="trend-stat-label">r</span>
                        <span className="trend-stat-value">
                          {data.r?.toFixed(3) ?? "—"}
                        </span>
                      </div>
                      <div className="trend-stat">
                        <span className="trend-stat-label">p</span>
                        <span className="trend-stat-value">
                          {data.p?.toFixed(3) ?? "—"}
                        </span>
                      </div>
                    </div>
                    <div className="trend-sig">
                      {data.p !== null && data.p < 0.05
                        ? "statistically significant"
                        : "not yet significant"}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <span className="spinner" />
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="footer">
        <span>Scale Tracker — practice with intention</span>
      </footer>
    </div>
  );
}