import { AbsoluteFill, useCurrentFrame } from "remotion";
import { chapters } from "./config";
import { outFrameAt, totalFrames, type TimelineCut } from "./edit";

export const ProgressBar = ({ timeline, ticks = true }: { timeline: TimelineCut[]; ticks?: boolean }) => {
  const frame = useCurrentFrame();
  const total = totalFrames(timeline);
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end" }}>
      <div style={{ position: "relative", height: 8, background: "rgba(255,255,255,0.25)" }}>
        <div style={{ width: `${Math.min(100, (frame / total) * 100)}%`, height: "100%", background: "#ff2b2b" }} />
        {ticks && chapters.slice(1).map((c) => (
          <div
            key={c.start}
            style={{
              position: "absolute", top: 0, bottom: 0, width: 3, background: "white",
              left: `${(outFrameAt(timeline, c.start) / total) * 100}%`,
            }}
          />
        ))}
      </div>
    </AbsoluteFill>
  );
};
