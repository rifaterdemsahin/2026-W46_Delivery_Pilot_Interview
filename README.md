# Delivery Pilot Interview - AI video processing (C1193.MP4)

AI-based flow that transcribes an English interview video, builds subtitles and chapter markers, decides the cuts, and edits it with Remotion (animated white/red captions).

**This repo holds code, metadata and docs only.** The raw video (`~/Downloads/C1193.MP4`, 20.9 GB) and every generated video/audio file (`work/`, `out/`, `public/*.mp4`) are git-ignored and never committed.

Docs: [workflow: prompts and stages](docs/WORKFLOW.md) | [plan](docs/PLAN.md) | [rationale for every step](docs/DECISIONS.md) | [readable transcript](data/transcript.txt)

## Flow

Green = done, yellow = built but not yet run in full, grey = not run.

```mermaid
flowchart TD
    SRC[("C1193.MP4<br/>~/Downloads, 4K, 28 min<br/>NOT in repo")]:::done
    S1["01 extract_audio.sh<br/>ffmpeg 16kHz mono WAV"]:::done
    WAV[("work/audio.wav<br/>git-ignored")]:::done
    S2["02 transcribe.py<br/>mlx-whisper large-v3-turbo<br/>prints ETA while running"]:::done
    FIX["02b apply_corrections.py<br/>data/corrections.json, 17 active rules"]:::done
    TJ[/"data/transcript.json + .txt<br/>corrected; transcript.raw.json = Whisper"/]:::done
    S3["03 make_subtitles.py"]:::done
    SUB[/"subtitles.srt/.vtt, cues.json<br/>(per-word timing)"/]:::done
    S4["04 make_chapters.py<br/>Claude topic segmentation"]:::done
    CH[/"chapters.json + .ffmetadata<br/>13 chapters"/]:::done
    S7["07 plan_cuts.py<br/>decide cuts for impact"]:::done
    EDL[/"data/cuts.json (EDL)<br/>main 16 cuts, highlights 7 clips<br/>+ main/combined subtitles + chapters"/]:::done
    S8["08 plan_explainers.py<br/>Claude picks 9 concept moments"]:::done
    EXP[/"data/explainers.json<br/>6 simple graphics, 3 infographics"/]:::done
    ENV[(".env FAL_KEY<br/>git-ignored, guarded by pre-commit hook")]:::secret
    S9["09 generate_visuals.py<br/>fal.ai flux/schnell, text-free art<br/>~$0.01 total"]:::done
    IMG[/"public/visuals/*.jpg<br/>+ visuals_manifest.json"/]:::done
    S5["05 make_proxy.sh<br/>ffmpeg 720p proxy"]:::done
    PX[("work/proxy.mp4<br/>git-ignored")]:::done
    RM["Remotion src/<br/>Series of cuts, animated white/red captions,<br/>left-side explainers, chapter cards"]:::done
    COMB["Combined composition<br/>highlights, then main<br/>bottom section-length bar"]:::done
    HL[("out/highlights.mp4<br/>rendered + checked")]:::done
    S6["06 render_and_embed.sh combined<br/>render + ffmpeg chapters + soft subs"]:::wip
    OUT[("out/combined_final.mp4<br/>git-ignored")]:::todo

    SRC --> S1 --> WAV --> S2 --> FIX --> TJ
    TJ --> S3 --> SUB
    TJ --> S4 --> CH
    TJ --> S7
    SUB --> S7
    CH --> S7
    S7 --> EDL
    TJ --> S8 --> EXP
    EXP --> S9
    ENV -.-> S9
    S9 --> IMG
    SRC --> S5 --> PX
    PX --> RM
    EDL --> RM
    SUB --> RM
    CH --> RM
    EXP --> RM
    IMG --> RM
    RM --> COMB
    RM --> HL
    COMB --> S6 --> OUT

    classDef done fill:#c8f7c5,stroke:#2e7d32,color:#000
    classDef wip fill:#fff3b0,stroke:#b58900,color:#000
    classDef todo fill:#eee,stroke:#999,color:#555
    classDef secret fill:#ffd6d6,stroke:#c62828,color:#000
```

## Secrets
API keys live only in `.env` (git-ignored; copy `.env.example`). `.githooks/pre-commit` blocks any commit containing something that looks like a key. Enable it once per clone: `git config core.hooksPath .githooks`.

## Speakers
Marianna asks the questions; Rifat Erdem Sahin answers ([data/speakers.json](data/speakers.json)).

## Setup
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
npm install
```
Needs `ffmpeg`/`ffprobe` (Homebrew) and an Apple Silicon Mac for mlx-whisper. Source path defaults to `~/Downloads/C1193.MP4` (override with `SOURCE_VIDEO=...`).

## Steps (run in order)
| # | Command | Output | Time |
|---|---------|--------|------|
| 1 | `scripts/01_extract_audio.sh` | `work/audio.wav` | 2 s |
| 2 | `.venv/bin/python -I scripts/02_transcribe.py` | `data/transcript.raw.json` | ~1-2 min, shows ETA |
| 2b | `.venv/bin/python -I scripts/02b_apply_corrections.py` | `data/transcript.json`, `.txt` (corrected) | instant, prints hits per rule |
| 3 | `.venv/bin/python -I scripts/03_make_subtitles.py` | SRT, VTT, captions/cues JSON | instant |
| 4 | `.venv/bin/python -I scripts/04_make_chapters.py` | chapters JSON, ffmetadata, YouTube list | instant |
| 5 | `scripts/05_make_proxy.sh` | `work/proxy.mp4`, `public/proxy.mp4` hard link | ~10 min |
| 6 | `.venv/bin/python -I scripts/07_plan_cuts.py` | `data/cuts.json` + remapped subtitles/chapters | instant |
| 6b | (same script) | `subtitles.combined.srt`, `chapters.combined.*` | |
| 6c | `.venv/bin/python -I scripts/08_plan_explainers.py` | `data/explainers.json` | instant |
| 6d | `.venv/bin/python -I scripts/09_generate_visuals.py` | `public/visuals/*.jpg`, `data/visuals_manifest.json` | ~10 s, ~$0.01 (needs `.env`) |
| 7 | `npm run studio` (then open http://localhost:3000 in Chrome) | live preview of `Main`, `Highlights` and `Combined` (highlights first, then the full interview, with a section-length bar) | |
| 8 | `scripts/06_render_and_embed.sh highlights` | `out/highlights.mp4` | ~35 s |
| 9 | `scripts/06_render_and_embed.sh main` | `out/final.mp4` with chapters + soft subs | ~20-30 min |
| 10 | `scripts/06_render_and_embed.sh combined` | `out/combined_final.mp4` (highlights first, explainers, section bar) | ~20-30 min |

## How the cuts are decided
See the docstring in [`scripts/07_plan_cuts.py`](scripts/07_plan_cuts.py). In short: drop pre/post-roll, shorten pauses over 0.8 s, cut filler words (main edit); hook-first, claim-by-claim highlights picked by Claude and located by exact phrase (highlights reel). Remotion plays `data/cuts.json` back-to-back, so changing the edit means editing the script and re-running step 6, not touching video.
