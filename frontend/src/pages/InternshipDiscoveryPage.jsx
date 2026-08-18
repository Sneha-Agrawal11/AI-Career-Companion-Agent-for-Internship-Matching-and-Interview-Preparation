import { ArrowRight, LoaderCircle, Search } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getApiErrorMessage } from "../services/api";
import { fetchMatches } from "../services/internshipService";
import { loadJson, saveJson, storageKeys } from "../utils/storage";

const loadingMessages = [
  "Analyzing your profile...",
  "Generating semantic representation...",
  "Searching internship knowledge base...",
  "Calculating semantic similarity...",
  "Ranking the best opportunities...",
];

const InternshipDiscoveryPage = () => {
  const navigate = useNavigate();
  const [topK, setTopK] = useState(loadJson(storageKeys.lastTopK, 5) || 5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const candidate = loadJson(storageKeys.latestResumeCandidate, null);

  const onFindMatches = async () => {
    if (!candidate) {
      setError("Your resume hasn't been uploaded yet.");
      return;
    }

    setError("");
    setLoading(true);
    try {
      const response = await fetchMatches(candidate, topK);
      saveJson(storageKeys.lastMatches, response);
      saveJson(storageKeys.lastTopK, topK);
      navigate("/matches");
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to fetch internship matches."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-stack">
      <section className="page-hero">
        <p className="eyebrow">Internship Matching</p>
        <h1>Find Your Best Internship Matches</h1>
        <p>
          Our semantic matching engine compares your resume with internship opportunities using
          skills, education, experience and semantic similarity.
        </p>
      </section>

      <section className="panel-card">
        <label htmlFor="topK" className="field-label">Select Top-K Results</label>
        <select id="topK" value={topK} onChange={(event) => setTopK(Number(event.target.value))}>
          <option value={5}>5</option>
          <option value={8}>8</option>
          <option value={10}>10</option>
        </select>

        {error ? <p className="error-text">{error}</p> : null}

        <button className="btn btn-primary" type="button" onClick={onFindMatches} disabled={loading}>
          {loading ? <LoaderCircle className="spin" size={16} /> : <Search size={16} />} {loading ? "Finding Matches..." : "Find Best Matches"}
        </button>
      </section>

      {loading ? (
        <section className="panel-card">
          {loadingMessages.map((message) => (
            <p key={message} className="loading-line"><LoaderCircle className="spin" size={14} /> {message}</p>
          ))}
        </section>
      ) : null}

      <section className="panel-card">
        <p className="muted-text">Need to refine your profile before matching?</p>
        <button type="button" className="inline-link as-button" onClick={() => navigate("/resume-analysis")}>
          Review Resume Analysis <ArrowRight size={14} />
        </button>
      </section>
    </div>
  );
};

export default InternshipDiscoveryPage;
