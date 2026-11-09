"""Extra site pages (workflow, checklist, thumbnails) and the matching docs/*.md. Imported by 13_build_site.py.
ONE source of truth: STAGES and CHECKLIST below. Edit them as the project moves; re-run 13_build_site.py."""
import html, json
esc = html.escape

# status: done | todo ; every stage = one step of the video production workflow
STAGES = [
 ("1", "Plan and set rules", "ffprobe, git", "docs/PLAN.md, CLAUDE.md", "Claude plans; user sets rules", "done", "Probe the source (4K, 28 min), decide the pipeline, no media in git, document and push every step."),
 ("2", "Extract audio and transcribe", "ffmpeg, mlx-whisper large-v3-turbo", "transcript.raw.json", "Whisper (local, free)", "done", "16 kHz audio, word timestamps, live ETA while running (about 2 min)."),
 ("3", "Correct the transcript", "data/corrections.json", "transcript.json / .txt", "Claude + user review", "done", "17 reviewed rules (names, products); raw kept; speakers: Marianna asks, Rifat Erdem Sahin answers."),
 ("4", "Subtitles and chapters", "03_make_subtitles, 04_make_chapters", "SRT/VTT, cues, 13 chapters", "Claude segments topics", "done", "Cues from word timing (42 chars/line, 2 lines). Chapters anchored by exact phrases."),
 ("5", "Proxy and clean audio", "ffmpeg h264_videotoolbox, afftdn + gate + loudnorm", "work/proxy.mp4 (not in git)", "Code, measured", "done", "720p proxy for fast edits; dialogue cleaned (speech-to-noise gap 28 to 44 dB), -16 LUFS."),
 ("6", "Decide the cuts", "07_plan_cuts.py", "cuts.json, TIMELINE.md", "Claude picks; code enforces", "done", "Edit decision list in source time; pre/post-roll and long pauses out; 8 duplicate ideas removed (159 s) with proof-read joins."),
 ("7", "Highlights and platform cuts", "07_plan_cuts.py", "Highlights 0:53, LinkedIn 12:36, X 1:22", "Claude picks the claims", "done", "Hook-first highlights reel; a LinkedIn cut capped at 14:00; an X cut capped at 2:15 (X allows 2:20 on standard accounts) with a closing card linking to YouTube."),
 ("8", "Explainer visuals", "08_plan_explainers, 09_generate_visuals, fal.ai flux/schnell", "explainers.json, visuals/*.jpg", "Claude picks moments; fal.ai art", "done", "6 simple animated graphics (free) and 3 infographics (AI art, labels drawn in Remotion)."),
 ("9", "Sound effects and music", "14_generate_audio.py, fal.ai cassetteai models, Sound.tsx", "public/audio/*.mp3 (8 clips)", "fal.ai generates; code places every cue", "done", "5 effects (whoosh, pop, ding, buzz, impact) on chapter cards, clip changes and explainer reveals; hook music and two alternating beds about 14 dB under speech; final loudness pass."),
 ("10", "Assemble in Remotion", "Remotion compositions", "Highlights, Main, Combined, LinkedIn", "Code", "done", "Animated white/red captions, 1.22x zoom, left-side explainers, chapter cards, section-length footer."),
 ("11", "Render and package", "06_render_and_embed.sh", "out/*.mp4 (not in git)", "Code", "done", "Combined, LinkedIn and X rendered with music and effects and a final -16 LUFS pass; chapters and subtitle track muxed in (not on X). The Combined render with sound is the Skool community version. ETA shown while rendering."),
 ("12", "Thumbnails (always 3)", "10_make_thumbnail.sh, 12_generate_thumbnail_art.py", "assets/thumbnails/test1_A/B/C", "fal.ai art; text drawn in Remotion", "done", "Three different concepts for YouTube Test & Compare: number+question, imperative, no-face identity."),
 ("13", "Write the publishing copy", "11_make_publish.py, 13_build_site.py", "PUBLISH.md, site pages", "Claude drafts; Rifat approves", "done", "YouTube title/description/chapters/tags, LinkedIn (first person), X posts and thread, all with character counters."),
 ("14", "Publish and test", "YouTube Studio, LinkedIn, X", "live posts", "Human", "todo", "Upload, set the 3 thumbnails, post, replace [LINK] with the YouTube URL, pin the comment, read results."),
 ("15", "Govern", "version.py, CHANGELOG, DECISIONS, pre-commit hook", "v0.x tags, snapshots", "Code + Claude", "done", "Every step documented, versioned, committed and pushed; keys only in .env; costs tracked."),
]

