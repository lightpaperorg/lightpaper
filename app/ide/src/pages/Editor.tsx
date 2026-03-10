import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../components/AuthProvider";
import { FileTree } from "../components/FileTree";
import { ReaderPanel } from "../components/ReaderPanel";
import { ChatPanel } from "../components/ChatPanel";
import { VerticalResizable } from "../components/ResizablePanels";
import {
  advanceWave,
  getFile,
  getSession,
  listMessages,
  publishSession,
  type FileContent,
  type FileEntry,
  type Message,
  type PublishResult,
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

function useIsMobile() {
  const [mobile, setMobile] = useState(
    typeof window !== "undefined" && window.innerWidth < 768
  );
  useEffect(() => {
    const mq = window.matchMedia("(max-width: 767px)");
    const handler = (e: MediaQueryListEvent) => setMobile(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);
  return mobile;
}

export function Editor() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { user, logout } = useAuth();
  const isMobile = useIsMobile();
  const [session, setSession] = useState<Session | null>(null);
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [publishResult, setPublishResult] = useState<PublishResult | null>(null);
  const [mobileTab, setMobileTab] = useState<"chat" | "manuscript">("chat");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

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
      if (isMobile) {
        setSidebarOpen(false);
        setMobileTab("manuscript");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleNewMessage = (msg: Message) => {
    setMessages((prev) => [...prev, msg]);
  };

  const handleFileCreated = (file: FileEntry) => {
    setFiles((prev) => [...prev, file]);
  };

  const handleStreamComplete = () => {
    if (sessionId) {
      getSession(sessionId).then((sess) => {
        setSession(sess);
        setFiles(sess.files || []);
      });
    }
  };

  const handleAdvanceWave = async () => {
    if (!sessionId || !session) return;
    try {
      const result = await advanceWave(sessionId);
      setSession({ ...session, current_wave: result.current_wave, wave_state: result.wave_state });
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to advance wave");
    }
  };

  const handlePublish = async () => {
    if (!sessionId || !session || publishing) return;
    if (!confirm("Publish this book to lightpaper.org? This will create a permanent public URL.")) return;
    setPublishing(true);
    try {
      const result = await publishSession(sessionId, {
        format: "post",
        description: session.book_config.description as string | undefined,
      });
      setPublishResult(result);
      setSession({ ...session, published_book_id: result.book_id, status: "completed" });
    } catch (err) {
      alert(err instanceof Error ? err.message : "Publishing failed");
    } finally {
      setPublishing(false);
    }
  };

  if (loading) return null;
  if (!session) return <div style={{ padding: "48px", textAlign: "center" }}>Session not found.</div>;

  const chatPanel = (
    <ChatPanel
      sessionId={session.id}
      currentWave={session.current_wave}
      messages={messages}
      onNewMessage={handleNewMessage}
      onFileCreated={handleFileCreated}
      onStreamComplete={handleStreamComplete}
    />
  );

  const readerPanel = (
    <ReaderPanel
      title={selectedFile?.title || ""}
      content={selectedFile?.content || ""}
    />
  );

  const filesSidebar = (
    <>
      <div className="sidebar-header">
        Files
        <span style={{ float: "right", fontWeight: "normal" }}>{files.length}</span>
      </div>
      <FileTree
        files={files}
        selectedId={selectedFile?.id || null}
        onSelect={handleFileSelect}
      />
    </>
  );

  return (
    <div className="editor-root">
      {/* Top bar */}
      <div className="topbar">
        {isMobile ? (
          <>
            <button
              className="btn btn-ghost topbar-hamburger"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              aria-label="Toggle files"
            >
              {sidebarOpen ? "\u2715" : "\u2630"}
            </button>
            <Link to="/" className="topbar-brand">lightpaper</Link>
            <span className="wave-badge">W{session.current_wave}</span>
            <div style={{ flex: 1 }} />
            <button
              className="btn btn-ghost topbar-more"
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label="More options"
            >
              \u22EF
            </button>
          </>
        ) : (
          <>
            <Link to="/" className="topbar-brand">lightpaper</Link>
            <span className="topbar-title">{session.title}</span>
            <span className="wave-badge">
              Wave {session.current_wave}: {waveLabel(session.current_wave)}
            </span>
            <button
              className="btn btn-secondary"
              onClick={handleAdvanceWave}
              style={{ fontSize: "12px", padding: "4px 12px" }}
            >
              Next Wave
            </button>
            {session.current_wave >= 4 && !session.published_book_id && (
              <button
                className="btn btn-primary"
                onClick={handlePublish}
                disabled={publishing}
                style={{ fontSize: "12px", padding: "4px 12px" }}
              >
                {publishing ? "Publishing..." : "Publish"}
              </button>
            )}
            {session.published_book_id && (
              <a
                href={publishResult?.url || `/books/${session.published_book_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-secondary"
                style={{ fontSize: "12px", padding: "4px 12px", textDecoration: "none", color: "var(--success)" }}
              >
                Published
              </a>
            )}
            <div style={{ flex: 1 }} />
            <span
              style={{ fontSize: "11px", color: "var(--text-mute)" }}
              title="Tokens used in this session"
            >
              {session.total_tokens_used.toLocaleString()} tokens
            </span>
            {user && (
              <>
                <span style={{ fontSize: "0.8rem", color: "var(--text-mute)" }}>
                  {user.display_name || user.handle}
                </span>
                <button className="btn btn-ghost" onClick={logout} style={{ fontSize: "0.8rem" }}>
                  Sign out
                </button>
              </>
            )}
          </>
        )}
      </div>

      {/* Mobile dropdown menu */}
      {isMobile && menuOpen && (
        <div className="mobile-menu">
          <div className="mobile-menu-title">{session.title}</div>
          <div className="mobile-menu-meta">
            Wave {session.current_wave}: {waveLabel(session.current_wave)}
            {" \u00B7 "}
            {session.total_tokens_used.toLocaleString()} tokens
          </div>
          <div className="mobile-menu-actions">
            <button className="btn btn-secondary" onClick={() => { handleAdvanceWave(); setMenuOpen(false); }}>
              Next Wave
            </button>
            {session.current_wave >= 4 && !session.published_book_id && (
              <button className="btn btn-primary" onClick={() => { handlePublish(); setMenuOpen(false); }} disabled={publishing}>
                {publishing ? "Publishing..." : "Publish"}
              </button>
            )}
            {session.published_book_id && (
              <a
                href={publishResult?.url || `/books/${session.published_book_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-secondary"
                style={{ textDecoration: "none", color: "var(--success)" }}
              >
                Published
              </a>
            )}
          </div>
          {user && (
            <div className="mobile-menu-user">
              <span>{user.display_name || user.handle}</span>
              <button className="btn btn-ghost" onClick={logout}>Sign out</button>
            </div>
          )}
        </div>
      )}

      {/* Publish success banner */}
      {publishResult && (
        <div className="publish-banner">
          Book published! {publishResult.chapter_count} chapters, {publishResult.total_word_count.toLocaleString()} words, quality {publishResult.quality_score}/100.
          <a href={publishResult.url} target="_blank" rel="noopener noreferrer" style={{ color: "white", fontWeight: 600 }}>
            View
          </a>
          <button
            className="btn btn-ghost"
            onClick={() => setPublishResult(null)}
            style={{ marginLeft: "auto", color: "white", fontSize: "0.75rem" }}
          >
            Dismiss
          </button>
        </div>
      )}

      {isMobile ? (
        /* ---- Mobile layout ---- */
        <>
          {/* Sidebar overlay */}
          {sidebarOpen && (
            <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
          )}
          <div className={`sidebar sidebar-mobile ${sidebarOpen ? "open" : ""}`}>
            {filesSidebar}
          </div>

          {/* Tab bar */}
          <div className="mobile-tabs">
            <button
              className={`mobile-tab ${mobileTab === "chat" ? "active" : ""}`}
              onClick={() => setMobileTab("chat")}
            >
              Chat
            </button>
            <button
              className={`mobile-tab ${mobileTab === "manuscript" ? "active" : ""}`}
              onClick={() => setMobileTab("manuscript")}
            >
              Manuscript
            </button>
          </div>

          {/* Content */}
          <div className="mobile-content">
            {mobileTab === "chat" ? chatPanel : readerPanel}
          </div>
        </>
      ) : (
        /* ---- Desktop layout ---- */
        <div className="ide-layout">
          <div className="sidebar">
            {filesSidebar}
          </div>
          <div className="main-area">
            <VerticalResizable
              defaultTopPercent={55}
              minTopPercent={15}
              minBottomPercent={20}
              top={readerPanel}
              bottom={chatPanel}
            />
          </div>
        </div>
      )}
    </div>
  );
}
