import { Link } from "react-router-dom";

const NotFoundPage = () => {
  return (
    <section className="panel-card">
      <h1>Page not found</h1>
      <p className="muted-text">The page you requested does not exist.</p>
      <Link to="/dashboard" className="btn btn-primary">Go to Dashboard</Link>
    </section>
  );
};

export default NotFoundPage;
