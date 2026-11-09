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
real = [i for i, x in enumerate(toks) if x]  # skip punctuation-only tokens such as "%"
ftoks = [toks[i] for i in real]


def span(a, b):
    """Word-index span from start phrase a to the first end phrase b after it (start asserted unique)."""
    pa = [x for x in map(norm, a.split()) if x]
    pb = [x for x in map(norm, b.split()) if x]
    ha = [k for k in range(len(ftoks) - len(pa) + 1) if ftoks[k:k + len(pa)] == pa]
    assert len(ha) == 1, f"start phrase {a!r} matched {len(ha)}"
    hb = [k for k in range(ha[0], len(ftoks) - len(pb) + 1) if ftoks[k:k + len(pb)] == pb]
    assert hb, f"end phrase {b!r} not found after start"
    return real[ha[0]], real[hb[0] + len(pb) - 1]


# Duplicated ideas removed from the MAIN edit. Rule: keep the first / fullest statement, drop restatements,
# never cut a sentence whose meaning is not said elsewhere. (start phrase, end phrase, why, where the idea is kept)
DEDUPE = [
    ("right it seems that today we dont need programmers", "crazy program that happened",
     "Host restates the guest's point (no need for programmers, build apps without coding)", "2:44-3:15 guest says it first"),
    ("what we need to become is become pilots", "doing their jobs properly",
     "Repeats 'become pilots rather than drivers' and the Cambridge-bots aside; host then says the bots tangent was too fast", "5:56-6:50 explains rider/driver/pilot in full"),
    ("if we never use ai we need to first become a writer", "old way of doing things",
     "Recap of rider/driver/pilot and 'AI builds the AI', already explained twice", "5:56-7:13 levels; 4:38-5:00 bots build bots"),
    ("what is happening right now is because the language", "but that means",
     "Says again that people become pilots and stop using keyboards", "6:44-7:13 stop typing, start directing"),
    ("a pilot versus a driver", "to answer your question",
     "Third telling of the horse/car/plane ladder, plus a stuttered repeat of 'to answer your question'", "5:56-6:50 levels"),
    ("a plane versus a car", "do meaningful stuff",
     "Repeats plane-versus-car and 'become more creative'", "24:35-25:01 what a pilot needs (creative, builder...)"),
    ("so the bot is more probabilistic", "complete the goal",
     "Repeats 'bots are probabilistic' within seconds of saying it", "9:16-9:35 and 14:19 first statements"),
    ("lets talk about ai skills first", "ai skills first",
     "Host asks to 'talk about AI skills' twice in 30 seconds", "5:22 first ask"),
]
first_seg = next(s for s in segs if "hello" in s["text"].lower())
last_seg = [s for s in segs if "thank you very much" in s["text"].lower()][-1]  # drops the extra trailing "Thank you."
i0 = next(i for i, w in enumerate(words) if w["start"] >= first_seg["start"] - 0.01)
i1 = max(i for i, w in enumerate(words) if w["end"] <= last_seg["end"] + 0.01)

removed = []
for a, b, why, kept in DEDUPE:
    ia, ib = span(a, b)
    assert i0 <= ia <= ib <= i1, f"dedupe span outside main range: {a!r}"
    removed.append(dict(ia=ia, ib=ib, src_start=words[ia]["start"], src_end=words[ib]["end"],
                        text=" ".join(w["w"] for w in words[ia:ib + 1]), why=why, kept_at=kept))
removed.sort(key=lambda x: x["ia"])
for x, y in zip(removed, removed[1:]):
    assert x["ib"] < y["ia"], "overlapping dedupe spans"

main, cur = [], i0
for x in removed:
    if x["ia"] > cur:
        main += tighten(cur, x["ia"] - 1, "speech (pauses tightened)")
    cur = x["ib"] + 1
main += tighten(cur, i1, "speech (pauses tightened)")
for x in removed:  # show each join so the edit can be proof-read
    ctx = lambda lo, hi: " ".join(w["w"] for w in words[lo:hi])
    print(f"CUT {x['src_start']:7.1f}-{x['src_end']:7.1f} ({x['src_end']-x['src_start']:4.1f}s)  ...{ctx(max(0,x['ia']-7),x['ia'])} [X] {ctx(x['ib']+1,x['ib']+8)}...")

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


