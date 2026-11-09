# Decisions log

## 1. Project setup and plan (2026-11-09)
- **Decision:** keep all media out of git and use the repo for metadata and processing code.
- **Why:** the source is 20.9 GB. Git would be unusable, and GitHub rejects files over 100 MB.
- **Decision:** transcribe from extracted 16 kHz audio, edit on a 720p proxy.
- **Why:** 4K decode dominates time and memory for no benefit when only speech or a preview is needed.

## 2. Library installation (2026-11-09)
- **Machine:** Apple Silicon (arm64), Node 26, Python 3.15, ffmpeg already installed via Homebrew.
- **Transcription:** `mlx-whisper` in a project-local `.venv` (pinned subset in `requirements.txt`).
  - **Why:** it runs Whisper on the Apple GPU through MLX, which is much faster than CPU `openai-whisper` on a Mac. It is free and local, so audio never leaves the machine. The global `whisper` CLI was not used so the project stays reproducible.
- **Editing:** `remotion`, `@remotion/cli`, `@remotion/captions`, `react`, `react-dom` (Remotion 4.0.542) via npm.
  - **Why:** `@remotion/captions` provides caption types and SRT parsing, which fits the subtitle step.
- **Not installed yet:** Whisper model weights. They download on the first transcription run (step 4) so this step stays light.

## 3. Audio extraction (2026-11-09)
- `scripts/01_extract_audio.sh`: `-map 0:a:0 -vn -ac 1 -ar 16000 -c:a pcm_s16le`.
- **Why:** the file has 3 streams (video, PCM audio, a data stream). Mapping only the first audio stream avoids the data stream. Result: 52 MB WAV in about 2 s, full 28:13 duration.

## 4. Transcription (2026-11-09)
- `scripts/02_transcribe.py`: `whisper-large-v3-turbo` (MLX), `language="en"`, `word_timestamps=True`, `condition_on_previous_text=False`.
- **Why:** turbo is near large-v3 accuracy at much higher speed. Disabling previous-text conditioning avoids the hallucinated repetition loops Whisper can fall into on long audio.
- **Result:** 283 segments, 4,494 words, about 2 min (plus a one-off 65 s model download).
- **Validation:** last segment ends at 1691.66 s (audio is 1693.4 s), no segment text repeated more than twice, no gap over 20 s.
- **Known caveat:** the opening segment "More, more." is room noise before the interview starts. Chapters/subtitles may trim it. Proper names (e.g. the interviewee's name) may need manual correction.
- `data/transcript.json` is committed (metadata, small). The audio is not.

## 5. Subtitles (2026-11-09)
- `scripts/03_make_subtitles.py` builds cues from **word** timestamps, not Whisper segments.
- **Why:** Whisper segments vary from 1 to 20+ s, too long to read. Word timing lets us enforce readability: max 2 lines of 42 chars, 76 chars per cue, 5.5 s per cue, break on sentence ends, pauses over 0.6 s, or gaps over 1.2 s. End times are clamped so cues never overlap.
- **Result:** 408 cues, none over 6.5 s, none under 0.5 s, 2 lines marginally over 42 chars. SRT for players and Remotion, VTT for web.
- **Tuning note:** the first pass (84 chars / 6 s) gave 7 long cues and 13 long lines, so limits were tightened.

## 6. Proxy (2026-11-09)
- `scripts/05_make_proxy.sh`: 1280x720, 25 fps, `h264_videotoolbox` 4 Mbit/s, AAC stereo, faststart.
- **Why:** hardware encoding is several times faster than libx264 for a 4K source, and a 720p file previews smoothly in Remotion Studio.
