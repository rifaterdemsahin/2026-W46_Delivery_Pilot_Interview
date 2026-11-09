import { AbsoluteFill, OffthreadVideo, Series, staticFile } from "remotion";
import { VIDEO_SRC } from "./config";
import { mainOffset, timelines, type Mode } from "./edit";
import { Subtitles } from "./Subtitles";
import { ChapterCard } from "./ChapterCard";
import { ProgressBar } from "./ProgressBar";
import { SectionBar } from "./SectionBar";

/** Plays the edit decision list (data/cuts.json) back-to-back, then layers captions on top. */
export const Edit = ({ mode }: { mode: Mode }) => {
  const tl = timelines[mode];
  const offset = mainOffset(mode);
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
      {mode === "combined" && <ChapterCard timeline={timelines.main} offset={offset} />}
      <Subtitles timeline={tl} bottom={mode === "combined" ? 44 : 28} />
      {mode === "main" && <ProgressBar timeline={tl} />}
      {mode === "combined" && <SectionBar />}
    </AbsoluteFill>
  );
};
