import type React from "react";
import { Audio, Sequence, interpolate, staticFile } from "remotion";
import cutsJson from "../data/cuts.json";
import { beatCues, beats, type Sfx } from "./Explainer";
import { FPS, chapters } from "./config";
import { isKept, labelStarts, mainOffset, outFrameAt, timelines, totalFrames, type Mode } from "./edit";

/* Tuning. Every file is pre-levelled (SFX peak -3 dBFS, music -20 LUFS) so these multipliers are comparable.
   Speech is about -16 LUFS; a 0.30 bed sits roughly 14 dB below it: felt, not noticed. */
export const SOUND = { bed: 0.3, hook: 0.45, xMusic: 0.4, sfx: { whoosh: 0.35, pop: 0.25, ding: 0.35, buzz: 0.3, impact: 0.55 } as Record<string, number> };
const SFX_FRAMES: Record<string, number> = { whoosh: 50, pop: 25, ding: 50, buzz: 25, impact: 75 };

const Sfx = ({ at, name }: { at: number; name: Sfx | "impact" }) => (
  <Sequence from={Math.max(0, Math.round(at))} durationInFrames={SFX_FRAMES[name]} layout="none">
    <Audio src={staticFile(`audio/sfx_${name}.mp3`)} volume={SOUND.sfx[name]} />
  </Sequence>
);

const Music = ({ from, dur, src, vol, fade = 36 }: { from: number; dur: number; src: string; vol: number; fade?: number }) => (
  <Sequence from={Math.round(from)} durationInFrames={Math.max(1, Math.round(dur))} layout="none">
    <Audio src={staticFile(`audio/${src}.mp3`)} loop volume={(f) => vol * interpolate(f, [0, fade, dur - fade, dur], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
  </Sequence>
);

/** Music bed + sound effects for every composition. Cues are computed from the same edit list the video uses. */
export const Sound = ({ mode }: { mode: Mode }) => {
  const tl = timelines[mode];
  const total = totalFrames(tl);
  const offset = mainOffset(mode);
  const mainTl = mode === "combined" ? timelines.main : tl;
  const els: React.ReactElement[] = [];

  // ----- music -----
  if (mode === "highlights") els.push(<Music key="m" from={0} dur={total} src="music_hook" vol={SOUND.hook} />);
  else if (mode === "x") els.push(<Music key="m" from={0} dur={total} src="music_hook" vol={SOUND.xMusic} />);
  else {
    if (mode === "combined") els.push(<Music key="mh" from={0} dur={offset} src="music_hook" vol={SOUND.hook} />);
    let starts: number[];
    if (mode === "linkedin") starts = labelStarts(cutsJson.linkedin).filter((_, i) => i % 3 === 0); // a new bed every 3 sections
    else starts = chapters.map((c) => outFrameAt(mainTl, c.start) + offset);
    starts = [...new Set(starts)].sort((a, b) => a - b);
    if (starts[0] > offset) starts.unshift(offset);
    starts.forEach((s, i) => {
      const e = starts[i + 1] ?? total;
      els.push(<Music key={`mb${i}`} from={s} dur={e - s} src={i % 2 ? "music_bed2" : "music_bed1"} vol={SOUND.bed} />);
    });
  }

  // ----- sound effects -----
  if (mode === "combined") els.push(<Sfx key="imp" at={offset - 4} name="impact" />);
  if (mode === "highlights") labelStarts(cutsJson.highlights).forEach((f, i) => i > 0 && els.push(<Sfx key={`h${i}`} at={f} name="whoosh" />));
  if (mode === "linkedin") labelStarts(cutsJson.linkedin).forEach((f, i) => i > 0 && els.push(<Sfx key={`l${i}`} at={f} name="whoosh" />));
  if (mode === "x") labelStarts(cutsJson.x).forEach((f, i) => i > 0 && els.push(<Sfx key={`x${i}`} at={f} name="whoosh" />));
  if (mode === "main" || mode === "combined") chapters.forEach((c, i) => els.push(<Sfx key={`c${i}`} at={outFrameAt(mainTl, c.start) + offset} name="whoosh" />));

  if (mode !== "highlights") {
    beats.forEach((b) => {
      if (!isKept(mainTl, b.start)) return; // the explainer is not on screen when its moment was cut
      const base = outFrameAt(mainTl, b.start) + offset;
      beatCues(b).forEach((c, i) => els.push(<Sfx key={`e${b.id}${i}`} at={base + c.t * FPS} name={c.sfx} />));
    });
  }
  return <>{els}</>;
};
