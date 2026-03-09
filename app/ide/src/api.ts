/** API client for the Writing IDE backend. */

const BASE = "/v1/write";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Auth
export const login = (api_key: string) =>
  request<{ handle: string; display_name: string; gravity_level: number }>(
    "/auth/login",
    { method: "POST", body: JSON.stringify({ api_key }) }
  );

export const logout = () =>
  request<{ ok: boolean }>("/auth/logout", { method: "POST" });

export const getMe = () =>
  request<{ id: string; handle: string; display_name: string; email: string; gravity_level: number }>(
    "/auth/me"
  );

// Sessions
export interface Session {
  id: string;
  title: string;
  status: string;
  current_wave: number;
  wave_state: Record<string, { status: string }>;
  book_config: Record<string, unknown>;
  total_tokens_used: number;
  published_book_id: string | null;
  created_at: string;
  updated_at: string;
  files?: FileEntry[];
}

export interface FileEntry {
  id: string;
  wave: number;
  file_type: string;
  chapter_number: number | null;
  title: string;
  word_count: number;
  sort_order: number;
}

export interface FileContent extends FileEntry {
  content: string;
}

export interface Message {
  id: string;
  wave: number;
  role: "user" | "assistant" | "system";
  content: string;
  files_generated: string[];
  created_at: string;
}

export const createSession = (title: string, book_config: Record<string, unknown> = {}) =>
  request<Session>("/sessions", {
    method: "POST",
    body: JSON.stringify({ title, book_config }),
  });

export const listSessions = () => request<Session[]>("/sessions");

export const getSession = (id: string) => request<Session>(`/sessions/${id}`);

export const deleteSession = (id: string) =>
  request<void>(`/sessions/${id}`, { method: "DELETE" });

// Files
export const listFiles = (sessionId: string) =>
  request<FileEntry[]>(`/sessions/${sessionId}/files`);

export const getFile = (sessionId: string, fileId: string) =>
  request<FileContent>(`/sessions/${sessionId}/files/${fileId}`);

export const updateFile = (sessionId: string, fileId: string, content: string) =>
  request<{ ok: boolean; word_count: number }>(
    `/sessions/${sessionId}/files/${fileId}`,
    { method: "PUT", body: JSON.stringify({ content }) }
  );

// Messages
export const listMessages = (sessionId: string, wave?: number) => {
  const params = wave !== undefined ? `?wave=${wave}` : "";
  return request<Message[]>(`/sessions/${sessionId}/messages${params}`);
};

// Chat (streaming)
export async function* streamChat(
  sessionId: string,
  message: string
): AsyncGenerator<string, void, unknown> {
  const res = await fetch(`${BASE}/sessions/${sessionId}/chat`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `Chat failed: ${res.status}`);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") return;
        if (data.startsWith("[ERROR]")) throw new Error(data);
        yield data;
      }
    }
  }
}

// Wave
export const advanceWave = (sessionId: string) =>
  request<{ current_wave: number; wave_state: Record<string, { status: string }> }>(
    `/sessions/${sessionId}/advance`,
    { method: "POST" }
  );
