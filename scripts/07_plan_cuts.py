#!/usr/bin/env python3
"""Decide the cuts. Writes data/cuts.json = an edit decision list (EDL) in SOURCE time that
Remotion plays back, plus main-timeline subtitles/chapters so the muxed file stays in sync.

Two edits, each chosen for impact:

MAIN (tightened full interview)
  1. Drop pre-roll ("More, more... Recording?") - the viewer should start on the host's welcome.
  2. Drop post-roll after the closing thanks ("This could be very long.").
  3. Shorten dead air: any pause > MAX_PAUSE between words is cut down to ~0.4 s. Pace feels
     livelier but speech is never touched, so there are no jump-cut artefacts mid-word.
  4. Cut filler words (um/uh/...) when Whisper emits them.
  Pads (0.15 s in / 0.25 s out, never more than half the gap to the neighbouring word) keep
  breaths natural. All cut points are snapped to the 25 fps grid so Remotion frames match exactly.

HIGHLIGHTS (~75 s reel for social)
  Claude read the transcript and picked self-contained, quotable claims. Order = hook first
  (the most provocative claim), then escalation, ending on the payoff. Each is anchored by
  start/end phrases located at WORD level (asserted unique), then pause-tightened.
"""
import json, re

FPS = 25
MAX_PAUSE, PAD_IN, PAD_OUT = 0.8, 0.15, 0.25
FILLERS = {"um", "umm", "uh", "erm", "er", "hmm", "ah"}

t = json.load(open("data/transcript.json"))
cues = json.load(open("data/cues.json"))
chapters = json.load(open("data/chapters.json"))
words = [dict(w=x["w"], start=x["start"], end=x["end"]) for s in t["segments"] for x in s["words"]]
segs = t["segments"]
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
toks = [norm(w["w"]) for w in words]
snap = lambda x: round(x * FPS) / FPS


def find(phrase, after=0):
    p = [x for x in map(norm, phrase.split()) if x]
    return [i for i in range(after, len(toks) - len(p) + 1) if toks[i:i + len(p)] == p], len(p)


def tighten(i0, i1, reason):
    """Words i0..i1 inclusive -> list of kept source intervals."""
    ivs, brk = [], True
    for i in range(i0, i1 + 1):
        w = words[i]
        if toks[i] in FILLERS:
            brk = True
            continue
        if not brk and ivs and w["start"] - words[ivs[-1][2]]["end"] <= MAX_PAUSE:
            ivs[-1][1], ivs[-1][2] = w["end"], i
        else:
            ivs.append([w["start"], w["end"], i, i])  # [start, end, last word idx, first word idx]
        brk = False
    out = []
    for s, e, last, first in ivs:
        gin = s - words[first - 1]["end"] if first > 0 else 1.0
        gout = words[last + 1]["start"] - e if last + 1 < len(words) else 1.0
        s2 = snap(s - min(PAD_IN, max(0.0, gin / 2)))
        e2 = snap(e + min(PAD_OUT, max(0.0, gout / 2)))
        if e2 <= s2:
            e2 = s2 + 1 / FPS
        if out and s2 <= out[-1]["src_end"]:
            out[-1]["src_end"] = max(out[-1]["src_end"], e2)
        else:
            out.append({"src_start": s2, "src_end": e2, "reason": reason})
    return out


# ---- MAIN ----
first_seg = next(s for s in segs if "hello" in s["text"].lower())
last_seg = [s for s in segs if "thank you" in s["text"].lower()][-1]
i0 = next(i for i, w in enumerate(words) if w["start"] >= first_seg["start"] - 0.01)
i1 = max(i for i, w in enumerate(words) if w["end"] <= last_seg["end"] + 0.01)
main = tighten(i0, i1, "speech (pauses tightened)")

