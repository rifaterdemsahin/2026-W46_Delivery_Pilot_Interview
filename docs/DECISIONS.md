# Decisions log

## 1. Project setup and plan (2026-11-09)
- **Decision:** keep all media out of git and use the repo for metadata and processing code.
- **Why:** the source is 20.9 GB. Git would be unusable, and GitHub rejects files over 100 MB.
- **Decision:** transcribe from extracted 16 kHz audio, edit on a 720p proxy.
- **Why:** 4K decode dominates time and memory for no benefit when only speech or a preview is needed.
