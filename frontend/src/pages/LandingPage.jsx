import { ArrowRight, BrainCircuit, FileScan, ListChecks, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

const LandingPage = () => {
  return (
    <div className="landing-wrap">
      <section className="hero-card">
        <p className="eyebrow">InternMatch AI</p>
        <h1>Find internships that actually match your skills.</h1>
        <p>
          Upload your resume and let our semantic matching engine discover the internships
          that best fit your skills, education, experience and projects.
        </p>
        <div className="hero-actions">
          <Link className="btn btn-primary" to="/register">
            Get Started <ArrowRight size={16} />
          </Link>
          <Link className="btn btn-soft" to="/login">
            Login
          </Link>
        </div>
      </section>

      <section className="feature-grid">
        <article className="feature-card"><FileScan size={18} />Resume Intelligence</article>
        <article className="feature-card"><BrainCircuit size={18} />Semantic Search</article>
        <article className="feature-card"><ListChecks size={18} />Skill Matching</article>
        <article className="feature-card"><Sparkles size={18} />Personalized Internship Recommendations</article>
      </section>

      <section className="flow-card">
        <h2>How it works</h2>
        <div className="flow-line">
          <span>Resume</span>
          <span>AI Parsing</span>
          <span>Semantic Search</span>
          <span>Best Matches</span>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
