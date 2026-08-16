import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { register } from "./api";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setMessage("");
    setError("");

    try {
      const user = await register({ email, password });
      setMessage(`Account created for ${user.email}. You can now log in.`);
      setPassword("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Registration failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section>
      <header className="feature-heading">
        <h1>Register</h1>
        <p>Create a generic BuildKit account.</p>
      </header>
      <article className="feature-card">
        <form className="form-stack" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="register-email">Email</label>
            <input id="register-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </div>
          <div className="form-field">
            <label htmlFor="register-password">Password</label>
            <input id="register-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required />
          </div>
          <button className="button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Registering…" : "Register"}
          </button>
          {error && <p className="status-message error">{error}</p>}
          {message && <p className="status-message success">{message}</p>}
          <p>Already registered? <Link to="/auth/login">Log in</Link>.</p>
        </form>
      </article>
    </section>
  );
}
