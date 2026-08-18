import { FileCheck2, FileUp, LoaderCircle, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getApiErrorMessage } from "../services/api";
import { fetchAllResumes, uploadResume } from "../services/resumeService";
import { mapParsedResumeToCandidateInput, parseStoredResumeRecord } from "../utils/resumeMapper";
import { loadJson, saveJson, storageKeys } from "../utils/storage";

const ResumePage = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [latestResume, setLatestResume] = useState(loadJson(storageKeys.latestResumeRaw, null));

  useEffect(() => {
    const hydrate = async () => {
      try {
        const all = await fetchAllResumes();
        if (Array.isArray(all) && all.length > 0) {
          const sorted = [...all].sort((a, b) => b.id - a.id);
          const parsedRaw = parseStoredResumeRecord(sorted[0]);
          const candidate = mapParsedResumeToCandidateInput(parsedRaw);
          saveJson(storageKeys.latestResumeRaw, parsedRaw);
          saveJson(storageKeys.latestResumeCandidate, candidate);
          setLatestResume(parsedRaw);
        }
      } catch {
        // keep silent to avoid blocking upload flow
      }
    };
    hydrate();
  }, []);

  const onFileChange = (event) => {
    setFile(event.target.files?.[0] || null);
  };

  const onUpload = async (event) => {
    event.preventDefault();
    if (!file) {
      setError("Please select a PDF or DOCX file.");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await uploadResume(file);
      const mappedCandidate = mapParsedResumeToCandidateInput(response);

      saveJson(storageKeys.latestResumeRaw, response);
      saveJson(storageKeys.latestResumeCandidate, mappedCandidate);
      setLatestResume(response);

      setSuccess("Resume analyzed successfully");
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to upload resume. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  const skills = useMemo(() => latestResume?.skills || [], [latestResume]);

  return (
    <div className="page-stack">
      <section className="page-hero">
        <p className="eyebrow">Resume</p>
        <h1>Upload your Resume</h1>
        <p>Upload your resume and extract profile details for intelligent internship matching.</p>
      </section>

      <form className="panel-card" onSubmit={onUpload}>
        <label htmlFor="resumeUpload" className="upload-zone">
          <FileUp size={24} />
          <p>Drag and drop your resume or click to browse.</p>
          <small>Accepted format: PDF and DOCX</small>
          <input id="resumeUpload" type="file" accept=".pdf,.docx" onChange={onFileChange} hidden />
        </label>

        {file ? <p className="muted-text">Selected: {file.name}</p> : null}
        {error ? <p className="error-text">{error}</p> : null}
        {success ? <p className="success-text">{success}</p> : null}

        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? <LoaderCircle className="spin" size={16} /> : <Sparkles size={16} />} {loading ? "Parsing resume..." : "Upload Resume"}
        </button>
      </form>

      <section className="panel-card">
        <h2>Latest Parsed Snapshot</h2>
        {latestResume ? (
          <>
            <p><strong>Name:</strong> {latestResume.name || "Not provided"}</p>
            <p><strong>Email:</strong> {latestResume.emails?.join(", ") || "Not provided"}</p>
            <p><strong>Phone:</strong> {latestResume.phones?.join(", ") || "Not provided"}</p>
            <p><strong>Skills:</strong> {skills.length ? skills.join(", ") : "Not provided"}</p>
            <div className="inline-actions">
              <Link to="/resume-analysis" className="btn btn-soft"><FileCheck2 size={16} />View Resume Analysis</Link>
              <Link to="/internships" className="btn btn-primary">Find Best Internship Matches</Link>
            </div>
          </>
        ) : (
          <p className="muted-text">Your resume hasn't been uploaded yet.</p>
        )}
      </section>
    </div>
  );
};

export default ResumePage;
