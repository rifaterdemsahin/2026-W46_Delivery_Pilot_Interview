#!/usr/bin/env python3
"""Apply data/corrections.json to the raw Whisper transcript.
data/transcript.raw.json (untouched Whisper output) -> data/transcript.json (+ transcript.txt).
Matching is case-insensitive on word tokens, within a segment. Trailing punctuation and an
initial capital are preserved. Word timings are kept (1:1 when the word count is equal, otherwise
the span is split evenly). Prints how many times each rule fired, so a 0 is visible."""
import json, re

raw = json.load(open("data/transcript.raw.json"))
rules = json.load(open("data/corrections.json"))
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
counts, skipped = {}, {}

def apply(rule, seg, active):
    n = 0
    ws = seg["words"]
    for phrase in rule["find"]:
        p = [norm(x) for x in phrase.split()]
        i = 0
        while i <= len(ws) - len(p):
            if [norm(w["w"]) for w in ws[i:i + len(p)]] == p:
                n += 1
                if active:
                    old = ws[i:i + len(p)]
                    tail = re.search(r"[^\w]+$", old[-1]["w"])
                    new = rule["replace"].split()
                    if old[0]["w"][:1].isupper() and new[0][:1].islower():
                        new[0] = new[0][:1].upper() + new[0][1:]
                    if tail and not new[-1].endswith(tail.group()):
                        new[-1] += tail.group()
                    s, e = old[0]["start"], old[-1]["end"]
                    if len(new) == len(old):
                        rep = [dict(w=nw, start=o["start"], end=o["end"]) for nw, o in zip(new, old)]
                    else:
                        step = (e - s) / len(new)
                        rep = [dict(w=nw, start=round(s + k * step, 2), end=round(s + (k + 1) * step, 2))
                               for k, nw in enumerate(new)]
                    ws[i:i + len(p)] = rep
                    seg["_dirty"] = True
                    i += len(rep)
                    continue
            i += 1
    return n

for rule in rules:
    total = 0
    for seg in raw["segments"]:
        total += apply(rule, seg, rule["active"])
    (counts if rule["active"] else skipped)[rule["id"]] = (rule["find"][0], rule["replace"], total)

for seg in raw["segments"]:
    if seg.pop("_dirty", False):
        txt = ""
        for w in seg["words"]:  # no space before tokens that start with punctuation (e.g. ".30")
            txt += w["w"] if (not txt or re.match(r"[.,!?;:%)]", w["w"])) else " " + w["w"]
        seg["text"] = txt
raw["text"] = " ".join(s["text"] for s in raw["segments"])
json.dump(raw, open("data/transcript.json", "w"), ensure_ascii=False, indent=1)
with open("data/transcript.txt", "w") as f:
    for s in raw["segments"]:
        f.write(f"[{int(s['start']//60):02}:{int(s['start']%60):02}] {s['text']}\n")

print("APPLIED"); [print(f"  #{k:<3} {a!r} -> {b!r}: {n}x") for k, (a, b, n) in counts.items()]
print("SKIPPED (inactive, matches found but NOT changed)"); [print(f"  #{k:<3} {a!r} -> {b!r}: {n} match(es)") for k, (a, b, n) in skipped.items()]
