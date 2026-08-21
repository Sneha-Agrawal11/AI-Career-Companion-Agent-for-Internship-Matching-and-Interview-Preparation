import { useEffect, useState } from "react";
import { LayoutDashboard, User, Search, Send, BarChart3, FileEdit, LogOut, Menu, X, ChevronsLeft, ChevronsRight, FileText } from "lucide-react";
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

  const [selectedInternship, setSelectedInternship] = useState(null);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [profile, setProfile] = useState({
  name: "",
  email: "",
  phone: "",
  college: "",
  education: "",
  skills: [],
  photo: null,
});

const [editingProfile, setEditingProfile] = useState(false);
const [sidebarOpen, setSidebarOpen] = useState(false);
const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
  return localStorage.getItem("sidebarCollapsed") === "true";
});
const [resumeLibrary, setResumeLibrary] = useState([]);

const fetchResumes = async (currentToken) => {
  try {
    const response = await fetch(`${API_BASE}/resume/all`, {
      headers: { Authorization: `Bearer ${currentToken}` },
    });
    if (response.ok) {
      const data = await response.json();
      setResumeLibrary(data);
    }
  } catch (err) {
    console.error("Failed to fetch resumes", err);
  }
};

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

const savedProfile = localStorage.getItem("profile");

if (savedProfile) {
  setProfile(JSON.parse(savedProfile));
} else {
  setProfile({
    name: email.split("@")[0],
    email: email,
    phone: "",
    college: "",
    education: "",
    skills: [],
    photo: null,
  });
}

setScreen("profile");
fetchResumes(accessToken);
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
    setResumeLibrary([]);
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

setProfile((prev) => ({
  ...prev,
  name: data.name || prev.name,
  email: data.emails?.[0] || prev.email,
  phone: data.phones?.[0] || prev.phone,
  education: data.education || "",
  skills: data.skills || [],
}));

