import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import explainersJson from "../data/explainers.json";
import { srcSecondsAt, type TimelineCut } from "./edit";

export type Beat = { id: string; kind: string; title: string; start: number; end: number; dur: number; image?: string; data: any };
export const beats = explainersJson as Beat[];

const RED = "#ff2b2b", GREEN = "#35d07f", AMBER = "#ffb020", GREY = "#8899aa";
const FONT = "Helvetica, Arial, sans-serif";
const stateColor = (s?: string) => (s === "fail" ? RED : s === "next" ? AMBER : s === "done" || s === "ok" ? GREEN : GREY);
const clamp01 = (x: number) => Math.min(1, Math.max(0, x));

/** time (s) since the beat started, and a reveal helper: item i appears every `gap` seconds */
type Ctx = { t: number; fps: number; dur: number };
const reveal = (c: Ctx, i: number, gap: number, first = 0.5) =>
  spring({ frame: Math.max(0, (c.t - first - i * gap) * c.fps), fps: c.fps, config: { damping: 14, stiffness: 180 } });

/* ---------- simple animated graphics ---------- */

const Flow = ({ c, d }: { c: Ctx; d: any }) => {
  const gap = Math.min(1.3, (c.dur - 1.5) / d.nodes.length);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "stretch" }}>
      {d.nodes.map((n: any, i: number) => {
        const p = reveal(c, i, gap);
        const col = stateColor(n.state);
        return (
          <div key={i}>
            {i > 0 && <div style={{ textAlign: "center", color: GREY, fontSize: 16, height: 16, lineHeight: "16px", opacity: p }}>↓</div>}
            <div style={{ opacity: p, transform: `translateX(${(1 - p) * -40}px)`, border: `3px solid ${col}`, borderRadius: 12, padding: "6px 14px", background: "rgba(255,255,255,0.06)", display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ fontSize: 24, color: col, width: 28, textAlign: "center" }}>{n.state === "fail" ? "✗" : n.state ? "✓" : "•"}</div>
              <div>
                <div style={{ fontSize: 24, fontWeight: 700 }}>{n.label}</div>
                {n.sub && <div style={{ fontSize: 16, opacity: 0.75 }}>{n.sub}</div>}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

const Tree = ({ c, d }: { c: Ctx; d: any }) => {
  const shown: number = Math.round(interpolate(c.t, [0.8, c.dur * 0.7], [1, d.count as number], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const dots = Math.max(1, Math.ceil((shown / d.count) * 120));
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ display: "inline-block", background: RED, borderRadius: 40, padding: "8px 26px", fontSize: 30, fontWeight: 800 }}>{d.root}</div>
      <div style={{ color: GREY, fontSize: 26 }}>↓ writes ↓</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, justifyContent: "center", margin: "6px 10px", minHeight: 110 }}>
        {Array.from({ length: dots }).map((_, i) => (
          <div key={i} style={{ width: 16, height: 16, borderRadius: 4, background: i % 7 === 0 ? RED : "#e8edf5" }} />
        ))}
      </div>
      <div style={{ fontSize: 52, fontWeight: 800, fontVariantNumeric: "tabular-nums" }}>{shown}<span style={{ fontSize: 28, opacity: 0.7 }}> bots</span></div>
      <div style={{ fontSize: 20, opacity: 0.8 }}>{d.caption}</div>
    </div>
  );
};

const Network = ({ c, d }: { c: Ctx; d: any }) => {
  const pts = [{ x: 280, y: 50 }, { x: 80, y: 240 }, { x: 480, y: 240 }];
  const edges = [[0, 1], [1, 2], [2, 0]];
  const frame = c.t * c.fps;
  return (
    <div style={{ textAlign: "center" }}>
      <svg width={500} height={277} viewBox="0 0 560 310">
        {edges.map(([a, b], i) => {
          const k = (frame / 40 + i / 3) % 1;
          return (
            <g key={i}>
              <line x1={pts[a].x} y1={pts[a].y} x2={pts[b].x} y2={pts[b].y} stroke={GREY} strokeWidth={3} strokeDasharray="8 8" />
              <circle cx={pts[a].x + (pts[b].x - pts[a].x) * k} cy={pts[a].y + (pts[b].y - pts[a].y) * k} r={8} fill={RED} />
            </g>
          );
        })}
        {pts.map((p, i) => {
          const s = reveal(c, i, 0.5, 0.3);
          return (
            <g key={i} transform={`translate(${p.x} ${p.y}) scale(${s})`}>
              <circle r={42} fill="#16243d" stroke="white" strokeWidth={4} />
              <rect x={-16} y={-14} width={32} height={26} rx={6} fill="white" /><circle cx={-7} cy={-2} r={4} fill="#16243d" /><circle cx={7} cy={-2} r={4} fill="#16243d" /><rect x={-1.5} y={-26} width={3} height={10} fill="white" />
              <text y={72} textAnchor="middle" fill="white" fontSize={24} fontWeight={700} fontFamily={FONT}>{d.nodes[i]}</text>
            </g>
          );
        })}
      </svg>
      <div style={{ fontSize: 24, fontWeight: 700, color: RED }}>{d.caption}</div>
    </div>
  );
};

const Stat = ({ c, d }: { c: Ctx; d: any }) => {
  const s = reveal(c, 0, 1, 0.2);
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: 96, fontWeight: 900, color: RED, transform: `scale(${0.6 + 0.4 * s})`, opacity: s, lineHeight: 1 }}>{d.value}</div>
      <div style={{ display: "flex", gap: 10, justifyContent: "center", margin: "14px 0" }}>
        {Array.from({ length: 10 }).map((_, i) => (
          <div key={i} style={{ width: 28, height: 28, borderRadius: 6, background: i < 3 ? RED : "#e8edf5", opacity: i === 2 ? 0.6 : 1 }} />
        ))}
      </div>
      <div style={{ fontSize: 28 }}>{d.caption}</div>
    </div>
  );
};

