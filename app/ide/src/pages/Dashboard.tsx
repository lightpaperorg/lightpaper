import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../components/AuthProvider";
import { createSession, listSessions, type Session } from "../api";

const WAVE_LABELS: Record<number, string> = {
  0: "Raw Capture",
  1: "Architecture",
  2: "Voice & Texture",
  3: "Pivotal Scenes",
  4: "Full Draft",
};

function waveLabel(wave: number): string {
  return WAVE_LABELS[wave] || `Edit Pass ${wave - 4}`;
}

export function Dashboard() {
  const { user, logout, loading: authLoading } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [title, setTitle] = useState("");
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      listSessions().then(setSessions).catch(console.error);
    }
  }, [user]);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim() || creating) return;
    setCreating(true);
    try {
      const session = await createSession(title.trim());
      navigate(`/${session.id}`);
    } catch (err) {
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  if (authLoading) return null;

  return (
    <div>
      <div className="topbar">
        <Link to="/" className="topbar-brand">lightpaper</Link>
        <span className="topbar-title">Writing IDE</span>
        {user && (
          <>
            <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
              {user.display_name || user.handle}
            </span>
            <button className="btn btn-ghost" onClick={logout} style={{ fontSize: "13px" }}>
              Sign out
            </button>
          </>
        )}
      </div>

      <div className="dashboard">
        <h1>Your Books</h1>
        <p className="dashboard-subtitle">
          Write a book using the Wave Method — from raw idea to published manuscript.
        </p>

        <form className="new-session-form" onSubmit={handleCreate}>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Working title for your new book..."
            autoFocus
          />
          <button className="btn btn-primary" type="submit" disabled={creating || !title.trim()}>
            {creating ? "Creating..." : "New Book"}
          </button>
        </form>

        <div className="session-list">
          {sessions.map((s) => (
            <Link to={`/${s.id}`} key={s.id} className="session-card">
              <div>
                <div className="session-card-title">{s.title}</div>
                <div className="session-card-meta">
                  Wave {s.current_wave}: {waveLabel(s.current_wave)}
                  {" · "}
                  {s.total_tokens_used.toLocaleString()} tokens used
                  {s.published_book_id && " · Published"}
                </div>
              </div>
              <span className="wave-badge">W{s.current_wave}</span>
            </Link>
          ))}
          {sessions.length === 0 && (
            <p style={{ color: "var(--text-muted)", padding: "16px 0" }}>
              No books yet. Enter a title above to start your first book.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
