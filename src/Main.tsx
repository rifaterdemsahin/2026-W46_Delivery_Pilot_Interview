import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { VIDEO_SRC } from "./config";
import { Subtitles } from "./Subtitles";
import { ChapterCard } from "./ChapterCard";
import { ProgressBar } from "./ProgressBar";

export const Main = () => (
  <AbsoluteFill style={{ backgroundColor: "black" }}>
    <OffthreadVideo src={staticFile(VIDEO_SRC)} />
    <ChapterCard />
    <Subtitles />
    <ProgressBar />
  </AbsoluteFill>
);
