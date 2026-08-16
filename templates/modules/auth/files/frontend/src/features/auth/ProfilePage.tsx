import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { clearAccessToken, getProfile, readAccessToken, type User } from "./api";

export default function ProfilePage() {
  const [token, setToken] = useState(() => readAccessToken());
  const [user, setUser] = useState<User | null>(null); const [error, setError] = useState("");
  const [loading, setLoading] = useState(Boolean(token));
  useEffect(() => {
    if (!token) return; let current = true; setLoading(true); setError("");
    getProfile(token).then((value) => { if (current) setUser(value); }).catch((reason: unknown) => { if (current) setError(reason instanceof Error ? reason.message : "Profile request failed"); }).finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [token]);
  function logout() { clearAccessToken(); setToken(null); setUser(null); setError(""); }
  return <section><header className="feature-heading"><h1>Profile</h1><p>An authenticated user example.</p></header><article className="feature-card">{!token && <p>Please <Link to="/auth/login">log in</Link> to view your profile.</p>}{loading && <p className="status-message">Loading profile…</p>}{error && <p className="status-message error">{error}</p>}{user && <><dl className="metadata-list"><dt>User ID</dt><dd>{user.id}</dd><dt>Email</dt><dd>{user.email}</dd><dt>Status</dt><dd>{user.is_active ? "Active" : "Inactive"}</dd></dl><button className="button" type="button" onClick={logout}>Log out</button></>}</article></section>;
}
