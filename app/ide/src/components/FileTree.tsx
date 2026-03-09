import { useState } from "react";
import type { FileEntry } from "../api";

const WAVE_LABELS: Record<number, string> = {
  0: "Wave 0 — Raw Capture",
  1: "Wave 1 — Architecture",
  2: "Wave 2 — Voice & Texture",
  3: "Wave 3 — Pivotal Scenes",
  4: "Wave 4 — Full Draft",
};

function waveLabel(wave: number): string {
  return WAVE_LABELS[wave] || `Wave ${wave} — Edit Pass ${wave - 4}`;
}

interface Props {
  files: FileEntry[];
  selectedId: string | null;
  onSelect: (file: FileEntry) => void;
}

export function FileTree({ files, selectedId, onSelect }: Props) {
  const [collapsed, setCollapsed] = useState<Set<number>>(new Set());

  // Group files by wave
  const byWave = new Map<number, FileEntry[]>();
  for (const f of files) {
    if (!byWave.has(f.wave)) byWave.set(f.wave, []);
    byWave.get(f.wave)!.push(f);
  }

  const waves = Array.from(byWave.keys()).sort((a, b) => a - b);

  const toggle = (wave: number) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(wave)) next.delete(wave);
      else next.add(wave);
      return next;
    });
  };

  if (files.length === 0) {
    return (
      <div className="file-tree" style={{ padding: "16px", color: "var(--text-muted)", fontSize: "13px" }}>
        No files yet. Start chatting to generate content.
      </div>
    );
  }

  return (
    <div className="file-tree">
      {waves.map((wave) => (
        <div key={wave} className="tree-folder">
          <div className="tree-folder-label" onClick={() => toggle(wave)}>
            <span>{collapsed.has(wave) ? "▸" : "▾"}</span>
            <span>{waveLabel(wave)}</span>
          </div>
          {!collapsed.has(wave) &&
            byWave.get(wave)!.map((f) => (
              <div
                key={f.id}
                className={`tree-file ${selectedId === f.id ? "active" : ""}`}
                onClick={() => onSelect(f)}
              >
                <span>{f.title}</span>
                <span className="tree-file-meta">
                  {f.word_count > 0 ? `${f.word_count}w` : ""}
                </span>
              </div>
            ))}
        </div>
      ))}
    </div>
  );
}
