# Plan: AI-based transcription, subtitles and chapters for C1193.MP4

Source: `~/Downloads/C1193.MP4` (English speech, never copied into this repo).
Probed with ffprobe: H.264 3840x2160, 25 fps, about 28m13s (1693 s), 20.9 GB, PCM audio.

## Rules for this project
1. **No media in git.** The repo holds metadata (transcripts, SRT/VTT, chapters JSON), scripts and Remotion code. `.gitignore` blocks video and audio. Heavy files live in `work/` (git-ignored).
2. **Every step is documented in `docs/DECISIONS.md`** with its rationale, then committed and pushed.
3. **Reproducible.** Each stage is a script that reads from and writes to a known path.

## Pipeline
| # | Stage | Input -> Output | Tool | Rationale |
|---|-------|-----------------|------|-----------|
| 1 | Audio extract | MP4 -> `work/audio.wav` (16 kHz mono) | ffmpeg | Whisper needs 16 kHz mono. Reading 20.9 GB of 4K video is wasteful when only audio is needed. |
| 2 | Transcribe | wav -> `data/transcript.json` (word timestamps) | mlx-whisper (Apple Silicon GPU), `large-v3-turbo` | Fast local run, free, private, word-level timing. Language fixed to `en` to skip detection errors. |
| 3 | Subtitles | transcript -> `data/subtitles.srt`, `.vtt` | script (max 42 chars/line, 2 lines, 1-6 s per cue) | Standard formats, and Remotion `@remotion/captions` can consume them. |
| 4 | Chapters | transcript -> `data/chapters.json` | LLM (Claude) over the transcript | AI semantic topic segmentation gives titles and start times. Output is reviewed before use. |
| 5 | Proxy | MP4 -> `work/proxy.mp4` (1280x720, low bitrate) | ffmpeg | Remotion previews and renders smoothly on a proxy. The 4K original stays untouched. |
| 6 | Edit | proxy + subtitles + chapters -> Remotion composition | Remotion (`remotion`, `@remotion/cli`, `@remotion/captions`) | Programmatic captions, chapter title cards, progress markers. |
| 7 | Render | composition -> `out/final.mp4` (git-ignored) | Remotion CLI | A proxy render for review first. A 4K render from the original only if the proxy cut is approved. |
| 8 | Chapter markers in file | `chapters.json` -> ffmetadata -> muxed into the final MP4 | ffmpeg | Gives native chapter navigation in players, plus a YouTube-style timestamp list. |

## Milestones (one commit + push each)
1. Plan, `.gitignore`, decisions log (this commit)
2. Install transcription libraries (Python venv + mlx-whisper) and Remotion
3. Audio extraction script and run
4. Transcription run, commit `data/transcript.json`
5. Subtitle generation, commit SRT/VTT
6. AI chapter generation, commit `chapters.json`
7. Proxy + Remotion composition scaffolding
8. Review render, then final render and chapter muxing

## Risks and open questions
- Disk space: the proxy and audio need a few GB free under `work/`.
- Audio is PCM big-endian in the MP4; ffmpeg handles it, to be verified in step 3.
- Transcript accuracy on names and jargon: a glossary prompt can be passed to Whisper if needed.
- Final deliverable resolution (720p proxy vs 4K) is a decision for after the review render.
