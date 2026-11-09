import { AbsoluteFill, OffthreadVideo, Series, staticFile } from "remotion";
import { VIDEO_SRC } from "./config";
import { timelines, type Mode } from "./edit";
import { Subtitles } from "./Subtitles";
import { ChapterCard } from "./ChapterCard";
import { ProgressBar } from "./ProgressBar";

/** Plays the edit decision list (data/cuts.json) back-to-back, then layers captions on top. */
export const Edit = ({ mode }: { mode: Mode }) => {
  const tl = timelines[mode];
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Series>
        {tl.map((c, i) => (
          <Series.Sequence key={i} durationInFrames={c.dur}>
            <OffthreadVideo src={staticFile(VIDEO_SRC)} startFrom={c.srcFrom} />
          </Series.Sequence>
        ))}
      </Series>
      {mode === "main" && <ChapterCard timeline={tl} />}
      <Subtitles timeline={tl} />
      {mode === "main" && <ProgressBar timeline={tl} />}
    </AbsoluteFill>
  );
};
