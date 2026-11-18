
import { useState } from "react";
import { ShieldCheck, Mail, Lock, Eye, EyeOff, ArrowRight } from "lucide-react";
import api from "../services/api";
import "./Login.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await api.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      localStorage.setItem("brandsentinel_token", response.data.access_token);
      localStorage.setItem("brandsentinel_user", JSON.stringify(response.data.user));

      window.location.href = "/";
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-brand-panel">
        <div className="login-brand">
          <div className="login-brand-icon"><ShieldCheck size={27} /></div>
          <span>BrandSentinel</span>
        </div>

        <div className="login-message">
          <span className="login-eyebrow">INTELLIGENT BRAND GOVERNANCE</span>
          <h1>Protect your brand.<br />Publish with confidence.</h1>
          <p>Maintain consistency, verify claims and review every piece of content before it reaches your audience.</p>
          <div className="login-feature">
            <ShieldCheck size={19} />
            <span>Explainable findings. Human oversight. Brand integrity.</span>
          </div>
        </div>

        <span className="login-copyright">© 2026 BrandSentinel</span>
      </div>

      <div className="login-form-panel">
        <form className="login-form" onSubmit={handleLogin}>
          <div className="mobile-login-logo"><ShieldCheck size={28} /> BrandSentinel</div>
          <span className="form-eyebrow">WELCOME BACK</span>
          <h2>Sign in to your account</h2>
          <p className="form-description">Enter your credentials to access your workspace.</p>

          {error && <div className="login-error">{error}</div>}

          <label>Email address</label>
          <div className="login-input">
            <Mail size={18} />
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <label>Password</label>
          <div className="login-input">
            <Lock size={18} />
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="button" className="password-toggle" onClick={() => setShowPassword(!showPassword)}>
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          <button type="submit" className="login-submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
            {!loading && <ArrowRight size={18} />}
          </button>

          <div className="login-security">
            <ShieldCheck size={16} />
            Your workspace is protected with secure authentication.
          </div>
        </form>
      </div>
    </div>
  );
}
