#!/usr/bin/env bash
# Extract 16 kHz mono WAV (Whisper's native format) from the source video.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/config.sh
mkdir -p "$WORK_DIR"
ffmpeg -y -hide_banner -loglevel error -stats -i "$SOURCE_VIDEO" \
  -map 0:a:0 -vn -ac 1 -ar 16000 -c:a pcm_s16le "$WORK_DIR/audio.wav"
ls -lh "$WORK_DIR/audio.wav"
