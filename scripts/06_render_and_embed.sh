#!/usr/bin/env bash
# Render the Remotion composition (burned-in captions, chapter cards, progress bar),
# then mux native chapter markers + a soft subtitle track with ffmpeg.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p out
npx remotion render src/index.ts Main out/edited.mp4 --codec=h264 --crf=20
ffmpeg -y -hide_banner -loglevel error \
  -i out/edited.mp4 -i data/chapters.ffmetadata -i data/subtitles.srt \
  -map 0:v -map 0:a -map 2:0 -map_metadata 1 -map_chapters 1 \
  -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng \
  -movflags +faststart out/final.mp4
ffprobe -v error -show_chapters -of csv=p=0 out/final.mp4 | wc -l | xargs echo "chapters in final.mp4:"
ls -lh out/final.mp4
