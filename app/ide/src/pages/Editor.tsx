import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../components/AuthProvider";
import { FileTree } from "../components/FileTree";
import { ReaderPanel } from "../components/ReaderPanel";
import { ChatPanel } from "../components/ChatPanel";
import { VerticalResizable } from "../components/ResizablePanels";
import {
  advanceWave,
  downloadPdf,
  getFile,
  getSession,
  listMessages,
  publishSession,
  savePdf,
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

function isBookSession(session: Session): boolean {
  return session.current_wave > 0 || (session.book_config as Record<string, unknown>)?.type === "book";
}

const FORMATS = [
  { value: "post", label: "Post", desc: "Blog, tutorial, practical" },
  { value: "essay", label: "Essay", desc: "Longform, narrative, literary" },
  { value: "paper", label: "Paper", desc: "Research, academic, technical" },
];

const LICENSES = [
  { value: "all-rights-reserved", label: "All Rights Reserved" },
  { value: "cc-by-4.0", label: "CC BY 4.0" },
  { value: "cc-by-sa-4.0", label: "CC BY-SA 4.0" },
  { value: "cc-by-nc-4.0", label: "CC BY-NC 4.0" },
  { value: "cc-by-nc-sa-4.0", label: "CC BY-NC-SA 4.0" },
  { value: "cc0", label: "CC0 (Public Domain)" },
];

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

  // Publish modal state
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [pubFormat, setPubFormat] = useState("post");
  const [pubLicense, setPubLicense] = useState("all-rights-reserved");
  const [pubDescription, setPubDescription] = useState("");
  const [pubAs, setPubAs] = useState<"auto" | "book" | "document">("auto");

  // PDF download state
  const [pdfLoading, setPdfLoading] = useState<string | null>(null);

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

  const isBook = session ? isBookSession(session) : false;
  const hasFiles = files.length > 0;
  const hasChapterFiles = files.some(f => f.chapter_number !== null);
  const canPublish = hasFiles && !session?.published_book_id;

  const openPublishModal = () => {
    if (session?.book_config?.description) {
      setPubDescription(session.book_config.description as string);
    }
    // Default publish_as based on content
    setPubAs(hasChapterFiles ? "book" : "document");
    setShowPublishModal(true);
    setMenuOpen(false);
  };

  const handlePublish = async () => {
    if (!sessionId || !session || publishing) return;
    setPublishing(true);
    try {
      const result = await publishSession(sessionId, {
        format: pubFormat,
        license: pubLicense,
        description: pubDescription || undefined,
        publish_as: pubAs,
      });
      setPublishResult(result);
      setSession({ ...session, published_book_id: result.book_id, status: "completed" });
      setShowPublishModal(false);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Publishing failed");
    } finally {
      setPublishing(false);
    }
  };

  const handleDownloadPdf = async (action: "preview" | "interior" | "cover" | "certificate") => {
    const bookId = session?.published_book_id;
    if (!bookId) return;
    setPdfLoading(action);
    try {
      const blob = await downloadPdf(bookId, action, action === "cover" ? 300 : undefined);
      const slug = session?.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/-+$/, "") || bookId;
      savePdf(blob, `${slug}-${action}.pdf`);
    } catch (err) {
      alert(err instanceof Error ? err.message : `Failed to generate ${action} PDF`);
    } finally {
      setPdfLoading(null);
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

  const publishModal = showPublishModal && (
    <div className="modal-overlay" onClick={() => setShowPublishModal(false)}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Publish to lightpaper.org</h2>
        <p style={{ color: "var(--text-mute)", marginBottom: "1.25rem", fontSize: "0.85rem" }}>
          This will create a permanent public URL.
        </p>

        {/* Publish as toggle — only show if there are chapter files (could be either) */}
        {hasChapterFiles && (
          <>
            <label className="modal-label">Publish as</label>
            <div className="modal-options" style={{ marginBottom: "1rem" }}>
              <button
                className={`modal-option ${pubAs === "document" ? "active" : ""}`}
                onClick={() => setPubAs("document")}
              >
                <strong>Article</strong>
                <span>Single page</span>
              </button>
              <button
                className={`modal-option ${pubAs === "book" ? "active" : ""}`}
                onClick={() => setPubAs("book")}
              >
                <strong>Book</strong>
                <span>Chapters + TOC</span>
              </button>
            </div>
          </>
        )}

        <label className="modal-label">Format</label>
        <div className="modal-options">
          {FORMATS.map((f) => (
            <button
              key={f.value}
              className={`modal-option ${pubFormat === f.value ? "active" : ""}`}
              onClick={() => setPubFormat(f.value)}
            >
              <strong>{f.label}</strong>
              <span>{f.desc}</span>
            </button>
          ))}
        </div>

        <label className="modal-label">License</label>
        <select
          value={pubLicense}
          onChange={(e) => setPubLicense(e.target.value)}
          style={{
            width: "100%",
            padding: "8px 12px",
            background: "var(--surface)",
            border: "1px solid var(--border-light)",
            borderRadius: "var(--radius)",
            color: "var(--text-bright)",
            fontSize: "0.85rem",
            marginBottom: "1rem",
          }}
        >
          {LICENSES.map((l) => (
            <option key={l.value} value={l.value}>{l.label}</option>
          ))}
        </select>

        <label className="modal-label">Description <span style={{ fontWeight: 400, color: "var(--text-mute)" }}>(optional)</span></label>
        <textarea
          value={pubDescription}
          onChange={(e) => setPubDescription(e.target.value)}
          placeholder="A brief description for the book landing page..."
          rows={3}
          style={{ marginBottom: "1.25rem", fontSize: "0.85rem" }}
        />

        <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
          <button className="btn btn-secondary" onClick={() => setShowPublishModal(false)}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={handlePublish} disabled={publishing}>
            {publishing ? "Publishing..." : "Publish"}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="editor-root">
      {publishModal}

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
            {isBook && (
              <>
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
              </>
            )}
            {canPublish && (isBook ? session.current_wave >= 4 : hasFiles) && (
              <button
                className="btn btn-primary"
                onClick={openPublishModal}
                disabled={publishing}
                style={{ fontSize: "12px", padding: "4px 12px" }}
              >
                Publish
              </button>
            )}
            {session.published_book_id && (
              <a
                href={publishResult?.url || `/${session.title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`}
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
            {isBook ? `Wave ${session.current_wave}: ${waveLabel(session.current_wave)}` : "Draft"}
            {" \u00B7 "}
            {session.total_tokens_used.toLocaleString()} tokens
          </div>
          <div className="mobile-menu-actions">
            {isBook && (
              <button className="btn btn-secondary" onClick={() => { handleAdvanceWave(); setMenuOpen(false); }}>
                Next Wave
              </button>
            )}
            {canPublish && (isBook ? session.current_wave >= 4 : hasFiles) && (
              <button className="btn btn-primary" onClick={openPublishModal} disabled={publishing}>
                Publish
              </button>
            )}
            {session.published_book_id && (
              <>
                <a
                  href={publishResult?.url || `/${session.title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                  style={{ textDecoration: "none", color: "var(--success)" }}
                >
                  View Book
                </a>
                <button
                  className="btn btn-secondary"
                  onClick={() => handleDownloadPdf("certificate")}
                  disabled={pdfLoading !== null}
                >
                  {pdfLoading === "certificate" ? "..." : "Certificate"}
                </button>
              </>
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

      {/* Publish success banner with PDF downloads */}
      {publishResult && (
        <div className="publish-banner">
          <div style={{ flex: 1 }}>
            <strong>Published!</strong> {publishResult.chapter_count} chapters, {publishResult.total_word_count.toLocaleString()} words, quality {publishResult.quality_score}/100.
            {" "}
            <a href={publishResult.url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent)", fontWeight: 600 }}>
              View
            </a>
          </div>
          {(pubAs === "book" || hasChapterFiles) && (
            <div className="banner-actions">
              <button
                className="btn btn-secondary banner-btn"
                onClick={() => handleDownloadPdf("preview")}
                disabled={pdfLoading !== null}
                title="First 10 pages as PDF"
              >
                {pdfLoading === "preview" ? "..." : "Preview PDF"}
              </button>
              <button
                className="btn btn-secondary banner-btn"
                onClick={() => handleDownloadPdf("interior")}
                disabled={pdfLoading !== null}
                title="Full 6&times;9 print-ready interior"
              >
                {pdfLoading === "interior" ? "..." : "Interior PDF"}
              </button>
              <button
                className="btn btn-secondary banner-btn"
                onClick={() => handleDownloadPdf("cover")}
                disabled={pdfLoading !== null}
                title="Cover PDF at 300 DPI"
              >
                {pdfLoading === "cover" ? "..." : "Cover PDF"}
              </button>
              <button
                className="btn btn-secondary banner-btn"
                onClick={() => handleDownloadPdf("certificate")}
                disabled={pdfLoading !== null}
                title="Certificate of Publication"
              >
                {pdfLoading === "certificate" ? "..." : "Certificate"}
              </button>
            </div>
          )}
          <button
            className="btn btn-ghost"
            onClick={() => setPublishResult(null)}
            style={{ color: "var(--text-mute)", fontSize: "0.75rem" }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* PDF downloads bar for already-published books (no publish result banner) */}
      {session.published_book_id && !publishResult && isBook && (
        <div className="pdf-bar">
          <span style={{ fontSize: "0.8rem", color: "var(--text-mute)" }}>
            Export:
          </span>
          <button
            className="btn btn-ghost pdf-btn"
            onClick={() => handleDownloadPdf("preview")}
            disabled={pdfLoading !== null}
          >
            {pdfLoading === "preview" ? "Generating..." : "Preview PDF"}
          </button>
          <button
            className="btn btn-ghost pdf-btn"
            onClick={() => handleDownloadPdf("interior")}
            disabled={pdfLoading !== null}
          >
            {pdfLoading === "interior" ? "Generating..." : "Interior PDF"}
          </button>
          <button
            className="btn btn-ghost pdf-btn"
            onClick={() => handleDownloadPdf("cover")}
            disabled={pdfLoading !== null}
          >
            {pdfLoading === "cover" ? "Generating..." : "Cover PDF"}
          </button>
          <button
            className="btn btn-ghost pdf-btn"
            onClick={() => handleDownloadPdf("certificate")}
            disabled={pdfLoading !== null}
          >
            {pdfLoading === "certificate" ? "Generating..." : "Certificate"}
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
