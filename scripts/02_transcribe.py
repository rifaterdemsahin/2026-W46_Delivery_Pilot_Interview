#!/usr/bin/env python3
"""Transcribe audio with mlx-whisper (word-level timestamps, English).

Usage: 02_transcribe.py [audio.wav] [out.json]
Prints the audio length, an up-front estimated completion time, and a live ETA
(clock time + minutes left) while running. Also writes a readable data/transcript.txt.
"""
import json, sys, time, subprocess, datetime as dt
import mlx_whisper
from tqdm import tqdm

MODEL = "mlx-community/whisper-large-v3-turbo"
AUDIO = sys.argv[1] if len(sys.argv) > 1 else "work/audio.wav"
OUT = sys.argv[2] if len(sys.argv) > 2 else "data/transcript.json"
SPEED_GUESS = 20.0  # x realtime measured on this Apple Silicon Mac (~25x); used for the first estimate

def clock(sec_from_now):
    return (dt.datetime.now() + dt.timedelta(seconds=sec_from_now)).strftime("%H:%M:%S")

dur = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO]).decode())
est = dur / SPEED_GUESS
print(f"Audio {dur/60:.1f} min. Started {clock(0)}. "
      f"Initial estimate: done around {clock(est + 30)} (~{est/60:.1f} min, excluding a first-run model download).",
      flush=True)

class EtaTqdm(tqdm):
    """Replace mlx-whisper's progress bar with one that shows the estimated finish time."""
    _last = 0.0
    def update(self, n=1):
        super().update(n)
        now = time.time()
        if now - EtaTqdm._last >= 5 and self.n and self.total:
            EtaTqdm._last = now
            rate = self.n / max(self.format_dict["elapsed"], 1e-6)
            left = (self.total - self.n) / rate
            print(f"  {100*self.n/self.total:5.1f}%  ETA {clock(left)}  (~{left/60:.1f} min left)", flush=True)

# mlx_whisper.transcribe is both a function and a module; patch tqdm in the module
sys.modules["mlx_whisper.transcribe"].tqdm.tqdm = EtaTqdm

t0 = time.time()
result = mlx_whisper.transcribe(
    AUDIO, path_or_hf_repo=MODEL, language="en", word_timestamps=True,
    condition_on_previous_text=False,  # reduces repetition loops on long audio
    verbose=False,
)
slim = {
    "model": MODEL, "language": result["language"], "text": result["text"].strip(),
    "segments": [
        {"id": s["id"], "start": round(s["start"], 2), "end": round(s["end"], 2),
         "text": s["text"].strip(),
         "words": [{"w": w["word"].strip(), "start": round(w["start"], 2),
                    "end": round(w["end"], 2)} for w in s.get("words", [])]}
        for s in result["segments"]
    ],
}
with open(OUT, "w") as f:
    json.dump(slim, f, ensure_ascii=False, indent=1)

if OUT == "data/transcript.json":  # human-readable copy
    with open("data/transcript.txt", "w") as f:
        for s in slim["segments"]:
            f.write(f"[{int(s['start']//60):02}:{int(s['start']%60):02}] {s['text']}\n")

took = time.time() - t0
print(f"Done {clock(0)}: {len(slim['segments'])} segments, {len(slim['text'].split())} words "
      f"in {took:.0f}s ({dur/took:.0f}x realtime) -> {OUT}")
