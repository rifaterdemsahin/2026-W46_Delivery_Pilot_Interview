import type { Caption } from "@remotion/captions";
import captionsJson from "../data/captions.json";
import chaptersJson from "../data/chapters.json";

export const FPS = 25;
export const WIDTH = 1280;
export const HEIGHT = 720;
export const DURATION_S = 1693.44; // ffprobe duration of the source
export const DURATION_FRAMES = Math.ceil(DURATION_S * FPS);
export const VIDEO_SRC = "proxy.mp4"; // public/proxy.mp4 -> work/proxy.mp4 (git-ignored)

export type Chapter = { title: string; start: number; end: number; summary: string };
export const captions = captionsJson as Caption[];
export const chapters = chaptersJson as Chapter[];
