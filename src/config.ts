import chaptersJson from "../data/chapters.json";

export const FPS = 25;
export const WIDTH = 1280;
export const HEIGHT = 720;
export const VIDEO_SRC = "proxy.mp4"; // public/proxy.mp4 -> work/proxy.mp4 (git-ignored)

export type Chapter = { title: string; start: number; end: number; summary: string };
export const chapters = chaptersJson as Chapter[]; // start/end in SOURCE seconds
