import { useCallback, useRef, useState, type ReactNode } from "react";

interface Props {
  top: ReactNode;
  bottom: ReactNode;
  defaultTopPercent?: number;
  minTopPercent?: number;
  minBottomPercent?: number;
}

export function VerticalResizable({
  top,
  bottom,
  defaultTopPercent = 55,
  minTopPercent = 20,
  minBottomPercent = 20,
}: Props) {
  const [topPercent, setTopPercent] = useState(defaultTopPercent);
  const containerRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    dragging.current = true;

    const onMouseMove = (e: MouseEvent) => {
      if (!dragging.current || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const percent = ((e.clientY - rect.top) / rect.height) * 100;
      const clamped = Math.max(minTopPercent, Math.min(100 - minBottomPercent, percent));
      setTopPercent(clamped);
    };

    const onMouseUp = () => {
      dragging.current = false;
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };

    document.body.style.cursor = "row-resize";
    document.body.style.userSelect = "none";
    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  }, [minTopPercent, minBottomPercent]);

  return (
    <div ref={containerRef} style={{ display: "flex", flexDirection: "column", flex: 1, overflow: "hidden" }}>
      <div style={{ height: `${topPercent}%`, overflow: "hidden", display: "flex", flexDirection: "column" }}>
        {top}
      </div>
      <div className="resize-handle" onMouseDown={handleMouseDown} />
      <div style={{ height: `${100 - topPercent}%`, overflow: "hidden", display: "flex", flexDirection: "column" }}>
        {bottom}
      </div>
    </div>
  );
}
