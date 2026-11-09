#!/usr/bin/env python3
"""Chapters. Topic boundaries/titles/summaries were written by Claude after reading
the full transcript (AI semantic segmentation). Each chapter is anchored to a unique
phrase; the start time is snapped to the matching transcript segment so timings stay
exact. Outputs: chapters.json, ffmetadata (for ffmpeg mux), YouTube-style timestamps."""
import json

CHAPTERS = [  # (anchor phrase or None for t=0, title, summary)
    (None, "Introduction", "Marianna opens the conversation with Rifat Erdem Sahin on technology, AI, progress and human evolution."),
    ("So the reality is I'm passionate", "Why a Delivery Pilot?", "A childhood dream of flying meets continuous integration and continuous delivery."),
    ("Can you help us to understand the history", "40 Years of Technology: From Atari to AI", "Early computers in 1985, learning languages to talk to machines, and how AI removes that barrier."),
    ("it seems that today we don't need programmers", "From Rider to Driver to Pilot", "Why we still need a pilot in the cockpit, and bots building other bots."),
    ("you jumped already to bots", "The Three Levels of AI Skills", "Rider (web chat), driver (Claude Code), pilot (observing and directing bots)."),
    ("the journey this technology", "The Journey to Pilot Level", "From prompting to frontier models to bots, digital twins and agent-to-agent communication."),
    ("let's come back a little bit", "Chatbots, Agents and Bots Explained", "Development vs operations, probabilistic bots, grocery and visa examples."),
    ("Let's talk a little bit about coding", "Do We Still Need to Learn Coding?", "Abstracted languages, fewer screens, bureaucracy, and why pilots need more training."),
    ("why continuous", "Continuous Learning and Adult Education", "Why learning never stops and adult education is set to rise."),
    ("I know that you like to learn a lot", "Teaching, Gatekeepers and the Future of Work", "Sharing knowledge, desk jobs changing, becoming directors of bots, beyond single majors."),
    ("mind digestion", "Adapting the Mind and Self-Learning", "Living with AI, self-learners, and the creative, operative pilot."),
    ("workshop that you are running", "Cambridge Workshops and the Skool Community", "Eventbrite sessions, weekly meetups, requirements, and pricing."),
    ("AI isn't for me", "\"AI Isn't for Me\" and the Bigger Picture", "The Amish comparison and AI investment surpassing past industrial revolutions."),
]

t = json.load(open("data/transcript.json"))
segs = t["segments"]
END = 1693.44  # media duration from ffprobe

out, prev = [], -1
for anchor, title, summary in CHAPTERS:
    if anchor is None:
        start = 0.0
    else:
        hits = [s for s in segs if anchor.lower() in s["text"].lower()]
        assert len(hits) == 1, f"anchor {anchor!r} matched {len(hits)} segments"
        start = hits[0]["start"]
    assert start > prev, f"chapter {title!r} out of order"
    prev = start
    out.append({"title": title, "start": start, "summary": summary})
for i, c in enumerate(out):
    c["end"] = out[i + 1]["start"] if i + 1 < len(out) else END

json.dump(out, open("data/chapters.json", "w"), indent=1, ensure_ascii=False)

with open("data/chapters.ffmetadata", "w") as f:
    f.write(";FFMETADATA1\n")
    for c in out:
        f.write(f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(c['start']*1000)}\nEND={round(c['end']*1000)}\ntitle={c['title']}\n")

def hms(x):
    m, s = divmod(int(x), 60); h, m = divmod(m, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"
with open("data/chapters.youtube.txt", "w") as f:
    f.write("\n".join(f"{hms(c['start'])} {c['title']}" for c in out) + "\n")
print(open("data/chapters.youtube.txt").read())
