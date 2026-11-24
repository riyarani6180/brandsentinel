
import { useState } from "react";
import {
  ShieldCheck,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  UserRound,
  ArrowLeft
} from "lucide-react";

import api from "../services/api";
import "./Login.css";

export default function Login() {
  const [selectedRole, setSelectedRole] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const resetSelection = () => {
    setSelectedRole("");
    setEmail("");
    setPassword("");
    setError("");
    setShowPassword(false);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    const cleanEmail = email.trim().toLowerCase();

    if (!cleanEmail) {
      setError("Please enter your email address.");
      return;
    }

    if (password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append("username", cleanEmail);
      formData.append("password", password);

      const response = await api.post(
        "/auth/login",
        formData,
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          }
        }
      );

      const token = response.data?.access_token;
      const user = response.data?.user;

      if (!token || !user) {
        throw new Error("Invalid login response from server.");
      }

      const actualRole = String(user.role || "").toUpperCase();

      if (
        selectedRole === "ADMIN" &&
        actualRole !== "BRAND_ADMIN"
      ) {
        setError(
          "Access denied. This account is not registered as an Admin."
        );
        return;
      }

      if (
        selectedRole === "CUSTOMER" &&
        actualRole !== "CREATOR"
      ) {
        setError(
          "Access denied. Please select the correct workspace for your account."
        );
        return;
      }

      localStorage.setItem("brandsentinel_token", token);
      localStorage.setItem(
        "brandsentinel_user",
        JSON.stringify(user)
      );

      window.location.replace("/");

    } catch (err) {
      console.error("Login error:", err);

      if (err.response) {
        const detail = err.response.data?.detail;

        if (err.response.status === 401) {
          setError("Incorrect email or password.");
        } else if (typeof detail === "string") {
          setError(detail);
        } else {
          setError("Unable to log in. Please try again.");
        }
      } else {
        setError(
          err.message ||
          "Cannot connect to the server. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">

      <div className="login-brand-panel">
        <div className="login-brand">
          <div className="login-brand-icon">
            <ShieldCheck size={27} />
          </div>
          <span>BrandSentinel</span>
        </div>

        <div className="login-message">
          <span className="login-eyebrow">
            INTELLIGENT BRAND GOVERNANCE
          </span>

          <h1>
            Protect your brand.
            <br />
            Publish with confidence.
          </h1>

          <p>
            Maintain consistency, verify claims and review every
            piece of content before it reaches your audience.
          </p>

          <div className="login-feature">
            <ShieldCheck size={19} />
            <span>
              Explainable findings. Human oversight. Brand integrity.
            </span>
          </div>
        </div>

        <span className="login-copyright">
          © 2026 BrandSentinel
        </span>
      </div>

      <div className="login-form-panel">

        {!selectedRole ? (
          <div className="login-form role-selection">

            <div className="mobile-login-logo">
              <ShieldCheck size={28} />
              BrandSentinel
            </div>

            <span className="form-eyebrow">
              WELCOME TO BRAND SENTINEL
            </span>

            <h2>Choose your workspace</h2>

            <p className="form-description">
              Select an account type to continue.
            </p>

            <div className="role-cards">

              <button
                type="button"
                className="role-card admin-role"
                onClick={() => {
                  setSelectedRole("ADMIN");
                  setError("");
                }}
              >
                <div className="role-icon">
                  <ShieldCheck size={30} />
                </div>

                <strong>Admin</strong>

                <ArrowRight
                  size={20}
                  className="role-arrow"
                />
              </button>

              <button
                type="button"
                className="role-card customer-role"
                onClick={() => {
                  setSelectedRole("CUSTOMER");
                  setError("");
                }}
              >
                <div className="role-icon">
                  <UserRound size={30} />
                </div>

                <strong>Customer</strong>

                <ArrowRight
                  size={20}
                  className="role-arrow"
                />
              </button>

            </div>

            <div className="login-security">
              <ShieldCheck size={16} />
              Secure role-based authentication.
            </div>

          </div>
        ) : (

          <form className="login-form" onSubmit={handleLogin}>

            <div className="mobile-login-logo">
              <ShieldCheck size={28} />
              BrandSentinel
            </div>

            <button
              type="button"
              className="back-role-button"
              onClick={resetSelection}
            >
              <ArrowLeft size={16} />
              Change workspace
            </button>

            <span className="form-eyebrow">
              {selectedRole === "ADMIN"
                ? "ADMINISTRATOR ACCESS"
                : "CUSTOMER ACCESS"}
            </span>

            <h2>
              {selectedRole === "ADMIN"
                ? "Admin sign in"
                : "Customer sign in"}
            </h2>

            <p className="form-description">
              {selectedRole === "ADMIN"
                ? "Enter your administrator credentials."
                : "Sign in or create your Customer account."}
            </p>

            {error && (
              <div className="login-error" role="alert">
                {error}
              </div>
            )}

            <label htmlFor="login-email">
              Email address
            </label>

            <div className="login-input">
              <Mail size={18} />

              <input
                id="login-email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <label htmlFor="login-password">
              Password
            </label>

            <div className="login-input">
              <Lock size={18} />

              <input
                id="login-password"
                type={showPassword ? "text" : "password"}
                placeholder="At least 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={6}
                autoComplete="current-password"
                required
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={
                  showPassword ? "Hide password" : "Show password"
                }
              >
                {showPassword
                  ? <EyeOff size={18} />
                  : <Eye size={18} />}
              </button>
            </div>

            <button
              type="submit"
              className="login-submit"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Continue"}

              {!loading && <ArrowRight size={18} />}
            </button>

            {selectedRole === "ADMIN" && (
              <p className="role-hint">
                Authorized administrators only.
              </p>
            )}

            <div className="login-security">
              <ShieldCheck size={16} />
              Secure authentication for your BrandSentinel workspace.
            </div>

          </form>
        )}

      </div>
    </div>
  );
}
