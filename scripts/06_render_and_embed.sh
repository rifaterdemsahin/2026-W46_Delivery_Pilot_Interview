#!/usr/bin/env bash
# Usage: scripts/06_render_and_embed.sh [highlights|main|combined|linkedin|x|all]   (default: all)
#  combined:   highlights first, then the full interview, with explainers + section bar (~1711 s, ~20 min)
#  highlights: ~53 s social reel, ~35 s to render
#  main:       tightened full interview, ~41k frames (~18 min on Apple Silicon)
# Renders with Remotion, then (main only) muxes native chapters + soft subtitles with ffmpeg.
# The chapters/subtitles used are the *remapped* ones from 07_plan_cuts.py, so they match the cut timeline.
set -euo pipefail
cd "$(dirname "$0")/.."
what="${1:-all}"
mkdir -p out
# Mixing music and effects over dialogue can push peaks; re-level the audio only (video is copied): -16 LUFS, true peak -1.5 dB
leveled() { ffmpeg -y -hide_banner -loglevel error -i "$1" -c:v copy -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:a aac -b:a 192k "$2"; }

if [[ "$what" == "highlights" || "$what" == "all" ]]; then
  npx remotion render src/index.ts Highlights out/highlights.mp4 --codec=h264 --crf=20
fi

if [[ "$what" == "x" || "$what" == "all" ]]; then
  # X: no soft subtitle track (captions are burned in); a plain H.264/AAC MP4 under X's limits (2:20, 512 MB)
  npx remotion render src/index.ts X out/x_raw.mp4 --codec=h264 --crf=20
  leveled out/x_raw.mp4 out/x_final.mp4
  ls -lh out/x_final.mp4
fi

if [[ "$what" == "linkedin" || "$what" == "all" ]]; then
  npx remotion render src/index.ts LinkedIn out/linkedin_mix.mp4 --codec=h264 --crf=20
  leveled out/linkedin_mix.mp4 out/linkedin_raw.mp4
  ffmpeg -y -hide_banner -loglevel error -i out/linkedin_raw.mp4 -i data/subtitles.linkedin.srt \
    -map 0:v -map 0:a -map 1:0 -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng \
    -movflags +faststart out/linkedin_final.mp4
  ls -lh out/linkedin_final.mp4
fi

if [[ "$what" == "combined" || "$what" == "all" ]]; then
  npx remotion render src/index.ts Combined out/combined_mix.mp4 --codec=h264 --crf=20
  leveled out/combined_mix.mp4 out/combined_raw.mp4
  ffmpeg -y -hide_banner -loglevel error \
    -i out/combined_raw.mp4 -i data/chapters.combined.ffmetadata -i data/subtitles.combined.srt \
    -map 0:v -map 0:a -map 2:0 -map_metadata 1 -map_chapters 1 \
    -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng \
    -movflags +faststart out/combined_final.mp4
  echo "chapters in combined_final.mp4: $(ffprobe -v error -show_chapters -of csv=p=0 out/combined_final.mp4 | wc -l)"
  ls -lh out/combined_final.mp4
fi

if [[ "$what" == "main" || "$what" == "all" ]]; then
  npx remotion render src/index.ts Main out/edited.mp4 --codec=h264 --crf=20
  ffmpeg -y -hide_banner -loglevel error \
    -i out/edited.mp4 -i data/chapters.main.ffmetadata -i data/subtitles.main.srt \
    -map 0:v -map 0:a -map 2:0 -map_metadata 1 -map_chapters 1 \
    -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng \
    -movflags +faststart out/final.mp4
  echo "chapters in final.mp4: $(ffprobe -v error -show_chapters -of csv=p=0 out/final.mp4 | wc -l)"
  ls -lh out/final.mp4
fi
