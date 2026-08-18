import { Link } from "react-router-dom";
import BadgeList from "../components/BadgeList";
import { loadJson, storageKeys } from "../utils/storage";

const Section = ({ title, children }) => (
  <section className="panel-card">
    <h2>{title}</h2>
    {children}
  </section>
);

const ResumeAnalysisPage = () => {
  const candidate = loadJson(storageKeys.latestResumeCandidate, null);

  if (!candidate) {
    return (
      <div className="page-stack">
        <section className="panel-card">
          <h1>Resume Intelligence</h1>
          <p className="muted-text">No parsed resume available yet.</p>
          <Link to="/resume" className="btn btn-primary">Upload Resume</Link>
        </section>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <section className="page-hero">
        <p className="eyebrow">Resume Intelligence</p>
        <h1>Resume Analysis</h1>
        <p>Structured candidate information extracted from your latest resume.</p>
      </section>

      <Section title="Candidate Information">
        <div className="info-grid">
          <p><strong>Name:</strong> {candidate.full_name || "Not provided"}</p>
          <p><strong>Email:</strong> {candidate.email || "Not provided"}</p>
          <p><strong>Phone:</strong> {candidate.phone || "Not provided"}</p>
          <p><strong>Address:</strong> {candidate.address || "Not provided"}</p>
          <p><strong>LinkedIn:</strong> {candidate.linkedin || "Not provided"}</p>
          <p><strong>GitHub:</strong> {candidate.github || "Not provided"}</p>
        </div>
      </Section>

      <Section title="Professional Summary"><p>{candidate.professional_summary || "Not provided"}</p></Section>
      <Section title="Technical Skills"><BadgeList items={candidate.technical_skills} emptyText="Not provided" /></Section>
      <Section title="Soft Skills"><BadgeList items={candidate.soft_skills} emptyText="Not provided" /></Section>
      <Section title="Skills"><BadgeList items={candidate.skills} emptyText="Not provided" /></Section>
      <Section title="Education"><ul className="list-clean">{candidate.education.length ? candidate.education.map((item, index) => <li key={`${item}-${index}`}>{item}</li>) : <li className="muted-text">Not provided</li>}</ul></Section>
      <Section title="Experience"><ul className="list-clean">{candidate.work_experience.length ? candidate.work_experience.map((item, index) => <li key={`${item}-${index}`}>{item}</li>) : <li className="muted-text">Not provided</li>}</ul></Section>
      <Section title="Projects"><ul className="list-clean">{candidate.projects.length ? candidate.projects.map((item, index) => <li key={`${item}-${index}`}>{item}</li>) : <li className="muted-text">Not provided</li>}</ul></Section>
      <Section title="Certifications"><ul className="list-clean">{candidate.certifications.length ? candidate.certifications.map((item, index) => <li key={`${item}-${index}`}>{item}</li>) : <li className="muted-text">Not provided</li>}</ul></Section>
      <Section title="Languages"><BadgeList items={candidate.languages} emptyText="Not provided" /></Section>
      <Section title="Achievements"><ul className="list-clean">{candidate.achievements.length ? candidate.achievements.map((item, index) => <li key={`${item}-${index}`}>{item}</li>) : <li className="muted-text">Not provided</li>}</ul></Section>
      <Section title="Other Relevant Information"><ul className="list-clean">{candidate.other_relevant_information.length ? candidate.other_relevant_information.map((item, index) => <li key={`${item}-${index}`}>{item}</li>) : <li className="muted-text">Not provided</li>}</ul></Section>

      <div className="inline-actions">
        <Link className="btn btn-primary" to="/internships">Find Best Internship Matches</Link>
      </div>
    </div>
  );
};

export default ResumeAnalysisPage;
