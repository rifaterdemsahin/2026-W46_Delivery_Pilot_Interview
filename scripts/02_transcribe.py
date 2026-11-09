#!/usr/bin/env python3
"""Transcribe work/audio.wav with mlx-whisper (word-level timestamps, English)."""
import json, sys
import mlx_whisper

MODEL = "mlx-community/whisper-large-v3-turbo"
AUDIO = "work/audio.wav"
OUT = "data/transcript.json"

result = mlx_whisper.transcribe(
    AUDIO,
    path_or_hf_repo=MODEL,
    language="en",
    word_timestamps=True,
    condition_on_previous_text=False,  # reduces repetition loops on long audio
    verbose=False,
)
slim = {
    "model": MODEL,
    "language": result["language"],
    "text": result["text"].strip(),
    "segments": [
        {
            "id": s["id"], "start": round(s["start"], 2), "end": round(s["end"], 2),
            "text": s["text"].strip(),
            "words": [{"w": w["word"].strip(), "start": round(w["start"], 2),
                       "end": round(w["end"], 2)} for w in s.get("words", [])],
        }
        for s in result["segments"]
    ],
}
with open(OUT, "w") as f:
    json.dump(slim, f, ensure_ascii=False, indent=1)
print(f"{len(slim['segments'])} segments, {len(slim['text'].split())} words -> {OUT}")
