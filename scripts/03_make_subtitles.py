#!/usr/bin/env python3
"""Build SRT + VTT from word timestamps: <=2 lines x 42 chars, 1-6 s per cue,
break preferably at sentence ends / pauses."""
import json

MAX_LINE, MAX_CHARS, MAX_DUR, PAUSE = 42, 76, 5.5, 0.6
words = [w for s in json.load(open("data/transcript.json"))["segments"] for w in s["words"]]

cues, cur = [], []
def flush():
    global cur
    if cur:
        cues.append(cur); cur = []

for i, w in enumerate(words):
    cur.append(w)
    text = " ".join(x["w"] for x in cur)
    dur = w["end"] - cur[0]["start"]
    nxt = words[i + 1] if i + 1 < len(words) else None
    gap = (nxt["start"] - w["end"]) if nxt else 99
    sentence_end = w["w"][-1:] in ".?!"
    if (len(text) >= MAX_CHARS - 6 or dur >= MAX_DUR
            or (sentence_end and (len(text) > 25 or gap > PAUSE))
            or gap > 1.2):
        flush()
flush()

def wrap(text):
    if len(text) <= MAX_LINE:
        return text
    mid = len(text) // 2
    sp = [i for i, c in enumerate(text) if c == " "]
    k = min(sp, key=lambda i: abs(i - mid))
    return text[:k] + "\n" + text[k + 1:]

def ts(t, sep):
    ms = round(t * 1000); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}{sep}{ms:03}"

srt, vtt = [], ["WEBVTT\n"]
for n, c in enumerate(cues, 1):
    start, end = c[0]["start"], max(c[-1]["end"], c[0]["start"] + 0.8)
    if n < len(cues):
        end = min(end, cues[n][0]["start"])  # no overlap with next cue
    body = wrap(" ".join(x["w"] for x in c))
    srt.append(f"{n}\n{ts(start, ',')} --> {ts(end, ',')}\n{body}\n")
    vtt.append(f"{ts(start, '.')} --> {ts(end, '.')}\n{body}\n")
open("data/subtitles.srt", "w").write("\n".join(srt))
open("data/subtitles.vtt", "w").write("\n".join(vtt))
print(f"{len(cues)} cues")

# Remotion @remotion/captions format, consumed directly by src/ (no runtime SRT parsing)
caps = []
for n, c in enumerate(cues):
    start, end = c[0]["start"], max(c[-1]["end"], c[0]["start"] + 0.8)
    if n + 1 < len(cues):
        end = min(end, cues[n + 1][0]["start"])
    caps.append({"text": wrap(" ".join(x["w"] for x in c)), "startMs": round(start * 1000),
                 "endMs": round(end * 1000), "timestampMs": round(start * 1000), "confidence": None})
json.dump(caps, open("data/captions.json", "w"), ensure_ascii=False)

# Cues with per-word timing (source timeline) for the animated white/red subtitles and for remapping after cuts
cues_out = []
for n, c in enumerate(cues):
    end = max(c[-1]["end"], c[0]["start"] + 0.8)
    if n + 1 < len(cues):
        end = min(end, cues[n + 1][0]["start"])
    cues_out.append({"start": c[0]["start"], "end": round(end, 2),
                     "words": [{"w": x["w"], "start": x["start"], "end": x["end"]} for x in c]})
json.dump(cues_out, open("data/cues.json", "w"), ensure_ascii=False)
