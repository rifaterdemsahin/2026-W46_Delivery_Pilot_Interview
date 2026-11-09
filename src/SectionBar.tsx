import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { chapters } from "./config";
import { outFrameAt, timelines, totalFrames } from "./edit";

const RED = "#ff2b2b";
const mmss = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;

/** Bottom indicator for the combined timeline: one segment per section (Highlights + chapters),
 *  each as wide as the section is long, with a label showing how long the current section is. */
export const SectionBar = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const hl = totalFrames(timelines.highlights);
  const total = totalFrames(timelines.combined);
  const starts = [0, ...chapters.map((c) => hl + outFrameAt(timelines.main, c.start))];
  const names = ["Highlights", ...chapters.map((c) => c.title)];
  const secs = starts.map((s, i) => ({ s, e: starts[i + 1] ?? total, name: names[i] }));
  const idx = Math.max(0, secs.findLastIndex((x) => frame >= x.s));
  const cur = secs[idx];
  const len = (cur.e - cur.s) / fps;
  const el = (frame - cur.s) / fps;
  const label = idx === 0 ? "HIGHLIGHTS" : `CH ${idx}/${chapters.length} · ${cur.name}`;

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end" }}>
      <div style={{ display: "flex", height: 48, background: "rgba(0,0,0,0.82)", fontFamily: "Helvetica, Arial, sans-serif" }}>
        <div style={{ width: 600, padding: "0 16px", color: "white", display: "flex", alignItems: "center", gap: 12, whiteSpace: "nowrap", overflow: "hidden" }}>
          <span style={{ fontSize: 21, fontWeight: 700, letterSpacing: 0.5, overflow: "hidden", textOverflow: "ellipsis" }}>{label}</span>
          <span style={{ marginLeft: "auto", fontSize: 21, fontVariantNumeric: "tabular-nums", color: RED, fontWeight: 700 }}>
            {mmss(el)} / {mmss(len)}
          </span>
        </div>
        <div style={{ position: "relative", flex: 1, display: "flex", gap: 2, alignItems: "center", padding: "0 8px 0 0" }}>
          {secs.map((x, i) => {
            const frac = Math.min(1, Math.max(0, (frame - x.s) / (x.e - x.s)));
            return (
              <div key={i} style={{ flex: x.e - x.s, height: i === idx ? 24 : 12, background: "rgba(255,255,255,0.22)", position: "relative", borderRadius: 2, overflow: "hidden" }}>
                <div style={{ width: `${frac * 100}%`, height: "100%", background: i === 0 ? "#ffffff" : RED }} />
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