# ---- LINKEDIN (<= 14 min): the strongest sections of the deduplicated interview, no repeated cold open ----
LINKEDIN_MAX_S = 14 * 60
LINKEDIN = [  # (start phrase, end phrase, section[, words to step back from the start phrase])
    ("so the reality is im passionate about technology", "this new profession comes to life", "Why a Delivery Pilot"),
    ("what is happening right now is we are moving from a rider", "so the ai is creating the other ai", "Rider, driver, pilot and bots building bots"),
    ("so i separated the ai skills into three", "the major thing that changes for us", "The three levels of AI skills"),
    ("but if you have the money spend the tokens", "campaign in the budget", "Frontier models, bots and agent-to-agent"),
    ("where is agent in between", "i like to deliver a pilot name", "Chatbot, agent, bot and Voltron"),
    ("yes the agent and the bot are very similar", "i want that goal to be achieved", "Agent vs bot vs robot"),
    ("lets talk a little bit about coding", "to use ai better", "Do we need to learn coding?"),
    ("to answer your question the engineering has to be learned", "comment and conquer more", "Pilots need more training"),
    ("right now most 20 30 of the world", "direct more than ever", "Jobs and directing bots"),
    ("that was my core niche", "create and operate all day long", "Self-learners and the pilot", 3),
    ("we are doing the eventbrite workshops", "what we implemented that week", "Join the workshops"),
    ("if someone is thinking oh ai isnt for me", "thank you very much", "Not for me? and closing"),
]
linkedin, li_sections = [], []
for a, b, label, *opt in LINKEDIN:
    ia, ib = span(a, b)
    if opt: ia = real[real.index(ia) - opt[0]]  # include a few words before the anchor (e.g. "Yes, the self-learning")
    assert i0 <= ia <= ib <= i1, f"linkedin span outside main range: {a!r}"
    cur, n0 = ia, len(linkedin)
    for x in removed:  # never reintroduce a duplicate that the main edit removed
        if x["ib"] < ia or x["ia"] > ib: continue
        assert x["ia"] >= ia and x["ib"] <= ib, f"dedupe span straddles linkedin span {label!r}"
        if x["ia"] > cur: linkedin += tighten(cur, x["ia"] - 1, label)
        cur = x["ib"] + 1
    linkedin += tighten(cur, ib, label)
    for iv in linkedin[n0:]: iv["label"] = label
    li_sections.append(label)
assert all(x["src_end"] <= y["src_start"] for x, y in zip(linkedin, linkedin[1:])), "linkedin spans overlap or are out of order"


# ---- X (standard accounts allow 2:20; we cap at 2:15): the sharpest distinct moments, chronological ----
X_MAX_S = 135
XSPANS = [  # (start phrase, end phrase, section)
    ("we are right now entered into", "building another ai", "Hook: AI is building AI"),
    ("i have 300 bots running", "write other bots", "300 bots, one writes the rest"),
    ("so i separated the ai skills into three", "you are not driving anymore", "Rider, driver, pilot"),
    ("instead of going to their keyboards", "observing and directing", "Stop typing, start directing"),
    ("they go out if they cant find the food in tesco", "any olives that we can eat", "A bot finds a way"),
    ("once i give you the task", "goal to be achieved", "The goal is what matters"),
    ("with a plane the risk is higher", "get certified", "Pilots need more training"),
    ("once ai does the job we either go to our corner", "learning and creating", "Closing"),
]
xcut, x_sections = [], []
for a, b, label in XSPANS:
    ia, ib = span(a, b)
    assert i0 <= ia <= ib <= i1, f"x span outside main range: {a!r}"
    cur, n0 = ia, len(xcut)
    for x in removed:  # never reintroduce a removed duplicate
        if x["ib"] < ia or x["ia"] > ib: continue
        assert x["ia"] >= ia and x["ib"] <= ib, f"dedupe span straddles x span {label!r}"
        if x["ia"] > cur: xcut += tighten(cur, x["ia"] - 1, label)
        cur = x["ib"] + 1
    xcut += tighten(cur, ib, label)
    for iv in xcut[n0:]: iv["label"] = label
    x_sections.append(label)
