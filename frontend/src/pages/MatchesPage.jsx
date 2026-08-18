import { Link } from "react-router-dom";
import BadgeList from "../components/BadgeList";
import ScoreBar from "../components/ScoreBar";
import { loadJson, storageKeys } from "../utils/storage";

const percentFromSimilarity = (score) => Math.max(0, Math.min(100, Number(score || 0) * 100));

const MatchesPage = () => {
  const result = loadJson(storageKeys.lastMatches, null);
  const candidate = result?.candidate;
  const matches = result?.matches || [];

  if (!result) {
    return (
      <section className="panel-card">
        <h1>Your Best Internship Matches</h1>
        <p className="muted-text">No matching results available yet.</p>
        <Link className="btn btn-primary" to="/internships">Find Matches</Link>
      </section>
    );
  }

  return (
    <div className="page-stack">
      <section className="page-hero">
        <p className="eyebrow">Results</p>
        <h1>Your Best Internship Matches</h1>
        <p>Ranked using semantic similarity and profile compatibility.</p>
        <p className="muted-text">Top {matches.length} matches found for {candidate?.name || "candidate"}.</p>
      </section>

      {matches.length === 0 ? (
        <section className="panel-card">
          <p>We couldn't find strong matches for this profile.</p>
          <p className="muted-text">Try updating your skills or resume.</p>
        </section>
      ) : null}

      <section className="match-grid">
        {matches.map((match) => (
          <article className="match-card" key={match.internship_id}>
            <div className="match-head">
              <div>
                <h2>{match.title}</h2>
                <p>{match.company}</p>
                <small>{match.domain} • {match.work_mode} • {match.duration}</small>
              </div>
              <div className="score-pill">{Number(match.final_score || 0).toFixed(1)}%</div>
            </div>

            <div className="meta-grid">
              <p><strong>Location:</strong> {match.location}</p>
              <p><strong>Stipend:</strong> {match.stipend}</p>
            </div>

            <ScoreBar label="Match Score" value={match.final_score} />
            <ScoreBar label="Semantic Match" value={percentFromSimilarity(match.semantic_similarity)} />
            <ScoreBar label="Skill Match" value={match.skill_match_percentage} />
            <ScoreBar label="Education Match" value={match.education_match} />
            <ScoreBar label="Experience Match" value={match.experience_match} />

            <div className="match-section">
              <h3>Matched Skills</h3>
              <BadgeList items={match.matched_skills} variant="success" emptyText="None" />
            </div>

            <div className="match-section">
              <h3>Missing Skills</h3>
              <BadgeList items={match.missing_skills} variant="danger" emptyText="None" />
            </div>

            <div className="match-section">
              <h3>Why this matches you</h3>
              <p className="muted-text">{match.reason || "Explanation not available."}</p>
            </div>

            <Link className="btn btn-soft" to={`/internships/${match.internship_id}`}>View Details</Link>
          </article>
        ))}
      </section>
    </div>
  );
};

export default MatchesPage;
