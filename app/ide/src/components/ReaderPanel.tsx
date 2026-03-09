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
          Select a file from the sidebar to view it here
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
