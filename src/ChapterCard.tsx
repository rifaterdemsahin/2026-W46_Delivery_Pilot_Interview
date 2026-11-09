import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { chapters } from "./config";
import { outFrameAt, type TimelineCut } from "./edit";

const SHOW_S = 5; // seconds a chapter title card stays on screen

export const ChapterCard = ({ timeline }: { timeline: TimelineCut[] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const starts = chapters.map((c) => outFrameAt(timeline, c.start));
  const idx = starts.findLastIndex((f) => frame >= f);
  const chapter = chapters[idx];
  if (!chapter) return null;
  const local = frame - starts[idx];
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
          background: "rgba(0,0,0,0.78)",
          borderLeft: "8px solid #ff2b2b",
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
