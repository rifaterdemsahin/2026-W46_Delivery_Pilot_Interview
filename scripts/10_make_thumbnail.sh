#!/usr/bin/env bash
# YouTube thumbnail: one frame from the 4K source (sharper than the proxy) + Remotion headline text.
# Usage: scripts/10_make_thumbnail.sh [seconds]   (default 404 = 6:44, expressive gesture, space on the left)
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/config.sh
t="${1:-404}"
mkdir -p public assets out
ffmpeg -y -hide_banner -loglevel error -ss "$t" -i "$SOURCE_VIDEO" -frames:v 1 -vf scale=1920:-1 -q:v 2 public/thumb_frame.jpg
npx remotion still src/index.ts Thumbnail out/thumbnail.png
ffmpeg -y -hide_banner -loglevel error -i out/thumbnail.png -q:v 2 assets/thumbnail.jpg
ls -lh assets/thumbnail.jpg
