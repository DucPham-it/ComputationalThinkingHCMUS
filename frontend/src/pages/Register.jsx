import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register as registerRequest } from "../services/authService";
import { useAuth } from "../hooks/useAuth";

const pageStyles = {
  minHeight: "calc(100vh - 140px)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "32px 16px"
};

const formStyles = {
  width: "min(100%, 560px)",
  display: "grid",
  gap: "20px"
};

const statusStyles = {
  padding: "12px 16px",
  borderRadius: "12px",
  textAlign: "center",
  background: "rgba(239, 246, 255, 0.9)",
  border: "1px solid rgba(37, 99, 235, 0.16)",
  color: "var(--color-primary-dark)"
};

const labelStyles = {
  display: "grid",
  gap: "8px",
  fontWeight: 600,
  color: "var(--color-text)"
};

const submitStyles = {
  width: "100%",
  padding: "14px 18px",
  borderRadius: "16px",
  fontSize: "1rem",
  fontWeight: 700
};

export default function Register() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const payload = {
      user_name: String(formData.get("user_name") || "").trim(),
      email: String(formData.get("email") || "").trim(),
      password: String(formData.get("password") || "")
    };

    try {
      const auth = await registerRequest(payload);
      setUser(auth.user);
      navigate("/profile");
    } catch (requestError) {
      setError(
        requestError?.response?.data?.detail ||
          "Register failed. Please check your information and try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section style={pageStyles}>
      <form className="card" style={formStyles} onSubmit={handleSubmit}>
        <div>
          <h1>Create Account</h1>
          <p>
            Start with your username, email, and password. We&apos;ll take you to
            the profile page right after this step.
          </p>
        </div>

        <label style={labelStyles}>
          Username
          <input
            name="user_name"
            type="text"
            placeholder="traveler01"
            autoComplete="username"
            minLength={3}
            required
          />
        </label>

        <label style={labelStyles}>
          Email
          <input
            name="email"
            type="email"
            placeholder="you@example.com"
            autoComplete="email"
            required
          />
        </label>

        <label style={labelStyles}>
          Password
          <input
            name="password"
            type="password"
            placeholder="At least 6 characters"
            autoComplete="new-password"
            minLength={6}
            required
          />
        </label>

        <button className="btn-primary" style={submitStyles} disabled={isSubmitting}>
          {isSubmitting ? "Creating account..." : "Register"}
        </button>

        <p style={{ marginBottom: 0, textAlign: "center" }}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>

        {error ? <div style={statusStyles}>{error}</div> : null}
      </form>
    </section>
  );
}
