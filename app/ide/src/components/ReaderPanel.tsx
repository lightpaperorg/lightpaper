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
            <div style={{
              width: "32px",
              height: "44px",
              background: "var(--text-muted)",
              borderRadius: "2px",
              margin: "0 auto 16px",
              opacity: 0.25,
            }} />
            <div style={{ fontSize: "14px", color: "var(--text-secondary)", marginBottom: "6px" }}>
              Your manuscript will appear here
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-muted)", maxWidth: "320px" }}>
              Start by chatting with your writing assistant below.
              Files will appear in the sidebar as content is generated.
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