assert all(a["src_end"] <= b["src_start"] for a, b in zip(xcut, xcut[1:])), "x spans overlap or are out of order"


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
m_li, tot_li = build_map(linkedin)
m_x, tot_x = build_map(xcut)
assert tot_x / FPS <= X_MAX_S, f"X cut is {tot_x / FPS:.0f}s, over the {X_MAX_S}s limit"
assert tot_li / FPS <= LINKEDIN_MAX_S, f"LinkedIn cut is {tot_li / FPS:.0f}s, over the {LINKEDIN_MAX_S}s limit"

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
write_srt("data/subtitles.linkedin.srt", cue_entries(m_li, tot_li, linkedin))
write_srt("data/subtitles.x.srt", cue_entries(m_x, tot_x, xcut))
# combined: highlights first, then the full (tightened) interview
write_srt("data/subtitles.combined.srt",
          cue_entries(m_hl, tot_hl, highlights) + cue_entries(m_main, tot_main, main, offset=hl_s))
write_chapters("chapters.combined",
               [{"title": "Highlights", "start": 0.0}] + [{"title": c["title"], "start": round(c["start"] + hl_s, 2)} for c in main_chs],
               hl_s + main_s)

src_len = chapters[-1]["end"]
dedupe_s = sum(x["src_end"] - x["src_start"] for x in removed)
stats = {
    "source_s": src_len, "main_s": round(tot_main / FPS, 1), "removed_s": round(src_len - tot_main / FPS, 1),
    "duplicates_removed_s": round(dedupe_s, 1), "duplicate_cuts": len(removed),
    "main_cuts": len(main), "highlights_s": round(tot_hl / FPS, 1), "highlight_clips": len(HIGHLIGHTS),
    "highlight_intervals": len(highlights), "linkedin_s": round(tot_li / FPS, 1), "x_s": round(tot_x / FPS, 1), "x_sections": len(XSPANS), "linkedin_sections": len(LINKEDIN), "combined_s": round((tot_hl + tot_main) / FPS, 1),
}
removed_out = [{k: (round(v, 2) if isinstance(v, float) else v) for k, v in x.items() if k not in ("ia", "ib")} for x in removed]
json.dump({"stats": stats, "main": main, "highlights": highlights, "linkedin": linkedin, "x": xcut, "removed": removed_out}, open("data/cuts.json", "w"), indent=1)


# ---- TIMELINE.md: always regenerated with the cuts ----
def mmss(x):
    x = int(round(x)); return f"{x // 60:02}:{x % 60:02}"
clean = lambda s: re.sub(r"[:;#\"]", "-", s)
comb_chs = json.load(open("data/chapters.combined.json"))
lines = ["# Timeline", "",
         "Regenerated by `scripts/07_plan_cuts.py` every time the cuts change. Times are on the **Combined** output "
         f"(highlights first, then the full interview), total **{mmss((tot_hl + tot_main) / FPS)}**.", "",
         "## Overview", "", "```mermaid", "gantt", "    title Combined timeline (mm:ss)", "    dateFormat mm:ss", "    axisFormat %M:%S",
         "    section Sections"]
for i, ch in enumerate(comb_chs):
    lines.append(f"    {clean(ch['title'])} :{'done' if i == 0 else 'active' if i % 2 else 'crit'}, c{i}, {mmss(ch['start'])}, {mmss(max(ch['end'], ch['start'] + 1))}")
ex_path = "data/explainers.json"
exs = json.load(open(ex_path)) if __import__("os").path.exists(ex_path) else []
if exs:
    lines.append("    section Explainers (left panel)")
    for i, e in enumerate(exs):
        s0 = to_out(m_main, tot_main, e["start"]) + hl_s
        lines.append(f"    {clean(e['title'])} :e{i}, {mmss(s0)}, {mmss(s0 + e['dur'])}")
