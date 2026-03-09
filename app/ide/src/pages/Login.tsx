import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../components/AuthProvider";
import { login } from "../api";

export function Login() {
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await login(apiKey);
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
        <h1>Writing IDE</h1>
        <p>Sign in with your lightpaper API key to start writing.</p>
        <form onSubmit={handleSubmit}>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="lp_free_... or lp_live_..."
            autoFocus
          />
          {error && <div className="login-error">{error}</div>}
          <button className="btn btn-primary" type="submit" disabled={loading || !apiKey}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p style={{ marginTop: "16px", fontSize: "12px", color: "var(--text-muted)" }}>
          Don't have an account? Create one at{" "}
          <a href="/" style={{ color: "var(--accent)" }}>lightpaper.org</a> using the API or MCP server.
        </p>
      </div>
    </div>
  );
}
