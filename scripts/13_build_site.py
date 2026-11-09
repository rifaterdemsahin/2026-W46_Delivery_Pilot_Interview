#!/usr/bin/env python3
"""Build the GitHub Pages site into site/ (static, no build step on GitHub): overview, costs, and copy-and-publish
pages for YouTube, LinkedIn and X. Content comes from data/ and docs/, so it never drifts from the project.
Deployed by .github/workflows/static.yml (uploads site/). Run after any change: .venv/bin/python -I scripts/13_build_site.py"""
import html, json, os, re, shutil

VERSION = open("VERSION").read().strip()
REPO = "https://github.com/rifaterdemsahin/2026-W46_Delivery_Pilot_Interview"
SITE_URL = "https://rifaterdemsahin.github.io/2026-W46_Delivery_Pilot_Interview/"
cuts = json.load(open("data/cuts.json"))["stats"]
desc = open("data/description.txt").read().strip()
chs = json.load(open("data/chapters.combined.json"))
manifest = json.load(open("data/visuals_manifest.json"))
mmss = lambda s: f"{int(s)//60}:{int(s)%60:02d}"
esc = html.escape
TOTAL = mmss(round(cuts["combined_s"]))

os.makedirs("site/assets", exist_ok=True)
for src, dst in [("assets/thumbnail.jpg", "thumbnail.jpg"), ("assets/thumbnails/v1-generic-become-a-delivery-pilot.jpg", "thumbnail_v1.jpg"),
                 ("assets/thumbnails/v2-curiosity-300-bots-1-pilot.jpg", "thumbnail_v2.jpg"), ("data/subtitles.combined.srt", "subtitles.srt"),
                 ("data/description.txt", "description.txt")]:
    shutil.copy(src, f"site/assets/{dst}")
open("site/.nojekyll", "w").write("")

CSS = """:root{--bg:#fff;--fg:#111827;--mut:#5b6472;--card:#f5f6f8;--line:#e3e6ea;--red:#ff2b2b}
@media (prefers-color-scheme:dark){:root{--bg:#0e1116;--fg:#eef0f3;--mut:#9aa4b2;--card:#171b22;--line:#262c36}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif}
header{border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:5}
nav{max-width:920px;margin:0 auto;padding:10px 16px;display:flex;gap:6px;flex-wrap:wrap;align-items:center}
nav b{margin-right:auto}nav a{color:var(--fg);text-decoration:none;padding:6px 10px;border-radius:8px;font-size:15px}
nav a:hover,nav a.on{background:var(--card)}nav a.on{border-bottom:2px solid var(--red)}
main{max-width:920px;margin:0 auto;padding:20px 16px 60px}h1{font-size:30px;line-height:1.2;margin:.2em 0}h2{margin-top:1.8em;font-size:21px}
.mut{color:var(--mut)}.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:12px 0}
img{max-width:100%;border-radius:10px}table{border-collapse:collapse;width:100%;font-size:15px}th,td{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}
textarea{width:100%;min-height:120px;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:10px;font:14px/1.5 ui-monospace,Menlo,monospace;resize:vertical}
button,.btn{background:var(--red);color:#fff;border:0;border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block;font-size:14px}
button.ok{background:#1f9d55}.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:6px 0}.cnt{font-size:13px;color:var(--mut)}.cnt.bad{color:var(--red);font-weight:700}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}.k{font-size:28px;font-weight:800}.tag{display:inline-block;background:var(--card);border:1px solid var(--line);border-radius:99px;padding:2px 10px;font-size:13px;margin:2px}
"""
JS = """function copyFrom(id,btn){var t=document.getElementById(id);t.select();var v=t.value;
 (navigator.clipboard?navigator.clipboard.writeText(v):Promise.reject()).catch(function(){document.execCommand('copy')}).then(function(){btn.textContent='Copied';btn.className='ok';setTimeout(function(){btn.textContent='Copy';btn.className=''},1600)})}
function count(id,out,limit){var t=document.getElementById(id),o=document.getElementById(out);function u(){var n=t.value.replace(/\\[LINK\\]/g,'x'.repeat(23)).length;o.textContent=n+(limit?' / '+limit:'')+' characters';o.className='cnt'+(limit&&n>limit?' bad':'')}t.addEventListener('input',u);u()}"""
open("site/style.css", "w").write(CSS); open("site/copy.js", "w").write(JS)

