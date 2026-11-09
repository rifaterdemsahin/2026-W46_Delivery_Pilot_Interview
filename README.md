# Delivery Pilot Interview - AI video processing (C1193.MP4)

AI-based flow that transcribes an English interview video, builds subtitles and chapter markers, and edits it with Remotion.
**This repo holds metadata and code only. Video and audio files are git-ignored.**
Plan: [docs/PLAN.md](docs/PLAN.md) | Rationale log: [docs/DECISIONS.md](docs/DECISIONS.md)

## Flow

Legend: done = green, pending = grey.

```mermaid
flowchart TD
    SRC[("C1193.MP4<br/>~/Downloads, 4K, 28 min<br/>NOT in repo")]:::done
    S1["01 extract_audio.sh<br/>ffmpeg to 16kHz mono WAV"]:::done
    WAV[("work/audio.wav<br/>git-ignored")]:::done
    S2["02 transcribe.py<br/>mlx-whisper large-v3-turbo"]:::done
    TJ[/"data/transcript.json<br/>283 segments, 4494 words"/]:::done
    S3["03 make_subtitles.py"]:::done
    SUB[/"data/subtitles.srt + .vtt"/]:::done
    S4["04 make_chapters.py<br/>Claude topic segmentation, 13 chapters"]:::done
    CH[/"data/chapters.json + .ffmetadata + .youtube.txt"/]:::done
    S5["05 make_proxy.sh<br/>ffmpeg 720p proxy"]:::wip
    PX[("work/proxy.mp4<br/>git-ignored")]:::wip
    RM["Remotion composition<br/>captions + chapter cards"]:::todo
    OUT[("out/final.mp4<br/>git-ignored")]:::todo
    S8["06 embed_chapters.sh<br/>ffmpeg metadata mux"]:::todo

    SRC --> S1 --> WAV --> S2 --> TJ
    TJ --> S3 --> SUB
    TJ --> S4 --> CH
    SRC --> S5 --> PX
    PX --> RM
    SUB --> RM
    CH --> RM
    RM --> OUT --> S8

    classDef done fill:#c8f7c5,stroke:#2e7d32,color:#000
    classDef wip fill:#fff3b0,stroke:#b58900,color:#000
    classDef todo fill:#eee,stroke:#999,color:#555
```

## Setup
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
npm install
```

## Run
```bash
scripts/01_extract_audio.sh                  # ~2 s
.venv/bin/python -I scripts/02_transcribe.py # ~2 min on Apple Silicon
.venv/bin/python -I scripts/03_make_subtitles.py
scripts/04_make_chapters.py
scripts/05_make_proxy.sh                     # ~10 min, hardware H.264
```
