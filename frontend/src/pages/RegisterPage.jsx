import { UserPlus } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { getApiErrorMessage } from "../services/api";

const RegisterPage = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    confirmPassword: "",
    role: "candidate",
  });

  const onChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await register({
        full_name: form.full_name,
        email: form.email,
        password: form.password,
        role: form.role,
      });
      setSuccess("Account created successfully. Redirecting to login...");
      setTimeout(() => navigate("/login"), 800);
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to create account."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={onSubmit}>
        <h1>Create Account</h1>
        <p className="muted-text">Start your AI-powered internship matching journey.</p>

        {error ? <p className="error-text">{error}</p> : null}
        {success ? <p className="success-text">{success}</p> : null}

        <label htmlFor="full_name">Full Name</label>
        <input id="full_name" name="full_name" required value={form.full_name} onChange={onChange} />

        <label htmlFor="email">Email</label>
        <input id="email" name="email" type="email" required value={form.email} onChange={onChange} />

        <label htmlFor="password">Password</label>
        <input id="password" name="password" type="password" required value={form.password} onChange={onChange} />

        <label htmlFor="confirmPassword">Confirm Password</label>
        <input id="confirmPassword" name="confirmPassword" type="password" required value={form.confirmPassword} onChange={onChange} />

        <button className="btn btn-primary" type="submit" disabled={loading}>
          <UserPlus size={16} /> {loading ? "Creating..." : "Create Account"}
        </button>

        <p className="muted-text auth-footer">Already have an account? <Link to="/login">Login</Link></p>
      </form>
    </div>
  );
};

export default RegisterPage;