SOUND = True  # flipped to True when the sound-and-music render is done
CHECKLIST = [
 ("Set up", [
  ("Probe the source video and write the plan", True), ("Install mlx-whisper (venv) and Remotion", True),
  ("Rules in place: no media in git, document each step, commit and push each step", True), ("CLAUDE.md written so every session follows the rules", True),
  ("FAL_KEY stored only in .env, pre-commit secret guard enabled", True), ("Rotate the fal.ai key (it was pasted into a chat)", False)]),
 ("Transcript and text", [
  ("Audio extracted and transcribed with word timestamps", True), ("Corrections applied (17 rules), raw transcript kept", True),
  ("Speakers recorded (Marianna asks, Rifat Erdem Sahin answers)", True), ("Check corrected names and products against the audio once", False),
  ("Subtitles (SRT/VTT) and 13 chapters generated", True)]),
 ("Edit", [
  ("Cuts decided as an edit list; timeline document generated", True), ("8 duplicated ideas removed, joins proof-read", True),
  ("Highlights reel (7 clips, 0:53)", True), ("LinkedIn cut under 14 minutes (12:36)", True),
  ("Dialogue audio cleaned, loudness -16 LUFS", True), ("Listen once to the cleaned audio (cannot be checked by ear here)", False),
  ("Zoom 1.22x, captions low, footer bigger", True)]),
 ("Visuals and sound", [
  ("6 simple animated explainers", True), ("3 fal.ai infographics (text-free art, Remotion labels)", True),
  ("Sound effects with fal.ai", SOUND), ("Music bed with fal.ai", SOUND), ("Re-render Combined and LinkedIn with sound", SOUND), ("Skool version exported: Combined with music and effects (C1193_skool_v0.15.0.mp4, 25:49)", True), ("Upload the Skool version to the Skool community", False), ("Confirm the caption \"Cambridge Sixth-form college\" (about 25:13 in the interview) against the audio: the event is at Hills Road Sixth Form College. If it is wrong, change the rule in corrections.json and re-render", False), ("Listen to the mix once: music level under speech, effects not too busy", False)]),
 ("Render", [
  ("Combined video rendered (25:49, 720p)", True), ("LinkedIn video rendered (12:36)", True), ("X video rendered (1:22, under the 2:20 limit)", True),
  ("Optional: re-render from the 4K original for a sharper final", False)]),
 ("Thumbnails", [
  ("Three different thumbnails made (A number+question, B imperative, C no-face)", True), ("Upload all three to YouTube Test & Compare", False),
  ("Let the test run, keep the winner, log the result on the Thumbnails page", False)]),
 ("Publishing copy and site", [
  ("YouTube title, description with chapters, tags, pinned comment", True), ("LinkedIn posts in first person", True),
  ("X posts and thread (each at most 280 characters)", True), ("Real Skool and Eventbrite links added", True),
  ("GitHub Pages site deployed", True), ("Costs page", True), ("Workflow, checklist and thumbnails pages", True)]),
 ("Go live", [
  ("Upload the Combined video to YouTube: https://youtu.be/VOtlOfpXVU8", True), ("X video (C1193_x, 1:22) uploaded and posted", True), ("Add the SRT and the three thumbnails (Test & Compare) to that YouTube video", False), ("Paste the new description into YouTube (host and guest links, Cambridge AI Academy event details)", False),
  ("LinkedIn post is live: https://lnkd.in/p/e5GMfT5V", True), ("Add the LinkedIn SRT to the LinkedIn video if it was not added", False), ("YouTube URL filled into the LinkedIn and X posts", True),
  ("Replace the YouTube upload with the sound-and-music version (or add it as an update)", False), ("X post is live: https://x.com/rifaterdemsahin/status/2119868364722208900", True), ("Pin the YouTube comment", False),
  ("Reply to comments in the first hour", False), ("After a week: record views, watch time and the thumbnail winner", False)]),
]