lines += ["```", "", "## Numbers", "", "| | seconds |", "|---|---|",
          f"| Source video | {stats['source_s']} |", f"| Main edit | {stats['main_s']} |",
          f"| Removed in total | {stats['removed_s']} |", f"| of which duplicated ideas | {stats['duplicates_removed_s']} ({len(removed)} cuts) |",
          f"| Highlights reel | {stats['highlights_s']} |", f"| Combined | {stats['combined_s']} |", "",
          "## Duplicates removed (meaning kept)", "",
          "| Source time | Length | Removed | Why | Idea kept at |", "|---|---|---|---|---|"]
for x in removed:
    txt = x["text"] if len(x["text"]) < 150 else x["text"][:70] + " ... " + x["text"][-70:]
    lines.append(f"| {mmss(x['src_start'])}-{mmss(x['src_end'])} | {x['src_end'] - x['src_start']:.0f} s | {txt} | {x['why']} | {x['kept_at']} |")
lines += ["", "## Sections", "", "| Output time | Section | Length |", "|---|---|---|"]
for ch in comb_chs:
    lines.append(f"| {mmss(ch['start'])} | {ch['title']} | {mmss(ch['end'] - ch['start'])} |")
if exs:
    lines += ["", "## Explainers", "", "| Output time | Kind | Title | Length |", "|---|---|---|---|"]
    for e in exs:
        lines.append(f"| {mmss(to_out(m_main, tot_main, e['start']) + hl_s)} | {e['kind']} | {e['title']} | {e['dur']:.0f} s |")
lines += ["", "## Highlights reel (first 52.8 s)", "", "| Output time | Source time | Why it is in |", "|---|---|---|"]
acc = 0.0
for h in highlights:
    d = h["src_end"] - h["src_start"]
    lines.append(f"| {mmss(acc)} | {mmss(h['src_start'])}-{mmss(h['src_end'])} | {h.get('label', '')} |"); acc += d
lines += ["", f"## LinkedIn version ({mmss(tot_li / FPS)}, limit 14:00)", "",
          "Own edit of the deduplicated interview: no repeated cold open, strongest sections only, captions burned in. Render: `scripts/06_render_and_embed.sh linkedin`.", "",
          "| Output time | Source time | Length | Section |", "|---|---|---|---|"]
acc = 0.0
for sec in li_sections:
    part = [iv for iv in linkedin if iv["label"] == sec]
    d = sum(iv["src_end"] - iv["src_start"] for iv in part)
    lines.append(f"| {mmss(acc)} | {mmss(part[0]['src_start'])}-{mmss(part[-1]['src_end'])} | {d:.0f} s | {sec} |"); acc += d
lines += ["", f"## X version ({mmss(tot_x / FPS)}, standard-account limit 2:20)", "",
          "Eight distinct moments in chronological order, captions burned in, closing card with the YouTube link. Render: `scripts/06_render_and_embed.sh x`.", "",
          "| Output time | Source time | Length | Section |", "|---|---|---|---|"]
acc = 0.0
for sec in x_sections:
    part = [iv for iv in xcut if iv["label"] == sec]
    d = sum(iv["src_end"] - iv["src_start"] for iv in part)
    lines.append(f"| {mmss(acc)} | {mmss(part[0]['src_start'])}-{mmss(part[-1]['src_end'])} | {d:.0f} s | {sec} |"); acc += d
lines += ["", "## Kept footage (main edit)", "", f"{len(main)} intervals; everything not listed was cut (pre-roll, long pauses, duplicates).", "",
          "| Output time | Source time | Length |", "|---|---|---|"]
acc = hl_s
for iv in main:
    d = iv["src_end"] - iv["src_start"]
    lines.append(f"| {mmss(acc)} | {mmss(iv['src_start'])}-{mmss(iv['src_end'])} | {d:.0f} s |"); acc += d
open("docs/TIMELINE.md", "w").write("\n".join(lines) + "\n")
print(json.dumps(stats, indent=1))
