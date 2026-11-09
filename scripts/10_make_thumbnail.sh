#!/usr/bin/env bash
# Always make THREE completely different thumbnails for A/B/C testing (YouTube Test & Compare allows 3).
#   A "300 bots / 1 pilot" (red/dark, number + open question, face card)
#   B "Stop typing."       (yellow/black, imperative, big face)
#   C "Driver / Pilot, which are you?" (cyan split screen, no face)
# Frames come from the 4K source (sharper than the proxy). Usage: scripts/10_make_thumbnail.sh [secondsA] [secondsB]
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/config.sh
ta="${1:-404}"; tb="${2:-285}"
mkdir -p public assets/thumbnails out
ffmpeg -y -hide_banner -loglevel error -ss "$ta" -i "$SOURCE_VIDEO" -frames:v 1 -vf scale=1920:-1 -q:v 2 public/thumb_frame.jpg
ffmpeg -y -hide_banner -loglevel error -ss "$tb" -i "$SOURCE_VIDEO" -frames:v 1 -vf scale=1920:-1 -q:v 2 public/thumb_frame_b.jpg
for v in A B C; do
  npx remotion still src/index.ts "Thumbnail$v" "out/thumbnail_$v.png" >/dev/null
done
ffmpeg -y -hide_banner -loglevel error -i out/thumbnail_A.png -q:v 2 assets/thumbnails/test1_A_300bots-1pilot.jpg
ffmpeg -y -hide_banner -loglevel error -i out/thumbnail_B.png -q:v 2 assets/thumbnails/test1_B_stop-typing.jpg
ffmpeg -y -hide_banner -loglevel error -i out/thumbnail_C.png -q:v 2 assets/thumbnails/test1_C_driver-or-pilot.jpg
cp assets/thumbnails/test1_A_300bots-1pilot.jpg assets/thumbnail.jpg   # default upload = A
ls -lh assets/thumbnails/test1_*
