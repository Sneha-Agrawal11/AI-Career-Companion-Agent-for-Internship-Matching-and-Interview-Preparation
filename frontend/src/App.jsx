import { useState } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function App() {
  const [screen, setScreen] = useState("auth");
  const [authMode, setAuthMode] = useState("login");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [userName, setUserName] = useState("");
  const [token, setToken] = useState("");

  const [file, setFile] = useState(null);
  const [resumeId, setResumeId] = useState(null);
  const [resumeData, setResumeData] = useState(null);

  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // ---------------- AUTH ----------------

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const body = new URLSearchParams();
      body.append("username", email);
      body.append("password", password);

      const response = await fetch(`${API_BASE}/auth/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Login failed");
      }

      const accessToken = data.access_token;

      setToken(accessToken);
      localStorage.setItem("access_token", accessToken);
      localStorage.setItem("user_name", email.split("@")[0]);

      setUserName(email.split("@")[0]);
      setScreen("dashboard");
    } catch (err) {
      setError(err.message || "Unable to login");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          email,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Registration failed");
      }

      setMessage("Account created successfully. Please login.");
      setAuthMode("login");
    } catch (err) {
      setError(err.message || "Unable to register");
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_name");

    setToken("");
    setUserName("");
    setResumeId(null);
    setResumeData(null);
    setMatches([]);
    setFile(null);
    setScreen("auth");
  };

  // ---------------- RESUME UPLOAD ----------------

  const handleResumeUpload = async () => {
    if (!file) {
      setError("Please select a PDF resume first.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/resume/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Resume upload failed");
      }

      setResumeId(data.resume_id);
      setResumeData(data);

      setMessage("Resume analyzed successfully.");
    } catch (err) {
      setError(err.message || "Resume upload failed");
    } finally {
      setLoading(false);
    }
  };

  // ---------------- MATCHING ----------------

  const findMatches = async () => {
    if (!resumeId) {
      setError("Please upload your resume first.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(
        `${API_BASE}/internships/match/${resumeId}?top_k=5`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Matching failed");
      }

      setMatches(data.matches || []);
      setScreen("results");
    } catch (err) {
      setError(err.message || "Unable to find matches");
    } finally {
      setLoading(false);
    }
  };

  // ---------------- AUTH SCREEN ----------------

  if (screen === "auth") {
    return (
      <div className="app-shell auth-shell">
        <div className="auth-left">
          <div className="brand">
            <div className="brand-mark">AI</div>
            <span>InternMatch</span>
          </div>

          <div className="hero-content">
            <div className="eyebrow">AI-POWERED INTERNSHIP MATCHING</div>

            <h1>
              Find the internship
              <span> that fits you.</span>
            </h1>

            <p>
              Upload your resume and let semantic AI matching discover
              internships based on your skills, education and experience.
            </p>

            <div className="hero-points">
              <div>
                <strong>01</strong>
                <span>Resume intelligence</span>
              </div>

              <div>
                <strong>02</strong>
                <span>Semantic matching</span>
              </div>

              <div>
                <strong>03</strong>
                <span>Personalized ranking</span>
              </div>
            </div>
          </div>

          <div className="footer-note">
            AI Internship Matching System
          </div>
        </div>

        <div className="auth-right">
          <div className="auth-card">
            <div className="auth-heading">
              <div className="mini-badge">✦ AI</div>

              <h2>
                {authMode === "login"
                  ? "Welcome back"
                  : "Create your account"}
              </h2>

              <p>
                {authMode === "login"
                  ? "Sign in to continue your internship search."
                  : "Start finding internships matched to your profile."}
              </p>
            </div>

            {error && <div className="alert error">{error}</div>}
            {message && <div className="alert success">{message}</div>}

            <form
              onSubmit={
                authMode === "login" ? handleLogin : handleRegister
              }
            >
              {authMode === "register" && (
                <label>
                  Full name
                  <input
                    type="text"
                    placeholder="Your full name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                  />
                </label>
              )}

              <label>
                Email
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </label>

              <label>
                Password
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </label>

              <button className="primary-btn" type="submit" disabled={loading}>
                {loading
                  ? "Please wait..."
                  : authMode === "login"
                  ? "Sign in"
                  : "Create account"}
                {!loading && <span>→</span>}
              </button>
            </form>

            <div className="auth-switch">
              {authMode === "login" ? (
                <>
                  Don't have an account?
                  <button onClick={() => setAuthMode("register")}>
                    Create one
                  </button>
                </>
              ) : (
                <>
                  Already have an account?
                  <button onClick={() => setAuthMode("login")}>
                    Sign in
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ---------------- DASHBOARD ----------------

  if (screen === "dashboard") {
    return (
      <div className="app-shell workspace">
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark">AI</div>
            <span>InternMatch</span>
          </div>

          <div className="topbar-right">
            <span className="user-name">
              {userName || "User"}
            </span>

            <button className="logout-btn" onClick={logout}>
              Logout
            </button>
          </div>
        </header>

        <main className="dashboard">
          <div className="dashboard-heading">
            <div>
              <div className="eyebrow">PERSONALIZED INTERNSHIP SEARCH</div>

              <h1>
                Find opportunities
                <span> made for you.</span>
              </h1>

              <p>
                Upload your resume. Our matching engine will analyze your
                profile and rank the internships that fit you best.
              </p>
            </div>
          </div>

          {error && <div className="alert error">{error}</div>}
          {message && <div className="alert success">{message}</div>}

          <section className="upload-card">
            <div className="upload-icon">↑</div>

            <h2>Upload your resume</h2>

            <p>
              Upload your latest resume in PDF format to generate personalized
              internship matches.
            </p>

            <label className="drop-zone">
              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={(e) => setFile(e.target.files[0])}
              />

              {file ? (
                <>
                  <div className="file-icon">PDF</div>
                  <strong>{file.name}</strong>
                  <span>Click to choose another file</span>
                </>
              ) : (
                <>
                  <div className="upload-cloud">↑</div>
                  <strong>Drop your resume here</strong>
                  <span>or click to browse · PDF only</span>
                </>
              )}
            </label>

            <button
              className="primary-btn upload-btn"
              onClick={handleResumeUpload}
              disabled={loading || !file}
            >
              {loading ? "Analyzing resume..." : "Analyze Resume"}
              {!loading && <span>→</span>}
            </button>
          </section>

          {resumeId && (
            <section className="resume-ready">
              <div className="status-check">✓</div>

              <div>
                <strong>Resume analyzed successfully</strong>
                <p>
                  Resume ID #{resumeId} is ready for AI internship matching.
                </p>
              </div>

              <button className="match-btn" onClick={findMatches}>
                Find Matching Internships →
              </button>
            </section>
          )}

          <section className="how-section">
            <div className="eyebrow">HOW IT WORKS</div>

            <h2>From resume to ranked opportunities.</h2>

            <div className="pipeline">
              <div>
                <span>01</span>
                <strong>Resume</strong>
                <small>Your PDF</small>
              </div>

              <i>→</i>

              <div>
                <span>02</span>
                <strong>Parsing</strong>
                <small>Extract profile</small>
              </div>

              <i>→</i>

              <div>
                <span>03</span>
                <strong>Vector Search</strong>
                <small>Semantic retrieval</small>
              </div>

              <i>→</i>

              <div>
                <span>04</span>
                <strong>Ranking</strong>
                <small>Best matches</small>
              </div>
            </div>
          </section>
        </main>
      </div>
    );
  }

  // ---------------- RESULTS ----------------

  return (
    <div className="app-shell workspace">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">AI</div>
          <span>InternMatch</span>
        </div>

        <div className="topbar-right">
          <button
            className="back-btn"
            onClick={() => setScreen("dashboard")}
          >
            ← New Search
          </button>

          <span className="user-name">
            {userName || "User"}
          </span>

          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      <main className="results-page">
        <div className="results-heading">
          <div>
            <div className="eyebrow">AI MATCHING RESULTS</div>

            <h1>
              Your best
              <span> opportunities.</span>
            </h1>

            <p>
              Ranked using semantic similarity, skills, education and
              experience compatibility.
            </p>
          </div>

          <div className="result-count">
            <strong>{matches.length}</strong>
            <span>Top Matches</span>
          </div>
        </div>

        {matches.length === 0 ? (
          <div className="empty-state">
            <div>✦</div>
            <h2>No matches found</h2>
            <p>Try uploading another resume.</p>
          </div>
        ) : (
          <div className="matches-grid">
            {matches.map((match, index) => (
              <article className="match-card" key={match.internship_id || index}>
                <div className="match-top">
                  <div className="rank">0{index + 1}</div>

                  <div className="score">
                    <strong>
                      {Number(match.final_score || 0).toFixed(1)}%
                    </strong>
                    <span>match</span>
                  </div>
                </div>

                <div className="match-title">
                  <h2>{match.title}</h2>
                  <p>{match.company}</p>
                </div>

                <div className="tags">
                  {match.domain && <span>{match.domain}</span>}
                  {match.location && <span>{match.location}</span>}
                  {match.work_mode && <span>{match.work_mode}</span>}
                </div>

                <div className="metrics">
                  <Metric
                    label="Semantic"
                    value={Number(match.semantic_similarity || 0) * 100}
                  />

                  <Metric
                    label="Skills"
                    value={Number(match.skill_match_percentage || 0)}
                  />

                  <Metric
                    label="Education"
                    value={Number(match.education_match || 0)}
                  />

                  <Metric
                    label="Experience"
                    value={Number(match.experience_match || 0)}
                  />
                </div>

                <div className="skill-section">
                  <h3>Matched skills</h3>

                  <div className="skill-list">
                    {(match.matched_skills || []).map((skill) => (
                      <span className="skill matched" key={skill}>
                        ✓ {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {(match.missing_skills || []).length > 0 && (
                  <div className="skill-section missing">
                    <h3>Skills to improve</h3>

                    <div className="skill-list">
                      {match.missing_skills.map((skill) => (
                        <span className="skill missing-skill" key={skill}>
                          + {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {match.reason && (
                  <div className="reason">
                    <strong>Why this matches</strong>
                    <p>{match.reason}</p>
                  </div>
                )}
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function Metric({ label, value }) {
  const safeValue = Math.max(0, Math.min(100, Number(value) || 0));

  return (
    <div className="metric">
      <div className="metric-label">
        <span>{label}</span>
        <strong>{safeValue.toFixed(0)}%</strong>
      </div>

      <div className="metric-bar">
        <div style={{ width: `${safeValue}%` }} />
      </div>
    </div>
  );
}

export default App;