# ---- HIGHLIGHTS ----  (start phrase, end phrase, why it lands)
HIGHLIGHTS = [
    ("we are right now entered into", "building another ai", "Hook: the boldest claim, opens the reel"),
    ("i have 300 bots running", "write other bots", "Concrete proof of scale, makes the hook credible"),
    ("what we need to become is become pilots", "working all together", "The core metaphor in one line"),
    ("instead of going to their keyboards", "observing and directing", "Vivid change in how people work"),
    ("once i give you the task", "goal to be achieved", "What a bot is, in plain words"),
    ("with a plane the risk is higher", "get certified", "Honest risk beat, adds credibility"),
    ("once ai does the job we either go to our corner", "learning and creating", "Closing payoff: the human role"),
]
highlights = []
for a, b, why in HIGHLIGHTS:
    ha, _ = find(a)
    assert len(ha) == 1, f"start phrase {a!r} matched {len(ha)}"
    hb, lb = find(b, ha[0])
    assert hb, f"end phrase {b!r} not found after start"
    ivs = tighten(ha[0], hb[0] + lb - 1, why)
    for iv in ivs:
        iv["label"] = why
    highlights += ivs


# ---- timeline remap (source seconds -> output seconds) ----
def build_map(ivs):
    m, acc = [], 0
    for iv in ivs:
        s, e = round(iv["src_start"] * FPS), round(iv["src_end"] * FPS)
        m.append((s, e, acc)); acc += e - s
    return m, acc


def to_out(m, total, sec):
    f = sec * FPS
    for s, e, o in m:
        if f < e:
            return (o + max(0.0, f - s)) / FPS
    return total / FPS


m_main, tot_main = build_map(main)
m_hl, tot_hl = build_map(highlights)

def srt_ts(x):
    ms = round(x * 1000); h, ms = divmod(ms, 3600000); mi, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{mi:02}:{s:02},{ms:03}"


def cue_entries(m, total, ivs, offset=0.0):
    """Cues restricted to words inside kept intervals, on the output timeline: [(start, end, text)]."""
    out = []
    for c in cues:
        ws = [w for w in c["words"] if any(iv["src_start"] <= (w["start"] + w["end"]) / 2 <= iv["src_end"] for iv in ivs)]
        if ws:
            s = to_out(m, total, ws[0]["start"]) + offset
            e = max(to_out(m, total, ws[-1]["end"]) + offset, s + 0.8)
            out.append([s, e, " ".join(w["w"] for w in ws)])
    for i in range(len(out) - 1):
        out[i][1] = min(out[i][1], out[i + 1][0])
    return out


def write_srt(path, entries):
    open(path, "w").write("\n".join(f"{n}\n{srt_ts(s)} --> {srt_ts(e)}\n{t}\n" for n, (s, e, t) in enumerate(entries, 1)))


def write_chapters(stem, chs, total_s):
    for i, c in enumerate(chs):
        c["end"] = chs[i + 1]["start"] if i + 1 < len(chs) else round(total_s, 2)
    json.dump(chs, open(f"data/{stem}.json", "w"), indent=1)
    with open(f"data/{stem}.ffmetadata", "w") as f:
        f.write(";FFMETADATA1\n")
        for c in chs:
            f.write(f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(c['start']*1000)}\nEND={round(c['end']*1000)}\ntitle={c['title']}\n")


hi = main[-1]["src_end"]
main_chs = [{"title": c["title"], "start": round(to_out(m_main, tot_main, c["start"]), 2)} for c in chapters if c["start"] < hi]
hl_s, main_s = tot_hl / FPS, tot_main / FPS

# main only
write_srt("data/subtitles.main.srt", cue_entries(m_main, tot_main, main))
write_chapters("chapters.main", [dict(c) for c in main_chs], main_s)
# combined: highlights first, then the full (tightened) interview
write_srt("data/subtitles.combined.srt",
          cue_entries(m_hl, tot_hl, highlights) + cue_entries(m_main, tot_main, main, offset=hl_s))
write_chapters("chapters.combined",
               [{"title": "Highlights", "start": 0.0}] + [{"title": c["title"], "start": round(c["start"] + hl_s, 2)} for c in main_chs],
               hl_s + main_s)

src_len = chapters[-1]["end"]
stats = {
    "source_s": src_len, "main_s": round(tot_main / FPS, 1), "removed_s": round(src_len - tot_main / FPS, 1),
    "main_cuts": len(main), "highlights_s": round(tot_hl / FPS, 1), "highlight_clips": len(HIGHLIGHTS),
    "highlight_intervals": len(highlights), "combined_s": round((tot_hl + tot_main) / FPS, 1),
}
json.dump({"stats": stats, "main": main, "highlights": highlights}, open("data/cuts.json", "w"), indent=1)
print(json.dumps(stats, indent=1))
