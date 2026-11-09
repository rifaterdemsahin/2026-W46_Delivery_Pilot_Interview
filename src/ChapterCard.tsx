import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { chapters } from "./config";

const SHOW_S = 5; // seconds a chapter title card stays on screen

export const ChapterCard = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const idx = chapters.findLastIndex((c) => t >= c.start);
  const chapter = chapters[idx];
  if (!chapter) return null;
  const local = (t - chapter.start) * fps;
  const total = SHOW_S * fps;
  if (local >= total) return null;
  const fade = 12;
  const opacity = interpolate(local, [0, fade, total - fade, total], [0, 1, 1, 0]);
  const x = interpolate(local, [0, fade], [-40, 0], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "flex-start", padding: 48 }}>
      <div
        style={{
          opacity,
          transform: `translateX(${x}px)`,
          fontFamily: "Helvetica, Arial, sans-serif",
          background: "rgba(10,25,60,0.85)",
          borderLeft: "8px solid #4da3ff",
          color: "white",
          padding: "14px 26px",
          borderRadius: 6,
        }}
      >
        <div style={{ fontSize: 20, opacity: 0.75, letterSpacing: 2 }}>
          CHAPTER {idx + 1} / {chapters.length}
        </div>
        <div style={{ fontSize: 40, fontWeight: 700 }}>{chapter.title}</div>
      </div>
    </AbsoluteFill>
  );
};
