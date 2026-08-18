import { AlertTriangle, Save, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { getApiErrorMessage } from "../services/api";
import { deleteAccount, fetchProfile, updateProfile } from "../services/profileService";

const ProfilePage = () => {
  const { logout, setUser } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [form, setForm] = useState({ full_name: "", email: "", role: "" });

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const profile = await fetchProfile();
        setForm({
          full_name: profile.full_name || "",
          email: profile.email || "",
          role: profile.role || "",
        });
        setUser(profile);
      } catch (err) {
        setError(getApiErrorMessage(err, "Unable to load profile."));
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [setUser]);

  const onSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      await updateProfile({ full_name: form.full_name });
      const refreshed = await fetchProfile();
      setUser(refreshed);
      setSuccess("Profile updated successfully.");
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to update profile."));
    } finally {
      setSaving(false);
    }
  };

  const onDelete = async () => {
    const confirmed = window.confirm("Delete account permanently?");
    if (!confirmed) return;

    try {
      await deleteAccount();
      logout();
      navigate("/register");
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to delete account."));
    }
  };

  if (loading) {
    return <div className="page-center">Loading profile...</div>;
  }

  return (
    <div className="page-stack">
      <section className="page-hero">
        <p className="eyebrow">Profile</p>
        <h1>Your Profile</h1>
        <p>Manage your account information.</p>
      </section>

      <form className="panel-card form-grid" onSubmit={onSubmit}>
        {error ? <p className="error-text">{error}</p> : null}
        {success ? <p className="success-text">{success}</p> : null}

        <label htmlFor="full_name">Name</label>
        <input
          id="full_name"
          value={form.full_name}
          onChange={(event) => setForm((prev) => ({ ...prev, full_name: event.target.value }))}
          required
        />

        <label htmlFor="email">Email</label>
        <input id="email" value={form.email} disabled />

        <label htmlFor="role">Role</label>
        <input id="role" value={form.role} disabled />

        <div className="readonly-grid">
          <div>
            <p className="field-label">Phone</p>
            <p className="muted-text">Not provided</p>
          </div>
          <div>
            <p className="field-label">Address</p>
            <p className="muted-text">Not provided</p>
          </div>
          <div>
            <p className="field-label">LinkedIn</p>
            <p className="muted-text">Not provided</p>
          </div>
          <div>
            <p className="field-label">GitHub</p>
            <p className="muted-text">Not provided</p>
          </div>
        </div>

        <div className="form-actions">
          <button className="btn btn-primary" disabled={saving} type="submit">
            <Save size={16} /> {saving ? "Saving..." : "Save Profile"}
          </button>
          <button className="btn btn-danger" type="button" onClick={onDelete}>
            <Trash2 size={16} /> Delete Account
          </button>
        </div>
      </form>

      <p className="hint-text"><AlertTriangle size={14} /> Profile API currently supports full name update.</p>
    </div>
  );
};

export default ProfilePage;