def stages_md():
    rows = "\n".join(f"| {n} | {'✅' if s == 'done' else '⬜'} | **{t}** | {tool} | {out} | {ai} | {note} |" for n, t, tool, out, ai, s, note in STAGES)
    return ("# Video production workflow\n\nGenerated by `scripts/13_build_site.py` from `scripts/site_pages.py`. Same content as the site's Workflow page.\n\n"
            "| # | | Stage | Tools | Output | AI role | What happens |\n|---|---|---|---|---|---|---|\n" + rows + "\n")

def checklist_md():
    out = ["# Checklist", "", "Generated from `scripts/site_pages.py`. The site's Checklist page has the same items with tickable boxes (saved in your browser).", ""]
    done = sum(d for _, items in CHECKLIST for _, d in items); total = sum(len(i) for _, i in CHECKLIST)
    out.append(f"**Progress: {done} of {total} done.**\n")
    for g, items in CHECKLIST:
        out.append(f"## {g}\n")
        out += [f"- [{'x' if d else ' '}] {t}" for t, d in items]; out.append("")
    return "\n".join(out)

def workflow_body():
    cards = "".join(f'<div class="card step {"ok" if s=="done" else "todo"}"><div class="row"><span class="num">{n}</span><b>{esc(t)}</b><span class="tag">{"done" if s=="done" else "to do"}</span></div>'
                    f'<p class="mut" style="margin:6px 0">{esc(note)}</p><div class="meta"><span><b>Tools</b> {esc(tool)}</span><span><b>Output</b> {esc(out)}</span><span><b>AI role</b> {esc(ai)}</span></div></div>'
                    for n, t, tool, out, ai, s, note in STAGES)
    return ('<h1>🎬 Video production workflow</h1><p class="mut">How this interview becomes a finished video, from raw footage to published posts. '
            'AI does the reading and choosing, code does the exact work, a human approves. Each step is documented, versioned, committed and pushed.</p>'
            f'{cards}<h2>Rules that apply to every stage</h2><ul><li>No video or audio in git (metadata and code only)</li><li>Keys only in <code>.env</code>, never committed</li>'
            '<li>Document the rationale for each step, then commit and push</li><li>Always create the timeline, always version, always three thumbnails</li>'
            '<li>Measure instead of guessing (audio levels, durations); proof-read every cut join</li><li>Cheap models first; cache everything; log the cost</li></ul>')

def checklist_body():
    groups = ""
    for gi, (g, items) in enumerate(CHECKLIST):
        rows = "".join(f'<label class="chk"><input type="checkbox" data-id="{gi}-{ii}" data-def="{1 if d else 0}"><span>{esc(t)}</span></label>' for ii, (t, d) in enumerate(items))
        groups += f'<div class="card"><b>{esc(g)}</b>{rows}</div>'
    return ('<h1>✅ Checklist</h1><p class="mut">One list for the whole project. Tick items as you go; your ticks are saved in this browser. '
            'The pre-ticked boxes are what is already done.</p><div class="card"><div class="row"><b id="prog_t">0 of 0 done</b><button onclick="resetChk()">Reset to project status</button></div>'
            '<div class="bar"><div id="prog_b"></div></div></div>' + groups +
            '<script>(function(){var K="dp-checklist-v1",st={};try{st=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}'
            'var bx=[].slice.call(document.querySelectorAll(".chk input"));function upd(){var d=bx.filter(function(b){return b.checked}).length;'
            'document.getElementById("prog_t").textContent=d+" of "+bx.length+" done";document.getElementById("prog_b").style.width=(100*d/bx.length)+"%"}'
            'bx.forEach(function(b){var id=b.dataset.id;b.checked=(id in st)?st[id]:b.dataset.def==="1";b.addEventListener("change",function(){st[id]=b.checked;try{localStorage.setItem(K,JSON.stringify(st))}catch(e){}upd()})});'
            'window.resetChk=function(){st={};try{localStorage.removeItem(K)}catch(e){}bx.forEach(function(b){b.checked=b.dataset.def==="1"});upd()};upd()})()</script>')

