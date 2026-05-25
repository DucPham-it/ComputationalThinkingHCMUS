import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import LoginPage from "@react-login-page/page1";
import { login as loginRequest } from "../services/authService";
import { useAuth } from "../hooks/useAuth";

const loginStyles = {
  minHeight: "calc(100vh - 140px)",
  padding: "32px 16px"
};

const statusStyles = {
  marginTop: "16px",
  padding: "12px 16px",
  borderRadius: "12px",
  backgroundColor: "rgba(255, 255, 255, 0.92)",
  boxShadow: "0 12px 30px rgba(31, 41, 55, 0.12)",
  color: "#7f1d1d",
  textAlign: "center"
};

function getLoginErrorMessage(error) {
  if (!error?.response) {
    return "Không kết nối được backend local. Hãy bật backend ở http://localhost:8000 rồi thử lại.";
  }

  return (
    error.response.data?.detail ||
    "Login failed. Please check your username/email and password."
  );
}


export default function LoginView() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const identifier = String(formData.get("identifier") || "").trim();
    const password = String(formData.get("password") || "");

    try {
      const auth = await loginRequest({ identifier, password });
      setUser(auth.user);
      if (!auth.user.first_name || !auth.user.last_name || !auth.user.birth_date) {
        navigate("/profile");
        return;
      }
      navigate("/");
    } catch (requestError) {
      setError(getLoginErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <LoginPage style={loginStyles}>
        <LoginPage.Logo visible={false} />
        <LoginPage.Title>Login</LoginPage.Title>
        <LoginPage.Username
          visible={false}
        />
        <LoginPage.Username
          keyname="identifier"
          name="identifier"
          type="text"
          placeholder="Username or email"
          autoComplete="username"
          required
        />
        <LoginPage.Password
          name="password"
          placeholder="Password"
          autoComplete="current-password"
          required
        />
        <LoginPage.Submit disabled={isSubmitting}>
          {isSubmitting ? "Running..." : "Login"}
        </LoginPage.Submit>
        <LoginPage.Footer>
          Don't have account? <Link to="/register">Register</Link>
        </LoginPage.Footer>
      </LoginPage>
      {error ? <div style={statusStyles}>{error}</div> : null}
    </form>
  );
}