PAGES = [("index.html", "Overview"), ("youtube.html", "YouTube"), ("linkedin.html", "LinkedIn"), ("x.html", "X"), ("costs.html", "Costs")]
def page(fn, title, body):
    nav = "".join(f'<a href="{f}"{" class=on" if f == fn else ""}>{n}</a>' for f, n in PAGES)
    open(f"site/{fn}", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} - Delivery Pilot</title><meta name="description" content="Publishing kit for the Delivery Pilot interview: copy, costs and assets."><link rel="stylesheet" href="style.css"><script src="copy.js" defer></script></head>
<body><header><nav><b>🎬 Delivery Pilot</b>{nav}<a href="{REPO}">Repo ↗</a></nav></header><main>{body}
<p class="mut" style="margin-top:40px">v{VERSION} · built from the project data by <code>scripts/13_build_site.py</code> · <a href="{REPO}">source</a></p></main></body></html>""")

def box(id, text, rows=8, limit=None, label=""):
    c = f'<span class="cnt" id="{id}_n"></span>'
    js = f'<script>window.addEventListener("DOMContentLoaded",function(){{count("{id}","{id}_n",{limit or "null"})}})</script>'
    return f'<div class="card"><div class="row"><b>{esc(label)}</b><button onclick="copyFrom(\'{id}\',this)">Copy</button>{c}</div><textarea id="{id}" rows="{rows}" readonly>{esc(text)}</textarea></div>{js}'

# ---------- index ----------
page("index.html", "Overview", f"""
<h1>Become a Delivery Pilot: the AI interview kit</h1>
<p class="mut">Rifat Erdem Sahin in conversation with Marianna. Everything below was produced by an AI-assisted pipeline: Whisper transcript, AI-chosen chapters and cuts, Remotion edit, fal.ai visuals.</p>
<img src="assets/thumbnail.jpg" alt="Thumbnail: 300 bots, 1 pilot">
<div class="grid" style="margin-top:14px">
 <div class="card"><div class="k">{TOTAL}</div><span class="mut">final video (Combined)</span></div>
 <div class="card"><div class="k">{len(chs)}</div><span class="mut">chapters incl. highlights</span></div>
 <div class="card"><div class="k">{cuts['duplicates_removed_s']:.0f} s</div><span class="mut">duplicated ideas removed</span></div>
 <div class="card"><div class="k">v{VERSION}</div><span class="mut">project version</span></div>
</div>
<h2>Copy and publish</h2>
<div class="grid">
 <a class="card" href="youtube.html"><b>▶️ YouTube</b><br><span class="mut">title, description, chapters, tags, thumbnail</span></a>
 <a class="card" href="linkedin.html"><b>💼 LinkedIn</b><br><span class="mut">long and short post</span></a>
 <a class="card" href="x.html"><b>✖️ X</b><br><span class="mut">single posts and a thread</span></a>
 <a class="card" href="costs.html"><b>💸 Costs</b><br><span class="mut">what this cost, and how</span></a>
</div>
<h2>Downloads</h2>
<p><a class="btn" href="assets/thumbnail.jpg" download>Thumbnail</a> <a class="btn" href="assets/subtitles.srt" download>Subtitles (.srt)</a> <a class="btn" href="assets/description.txt" download>Description (.txt)</a></p>
<h2>Thumbnail versions</h2>
<div class="grid"><div><img src="assets/thumbnail_v1.jpg" alt="v1"><div class="mut">v1 generic</div></div><div><img src="assets/thumbnail_v2.jpg" alt="v2"><div class="mut">v2 curiosity (current)</div></div></div>
<h2>Chapters</h2>
<table>{"".join(f"<tr><td>{mmss(c['start'])}</td><td>{esc(c['title'])}</td></tr>" for c in chs)}</table>
<h2>Project</h2>
<p><a href="{REPO}">Repository</a> · <a href="{REPO}/blob/main/docs/TIMELINE.md">Timeline</a> · <a href="{REPO}/blob/main/docs/DECISIONS.md">Decisions</a> · <a href="{REPO}/blob/main/CHANGELOG.md">Changelog</a> · <a href="{REPO}/blob/main/README.md">README and flow diagram</a></p>""")

# ---------- youtube ----------
title = re.search(r"TITLE = \"(.+?)\"", open("scripts/11_make_publish.py").read()).group(1)
alts = re.findall(r'^\s+"(.+?)",?$', re.search(r"ALT_TITLES = \[(.*?)\]", open("scripts/11_make_publish.py").read(), re.S).group(1), re.M)
tags = re.search(r"TAGS = \[(.*?)\]", open("scripts/11_make_publish.py").read(), re.S).group(1)
tags = ", ".join(re.findall(r'"(.+?)"', tags))
pinned = re.search(r'PINNED = "(.+?)"', open("scripts/11_make_publish.py").read()).group(1)
page("youtube.html", "YouTube", f"""<h1>▶️ YouTube</h1><p class="mut">Copy each block into YouTube Studio. Video length {TOTAL}.</p>
<img src="assets/thumbnail.jpg" alt="thumbnail" style="max-width:480px"><p><a class="btn" href="assets/thumbnail.jpg" download>Download thumbnail (1280x720)</a></p>
{box("yt_title", title, 2, 100, "Title (limit 100)")}
<div class="card"><b>Alternative titles</b><ul>{"".join(f"<li>{esc(a)}</li>" for a in alts)}</ul></div>
{box("yt_desc", desc, 22, 5000, "Description (chapters included, first at 0:00)")}
{box("yt_tags", tags, 3, 500, "Tags")}
{box("yt_pin", pinned, 2, None, "Pinned comment")}
<div class="card"><b>Checklist</b><ul><li>Upload <code>C1193_combined</code> render, set the thumbnail</li><li>Add the subtitles: <a href="assets/subtitles.srt" download>subtitles.srt</a> (English)</li>
<li>Links to the Skool community and the Eventbrite event are already in the description</li><li>Category: Science and Technology · Language: English · Not made for kids</li><li>Chapters appear automatically from the description</li></ul></div>""")

# ---------- linkedin ----------
LONG = """I just watched a conversation that reframed how I think about AI at work.

