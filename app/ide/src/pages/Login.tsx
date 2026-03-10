import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../components/AuthProvider";
import { login, sendOtp, verifyOtp } from "../api";

type Step = "email" | "code" | "apikey";

export function Login() {
  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [code, setCode] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const handleEmailSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!email.trim() || loading) return;
    setError("");
    setLoading(true);
    try {
      const result = await sendOtp(email.trim());
      setSessionId(result.session_id);
      setMessage(result.message);
      setStep("code");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send code");
    } finally {
      setLoading(false);
    }
  };

  const handleCodeSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!code.trim() || loading) return;
    setError("");
    setLoading(true);
    try {
      const result = await verifyOtp(sessionId, code.trim());
      setUser({
        id: "",
        handle: result.handle,
        display_name: result.display_name,
        email: result.email,
        gravity_level: result.gravity_level,
      });
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleApiKeySubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim() || loading) return;
    setError("");
    setLoading(true);
    try {
      const result = await login(apiKey.trim());
      setUser({
        id: "",
        handle: result.handle,
        display_name: result.display_name,
        email: "",
        gravity_level: result.gravity_level,
      });
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-mark" />
        <h1>lightpaper</h1>

        {step === "email" && (
          <>
            <p>Sign in or create an account.</p>
            <form onSubmit={handleEmailSubmit}>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                autoFocus
              />
              {error && <div className="login-error">{error}</div>}
              <button className="btn btn-primary" type="submit" disabled={loading || !email.trim()}>
                {loading ? "Sending code..." : "Continue with email"}
              </button>
            </form>
            <p style={{ marginTop: "1.25rem" }}>
              Already have an API key?{" "}
              <button
                className="link-btn"
                onClick={() => { setStep("apikey"); setError(""); }}
              >
                Sign in with API key
              </button>
            </p>
          </>
        )}

        {step === "code" && (
          <>
            <p>{message}</p>
            <form onSubmit={handleCodeSubmit}>
              <input
                type="text"
                inputMode="numeric"
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                placeholder="6-digit code"
                autoFocus
                style={{ letterSpacing: "4px", textAlign: "center", fontSize: "1.1rem" }}
              />
              {error && <div className="login-error">{error}</div>}
              <button className="btn btn-primary" type="submit" disabled={loading || code.length !== 6}>
                {loading ? "Verifying..." : "Verify code"}
              </button>
            </form>
            <p style={{ marginTop: "1.25rem" }}>
              <button
                className="link-btn"
                onClick={() => { setStep("email"); setError(""); setCode(""); }}
              >
                Use a different email
              </button>
            </p>
          </>
        )}

        {step === "apikey" && (
          <>
            <p>Sign in with your lightpaper API key.</p>
            <form onSubmit={handleApiKeySubmit}>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="lp_free_... or lp_live_..."
                autoFocus
              />
              {error && <div className="login-error">{error}</div>}
              <button className="btn btn-primary" type="submit" disabled={loading || !apiKey.trim()}>
                {loading ? "Signing in..." : "Sign in"}
              </button>
            </form>
            <p style={{ marginTop: "1.25rem" }}>
              <button
                className="link-btn"
                onClick={() => { setStep("email"); setError(""); }}
              >
                Sign in with email instead
              </button>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
