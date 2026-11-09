# Delivery Pilot Interview - AI video processing (C1193.MP4)

AI-based flow that transcribes an English interview video, builds subtitles and chapter markers, and edits it with Remotion.
**This repo holds metadata and code only. Video and audio files are git-ignored.**
Plan: [docs/PLAN.md](docs/PLAN.md) | Rationale log: [docs/DECISIONS.md](docs/DECISIONS.md)

## Flow

Legend: done = green, pending = grey.

```mermaid
flowchart TD
    SRC[("C1193.MP4<br/>~/Downloads, 4K, 28 min<br/>NOT in repo")]:::done
    S1["01 extract_audio.sh<br/>ffmpeg to 16kHz mono WAV"]:::wip
    WAV[("work/audio.wav<br/>git-ignored")]:::wip
    S2["02 transcribe.py<br/>mlx-whisper large-v3-turbo"]:::todo
    TJ[/"data/transcript.json<br/>word timestamps"/]:::todo
    S3["03 make_subtitles.py"]:::todo
    SUB[/"data/subtitles.srt + .vtt"/]:::todo
    S4["04 make_chapters.py<br/>Claude topic segmentation"]:::todo
    CH[/"data/chapters.json"/]:::todo
    S5["05 make_proxy.sh<br/>ffmpeg 720p proxy"]:::todo
    PX[("work/proxy.mp4<br/>git-ignored")]:::todo
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
scripts/01_extract_audio.sh
```
