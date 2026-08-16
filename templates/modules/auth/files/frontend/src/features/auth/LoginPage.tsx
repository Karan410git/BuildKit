import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login, storeAccessToken } from "./api";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setLoading(true); setError("");
    try { const response = await login({ email, password }); storeAccessToken(response.access_token); navigate("/auth/profile"); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Login failed"); }
    finally { setLoading(false); }
  }
  return <section><header className="feature-heading"><h1>Login</h1><p>Sign in with an existing BuildKit account.</p></header><article className="feature-card"><form className="form-stack" onSubmit={submit}><div className="form-field"><label htmlFor="login-email">Email</label><input id="login-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></div><div className="form-field"><label htmlFor="login-password">Password</label><input id="login-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></div><button className="button" disabled={loading}>{loading ? "Logging in…" : "Login"}</button>{error && <p className="status-message error">{error}</p>}<p>Need an account? <Link to="/auth/register">Register</Link>.</p></form></article></section>;
}
