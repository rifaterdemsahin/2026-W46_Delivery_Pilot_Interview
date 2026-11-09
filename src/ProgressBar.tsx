import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { chapters, DURATION_S } from "./config";

export const ProgressBar = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pct = Math.min(100, ((frame / fps) / DURATION_S) * 100);
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end" }}>
      <div style={{ position: "relative", height: 8, background: "rgba(255,255,255,0.25)" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: "#4da3ff" }} />
        {chapters.slice(1).map((c) => (
          <div
            key={c.start}
            style={{
              position: "absolute", top: 0, bottom: 0, width: 3,
              left: `${(c.start / DURATION_S) * 100}%`, background: "white",
            }}
          />
        ))}
      </div>
    </AbsoluteFill>
  );
};