THUMBS = [
 ("A", "test1_A_300bots-1pilot", "300 Bots / 1 Pilot", "Specific number + open question, face card, red on dark", "A surprising number from the interview plus a question creates a curiosity gap."),
 ("B", "test1_B_stop-typing", "Stop Typing.", "Imperative, big face, yellow on black", "A command that interrupts a habit; a large face adds human trust."),
 ("C", "test1_C_driver-or-pilot", "Driver / Pilot: Which are you?", "No face, cyan split screen", "Self-identification (\"which am I?\") works without a face and stands out in a feed of faces."),
]
def thumbs_body():
    cards = "".join(f'<div class="card"><div class="row"><span class="num">{k}</span><b>{esc(t)}</b></div><img src="assets/thumb_{k}.jpg" alt="Thumbnail {k}"><p class="mut"><b>Look:</b> {esc(look)}<br><b>Hypothesis:</b> {esc(h)}</p>'
                    f'<a class="btn" href="assets/thumb_{k}.jpg" download>Download {k}</a></div>' for k, f, t, look, h in THUMBS)
    return ('<h1>🖼️ Thumbnails: A/B/C test</h1><p class="mut">Always three completely different thumbnails, so each one tests a different idea (not just a colour change). '
            'YouTube Studio\'s <b>Test &amp; Compare</b> accepts three.</p><div class="grid3">' + cards + '</div>'
            '<h2>How to run the test</h2><ol><li>YouTube Studio, open the video, Thumbnail, <b>Test &amp; Compare</b>, upload A, B and C</li><li>Let it run until YouTube names a winner (it optimises for watch time share)</li>'
            '<li>Keep the winner; write the result below</li><li>Next video: three new concepts, informed by what won</li></ol>'
            '<h2>Results</h2><p class="mut">Click a cell to type. Saved in this browser.</p><table id="res"><tr><th>Thumbnail</th><th>Impressions</th><th>Click-through</th><th>Watch time share</th><th>Winner?</th></tr>' +
            "".join(f'<tr><td>{k}</td>' + "".join(f'<td contenteditable data-k="{k}{c}"></td>' for c in range(4)) + '</tr>' for k, *_ in THUMBS) + '</table>'
            '<script>(function(){var K="dp-thumb-results",s={};try{s=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}[].slice.call(document.querySelectorAll("#res td[data-k]")).forEach(function(c){c.textContent=s[c.dataset.k]||"";c.addEventListener("input",function(){s[c.dataset.k]=c.textContent;try{localStorage.setItem(K,JSON.stringify(s))}catch(e){}})})})()</script>')

EXTRA_CSS = """
.step.todo{border-left:5px solid #f0b429}.step.ok{border-left:5px solid #1f9d55}.num{display:inline-flex;width:28px;height:28px;border-radius:50%;background:var(--red);color:#fff;align-items:center;justify-content:center;font-weight:800;font-size:14px}
.meta{display:flex;gap:14px;flex-wrap:wrap;font-size:13px;color:var(--mut)}.meta b{color:var(--fg)}
.chk{display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-top:1px solid var(--line);cursor:pointer}.chk input{width:20px;height:20px;margin-top:2px;accent-color:#ff2b2b}
.bar{height:12px;background:var(--line);border-radius:99px;overflow:hidden;margin-top:10px}.bar div{height:100%;background:#1f9d55;width:0;transition:width .25s}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}td[contenteditable]{min-width:70px;background:var(--bg)}
"""
