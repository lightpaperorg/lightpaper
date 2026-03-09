import { useEffect, useRef, useState } from "react";
import type { Message } from "../api";
import { streamChat } from "../api";

const WAVE_LABELS: Record<number, string> = {
  0: "Raw Capture",
  1: "Architecture",
  2: "Voice & Texture",
  3: "Pivotal Scenes",
  4: "Full Draft",
};

interface Props {
  sessionId: string;
  currentWave: number;
  messages: Message[];
  onNewMessage: (msg: Message) => void;
  onStreamComplete: () => void;
}

export function ChatPanel({ sessionId, currentWave, messages, onNewMessage, onStreamComplete }: Props) {
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [streamText, setStreamText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamText]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || streaming) return;

    setInput("");
    setStreaming(true);
    setStreamText("");

    // Optimistically add user message
    const userMsg: Message = {
      id: `temp-${Date.now()}`,
      wave: currentWave,
      role: "user",
      content: text,
      files_generated: [],
      created_at: new Date().toISOString(),
    };
    onNewMessage(userMsg);

    try {
      let fullResponse = "";
      for await (const chunk of streamChat(sessionId, text)) {
        fullResponse += chunk;
        setStreamText(fullResponse);
      }

      // Add assistant message
      const assistantMsg: Message = {
        id: `temp-${Date.now()}-a`,
        wave: currentWave,
        role: "assistant",
        content: fullResponse,
        files_generated: [],
        created_at: new Date().toISOString(),
      };
      onNewMessage(assistantMsg);
    } catch (err) {
      const errorMsg: Message = {
        id: `temp-${Date.now()}-err`,
        wave: currentWave,
        role: "assistant",
        content: `Error: ${err instanceof Error ? err.message : "Unknown error"}`,
        files_generated: [],
        created_at: new Date().toISOString(),
      };
      onNewMessage(errorMsg);
    } finally {
      setStreaming(false);
      setStreamText("");
      onStreamComplete();
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSend();
    }
  };

  const waveName = WAVE_LABELS[currentWave] || `Edit Pass ${currentWave - 4}`;

  return (
    <div className="chat-panel">
      <div style={{ padding: "6px 16px", fontSize: "11px", color: "var(--text-muted)", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: "8px" }}>
        <span className="wave-badge">Wave {currentWave}</span>
        <span>{waveName}</span>
        {streaming && <span className="streaming-indicator" />}
      </div>
      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message ${msg.role}`}>
            <div className="chat-message-role">{msg.role}</div>
            <div className="chat-message-content">{msg.content}</div>
          </div>
        ))}
        {streaming && streamText && (
          <div className="chat-message assistant">
            <div className="chat-message-role">assistant</div>
            <div className="chat-message-content">
              {streamText}
              <span className="streaming-indicator" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-area">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Message your writing assistant... (${navigator.platform.includes("Mac") ? "⌘" : "Ctrl"}+Enter to send)`}
          rows={2}
          disabled={streaming}
        />
        <button
          className="btn btn-primary"
          onClick={handleSend}
          disabled={streaming || !input.trim()}
        >
          {streaming ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
