import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { captions } from "./config";

export const Subtitles = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ms = (frame / fps) * 1000;
  const cue = captions.find((c) => ms >= c.startMs && ms < c.endMs);
  if (!cue) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 56 }}>
      <div
        style={{
          fontFamily: "Helvetica, Arial, sans-serif",
          fontSize: 38,
          lineHeight: 1.25,
          color: "white",
          textAlign: "center",
          whiteSpace: "pre-line",
          background: "rgba(0,0,0,0.6)",
          padding: "8px 20px",
          borderRadius: 8,
          maxWidth: 1100,
        }}
      >
        {cue.text}
      </div>
    </AbsoluteFill>
  );
};
