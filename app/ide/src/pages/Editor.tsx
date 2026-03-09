import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../components/AuthProvider";
import { FileTree } from "../components/FileTree";
import { ReaderPanel } from "../components/ReaderPanel";
import { ChatPanel } from "../components/ChatPanel";
import {
  advanceWave,
  getFile,
  getSession,
  listMessages,
  type FileContent,
  type FileEntry,
  type Message,
  type Session,
} from "../api";

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

export function Editor() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { user, logout } = useAuth();
  const [session, setSession] = useState<Session | null>(null);
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileContent | null>(null);
  const [loading, setLoading] = useState(true);

  const loadSession = useCallback(async () => {
    if (!sessionId) return;
    try {
      const [sess, msgs] = await Promise.all([
        getSession(sessionId),
        listMessages(sessionId),
      ]);
      setSession(sess);
      setFiles(sess.files || []);
      setMessages(msgs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    loadSession();
  }, [loadSession]);

  const handleFileSelect = async (file: FileEntry) => {
    if (!sessionId) return;
    try {
      const content = await getFile(sessionId, file.id);
      setSelectedFile(content);
    } catch (err) {
      console.error(err);
    }
  };

  const handleNewMessage = (msg: Message) => {
    setMessages((prev) => [...prev, msg]);
  };

  const handleStreamComplete = () => {
    // Refresh session to pick up any new files
    loadSession();
  };

  const handleAdvanceWave = async () => {
    if (!sessionId || !session) return;
    try {
      const result = await advanceWave(sessionId);
      setSession({ ...session, current_wave: result.current_wave, wave_state: result.wave_state });
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return null;
  if (!session) return <div style={{ padding: "48px", textAlign: "center" }}>Session not found.</div>;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* Top bar */}
      <div className="topbar">
        <Link to="/" className="topbar-brand">lightpaper</Link>
        <span className="topbar-title">{session.title}</span>
        <span className="wave-badge">
          Wave {session.current_wave}: {waveLabel(session.current_wave)}
        </span>
        <button className="btn btn-secondary" onClick={handleAdvanceWave} style={{ fontSize: "12px", padding: "4px 12px" }}>
          Next Wave →
        </button>
        <div style={{ flex: 1 }} />
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

      {/* IDE layout */}
      <div className="ide-layout">
        {/* Sidebar */}
        <div className="sidebar">
          <div className="sidebar-header">Files</div>
          <FileTree
            files={files}
            selectedId={selectedFile?.id || null}
            onSelect={handleFileSelect}
          />
        </div>

        {/* Main area: reader (top) + chat (bottom) */}
        <div className="main-area">
          <ReaderPanel
            title={selectedFile?.title || ""}
            content={selectedFile?.content || ""}
          />
          <div className="resize-handle" />
          <ChatPanel
            sessionId={session.id}
            currentWave={session.current_wave}
            messages={messages}
            onNewMessage={handleNewMessage}
            onStreamComplete={handleStreamComplete}
          />
        </div>
      </div>
    </div>
  );
}
