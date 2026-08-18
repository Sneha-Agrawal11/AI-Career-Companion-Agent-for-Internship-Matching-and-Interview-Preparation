import { Link, NavLink, useNavigate } from "react-router-dom";
import { BriefcaseBusiness, FileText, LayoutDashboard, LogOut, UserCircle2 } from "lucide-react";
import { useAuth } from "../hooks/useAuth";

const TopNav = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const onLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="top-nav">
      <div className="container nav-inner">
        <Link to="/dashboard" className="brand">
          <span className="brand-dot" />
          <div>
            <p className="brand-title">InternMatch AI</p>
            <p className="brand-subtitle">AI-powered internship matching from your resume</p>
          </div>
        </Link>

        <nav className="nav-links" aria-label="Primary">
          <NavLink to="/dashboard"><LayoutDashboard size={16} />Dashboard</NavLink>
          <NavLink to="/resume"><FileText size={16} />Resume</NavLink>
          <NavLink to="/internships"><BriefcaseBusiness size={16} />Internships</NavLink>
          <NavLink to="/profile"><UserCircle2 size={16} />Profile</NavLink>
        </nav>

        <div className="nav-user">
          <div className="avatar">{(user?.full_name || "U").slice(0, 1).toUpperCase()}</div>
          <div className="user-meta">
            <p>{user?.full_name || "User"}</p>
            <small>{user?.email || ""}</small>
          </div>
          <button type="button" className="btn btn-ghost" onClick={onLogout}>
            <LogOut size={16} />Logout
          </button>
        </div>
      </div>
    </header>
  );
};

export default TopNav;
