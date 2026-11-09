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
