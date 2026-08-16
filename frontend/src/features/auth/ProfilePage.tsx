import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  clearAccessToken,
  getProfile,
  readAccessToken,
  type User,
} from "./api";

export default function ProfilePage() {
  const [token, setToken] = useState(() => readAccessToken());
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(Boolean(token));

  useEffect(() => {
    if (!token) return;

    let isCurrent = true;
    setIsLoading(true);
    setError("");

    getProfile(token)
      .then((profile) => {
        if (isCurrent) setUser(profile);
      })
      .catch((requestError: unknown) => {
        if (isCurrent) {
          setError(requestError instanceof Error ? requestError.message : "Profile request failed");
        }
      })
      .finally(() => {
        if (isCurrent) setIsLoading(false);
      });

    return () => {
      isCurrent = false;
    };
  }, [token]);

  function logout() {
    clearAccessToken();
    setToken(null);
    setUser(null);
    setError("");
  }

  return (
    <section>
      <header className="feature-heading">
        <h1>Profile</h1>
        <p>An authenticated user example.</p>
      </header>
      <article className="feature-card">
        {!token && <p>Please <Link to="/auth/login">log in</Link> to view your profile.</p>}
        {isLoading && <p className="status-message">Loading profile…</p>}
        {error && <p className="status-message error">{error}</p>}
        {user && (
          <>
            <dl className="metadata-list">
              <dt>User ID</dt>
              <dd>{user.id}</dd>
              <dt>Email</dt>
              <dd>{user.email}</dd>
              <dt>Status</dt>
              <dd>{user.is_active ? "Active" : "Inactive"}</dd>
            </dl>
            <button className="button" type="button" onClick={logout}>Log out</button>
          </>
        )}
      </article>
    </section>
  );
}
