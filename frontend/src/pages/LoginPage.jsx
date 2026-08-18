import { Eye, EyeOff, LogIn } from "lucide-react";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { getApiErrorMessage } from "../services/api";

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ email: "", password: "" });

  const onChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(form);
      const to = location.state?.from || "/dashboard";
      navigate(to, { replace: true });
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to login. Please check your credentials."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={onSubmit}>
        <h1>Login</h1>
        <p className="muted-text">Continue to your internship matching workspace.</p>

        {location.search.includes("session=expired") ? (
          <p className="notice">Your session has expired. Please login again.</p>
        ) : null}
        {error ? <p className="error-text">{error}</p> : null}

        <label htmlFor="email">Email</label>
        <input id="email" name="email" type="email" required value={form.email} onChange={onChange} />

        <label htmlFor="password">Password</label>
        <div className="password-wrap">
          <input
            id="password"
            name="password"
            type={showPassword ? "text" : "password"}
            required
            value={form.password}
            onChange={onChange}
          />
          <button type="button" onClick={() => setShowPassword((prev) => !prev)} className="icon-btn" aria-label="Toggle password visibility">
            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>

        <button className="btn btn-primary" type="submit" disabled={loading}>
          <LogIn size={16} /> {loading ? "Logging in..." : "Login"}
        </button>

        <p className="muted-text auth-footer">Don't have an account? <Link to="/register">Create one</Link></p>
      </form>
    </div>
  );
};

export default LoginPage;
