#!/usr/bin/env bash
# 720p proxy for fast Remotion preview/render. Uses Apple VideoToolbox hardware H.264.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/config.sh
mkdir -p "$WORK_DIR"
ffmpeg -y -hide_banner -loglevel error -stats -i "$SOURCE_VIDEO" \
  -map 0:v:0 -map 0:a:0 -vf "scale=1280:720" -r 25 \
  -c:v h264_videotoolbox -b:v 4M -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ac 2 -movflags +faststart "$WORK_DIR/proxy.mp4"
ls -lh "$WORK_DIR/proxy.mp4"
