import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import linksJson from "../data/links.json";
import { totalFrames, type TimelineCut } from "./edit";

/** Closing card for short cuts: points to the full conversation. Shown over the last `seconds` seconds. */
export const EndCard = ({ timeline, seconds = 7 }: { timeline: TimelineCut[]; seconds?: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const total = totalFrames(timeline);
  const start = total - seconds * fps;
  if (frame < start) return null;
  const local = frame - start;
  const enter = spring({ frame: local, fps, config: { damping: 14, stiffness: 170 } });
  const out = interpolate(local, [seconds * fps - 8, seconds * fps], [1, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 36 }}>
      <div style={{ opacity: enter * out, transform: `translateY(${(1 - enter) * -40}px)`, background: "rgba(0,0,0,0.82)", border: "4px solid #ff2b2b", borderRadius: 14, padding: "12px 28px", textAlign: "center", fontFamily: "Helvetica, Arial, sans-serif", color: "white" }}>
        <div style={{ fontSize: 22, letterSpacing: 3, color: "#ff2b2b", fontWeight: 800 }}>FULL CONVERSATION</div>
        <div style={{ fontSize: 44, fontWeight: 900 }}>▶ {linksJson.youtube.replace("https://", "")}</div>
      </div>
    </AbsoluteFill>
  );
};