setMessage("Resume analyzed successfully.");
setScreen("extraction");
fetchResumes(token);
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

  
  const useResume = async (id) => {
    try {
      const response = await fetch(`${API_BASE}/resume/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setResumeId(data.id);
        setResumeData(data);
        setProfile((prev) => ({
          ...prev,
          name: data.name || prev.name,
          email: data.emails?.[0] || prev.email,
          phone: data.phones?.[0] || prev.phone,
          education: data.education || "",
          skills: data.skills || [],
        }));
        setScreen("extraction");
      }
    } catch (err) {
      console.error("Failed to load resume", err);
    }
  };

  const sidebarProps = { sidebarCollapsed, setSidebarCollapsed,  screen, setScreen, selectedInternship, profile, userName, email, logout, sidebarOpen, setSidebarOpen, matches };

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


  let content = null;

 if (screen === "extraction") {
  const extracted = resumeData || {};

  content = (
      <>
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

      <main className="extraction-page">

        {/* HEADER */}

        <div className="extraction-header">

          <button
            className="back-btn"
            onClick={() => setScreen("dashboard")}
          >
            ← Back to Resume
          </button>

          <div className="extraction-title">

            <div className="eyebrow">
              RESUME INTELLIGENCE
            </div>

            <h1>
              Your resume is
              <span> understood.</span>
            </h1>

            <p>
              We've extracted the important information from your resume.
              Review the detected profile before finding internships.
            </p>

          </div>

          <div className="extraction-status">
            <span>✓</span>
            Extraction complete
          </div>

        </div>


        {/* PROFILE SUMMARY */}

        <section className="extraction-card profile-summary-card">

          <div className="section-heading">
            <div>
              <span className="section-kicker">
                CANDIDATE PROFILE
              </span>

              <h2>Extracted information</h2>
            </div>

            <span className="resume-id">
              Resume #{resumeId}
            </span>
          </div>


          <div className="extracted-grid">

            <div className="extracted-item">
              <span>Name</span>
              <strong>
                {extracted.name || "Not detected"}
              </strong>
            </div>

            <div className="extracted-item">
              <span>Email</span>
              <strong>
                {extracted.email || extracted.emails?.[0] || "Not detected"}
              </strong>
            </div>

            <div className="extracted-item">
              <span>Phone</span>
              <strong>
                  {extracted.phone || extracted.phones?.[0] || "Not detected"}
              </strong>
            </div>

            <div className="extracted-item education">
              <span>Education</span>
              <strong>
                {extracted.education || "Not detected"}
              </strong>
            </div>

          </div>

        </section>


        {/* SKILLS */}

        <section className="extraction-card">

          <div className="section-heading">

            <div>
              <span className="section-kicker">
                SKILLS
              </span>

              <h2>Detected skills</h2>
            </div>

            <div className="skill-count">
              {(extracted.skills || []).length} skills
            </div>

          </div>


          <div className="extracted-skills">

            {(extracted.skills || []).length > 0 ? (

              extracted.skills.map((skill) => (
                <span
                  className="extracted-skill"
                  key={skill}
                >
                  ✓ {skill}
                </span>
              ))

            ) : (

              <p className="muted">
                No skills were detected.
              </p>

            )}

          </div>

        </section>


        {/* RAW CONTENT */}

        <section className="extraction-card raw-card">

          <div className="section-heading">

            <div>
              <span className="section-kicker">
                SOURCE DOCUMENT
              </span>

              <h2>Resume content</h2>
            </div>

            <span className="raw-label">
              Parsed text
            </span>

          </div>

          <div className="raw-resume">

            {extracted.text ||
              extracted.raw_text ||
              "Resume text was extracted successfully."}

          </div>

        </section>


        {/* ACTIONS */}

        <div className="extraction-actions">

          <button
            className="secondary-btn"
            onClick={() => setScreen("dashboard")}
          >
            ← Upload another resume
          </button>

          <button
            className="secondary-btn"
            onClick={() => setScreen("profile")}
          >
            Review Profile
          </button>

          <button
            className="primary-btn"
            onClick={findMatches}
            disabled={loading}
          >
            {loading
              ? "Finding matches..."
              : "Find Internship Matches"}
            {!loading && <span>→</span>}
          </button>

        </div>

      </main>
      </>
    );
  }

// ---------------- INTERNSHIP ACTIONS ----------------

const openApplyPage = (internship) => {
  setSelectedInternship(internship);
  setScreen("apply");
};

const openSkillGap = (internship) => {
  setSelectedInternship(internship);
  setScreen("skill-gap");
};

const openCoverLetter = (internship) => {
  setSelectedInternship(internship);
  setScreen("coverletter");
};


// ---------------- PROFILE ----------------

if (screen === "profile") {
  const saveProfile = () => {
    localStorage.setItem("profile", JSON.stringify(profile));
    setEditingProfile(false);
    setMessage("Profile updated successfully.");
  };

  content = (
      <>
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

      <main className="profile-page">

        <div className="profile-heading">
          <div>
            <div className="eyebrow">YOUR PROFILE</div>

            <h1>
              Build your
              <span> internship profile.</span>
            </h1>

            <p>
              Keep your personal and academic information updated.
              This information helps InternMatch provide better
              internship recommendations.
            </p>
          </div>

          <button
            className="secondary-btn"
            onClick={() => setScreen("dashboard")}
          >
            Skip to Resume →
          </button>
        </div>


        <section className="profile-card">

          <div className="profile-cover"></div>

          <div className="profile-main">

            <div className="profile-avatar-wrapper">

              {profile.photo ? (
                <img
                  src={profile.photo}
                  className="profile-avatar"
                  alt="Profile"
                />
              ) : (
                <div className="profile-avatar placeholder-avatar">
                  {(profile.name || userName || "U")
                    .charAt(0)
                    .toUpperCase()}
                </div>
              )}

              <label className="photo-upload">
                Change photo
                <input
                  type="file"
                  accept="image/*"
                  hidden
                  onChange={(e) => {
                    const selected = e.target.files?.[0];

                    if (selected) {
                      const reader = new FileReader();

                      reader.onload = () => {
                        setProfile((prev) => ({
                          ...prev,
                          photo: reader.result,
                        }));
                      };

                      reader.readAsDataURL(selected);
                    }
                  }}
                />
              </label>

            </div>


            <div className="profile-intro">
              <h2>{profile.name || userName || "Your Name"}</h2>
              <p>{profile.email || email}</p>

              <span className="profile-status">
                ✓ Profile active
              </span>
            </div>

          </div>


          <div className="profile-form">

            <div className="form-section-title">
              <span>PERSONAL INFORMATION</span>
              <h2>About you</h2>
            </div>


            <div className="profile-grid">

              <label>
                Full name
                <input
                  value={profile.name}
                  disabled={!editingProfile}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      name: e.target.value,
                    })
                  }
                  placeholder="Your full name"
                />
              </label>


              <label>
                Email
                <input
                  value={profile.email}
                  disabled
                  placeholder="Email address"
                />
              </label>


              <label>
                Phone number
                <input
                  value={profile.phone}
                  disabled={!editingProfile}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      phone: e.target.value,
                    })
                  }
                  placeholder="+91 XXXXX XXXXX"
                />
              </label>


              <label>
                College / University
                <input
                  value={profile.college}
                  disabled={!editingProfile}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      college: e.target.value,
                    })
                  }
                  placeholder="Your college or university"
                />
              </label>


              <label className="full-field">
                Education
                <input
                  value={profile.education}
                  disabled={!editingProfile}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      education: e.target.value,
                    })
                  }
                  placeholder="e.g. B.Tech Information Technology"
                />
              </label>

            </div>


            <div className="form-section-title skills-title">
              <span>YOUR SKILLS</span>
              <h2>Skills extracted from your resume</h2>
            </div>


            <div className="profile-skills">

              {(profile.skills || []).length > 0 ? (
                profile.skills.map((skill, index) => (
                  <span className="profile-skill" key={index}>
                    ✓ {skill}
                  </span>
                ))
              ) : (
                <p className="muted">
                  Upload your resume to automatically detect your skills.
                </p>
              )}

            </div>


            <div className="profile-actions">

              {!editingProfile ? (
                <button
                  className="secondary-btn"
                  onClick={() => setEditingProfile(true)}
                >
                  Edit Profile
                </button>
              ) : (
                <>
                  <button
                    className="secondary-btn"
                    onClick={() => setEditingProfile(false)}
                  >
                    Cancel
                  </button>

                  <button
                    className="primary-btn"
                    onClick={saveProfile}
                  >
                    Save Profile →
                  </button>
                </>
              )}

              <button
                className="primary-btn"
                onClick={() => setScreen("dashboard")}
              >
                Continue to Resume →
              </button>

            </div>

          </div>

        </section>

      </main>
      </>
    );
  }



    // ---------------- DASHBOARD ----------------

  if (screen === "dashboard") {
    content = (
      <>
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark">AI</div>
            <span>InternMatch</span>
          </div>

          <div className="topbar-right">
  <button
    className="profile-nav-btn"
    onClick={() => setScreen("profile")}
  >
    My Profile
  </button>

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
      </>
    );
  }

  // ---------------- RESULTS ----------------

  if (screen === "results") {
    content = (
      <>
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

  <button
    className="profile-nav-btn"
    onClick={() => setScreen("profile")}
  >
    My Profile
  </button>

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

                    <div className="match-actions">

  <button
    className="primary-btn apply-btn"
    onClick={() => {
      setSelectedInternship(match);
      setScreen("apply");
    }}
  >
    Apply Now →
  </button>

  <button
    className="secondary-btn"
    onClick={() => {
      setSelectedInternship(match);
      setScreen("skill-gap");
    }}
  >
    Skill Gap
  </button>

</div>
                    <strong>Why this matches</strong>
                    <p>{match.reason}</p>
                  </div>
                )}
              </article>
            ))}
          </div>
        )}
      </main>
      </>
    );
  }

// ---------------- APPLY PAGE ----------------

if (screen === "apply") {
  const internship = selectedInternship;

  if (!internship) {
    content = (
      <>
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark">AI</div>
            <span>InternMatch</span>
          </div>
        </header>
        <main className="sidebar-empty-state">
          <div className="sidebar-empty-icon">📤</div>
          <h2>Select an internship</h2>
          <p>Select an internship to start your application.</p>
          <button className="primary-btn" onClick={() => setScreen("results")}>View Matches →</button>
        </main>
      </>
    );
  } else {


  content = (
      <>
        <header className="topbar">
        <div className="brand">
          <div className="brand-mark">AI</div>
          <span>InternMatch</span>
        </div>

        <div className="topbar-right">
          <button
            className="back-btn"
            onClick={() => setScreen("results")}
          >
            ← Back to Matches
          </button>

          <button
            className="profile-nav-btn"
            onClick={() => setScreen("profile")}
          >
            My Profile
          </button>

          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </header>


      <main className="apply-page">

        <button
          className="page-back"
          onClick={() => setScreen("results")}
        >
          ← Back to internship matches
        </button>


        <div className="apply-hero">

          <div className="apply-eyebrow">
            INTERNSHIP APPLICATION
          </div>

          <h1>
            Your application,
            <span> step by step.</span>
          </h1>

          <p>
            Everything you need to know before applying to this
            internship. Follow the steps below to complete your
            application confidently.
          </p>

        </div>


        {/* INTERNSHIP SUMMARY */}

        <section className="apply-company-card">

          <div className="company-icon">
            {internship.company?.charAt(0)?.toUpperCase() || "I"}
          </div>

          <div className="company-info">

            <span className="company-label">
              {internship.domain || "INTERNSHIP"}
            </span>

            <h2>{internship.title}</h2>

            <p>{internship.company}</p>

          </div>

          <div className="apply-score">
            <strong>
              {Number(internship.final_score || 0).toFixed(1)}%
            </strong>

            <span>match</span>
          </div>

        </section>


        {/* APPLICATION PROCESS */}

        <section className="application-card">

          <div className="section-kicker">
            APPLICATION PROCESS
          </div>

          <h2>How to apply</h2>

          <p className="section-description">
            Follow these steps to complete your application.
          </p>


          <div className="application-steps">

            <div className="application-step">

              <div className="step-number">01</div>

              <div>
                <h3>Review the internship</h3>

                <p>
                  Check the role, required skills, location and
                  work mode before submitting your application.
                </p>
              </div>

            </div>


            <div className="application-step">

              <div className="step-number">02</div>

              <div>
                <h3>Prepare your resume</h3>

                <p>
                  Make sure your latest resume highlights the
                  skills and experience relevant to this role.
                </p>
              </div>

            </div>


            <div className="application-step">

              <div className="step-number">03</div>

              <div>
                <h3>Prepare your cover letter</h3>

                <p>
                  Create a focused cover letter explaining why
                  you are a good fit for this internship.
                </p>
              </div>

            </div>


            <div className="application-step">

              <div className="step-number">04</div>

              <div>
                <h3>Submit your application</h3>

                <p>
                  Visit the company's application page and submit
                  your resume and other required information.
                </p>
              </div>

            </div>

          </div>

        </section>


        {/* BEFORE YOU APPLY */}

        <section className="before-apply-card">

          <div>
            <span className="section-kicker">
              BEFORE YOU APPLY
            </span>

            <h2>Make your application stronger.</h2>

            <p>
              Review your skill gaps and create a tailored cover
              letter before submitting your application.
            </p>
          </div>


          <div className="apply-actions">

            <button
              className="secondary-action"
              onClick={() => openSkillGap(internship)}
            >
              View Skill Gap →
            </button>

            <button
              className="primary-action"
              onClick={() => openCoverLetter(internship)}
            >
              Create Cover Letter →
            </button>

          </div>

        </section>


        {/* FINAL APPLY */}

        <section className="final-apply-card">

          <div>

            <span className="ready-badge">
              ✓ READY TO APPLY
            </span>

            <h2>
              You're ready for the next step.
            </h2>

            <p>
              Use the company's official application process to
              submit your application.
            </p>

          </div>


          <button
            className="large-apply-btn"
            onClick={() => openCoverLetter(internship)}
          >
            Prepare Application →
          </button>

        </section>

      </main>
      </>
    );
  }

  }
// ---------------- SKILL GAP PAGE ----------------

if (screen === "skill-gap") {
  const internship = selectedInternship;

  if (!internship) {
    content = (
      <>
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark">AI</div>
            <span>InternMatch</span>
          </div>
        </header>
        <main className="sidebar-empty-state">
          <div className="sidebar-empty-icon">📊</div>
          <h2>Select an internship</h2>
          <p>Select an internship to view your skill gap analysis.</p>
          <button className="primary-btn" onClick={() => setScreen("results")}>View Matches →</button>
        </main>
      </>
    );
  } else {


  content = (
      <>
        <header className="topbar">
        <div className="brand">
          <div className="brand-mark">AI</div>
          <span>InternMatch</span>
        </div>
        <div className="topbar-right">
          <button className="back-btn" onClick={() => setScreen("results")}>← Back to Matches</button>
          <button className="profile-nav-btn" onClick={() => setScreen("profile")}>My Profile</button>
          <button className="logout-btn" onClick={logout}>Logout</button>
        </div>
      </header>

      <main className="apply-page">
        <button className="page-back" onClick={() => setScreen("results")}>
          ← Back to internship matches
        </button>

        <div className="apply-hero">
          <div className="apply-eyebrow">PROFILE VS INTERNSHIP</div>
          <h1>Skill Gap <span>Analysis.</span></h1>
          <p>Compare your current skills with the requirements for <strong>{internship.title}</strong> at <strong>{internship.company}</strong>.</p>
        </div>

        <section className="apply-company-card">
          <div className="company-icon">{internship.company?.charAt(0)?.toUpperCase() || "I"}</div>
          <div className="company-info">
            <span className="company-label">{internship.domain || "INTERNSHIP"}</span>
            <h2>{internship.title}</h2>
            <p>{internship.company}</p>
          </div>
          <div className="apply-score">
            <strong>{Number(internship.skill_match_percentage || 0).toFixed(0)}%</strong>
            <span>skill match</span>
          </div>
        </section>

        <section className="application-card">
          <div className="section-kicker">WHAT YOU ALREADY HAVE</div>
          <h2>Matched Skills</h2>
          <p className="section-description">These skills are present on your resume and match the job requirements.</p>
          <div className="skill-list" style={{ marginTop: '1rem' }}>
            {(internship.matched_skills || []).length > 0 ? (
              internship.matched_skills.map((skill) => (
                <span className="skill matched" key={skill}>✓ {skill}</span>
              ))
            ) : (
              <p>No matched skills found.</p>
            )}
          </div>
        </section>

        <section className="application-card">
          <div className="section-kicker">WHAT YOU'RE MISSING</div>
          <h2>Skill Gaps</h2>
          <p className="section-description">These skills are required for the role but missing from your resume. Consider learning these or adding them to your resume if you have experience.</p>
          <div className="skill-list" style={{ marginTop: '1rem' }}>
            {(internship.missing_skills || []).length > 0 ? (
              internship.missing_skills.map((skill) => (
                <span className="skill missing-skill" key={skill}>+ {skill}</span>
              ))
            ) : (
              <p>Great! You have no missing skills for this role.</p>
            )}
          </div>
        </section>

        <section className="before-apply-card">
          <div>
            <span className="section-kicker">NEXT STEPS</span>
            <h2>Continue your application</h2>
          </div>
          <div className="apply-actions">
            <button className="secondary-action" onClick={() => setScreen("apply")}>
              Apply Now →
            </button>
            <button className="primary-action" onClick={() => openCoverLetter(internship)}>
              Create Cover Letter →
            </button>
          </div>
        </section>
      </main>
      </>
    );
  }

  }
// ---------------- COVER LETTER PAGE ----------------

if (screen === "coverletter") {
  const internship = selectedInternship;

  if (!internship) {
    content = (
      <>
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark">AI</div>
            <span>InternMatch</span>
          </div>
        </header>
        <main className="sidebar-empty-state">
          <div className="sidebar-empty-icon">✍️</div>
          <h2>Select an internship</h2>
          <p>Choose an internship to generate a cover letter.</p>
          <button className="primary-btn" onClick={() => setScreen("results")}>View Matches →</button>
        </main>
      </>
    );
  } else {


  const matchedSkills = internship.matched_skills || [];

  const generatedCoverLetter = `
Dear Hiring Manager,

I am writing to express my interest in the ${internship.title} position at ${internship.company}.

My background and technical skills align well with this opportunity. In particular, my experience with ${matchedSkills.slice(0, 5).join(", ") || "relevant technical skills"} makes me well prepared to contribute to the role.

I am excited about the opportunity to apply my skills, learn from your team, and contribute meaningfully to the work at ${internship.company}.

Thank you for considering my application. I would welcome the opportunity to discuss how my background and skills can contribute to your team.

Sincerely,
${userName || "Your Name"}
`.trim();


  content = (
      <>
        <header className="topbar">

        <div className="brand">
          <div className="brand-mark">AI</div>
          <span>InternMatch</span>
        </div>

        <div className="topbar-right">

          <button
            className="back-btn"
            onClick={() => setScreen("apply")}
          >
            ← Back to Application
          </button>

          <button
            className="profile-nav-btn"
            onClick={() => setScreen("profile")}
          >
            My Profile
          </button>

          <button className="logout-btn" onClick={logout}>
            Logout
          </button>

        </div>

      </header>


      <main className="cover-page">

        <button
          className="page-back"
          onClick={() => setScreen("apply")}
        >
          ← Back to application
        </button>


        <div className="cover-hero">

          <div className="apply-eyebrow">
            COVER LETTER
          </div>

          <h1>
            Make your application
            <span> stand out.</span>
          </h1>

          <p>
            A tailored cover letter based on your profile and
            the internship you're applying for.
          </p>

        </div>


        {/* TARGET ROLE */}

        <section className="cover-target">

          <div className="cover-company-icon">
            {internship.company?.charAt(0)?.toUpperCase() || "I"}
          </div>

          <div>

            <span>APPLICATION FOR</span>

            <h2>
              {internship.title}
            </h2>

            <p>
              {internship.company}
            </p>

          </div>

        </section>


        {/* COVER LETTER */}

        <section className="cover-editor-card">

          <div className="cover-editor-header">

            <div>

              <span className="section-kicker">
                AI DRAFT
              </span>

              <h2>Your cover letter</h2>

            </div>

            <span className="ai-generated">
              ✦ AI Assisted
            </span>

          </div>


          <textarea
            className="cover-textarea"
            defaultValue={generatedCoverLetter}
          />


          <div className="cover-footer">

            <span>
              Review and personalize before submitting.
            </span>

            <button
              className="copy-cover-btn"
              onClick={() => {
                navigator.clipboard.writeText(
                  generatedCoverLetter
                );
              }}
            >
              Copy Cover Letter
            </button>

          </div>

        </section>


        {/* APPLICATION CHECKLIST */}

        <section className="cover-checklist">

          <div className="section-kicker">
            BEFORE SUBMITTING
          </div>

          <h2>Quick application checklist</h2>


          <div className="checklist-grid">

            <div>
              <span>✓</span>
              <strong>Resume updated</strong>
              <small>Use your latest version</small>
            </div>

            <div>
              <span>✓</span>
              <strong>Cover letter reviewed</strong>
              <small>Personalize the AI draft</small>
            </div>

            <div>
              <span>✓</span>
              <strong>Skills checked</strong>
              <small>Review the skill gap</small>
            </div>

          </div>

        </section>


        <div className="cover-actions">

          <button
            className="secondary-action"
            onClick={() => openSkillGap(internship)}
          >
            ← Review Skill Gap
          </button>

          <button
            className="primary-action"
            onClick={() => setScreen("apply")}
          >
            Back to Application →
          </button>

        </div>

      </main>
      </>
    );
  }
  }

  // ---------------- RESUMES SCREEN ----------------

  if (screen === "resumes") {
    content = (
      <>
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark">AI</div>
            <span>InternMatch</span>
          </div>
          <div className="topbar-right">
            <button className="primary-btn" onClick={() => setScreen("dashboard")}>Upload New Resume</button>
            <button className="logout-btn" onClick={logout}>Logout</button>
          </div>
        </header>
        <main className="dashboard-content">
          <div className="dashboard-header">
            <h1>My Resumes</h1>
            <p>You have {resumeLibrary.length} resume(s) uploaded.</p>
          </div>
          {resumeLibrary.length === 0 ? (
            <div className="sidebar-empty-state">
              <div className="sidebar-empty-icon"><FileText size={32}/></div>
              <h2>No resumes yet</h2>
              <p>Upload your first resume to start building your internship profile.</p>
              <button className="primary-btn" onClick={() => setScreen("dashboard")}>Upload Resume</button>
            </div>
          ) : (
            <div className="resume-list">
              {resumeLibrary.map((res) => (
                <div key={res.id} className={`resume-card ${resumeId === res.id ? "active" : ""}`}>
                  <div className="resume-card-info">
                    <h3>{res.filename || "Resume"}</h3>
                    <div className="resume-card-meta">
                      <span>Uploaded {res.uploaded_at ? new Date(res.uploaded_at).toLocaleDateString() : "—"}</span>
                    </div>
                  </div>
                  <div className="resume-card-actions">
                    {resumeId === res.id ? (
                      <span style={{color: "var(--purple)", fontWeight: "700", border: "1px solid var(--purple)", padding: "4px 12px", borderRadius: "8px", fontSize: "12px"}}>Active</span>
                    ) : (
                      <button className="secondary-btn" onClick={() => useResume(res.id)}>Use This Resume</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </>
    );
  }

  // ---------------- WORKSPACE SHELL ----------------

  return (
    <div className="app-shell workspace with-sidebar">
      <Sidebar {...sidebarProps} />
      <div className="main-area">
        {content}
      </div>
    </div>
  );
}

function Sidebar({ screen, setScreen, selectedInternship, profile, userName, email, logout, sidebarOpen, setSidebarOpen, matches, sidebarCollapsed, setSidebarCollapsed }) {
  const navItems = [
    { section: "WORKSPACE", items: [
      { label: "Dashboard", icon: LayoutDashboard, target: "dashboard", activeScreens: ["dashboard", "extraction"] },
      { label: "My Resumes", icon: FileText, target: "resumes", activeScreens: ["resumes"] },
      { label: "My Profile", icon: User, target: "profile", activeScreens: ["profile"] },
      { label: "Matches", icon: Search, target: "results", activeScreens: ["results"] },
    ]},
    { section: "APPLICATION", items: [
      { label: "Apply", icon: Send, target: "apply", activeScreens: ["apply"] },
      { label: "Skill Gap", icon: BarChart3, target: "skill-gap", activeScreens: ["skill-gap"] },
      { label: "Cover Letter", icon: FileEdit, target: "coverletter", activeScreens: ["coverletter"] },
    ]},
  ];

  return (
    <>
      <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""} ${sidebarCollapsed ? "sidebar-collapsed" : ""}`}>
        <div className="sidebar-brand">
          <div className="brand-mark">AI</div>
          <span>InternMatch</span>
        </div>

        <button
          className="sidebar-collapse-btn"
          onClick={() => {
            const newVal = !sidebarCollapsed;
            setSidebarCollapsed(newVal);
            localStorage.setItem("sidebarCollapsed", newVal);
          }}
          title={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          {sidebarCollapsed ? <ChevronsRight size={20} /> : <ChevronsLeft size={20} />}
        </button>

        <nav className="sidebar-nav">
          {navItems.map((group) => (
            <div className="sidebar-section" key={group.section}>
              <div className="sidebar-section-label">{group.section}</div>
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = item.activeScreens.includes(screen);
                return (
                  <button
                    key={item.label}
                    className={`sidebar-item ${isActive ? "active" : ""}`}
                    onClick={() => {
                      setScreen(item.target);
                      setSidebarOpen(false);
                    }}
                    title={item.label}
                  >
                    <Icon size={18} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-profile">
            <div className="sidebar-avatar">
              {(profile.name || userName || "U").charAt(0).toUpperCase()}
            </div>
            <div className="sidebar-user-info">
              <strong>{profile.name || userName || "User"}</strong>
              <span>{profile.email || email || ""}</span>
            </div>
          </div>
          <button className="sidebar-logout" onClick={logout}>
            <LogOut size={16} />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </>
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