const Card = ({ c, d }: { c: Ctx; d: any }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
    {d.bullets.map((b: string, i: number) => {
      const p = reveal(c, i, 1.6);
      return (
        <div key={i} style={{ opacity: p, transform: `translateX(${(1 - p) * -30}px)`, display: "flex", gap: 14, alignItems: "flex-start", fontSize: 26, lineHeight: 1.2 }}>
          <div style={{ width: 14, height: 14, borderRadius: 7, background: RED, marginTop: 10, flex: "none" }} />
          <div>{b}</div>
        </div>
      );
    })}
  </div>
);

/** Complex idea: AI-generated (fal.ai) text-free art + crisp animated labels from Remotion. */
const Infographic = ({ c, d, image }: { c: Ctx; d: any; image: string }) => {
  const zoom = 1 + 0.06 * clamp01(c.t / c.dur);
  const gap = Math.min(2.5, (c.dur - 2) / d.items.length);
  const chips = d.items.every((x: any) => !x.sub);
  return (
    <div>
      <div style={{ height: 150, overflow: "hidden", borderRadius: 10, background: "white" }}>
        <Img src={staticFile(image)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})` }} />
      </div>
      <div style={{ display: "flex", flexWrap: chips ? "wrap" : "nowrap", flexDirection: chips ? "row" : "column", gap: 8, marginTop: 10 }}>
        {d.items.map((it: any, i: number) => {
          const p = reveal(c, i, gap, 0.8);
          return (
            <div key={i} style={{ opacity: p, transform: `translateY(${(1 - p) * 20}px)`, display: "flex", alignItems: "center", gap: 12, background: chips ? RED : "rgba(255,255,255,0.08)", borderRadius: 10, padding: chips ? "6px 16px" : "5px 12px", borderLeft: chips ? undefined : `6px solid ${RED}` }}>
              {!chips && <div style={{ fontSize: 30, fontWeight: 900, color: RED }}>{i + 1}</div>}
              <div>
                <div style={{ fontSize: chips ? 24 : 24, fontWeight: 800 }}>{it.label}</div>
                {it.sub && <div style={{ fontSize: 16, opacity: 0.8 }}>{it.sub}</div>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/* ---------- panel on the left ---------- */

export const Explainers = ({ timeline, offset = 0 }: { timeline: TimelineCut[]; offset?: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (frame < offset) return null;
  const s = srcSecondsAt(timeline, frame);
  const beat = beats.find((b) => s >= b.start && s <= b.end);
  if (!beat) return null;
  const t = s - beat.start;
  const enter = spring({ frame: Math.max(0, t * fps), fps, config: { damping: 16, stiffness: 160 } });
  const opacity = Math.min(enter, clamp01((beat.end - s) / 0.4));
  const c: Ctx = { t, fps, dur: beat.dur };
  const d = beat.data;
  return (
    <AbsoluteFill style={{ padding: "48px 0 0 36px", alignItems: "flex-start", justifyContent: "flex-start" }}>
      <div style={{ width: 560, opacity, transform: `translateX(${(1 - enter) * -80}px)`, fontFamily: FONT, color: "white", background: "rgba(8,14,30,0.9)", borderLeft: `8px solid ${RED}`, borderRadius: 14, padding: "12px 20px 16px", boxShadow: "0 10px 30px rgba(0,0,0,0.45)" }}>
        <div style={{ fontSize: 16, letterSpacing: 3, color: RED, fontWeight: 800 }}>EXPLAINED</div>
        <div style={{ fontSize: 32, fontWeight: 800, marginBottom: 8 }}>{beat.title}</div>
        {beat.kind === "flow" && <Flow c={c} d={d} />}
        {beat.kind === "tree" && <Tree c={c} d={d} />}
        {beat.kind === "network" && <Network c={c} d={d} />}
        {beat.kind === "stat" && <Stat c={c} d={d} />}
        {beat.kind === "card" && <Card c={c} d={d} />}
        {beat.kind === "infographic" && beat.image && <Infographic c={c} d={d} image={beat.image} />}
      </div>
    </AbsoluteFill>
  );
};

export type Sfx = "whoosh" | "pop" | "ding" | "buzz";
/** Seconds after the beat starts, and which sound, mirroring the reveal timing of each graphic. */
export const beatCues = (b: Beat): { t: number; sfx: Sfx }[] => {
  const d = b.data;
  const cues: { t: number; sfx: Sfx }[] = [{ t: 0, sfx: "whoosh" }];
  if (b.kind === "flow") {
    const gap = Math.min(1.3, (b.dur - 1.5) / d.nodes.length);
    d.nodes.forEach((n: any, i: number) => cues.push({ t: 0.5 + i * gap, sfx: n.state === "fail" ? "buzz" : n.state === "ok" ? "ding" : "pop" }));
  } else if (b.kind === "tree") cues.push({ t: 0.8, sfx: "pop" });
  else if (b.kind === "network") d.nodes.forEach((_: any, i: number) => cues.push({ t: 0.3 + i * 0.5, sfx: "pop" }));
  else if (b.kind === "stat") cues.push({ t: 0.2, sfx: "ding" });
  else if (b.kind === "card") d.bullets.forEach((_: any, i: number) => cues.push({ t: 0.5 + i * 1.6, sfx: "pop" }));
  else if (b.kind === "infographic") {
    const gap = Math.min(2.5, (b.dur - 2) / d.items.length);
    d.items.forEach((_: any, i: number) => cues.push({ t: 0.8 + i * gap, sfx: "pop" }));
  }
  return cues;
};
