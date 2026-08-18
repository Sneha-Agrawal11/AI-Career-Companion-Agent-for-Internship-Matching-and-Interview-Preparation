import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import BadgeList from "../components/BadgeList";
import { getApiErrorMessage } from "../services/api";
import { fetchInternshipById } from "../services/internshipService";

const InternshipDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [internship, setInternship] = useState(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await fetchInternshipById(id);
        setInternship(data);
      } catch (err) {
        setError(getApiErrorMessage(err, "Unable to load internship details."));
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [id]);

  if (loading) {
    return <div className="page-center">Loading internship details...</div>;
  }

  if (error) {
    return <section className="panel-card"><p className="error-text">{error}</p></section>;
  }

  if (!internship) {
    return <section className="panel-card"><p className="muted-text">Internship not found.</p></section>;
  }

  return (
    <div className="page-stack">
      <section className="page-hero">
        <p className="eyebrow">Internship Details</p>
        <h1>{internship.title}</h1>
        <p>{internship.company}</p>
      </section>

      <section className="panel-card">
        <p><strong>Domain:</strong> {internship.domain}</p>
        <p><strong>Location:</strong> {internship.location}</p>
        <p><strong>Work Mode:</strong> {internship.work_mode}</p>
        <p><strong>Duration:</strong> {internship.duration}</p>
        <p><strong>Stipend:</strong> {internship.stipend}</p>
      </section>

      <section className="panel-card">
        <h2>Description</h2>
        <p>{internship.description || "Not provided"}</p>
      </section>

      <section className="panel-card">
        <h2>Required Skills</h2>
        <BadgeList items={internship.required_skills || []} emptyText="Not provided" />
      </section>

      <section className="panel-card">
        <h2>Preferred Skills</h2>
        <BadgeList items={internship.preferred_skills || []} emptyText="Not provided" />
      </section>

      <section className="panel-card">
        <h2>Education Requirements</h2>
        <p>{internship.education_requirements || "Not provided"}</p>
        <h2>Experience Requirements</h2>
        <p>{internship.experience_requirements || "Not provided"}</p>
      </section>

      <section className="panel-card">
        <h2>Responsibilities</h2>
        <ul className="list-clean">
          {(internship.responsibilities || []).length
            ? internship.responsibilities.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)
            : <li className="muted-text">Not provided</li>}
        </ul>
      </section>

      <section className="panel-card">
        <h2>Eligibility</h2>
        <p>{internship.eligibility || "Not provided"}</p>
      </section>

      <button type="button" className="btn btn-primary" onClick={() => navigate("/matches")}>Back to Matches</button>
    </div>
  );
};

export default InternshipDetailsPage;
