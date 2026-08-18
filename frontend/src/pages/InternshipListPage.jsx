import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getApiErrorMessage } from "../services/api";
import { fetchInternships } from "../services/internshipService";

const InternshipListPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [records, setRecords] = useState([]);
  const [filters, setFilters] = useState({ search: "", domain: "", work_mode: "", location: "" });

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await fetchInternships();
        setRecords(data?.internships || []);
      } catch (err) {
        setError(getApiErrorMessage(err, "Unable to load internships."));
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const domains = useMemo(() => Array.from(new Set(records.map((item) => item.domain))).filter(Boolean), [records]);
  const modes = useMemo(() => Array.from(new Set(records.map((item) => item.work_mode))).filter(Boolean), [records]);
  const locations = useMemo(() => Array.from(new Set(records.map((item) => item.location))).filter(Boolean), [records]);

  const filtered = useMemo(() => {
    return records.filter((item) => {
      const text = `${item.title || ""} ${item.company || ""}`.toLowerCase();
      const bySearch = filters.search ? text.includes(filters.search.toLowerCase()) : true;
      const byDomain = filters.domain ? item.domain === filters.domain : true;
      const byMode = filters.work_mode ? item.work_mode === filters.work_mode : true;
      const byLocation = filters.location ? item.location === filters.location : true;
      return bySearch && byDomain && byMode && byLocation;
    });
  }, [records, filters]);

  if (loading) {
    return <div className="page-center">Loading internships...</div>;
  }

  return (
    <div className="page-stack">
      <section className="page-hero">
        <p className="eyebrow">Explore</p>
        <h1>Internships</h1>
        <p>Browse available internship opportunities.</p>
      </section>

      <section className="panel-card filter-grid">
        <input
          placeholder="Search by title or company"
          value={filters.search}
          onChange={(event) => setFilters((prev) => ({ ...prev, search: event.target.value }))}
        />

        <select value={filters.domain} onChange={(event) => setFilters((prev) => ({ ...prev, domain: event.target.value }))}>
          <option value="">All Domains</option>
          {domains.map((domain) => <option key={domain} value={domain}>{domain}</option>)}
        </select>

        <select value={filters.work_mode} onChange={(event) => setFilters((prev) => ({ ...prev, work_mode: event.target.value }))}>
          <option value="">All Work Modes</option>
          {modes.map((mode) => <option key={mode} value={mode}>{mode}</option>)}
        </select>

        <select value={filters.location} onChange={(event) => setFilters((prev) => ({ ...prev, location: event.target.value }))}>
          <option value="">All Locations</option>
          {locations.map((location) => <option key={location} value={location}>{location}</option>)}
        </select>
      </section>

      {error ? <p className="error-text">{error}</p> : null}

      <section className="list-grid">
        {filtered.map((item) => (
          <article className="panel-card" key={item.id}>
            <h3>{item.title}</h3>
            <p>{item.company}</p>
            <p className="muted-text">{item.domain} • {item.work_mode} • {item.location}</p>
            <div className="inline-actions">
              <Link className="btn btn-soft" to={`/internships/${item.id}`}>View Details</Link>
            </div>
          </article>
        ))}
        {!filtered.length ? <p className="muted-text">No internships match your filters.</p> : null}
      </section>
    </div>
  );
};

export default InternshipListPage;
