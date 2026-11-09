#!/usr/bin/env python3
"""Plan explainer visuals shown on the LEFT of the frame while a concept is being explained.
Claude chose the moments by reading the transcript; each is anchored to start/end phrases
(word level, asserted unique) so timing follows the transcript. Output: data/explainers.json.

kind = simple graphic (animated natively in Remotion, free):  flow | tree | network | stat | card
kind = infographic (complex idea): fal.ai generates TEXT-FREE art with a cheap model; the labels are
         overlaid by Remotion so text is always crisp and correct (see scripts/09_generate_visuals.py).
"""
import json, re

FPS = 25
t = json.load(open("data/transcript.json"))
words = [w for s in t["segments"] for w in s["words"]]
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
toks = [norm(w["w"]) for w in words]
real = [i for i, x in enumerate(toks) if x]  # skip punctuation-only tokens such as "%"
ftoks = [toks[i] for i in real]
snap = lambda x: round(x * FPS) / FPS

STYLE = "flat vector infographic illustration, clean minimal style, white background, navy and red accent colors, soft shapes, no text, no letters, no words"

BEATS = [
  dict(id="ci_cd", kind="flow", title="From CI to CD",
       start="we came to an age with the rise", end="brings me to my childhood",
       data=dict(nodes=[dict(label="Code", sub="write"), dict(label="Continuous Integration", sub="possible now with AI", state="done"),
                        dict(label="Continuous Delivery", sub="the next step", state="next"), dict(label="Delivery Pilot", sub="the new role", state="ok")])),
  dict(id="bots_build_bots", kind="tree", title="Bots build bots",
       start="i have 300 bots running", end="write other bots",
       data=dict(root="1 bot", count=300, caption="I write one bot to write other bots")),
  dict(id="levels", kind="infographic", title="Rider, Driver, Pilot",
       start="i separated the ai skills into three", end="observing and directing",
       prompt=f"{STYLE}, three stages of progress shown as a rising path from a horse rider to a car driver to an airplane pilot",
       data=dict(items=[dict(label="Rider", sub="web chat, hands-on"), dict(label="Driver", sub="Claude Code builds things"),
                        dict(label="Pilot", sub="observes and directs bots")])),
  dict(id="agent_network", kind="network", title="Agent to agent",
       start="something called agent to agent communication", end="campaign in the budget",
       data=dict(nodes=["Campaign bot", "Finance bot", "Capacity bot"], caption="Bots talking to bots")),
  dict(id="agent_bot_robot", kind="infographic", title="Agent vs Bot vs Robot",
       start="the agent and the bot are very similar", end="bots are more probabilistic",
       prompt=f"{STYLE}, three pictograms side by side: a small figure standing inside a closed box, a glowing cloud floating freely, and a tall humanoid robot, wordless icon illustration",
       data=dict(items=[dict(label="Agent", sub="less autonomy, stays in its sandbox"), dict(label="Bot", sub="digital world, no body, goal-driven"),
                        dict(label="Robot", sub="real world, has a body")])),
  dict(id="grocery_fallback", kind="flow", title="A bot finds a way",
       start="they go out if they cant find the food in tesco", end="any olives that we can eat",
       data=dict(nodes=[dict(label="Tesco", sub="out of stock", state="fail"), dict(label="Sainsbury's", sub="out of stock", state="fail"),
                        dict(label="Knock on Maria's door", sub="olives!", state="ok")])),
  dict(id="desk_jobs", kind="stat", title="Desk-based jobs",
       start="right now most 20 30 of the world", end="desk based job",
       data=dict(value="20-30%", caption="of the world does a desk-based job")),
  dict(id="pilot_traits", kind="infographic", title="What a pilot needs",
       start="the pilots needs to be creative", end="create and operate all day long",
       prompt=f"{STYLE}, airplane cockpit view with glowing icons of a lightbulb, a gear, a blueprint and a compass",
       data=dict(items=[dict(label="Creative"), dict(label="Operative"), dict(label="Builder"), dict(label="Architect"), dict(label="Strategist")])),
  dict(id="workshops", kind="card", title="Join the workshops",
       start="we are doing the eventbrite workshops", end="what we implemented that week",
       data=dict(bullets=["Eventbrite workshops in Cambridge", "Free weekly session on Skool, Sundays 1:30", "Showcase, one topic, gratitude, what we learned"])),
]

def find(phrase, after=0):
    p = [x for x in map(norm, phrase.split()) if x]
    fa = next((k for k, i in enumerate(real) if i >= after), len(real))
    return [real[k] for k in range(fa, len(ftoks) - len(p) + 1) if ftoks[k:k + len(p)] == p], len(p)

out = []
for b in BEATS:
    ha, _ = find(b["start"])
    assert len(ha) == 1, f"{b['id']}: start {b['start']!r} matched {len(ha)}"
    hb, lb = find(b["end"], ha[0])
    assert hb, f"{b['id']}: end phrase not found"
    last = real[real.index(hb[0]) + lb - 1]
    start, end = snap(words[ha[0]]["start"]), snap(words[last]["end"] + 0.4)
    beat = {k: b[k] for k in ("id", "kind", "title", "data")}
    beat.update(start=start, end=end, dur=round(end - start, 2))
    if b["kind"] == "infographic":
        beat.update(prompt=b["prompt"], image=f"visuals/{b['id']}.jpg")
    out.append(beat)
    print(f"{b['id']:<17}{b['kind']:<12}{int(start//60)}:{int(start%60):02}  {beat['dur']:>5}s")
json.dump(out, open("data/explainers.json", "w"), indent=1, ensure_ascii=False)