Rifat Erdem Sahin says we are moving from riders (chatting with AI), to drivers (building with tools like Claude Code), to pilots: people who direct many AI bots and make sure the direction is right.

His own example: 300 bots running at once, and one bot that writes the other bots. The job is less about writing every line and more about observing, directing and being accountable.

Three ideas I'm taking away:

→ Pilots need MORE training, not less. More power means more responsibility.
→ A bot is not the same as an agent. Agents stay inside their sandbox; bots chase the goal. No olives at Tesco? Try Sainsbury's. Still none? Knock on a neighbour's door.
→ Continuous integration has become possible with AI. Continuous delivery is the next step, and that is where the "Delivery Pilot" comes in.

The full conversation with Marianna is 25 minutes: [LINK]

Join the free Skool community: https://www.skool.com/delivery-pilot-8938
Build your own AI agents in Cambridge: https://www.eventbrite.co.uk/e/cambridge-ai-academy-build-your-own-ai-agents-tickets-2003566080080

Are you a rider, a driver or a pilot today?

#AI #AIAgents #FutureOfWork #ClaudeCode #ContinuousDelivery"""
SHORT = """300 bots. 1 pilot.

Rifat Erdem Sahin on why we are moving from riders, to drivers, to pilots of AI, and why pilots need more training, not less.

25-minute conversation with Marianna: [LINK]

Rider, driver or pilot: where are you today?

#AI #AIAgents #FutureOfWork"""
page("linkedin.html", "LinkedIn", f"""<h1>💼 LinkedIn</h1><p class="mut">Post natively on LinkedIn; add the YouTube link where it says <code>[LINK]</code> (put it in the first comment instead if you want more reach). Use the thumbnail as the image.</p>
<p><a class="btn" href="assets/thumbnail.jpg" download>Download image</a></p>
{box("li_long", LONG, 24, 3000, "Long post (limit 3,000)")}
{box("li_short", SHORT, 9, 3000, "Short post")}
<div class="card"><b>Tips</b><ul><li>First two lines are what shows before "see more": keep the hook there</li><li>Tag Marianna and Rifat Erdem Sahin if they agree</li><li>Reply to every comment in the first hour</li></ul></div>""")

# ---------- x ----------
SINGLES = [
 "300 bots. 1 pilot.\n\nRifat Erdem Sahin on why we're moving from riders to drivers to pilots of AI, and why pilots need MORE training, not less.\n\n25 min: [LINK]",
 "AI is building AI. So what's left for people?\n\nDirect it. Observe it. Stay accountable for it.\n\nThe Delivery Pilot idea in 25 minutes: [LINK]",
 "A chatbot answers. An agent works inside its sandbox. A bot chases the goal.\n\nNo olives at Tesco? Try Sainsbury's. Still none? Knock on a neighbour's door.\n\n[LINK]",
]
THREAD = [
 "300 bots. 1 pilot. 🧵\n\nI listened to Rifat Erdem Sahin explain why we're moving from riders to drivers to pilots of AI. Here's what stuck with me:",
 "1/ Rider: you chat with AI and do everything by hand.\nDriver: you build with tools like Claude Code.\nPilot: you direct many bots and make sure the direction is right.",
 "2/ His example: 300 bots running at once, and one bot that writes the other bots.\n\nThe human job shifts from typing to observing and directing.",
 "3/ Agent vs bot: agents stay in their sandbox. Bots chase the goal and find another way.\n\nNo olives at Tesco? Sainsbury's. Still none? Knock on a neighbour's door.",
 "4/ The counter-intuitive part: pilots need MORE training, not less.\n\nMore power, more responsibility. 300 bots is more dangerous than 1.",
 "5/ CI became possible with AI. Continuous delivery is next. That's the Delivery Pilot.\n\nFull conversation with Marianna (25 min): [LINK]\n\nRider, driver or pilot: where are you today?",
]
for t in SINGLES + THREAD:
    assert len(t.replace("[LINK]", "x" * 23)) <= 280, f"too long ({len(t)}): {t[:40]}"
