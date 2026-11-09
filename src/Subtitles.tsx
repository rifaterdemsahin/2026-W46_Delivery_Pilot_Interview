import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { cues, cutAt, srcSecondsAt, type TimelineCut } from "./edit";

const WHITE = "#ffffff";
const RED = "#ff2b2b";

/** Animated captions: cue springs in, every word is white, the word being spoken turns red and pops. */
export const Subtitles = ({ timeline }: { timeline: TimelineCut[] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = srcSecondsAt(timeline, frame);
  const cue = cues.find((c) => s >= c.start - 0.04 && s <= c.end + 0.1);
  if (!cue) return null;

  const enter = spring({
    frame: Math.max(0, (s - cue.start) * fps),
    fps,
    config: { damping: 14, stiffness: 220 },
  });
  // Only show words that are inside the kept footage (a cut can start mid-cue).
  const c = cutAt(timeline, frame);
  const words = cue.words.filter((w) => w.end * fps > c.srcFrom && w.start * fps < c.srcFrom + c.dur);
  if (!words.length) return null;
  const activeIdx = words.reduce((a, w, i) => (w.start <= s ? i : a), -1);

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 28 }}>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          maxWidth: 1080,
          opacity: Math.min(1, enter * 1.5),
          transform: `translateY(${(1 - enter) * 24}px) scale(${0.85 + 0.15 * enter})`,
          fontFamily: "Impact, 'Arial Black', Helvetica, sans-serif",
          fontSize: 56,
          lineHeight: 1.15,
          textTransform: "uppercase",
          letterSpacing: 1,
        }}
      >
        {words.map((w, i) => {
          const active = i === activeIdx;
          const pop = active
            ? spring({ frame: Math.max(0, (s - w.start) * fps), fps, config: { damping: 9, stiffness: 320 } })
            : 0;
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                margin: "0 14px",
                color: active ? RED : WHITE,
                transform: `scale(${1 + 0.2 * pop}) rotate(${active ? -1.5 * pop : 0}deg)`,
                WebkitTextStroke: "7px #000",
                paintOrder: "stroke fill",
                textShadow: "0 4px 10px rgba(0,0,0,0.6)",
              }}
            >
              {w.w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
