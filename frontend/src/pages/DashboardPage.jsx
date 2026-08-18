import { ArrowRight, CheckCircle2, FileUp, SearchCheck, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { loadJson, storageKeys } from "../utils/storage";

const DashboardPage = () => {
  const { user } = useAuth();
  const candidate = loadJson(storageKeys.latestResumeCandidate, null);
  const matches = loadJson(storageKeys.lastMatches, []);

  const skillsCount = candidate?.skills?.length || 0;
  const projectsCount = candidate?.projects?.length || 0;
  const topMatchesCount = Array.isArray(matches) ? matches.length : 0;

  return (
    <div className="page-stack">
      <section className="page-hero">
        <p className="eyebrow">Dashboard</p>
        <h1>Welcome back, {user?.full_name || "Candidate"}</h1>
        <p>Let's find internships that match your profile.</p>
      </section>

      <section className="status-card">
        <div>
          <h2>Resume Status</h2>
          <p>{candidate ? "Resume Ready" : "Your resume hasn't been uploaded yet."}</p>
        </div>
        <div className="status-actions">
          <Link className="btn btn-soft" to="/resume"><FileUp size={16} />Upload Resume</Link>
          {candidate ? (
            <Link className="btn btn-primary" to="/internships"><SearchCheck size={16} />Find Matching Internships</Link>
          ) : null}
        </div>
      </section>

      <section className="stats-grid">
        <article className="stat-card">
          <CheckCircle2 size={18} />
          <h3>Resume Status</h3>
          <p>{candidate ? "Uploaded" : "Pending"}</p>
        </article>
        <article className="stat-card">
          <Sparkles size={18} />
          <h3>Skills Detected</h3>
          <p>{skillsCount || "Not available"}</p>
        </article>
        <article className="stat-card">
          <Sparkles size={18} />
          <h3>Projects</h3>
          <p>{projectsCount || "Not available"}</p>
        </article>
        <article className="stat-card">
          <Sparkles size={18} />
          <h3>Top Matches</h3>
          <p>{topMatchesCount || "Not available"}</p>
        </article>
      </section>

      <section className="quick-links">
        <Link className="inline-link" to="/resume-analysis">View Resume Analysis <ArrowRight size={14} /></Link>
        <Link className="inline-link" to="/matches">View Latest Match Results <ArrowRight size={14} /></Link>
      </section>
    </div>
  );
};

export default DashboardPage;
