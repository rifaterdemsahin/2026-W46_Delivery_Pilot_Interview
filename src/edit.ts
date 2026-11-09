import cutsJson from "../data/cuts.json";
import cuesJson from "../data/cues.json";
import { FPS } from "./config";

export type Cut = { src_start: number; src_end: number };
export type TimelineCut = { srcFrom: number; dur: number; outFrom: number };
export type Word = { w: string; start: number; end: number };
export type Cue = { start: number; end: number; words: Word[] };
export type Mode = "main" | "highlights" | "combined" | "linkedin";

export const cues = cuesJson as Cue[];

/** Edit decision list (source seconds) -> frame timeline. Cut points are pre-snapped to the 25 fps grid. */
export const toTimeline = (cuts: Cut[]): TimelineCut[] => {
  let acc = 0;
  return cuts.map((c) => {
    const srcFrom = Math.round(c.src_start * FPS);
    const dur = Math.max(1, Math.round((c.src_end - c.src_start) * FPS));
    const t = { srcFrom, dur, outFrom: acc };
    acc += dur;
    return t;
  });
};

export const timelines: Record<Mode, TimelineCut[]> = {
  main: toTimeline(cutsJson.main),
  highlights: toTimeline(cutsJson.highlights),
  // highlights first, then the tightened full interview
  combined: toTimeline([...cutsJson.highlights, ...cutsJson.main]),
  // <= 14 min cut for LinkedIn
  linkedin: toTimeline(cutsJson.linkedin),
};

export const totalFrames = (tl: TimelineCut[]) => tl.reduce((a, c) => a + c.dur, 0);

/** Output frame -> source seconds (what is on screen right now). */
export const srcSecondsAt = (tl: TimelineCut[], outFrame: number) => {
  const c = tl.find((x) => outFrame >= x.outFrom && outFrame < x.outFrom + x.dur) ?? tl[tl.length - 1];
  return (c.srcFrom + (outFrame - c.outFrom)) / FPS;
};

/** Source seconds -> output frame (snaps to the next kept cut if the moment was cut out). */
export const outFrameAt = (tl: TimelineCut[], srcSec: number) => {
  const f = srcSec * FPS;
  const c = tl.find((x) => f < x.srcFrom + x.dur);
  if (!c) return totalFrames(tl);
  return c.outFrom + Math.max(0, f - c.srcFrom);
};

/** The kept cut that output frame falls in. */
export const cutAt = (tl: TimelineCut[], outFrame: number) =>
  tl.find((x) => outFrame >= x.outFrom && outFrame < x.outFrom + x.dur) ?? tl[tl.length - 1];

/** Frames before the full interview starts (0 unless highlights are placed first). */
export const mainOffset = (mode: Mode) => (mode === "combined" ? totalFrames(timelines.highlights) : 0);