x_html = "".join(box(f"x_s{i}", t, 5, 280, f"Post {i+1}") for i, t in enumerate(SINGLES))
t_html = "".join(box(f"x_t{i}", t, 5, 280, f"Thread {i+1}/{len(THREAD)}") for i, t in enumerate(THREAD))
page("x.html", "X", f"""<h1>✖️ X</h1><p class="mut">Each post is checked to fit 280 characters (a link counts as 23). Attach the thumbnail to the first post. Replace <code>[LINK]</code> with the YouTube URL.</p>
<p><a class="btn" href="assets/thumbnail.jpg" download>Download image</a></p>
<h2>Single posts (pick one)</h2>{x_html}<h2>Thread</h2>{t_html}""")

# ---------- costs ----------
size = lambda k: (manifest[k].get("width") or (1024 if "thumb_art" in k else 1024), manifest[k].get("height") or (576 if "thumb_art" in k else 768))
mp = lambda k: size(k)[0] * size(k)[1] / 1e6
PRICE = 0.003
rows = []
fal = 0.0
for k, v in manifest.items():
    c = v["est_cost_usd"]; fal += c; rows.append((k, v["model"], "%dx%d" % size(k), f"${c:.4f}"))
discarded = mp("agent_bot_robot") * PRICE  # first agent/bot/robot image had garbled text and was regenerated
fal += discarded
rows.append(("agent_bot_robot (first try, discarded: garbled text)", "fal-ai/flux/schnell", "1024x768", f"${discarded:.4f}"))
page("costs.html", "Costs", f"""<h1>💸 Costs</h1>
<p class="mut">What producing this video cost. fal.ai amounts are <b>estimates</b> from the published list price (about $0.003 per megapixel for <code>flux/schnell</code>): check your fal.ai dashboard for exact billing.</p>
<div class="grid"><div class="card"><div class="k">${fal:.3f}</div><span class="mut">fal.ai images (est.)</span></div>
<div class="card"><div class="k">$0</div><span class="mut">local compute and hosting</span></div>
<div class="card"><div class="k">{len(manifest)+1}</div><span class="mut">images generated</span></div></div>
<h2>fal.ai images</h2>
<table><tr><th>Image</th><th>Model</th><th>Size</th><th>Est. cost</th></tr>{"".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{c}</td><td>{d}</td></tr>" for a,b,c,d in rows)}
<tr><td><b>Total</b></td><td></td><td></td><td><b>${fal:.4f}</b></td></tr></table>
<h2>Everything else</h2>
<table><tr><th>Item</th><th>Cost</th><th>Notes</th></tr>
<tr><td>Transcription (Whisper large-v3-turbo, MLX)</td><td>$0</td><td>Runs locally on Apple Silicon, about 2 minutes</td></tr>
<tr><td>720p proxy, audio cleanup, renders (Remotion + ffmpeg)</td><td>$0</td><td>Local: proxy 10 min, Combined render 14 min</td></tr>
<tr><td>Hosting (GitHub Pages) and repo</td><td>$0</td><td>Free for public repositories</td></tr>
<tr><td>Claude Code (planning, code, copy, chapters, cuts)</td><td>not measured</td><td>Billed through your Claude plan; see your usage page</td></tr>
<tr><td>Sound effects and music (fal.ai)</td><td>planned</td><td>Not generated yet; will be added here when done</td></tr></table>
<h2>How costs are kept low</h2><ul><li>Cheapest suitable model (4-step <code>flux/schnell</code>), one image per idea</li><li>Images are cached: re-running never pays twice (<code>--force --only</code> to redo one)</li>
<li>Text-free art, words drawn in Remotion, so fewer regenerations</li><li>Everything heavy (transcription, rendering) runs locally for free</li><li>Cost logged per image in <code>data/visuals_manifest.json</code></li></ul>""")
print("built site/:", ", ".join(sorted(os.listdir("site"))))
