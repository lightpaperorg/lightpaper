import ReactMarkdown from "react-markdown";

interface Props {
  title: string;
  content: string;
}

export function ReaderPanel({ title, content }: Props) {
  if (!content) {
    return (
      <div className="reader-panel">
        <div className="reader-empty">
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: "32px", marginBottom: "12px", opacity: 0.3 }}>&#9998;</div>
            <div style={{ fontSize: "15px", marginBottom: "8px", color: "var(--text-secondary)" }}>
              Your manuscript will appear here
            </div>
            <div style={{ fontSize: "13px", color: "var(--text-muted)", maxWidth: "360px" }}>
              Start by chatting with your writing assistant below.
              As content is generated, select files from the sidebar to read them.
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="reader-panel">
      <div className="reader-content">
        {title && <h1>{title}</h1>}
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
}
