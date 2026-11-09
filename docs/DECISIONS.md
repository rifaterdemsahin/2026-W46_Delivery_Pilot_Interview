# Decisions log

## 1. Project setup and plan (2026-11-09)
- **Decision:** keep all media out of git and use the repo for metadata and processing code.
- **Why:** the source is 20.9 GB. Git would be unusable, and GitHub rejects files over 100 MB.
- **Decision:** transcribe from extracted 16 kHz audio, edit on a 720p proxy.
- **Why:** 4K decode dominates time and memory for no benefit when only speech or a preview is needed.

## 2. Library installation (2026-11-09)
- **Machine:** Apple Silicon (arm64), Node 26, Python 3.15, ffmpeg already installed via Homebrew.
- **Transcription:** `mlx-whisper` in a project-local `.venv` (pinned subset in `requirements.txt`).
  - **Why:** it runs Whisper on the Apple GPU through MLX, which is much faster than CPU `openai-whisper` on a Mac. It is free and local, so audio never leaves the machine. The global `whisper` CLI was not used so the project stays reproducible.
- **Editing:** `remotion`, `@remotion/cli`, `@remotion/captions`, `react`, `react-dom` (Remotion 4.0.542) via npm.
  - **Why:** `@remotion/captions` provides caption types and SRT parsing, which fits the subtitle step.
- **Not installed yet:** Whisper model weights. They download on the first transcription run (step 4) so this step stays light.

## 3. Audio extraction (2026-11-09)
- `scripts/01_extract_audio.sh`: `-map 0:a:0 -vn -ac 1 -ar 16000 -c:a pcm_s16le`.
- **Why:** the file has 3 streams (video, PCM audio, a data stream). Mapping only the first audio stream avoids the data stream. Result: 52 MB WAV in about 2 s, full 28:13 duration.

## 4. Transcription (2026-11-09)
- `scripts/02_transcribe.py`: `whisper-large-v3-turbo` (MLX), `language="en"`, `word_timestamps=True`, `condition_on_previous_text=False`.
- **Why:** turbo is near large-v3 accuracy at much higher speed. Disabling previous-text conditioning avoids the hallucinated repetition loops Whisper can fall into on long audio.
- **Result:** 283 segments, 4,494 words, about 2 min (plus a one-off 65 s model download).
- **Validation:** last segment ends at 1691.66 s (audio is 1693.4 s), no segment text repeated more than twice, no gap over 20 s.
- **Known caveat:** the opening segment "More, more." is room noise before the interview starts. Chapters/subtitles may trim it. Proper names (e.g. the interviewee's name) may need manual correction.
- `data/transcript.json` is committed (metadata, small). The audio is not.

## 5. Subtitles (2026-11-09)
- `scripts/03_make_subtitles.py` builds cues from **word** timestamps, not Whisper segments.
- **Why:** Whisper segments vary from 1 to 20+ s, too long to read. Word timing lets us enforce readability: max 2 lines of 42 chars, 76 chars per cue, 5.5 s per cue, break on sentence ends, pauses over 0.6 s, or gaps over 1.2 s. End times are clamped so cues never overlap.
- **Result:** 408 cues, none over 6.5 s, none under 0.5 s, 2 lines marginally over 42 chars. SRT for players and Remotion, VTT for web.
- **Tuning note:** the first pass (84 chars / 6 s) gave 7 long cues and 13 long lines, so limits were tightened.

## 6. Proxy (2026-11-09)
- `scripts/05_make_proxy.sh`: 1280x720, 25 fps, `h264_videotoolbox` 4 Mbit/s, AAC stereo, faststart.
- **Why:** hardware encoding is several times faster than libx264 for a 4K source, and a 720p file previews smoothly in Remotion Studio.

## 7. Chapters (2026-11-09)
- **Method:** Claude read the whole timestamped transcript and chose 13 topic boundaries, titles and one-line summaries. These are encoded in `scripts/04_make_chapters.py`.
- **Why not a pure algorithm:** topic-shift detection by embeddings is noisy on a conversational interview, and an LLM read gives human-quality titles. No external API call is needed, so there is no key or cost.
- **Why anchors, not hard-coded times:** each chapter is tied to a unique phrase and snapped to that segment's start. If the transcript is re-run, times follow. The script asserts each anchor matches exactly one segment and that order is increasing.
- **Outputs:** `chapters.json` (Remotion), `chapters.ffmetadata` (ffmpeg MP4 chapter atoms), `chapters.youtube.txt` (description paste).
- **Review needed:** boundaries are my judgement, so please skim `data/chapters.youtube.txt`. The 28:05 closing thanks is folded into the last chapter.

## 8. Remotion setup (2026-11-09)
- Composition `Main`: 1280x720 @ 25 fps, 42,336 frames, matching the proxy so there is no resampling.
- Layers: `OffthreadVideo` (proxy) -> `ChapterCard` (5 s lower-third at each chapter start) -> `Subtitles` (burned-in, 38 px, dark box for contrast on any background) -> `ProgressBar` (with white chapter ticks).
- **Captions as JSON:** `scripts/03_make_subtitles.py` also writes `data/captions.json` in `@remotion/captions` format, so the composition needs no runtime SRT parsing or delayRender fetch.
- **Media access:** `public/proxy.mp4` is a symlink to `work/proxy.mp4`. Both are git-ignored, so no video ever enters the repo.
- **Delivery:** `scripts/06_render_and_embed.sh` renders, then ffmpeg stream-copies and adds native MP4 chapters (from `chapters.ffmetadata`) and a toggleable `mov_text` subtitle track. Burned-in captions suit social platforms; the soft track suits players.

## 9. Transcript saved + ETA (2026-11-09)
- `data/transcript.json` (word timings) and `data/transcript.txt` (readable, `[mm:ss] text`) are committed. They are text metadata (about 400 KB).
- `02_transcribe.py` now prints the audio length and an up-front estimated finish time, then a live line every 5 s (`% done, ETA clock time, minutes left`). It swaps mlx-whisper's tqdm bar for one that does this. Verified on a 6-minute clip: 27x realtime, ETA lines correct. Estimate uses 20x realtime before measuring.

## 10. Cut decisions (2026-11-09)
- **Approach:** an edit decision list (EDL) in source time, `data/cuts.json`, produced by `scripts/07_plan_cuts.py`. Remotion never hard-codes cut times, so the edit is code-reviewable and re-runnable.
- **Main edit:** drop pre-roll and post-roll, shorten pauses over 0.8 s to about 0.4 s, cut fillers. Result: 16 cuts, 35.2 s removed (1693.4 to 1658.3 s). The saving is small because this speaker rarely pauses long. I chose not to cut more, because removing content or mid-sentence breaths would hurt the interview's natural feel.
- **Highlights reel:** 7 self-contained claims chosen by Claude from the transcript, hook first ("AI is building another AI"), then scale (300 bots), the pilot metaphor, the new way of working, what a bot is, a risk beat, and a payoff close. Each is found by exact start/end phrase at word level (asserted unique), so timing follows the transcript. Total 52.8 s.
- **Frame snapping:** all cut points are snapped to the 25 fps grid, so Python's output timeline equals Remotion's frame count exactly (rendered reel measured 52.800 s).
- **Kept in sync:** because cuts shift time, `07` also writes `subtitles.main.srt` and `chapters.main.*` on the output timeline. The mux step uses these, not the source-time files.

## 11. Remotion edit + animated captions (2026-11-09)
- `Main` and `Highlights` compositions share one `Edit` component: `Series` of `OffthreadVideo` clips (`startFrom` from the EDL), then captions, chapter cards (main only) and progress bar (main only).
- **Captions:** uppercase Impact, white with heavy black stroke. The cue springs in. The word being spoken turns red and pops (spring scale and slight tilt). Words outside the kept footage are hidden, so a cut that starts mid-cue never shows words that were cut. Checked on rendered frames.
- **Gotcha:** Remotion's bundler does not follow symlinks in `public/` (404). `05_make_proxy.sh` now makes a hard link (no extra disk).
- **Verified:** `out/highlights.mp4` rendered in 35 s, 52.8 s long, captions and audio present. The full main render (about 18 min) is scripted but not yet run.

## 12. Studio + workflow record (2026-11-09)
- Remotion Studio runs on port 3000 (`npm run studio`) and is opened in Google Chrome. It plays the 720p proxy through the same cut list as the renders, so the preview matches the output.
- `docs/WORKFLOW.md` records the user prompts in order, the stages with their scripts/outputs, which outputs are committed vs not, the role of each AI/code step, and reusable prompt templates for the next video.

## 13. Transcript corrections and speakers (2026-11-09)
- **Raw vs corrected:** Whisper output is kept untouched in `data/transcript.raw.json`. `scripts/02b_apply_corrections.py` applies `data/corrections.json` to produce `transcript.json`/`.txt`. Every downstream step (subtitles, chapters, cuts, Remotion captions) reads the corrected file, so a re-run of 02, then 02b, 03, 04, 07 reproduces everything.
- **Why rules as data, not hand edits:** each fix is auditable, can be switched off (`"active": false`), and survives a re-transcription. The script prints how often each rule fired, so a rule that matches nothing is visible.
- **Matching:** case-insensitive on word tokens inside a segment. Trailing punctuation and an initial capital are kept, and word timings are preserved (caption highlighting stays in sync).
- **Applied (17 rules):** Claude Code (3), daemons (2), Skool platform/community (3), for the Skool, the Skools that, 300 bots, COBALTS, Sixth-form college, Grokbot, Dots, hello, Marianna, got abstracted, getting disrupted. Rules 3 (Voltron), 11 (Muse) and 17 (Muses at home) matched nothing because Whisper already wrote them correctly.
- **Wording variants added** because this transcript differs from the list given: "demos" for "delts" (rule 2), "growth bot" for "broad bot" (12), "DOTS" for "duts" (13), "got obstructed" for "got absurd" (15). Please check these against the audio.
- **Left switched off (unconfirmed):** Tesco, thumbnails, lots of, sandboxes, I thought. None matched anyway.
- **Known leftover:** "the boats are building the boats" (about 08:04) was not in the list, so it is unchanged. It probably means "bots".
- **Chapter title** now reads "Skool Community". The sixth-form rule lowercases "college" as written ("Cambridge Sixth-form college"); adjust the rule if you prefer the proper-noun capitals.
- **Speakers:** Marianna asks the questions, Rifat Erdem Sahin answers (`data/speakers.json`, intro chapter summary). Whisper does not label speakers, so this is metadata only, not per-line labels.

## 14. Combined timeline + section indicator (2026-11-09)
- **`Combined` composition:** the 7-clip highlights reel first (52.8 s), then the tightened full interview (1658.3 s). 1711.1 s total. It is just `[...cuts.highlights, ...cuts.main]` in the same edit list, so captions, cuts and audio need no new logic.
- **Why highlights first:** the hook plays before the viewer can leave, then the full conversation follows (cold-open pattern).
- **Bottom indicator (`SectionBar`):** one segment per section (Highlights + 13 chapters), each as wide as the section is long, filling as it plays. A label on the left shows the current section and `elapsed / length` (for example `CH 2/13 - Why a Delivery Pilot? 0:06 / 1:15`). Chapter cards are offset by the highlights length so they still land on the right moment. Captions sit 44 px up in this mode to clear the bar.
- **Sync:** `07_plan_cuts.py` also writes `subtitles.combined.srt` and `chapters.combined.*` (Highlights as chapter 0). Subtitle cues are now clipped to the words actually inside the kept footage.

## 15. Secrets (2026-11-09)
- The fal.ai key lives only in `.env` (git-ignored). `.env.example` is committed with a placeholder. `scripts/09_generate_visuals.py` reads it and never prints it.
- `.githooks/pre-commit` (enabled with `git config core.hooksPath .githooks`) blocks commits that contain env files or key-like strings (fal, Anthropic, OpenAI-style, AWS, `*_KEY=...`). Tested: it blocked a fake key. Verified the real key is not in tracked files or git history.
- **Recommendation:** because the key was pasted into a chat, treat it as exposed and rotate it in the fal.ai dashboard when convenient, then update `.env`.

## 16. Explainer visuals with fal.ai (2026-11-09)
- **Selection:** Claude read the transcript and picked 9 moments where a concept is being explained (`scripts/08_plan_explainers.py`), each anchored to start/end phrases at word level (asserted unique). 6 are simple, 3 are complex.
- **Simple (free):** native Remotion animation, no AI image needed: CI to CD flow, bots building bots (counter and growing grid), agent-to-agent network (moving pulses), the grocery fallback chain (Tesco, Sainsbury's, Maria's door), the 20-30% desk-jobs stat, and the workshops card.
- **Complex (fal.ai):** Rider/Driver/Pilot, Agent vs Bot vs Robot, and what a pilot needs. Each shows an AI-generated illustration with animated, numbered labels overlaid.
- **Cost-effective model:** `fal-ai/flux/schnell` (4 steps, about $0.003 per megapixel at the time of writing). 4 images at 1024x768 cost about $0.009 in total, including one regeneration. Verify against the fal.ai dashboard.
- **Text-free art, labels in Remotion:** image models garble text (the first agent/bot/robot image contained "A Tovd Rigpot"), so prompts ask for wordless art and the real words are drawn by Remotion. The prompt was rewritten and that one image regenerated.
- **Layout:** panel on the left, 560 px wide, where the footage has the window and the speaker sits on the right. It is sized to end above the captions (captions reduced from 56 to 48 px to guarantee that). It enters with a spring and fades out over 0.4 s. It is not shown during the highlights reel.
- **Reproducible:** images are cached (skipped if present), `--force --only <id>` regenerates one, and `data/visuals_manifest.json` records prompt, seed, size and estimated cost.
- **Caption fix found while testing:** Whisper split "20-30%", "desk-based" and "1.30" into pieces, which showed as "20 -30 %". `03_make_subtitles.py` now glues such tokens back together.
- **Verified:** one still per explainer from the Combined composition, plus an 8 s video render of an infographic section. Full Combined render is scripted but not run (estimated 20-30 min).

## 17. Slight zoom (2026-11-09)
- Footage is scaled 1.12x (`ZOOM` in `src/config.ts`), anchored at 68% / 45% so the speaker on the right stays framed and the empty window area on the left is cropped. Applies to Main, Highlights and Combined. Only the video layer scales, so captions, panel and bars are unaffected. Change `ZOOM` (1.0 = none) to adjust.
- Source is 4K and the proxy is 720p, so a zoom softens the proxy slightly. For a final 4K render, render from the original to keep it sharp.

## 18. Thumbnail, title, description (2026-11-09)
- **Thumbnail:** a real frame (6:44, expressive gesture, empty window area on the left for text) from the **4K source** (sharper than the proxy) plus a three-word headline drawn in Remotion ("Become a Delivery Pilot", PILOT in red) and the line "AI builds the bots. You fly them." Same white/red look as the captions. Text is drawn by Remotion, not an image model. 1280x720 JPG, 166 KB. Gotcha: `OffthreadVideo startFrom` is ignored in a single-frame Still (it showed the empty chair), so the frame is extracted with ffmpeg and used as an image.
- **Title:** 72 characters, keyword first, a curiosity hook, no clickbait claims. Three alternatives listed.
- **Description:** hook, bullet summary of what is covered, exact chapter timestamps from `chapters.combined.json` (first at 0:00, all over 10 s, as YouTube requires), host/guest, link placeholders, hashtags. Skool and Eventbrite links were not provided, so they are marked `[ADD LINK]` rather than invented.
- `scripts/11_make_publish.py` generates `docs/PUBLISH.md` and `data/description.txt`, so chapter times stay correct if cuts change.

## 19. Audio cleanup (2026-11-09)
- `scripts/05b_clean_audio.py` cleans the dialogue and swaps it into the proxy (video stream copied, no re-encode): high-pass 70 Hz, one conservative FFT denoise pass (`afftdn`), a soft downward gate, then two-pass loudness normalisation to -16 LUFS (true peak -1.5 dB).
- **Measured, not guessed:** room noise in a silent gap fell from -53.2 to -63.6 dB, and the speech-to-noise gap grew from 28.3 to 43.7 dB. Loudness went from -20.9 to -16.0 LUFS; peak -4.3 to -1.5 dBFS.
- **My first attempt was wrong:** I used a compressor, which lifted the quiet pauses and cancelled the denoise gain (gap stayed about 28 dB). Caught by measuring the gap, replaced by the gate.
- **Why not stronger:** a second denoise pass or a harder gate reaches about 48 dB but risks warbly or unnaturally dead pauses. I cannot listen, so I chose the conservative setting. Please listen once; the knobs are `BASE` in the script.
- Transcription was done on the original audio, which is fine since timings are identical.

## 20. Bigger footer and tighter zoom (2026-11-09)
- Footer (`SectionBar`) is 48 px tall (was 30) with 21 px text and a thicker segmented bar; captions in the Combined timeline sit 66 px up to clear it.
- `ZOOM` raised from 1.12 to 1.22, still anchored at 68%/45% so the speaker stays framed.

## 21. Duplicated ideas removed + always-on timeline (2026-11-09)
- **Rule:** keep the first / fullest statement of an idea, drop restatements, never cut a sentence whose meaning is not said elsewhere. Eight cuts, all in `DEDUPE` in `scripts/07_plan_cuts.py`, each anchored by exact phrases (asserted unique) and documented with why it is a duplicate and where the idea is kept:
  1. host restates "no need for programmers" (3:15-3:43), 2. repeat of "become pilots" plus bots aside (4:59-5:18), 3. recap of rider/driver/pilot and "AI builds the AI" (7:20-8:19, the longest, 57 s), 4. "people become pilots, stop using keyboards" again (15:30-15:52), 5. third telling of the horse/car/plane ladder plus a stuttered "to answer your question" (17:10-17:29), 6. "plane versus a car, more creative" again (22:41-22:51), 7. "bots are probabilistic" repeated within seconds (14:37), 8. host asks to "talk about AI skills" twice (5:49). The trailing duplicate "Thank you." is also dropped.
- **Total:** 159 s of duplicated ideas removed. Main edit 1658.3 s to 1495.8 s; Combined 1548.6 s (25:49).
- **Proof-read:** the planner prints the words before and after every cut, and all eight joins read as continuous sentences. One join ("the white-collar jobs ...") loses the connector "But that means"; acceptable, flag it if it bothers you.
- **Not cut on purpose:** the highlights reel (a teaser, so repeating main content is intended), the "Yes." back-and-forth in the chatbot/agent Q&A (cutting would break the Q/A), and the "stop looking at screens" mental-health point (adds a new angle).
- **Timeline:** `docs/TIMELINE.md` is regenerated by the same script on every run: Mermaid gantt of sections and explainers, numbers, every duplicate removed (what, why, where kept), sections, explainers, highlights, and the kept-footage list with output times. Subtitles, chapters, SectionBar and publish copy follow automatically.

## 22. Curiosity thumbnail with fal.ai (2026-11-09)
- **Why the old one was weak:** a pleasant but generic "Become a Delivery Pilot" label gave no reason to click.
- **Curiosity levers:** a specific, surprising number from the interview ("I have 300 bots running"), a contrast ("300 bots / 1 pilot"), an open question ("Who is flying yours?"), and a visual that begs explanation (a lone silhouette facing a wall of hundreds of glowing bot screens). The real speaker appears on a framed "witness" card so it still feels like a human story, not stock art.
- **fal.ai:** 3 background variants with `fal-ai/flux/schnell` (about $0.005 total, cheap model), I picked the pilot-facing-the-wall one. Others: a swarm of red drones in a storm sky, and an airplane made of bots. The art is text-free and all words are drawn in Remotion, since image models garble text.
- **Honesty check:** "300 bots" is the guest's own claim in the interview (04:38), not invented.
- **A/B idea:** upload `assets/thumbnail.jpg` and test it against the earlier "Become a Delivery Pilot" version in YouTube's thumbnail test.

## 23. Versions and CLAUDE.md (2026-11-09)
- **Versioning scheme:** one project version `0.MINOR.PATCH` (file `VERSION`), a git tag per version, a snapshot of the small deliverables in `versions/v<version>/` with `manifest.json` (commit, date, notes, stats), and an entry in `CHANGELOG.md` plus a "current artifact versions" table at its top. `scripts/version.py bump` does the snapshot, changelog and version bump in one command; `scripts/version.py snapshot <ref> <ver>` recovers an old version from git history.
- **Why snapshots, not only tags:** tags freeze the whole repo, but the user wants to compare artifacts side by side (thumbnail v1 vs v2, main edit 27:38 vs 24:56) without checking out old commits. Snapshots hold only small text/metadata and the thumbnail (about 300 KB each, 1.2 MB for the four recovered ones); media is excluded and reproducible.
- **Retroactive versions:** v0.1.0 to v0.11.0 were tagged on the matching commits, and v0.8.0 to v0.11.0 were snapshotted from history. Verified: the v0.9.0 snapshot has the main edit at 1658.3 s, v0.10.0 at 1495.8 s.
- **Thumbnails:** both kept, `assets/thumbnails/v1-generic-...jpg` and `v2-curiosity-...jpg`; `assets/thumbnail.jpg` is always the latest.
- **CLAUDE.md:** the user's standing instructions (document rationale, commit/push every step, no media, never commit keys, keep README flow current, always timeline, always version, ETA, Chrome, cost-effective fal.ai) plus conventions and gotchas, so any future session follows the same rules without being re-told.

## 24. Export of the Combined video (2026-11-09)
- Rendered `Combined` (highlights, then the full interview) with `scripts/06_render_and_embed.sh combined`: 38,716 frames in about 14 minutes (ETA was shown live), then ffmpeg muxed 14 chapter markers and a soft subtitle track (`mov_text`).
- **Result:** 25:49 (1548.65 s, matches the planned 1548.6 s), 1280x720 25 fps, H.264 + AAC, 366 MB, loudness -16.1 LUFS, peak -1.4 dBFS.
- **Location:** `out/combined_final.mp4` (git-ignored) and a versioned copy `~/Downloads/C1193_combined_v0.12.0.mp4`. Media is not committed.
- **Known limits:** it is 720p because it is rendered from the proxy; at the 1.22x zoom a 4K-source render would be sharper. This version has no sound effects or music yet. The footer label truncates long chapter names ("Chatbots, Agents and Bots Exp..."); widening the label fixes it.

## 25. GitHub Pages site (2026-11-09)
- **What:** a static site in `site/` with an overview, a **YouTube** page (title, alternatives, description with chapters, tags, pinned comment, thumbnail, subtitles download, checklist), a **LinkedIn** page (long and short post), an **X** page (3 single posts and a 6-post thread), and a **Costs** page. Every text block has a Copy button and a live character counter (YouTube title 100, description 5,000; LinkedIn 3,000; X 280 with a link counted as 23). All X posts are asserted to fit at build time.
- **Why generated:** `scripts/13_build_site.py` builds the pages from `data/` and `docs/`, so the copy, chapters and costs cannot drift from the project. The site is committed, so GitHub does not need Python or Node to deploy.
- **Workflow:** the user's `static.yml` uploaded the whole repo (`path: '.'`), which would publish raw scripts and data. Changed to `path: 'site'` so only the site is public. Pages was already enabled (build type: workflow). No key or media is in `site/`.
- **X vs x.ai:** "x.ai" was taken to mean posting on X (formerly Twitter). If xAI/Grok was meant, say so.
- **Costs page:** fal.ai spend is an estimate from the list price (about $0.003 per megapixel), about $0.015 for 7 images (including one discarded and one regenerated). Local compute and hosting are $0. Claude usage is not measured here. Sound and music are marked as planned.
- **Placeholders:** the YouTube link (`[LINK]`) and the Skool/Eventbrite links (`[ADD LINK]`) are not known, so they stay as placeholders instead of invented URLs.

## 26. Real links and the Pages deploy failures (2026-11-09)
- **Links added** (provided by the user): Skool community `https://www.skool.com/delivery-pilot-8938` and the Eventbrite event "Cambridge AI Academy: Build Your Own AI Agents". They replace the `[ADD LINK]` placeholders in the YouTube description, the LinkedIn post and the site. Only the YouTube URL (`[LINK]`) is still unknown until the video is published.
- **Deploy failures investigated:** push-triggered runs `c866267`, `ef432d9` and `84f1859` failed with "workflow file issue" and zero jobs, while a manual `workflow_dispatch` run of the same file succeeded and deployed (all 6 pages return 200). The only pattern: the failing pushes also carried git tags (`git push --tags`); earlier branch-only pushes deployed fine. Working theory (unconfirmed): pushing many tags together with the branch trips GitHub's workflow evaluation. Mitigation: push the branch first, tags separately (`git push origin vX.Y.Z`), and trigger `gh workflow run static.yml` if a run is missing.

## 27. LinkedIn in first person (2026-11-09)
- Rewritten as Rifat Erdem Sahin announcing the release ("I sat down with Marianna...", "I have 300 bots running right now"). It uses only things he says in the interview: rider/driver/pilot, 300 bots and one bot that writes the others, pilots need more training, agent vs bot vs robot with the Tesco/Sainsbury's/neighbour example, CI now possible and CD next, adult education and self-learning, first computer at age five and the pilot dream. Marianna is thanked for the questions. Long post 1,642 characters, short post 445 (limit 3,000). Links to the Skool community and the Eventbrite event are included.
- The X posts remain written about him in the third person; they can be switched to first person on request.

## 28. LinkedIn cut, A/B/C thumbnails, checklist and workflow pages (2026-11-09)
- **LinkedIn version (12:36, limit 14:00):** its own edit list in `scripts/07_plan_cuts.py` (12 phrase-anchored sections), asserted under 14 minutes. No repeated cold open (a hook made of clips that reappear later would duplicate ideas), and it reuses the duplicate removals. Proof-reading the section boundaries found three openings that referred to something not in the cut ("that was my core niche", "Once you start doing that", "this question"); each now includes the host question or the setup before it. "Continuous learning" was dropped because self-learners covers it. Rendered as `LinkedIn` composition (progress bar without chapter ticks, captions burned in, soft SRT also muxed): 755.6 s, 1280x720, -16.0 LUFS, 180 MB (not in git). Subtitles for it: `data/subtitles.linkedin.srt`.
- **Three thumbnails, always (new standing rule):** A "300 Bots / 1 Pilot" (number + question, red/dark, face card), B "Stop Typing." (imperative, yellow/black, big face; art: a keyboard dissolving into particles), C "Driver / Pilot: Which are you?" (cyan split screen, no face). They differ in hook, palette and layout so the test learns something. fal.ai art for B and C cost about $0.012 (6 variants). I avoided the variant of the steering wheel that showed a car brand logo.
- **Checklist and workflow pages:** `scripts/site_pages.py` is the single source (STAGES and CHECKLIST) for the site pages and the repo docs (`docs/VIDEO_PRODUCTION.md`, `docs/CHECKLIST.md`). The checklist is pre-ticked with real project status (27 of 42 done), saves ticks in the browser, and ends with the go-live steps (upload, A/B test, replace `[LINK]`, post, pin, reply, review after a week). The Thumbnails page has the hypotheses, how to run YouTube's test and an editable results table.
- **Sound and music** are still open (stage 9, checklist items) and listed as such.

## 29. YouTube link documented (2026-11-09)
- The video is live at https://youtu.be/VOtlOfpXVU8 (`data/links.json` is now the single source for the YouTube, Skool and Eventbrite links). Assumption: this first upload is the Combined render v0.12.1 (25:49, no sound effects or music); a sound-and-music version follows.
- The URL is filled into the LinkedIn posts, X posts and thread, the YouTube page and the site overview (Watch button) and the README. X counts every link as 23 characters, so the counters and the build-time 280-character check now treat any URL as 23 characters.
- Checklist: "Upload the Combined video to YouTube" and "URL filled into posts" are ticked; adding the SRT and the three Test & Compare thumbnails to that video is a new open item.

## 30. LinkedIn post documented (2026-11-09)
- The LinkedIn post is live at https://lnkd.in/p/e5GMfT5V (shortened link as shared; stored in `data/links.json`, shown on the site's LinkedIn page and overview, in the README and ticked on the checklist). Open item: confirm the LinkedIn SRT was added to that video. I did not open the link, so what the post contains (which cut, which text) is the user's, not verified here.

## 31. X version (2026-11-09)
- **Problem:** uploading to X failed with "the duration of the video you tried to upload was too long". Standard X accounts allow 2 minutes 20 seconds; the Combined (25:49) and LinkedIn (12:36) cuts are far over.
- **Fix:** a dedicated X cut, `X` composition, capped at 2:15 by an assert in `scripts/07_plan_cuts.py`. Result: **1:22 (82.3 s)**, 1280x720, 18 MB (X allows 512 MB), H.264/AAC. Eight distinct moments in chronological order, each anchored by exact phrases: AI is building AI, 300 bots and one writes the rest, rider/driver/pilot, stop typing and start directing, the bot that finds olives (Tesco, Sainsbury's, Maria's door), the goal matters more than the method, pilots need more training, and the self-learner closing. No duplicated idea (the 300-bots and AI-builds-AI lines are a progression, not a repeat) and no removed duplicate is reintroduced.
- **Platform choices:** captions burned in (most feeds start muted); no soft subtitle track (X ignores it; SRT provided for reference); closing card for the last 7 s "FULL CONVERSATION, youtu.be/VOtlOfpXVU8" so viewers can find the whole interview; progress bar without chapter ticks.
- **Lesson recorded in CLAUDE.md:** check a platform's duration and size limits before building a version for it.

## 32. Sound effects and music with fal.ai (2026-11-09)
- **Models:** `cassetteai/sound-effects-generator` (effects) and `cassetteai/music-generator` (music); both returned audio on the first call. 8 clips (5 effects, 3 music tracks) for an estimated **$0.125** (assumed list prices, the API does not report cost: check the dashboard).
- **Effects:** whoosh (chapter cards, clip/section changes, panel entrance), pop (explainer reveals), ding (success, stat), buzz (a failed step such as "Tesco out of stock"), impact (the cut from highlights into the full interview).
- **Music:** an energetic hook track over the highlights reel and the X cut; two calm beds (ambient pads, warm piano) alternating per chapter so the 90-second loops do not repeat audibly for minutes. Fade in and out at every boundary.
- **Levels:** every file is levelled at generation (effects peak -3 dBFS, music -20 LUFS) so the multipliers in `src/Sound.tsx` mean the same for all. Beds at 0.30 sit about 14 dB under the dialogue (-16 LUFS): felt, not noticed. Effects 0.25 to 0.55.
- **Placement:** cues are computed from the same edit list as the video (`labelStarts`, chapter starts, and the reveal timing of each explainer through `beatCues`), and effects for an explainer are skipped when its moment was cut from that version.
- **Safety net:** mixing music over dialogue can push peaks, so every render gets a final `loudnorm` pass (-16 LUFS, true peak -1.5 dB); the X render measured -15.7 LUFS, peak -1.4 dBFS.
- **Not verified by ear:** I cannot listen; levels are set by measurement and convention. The checklist asks for one listen.

## 33. Description sections, X post, Skool export (2026-11-09)
- **Description:** the YouTube description now has a People section (Host: Marianna Nechypor and Guest: Erdem Sahin, each with a LinkedIn link), a Cambridge AI Academy section (name, Wed 25 Nov 18:00, Hills Road Sixth Form College, tickets, more info at cambridgeaiacademy.co.uk) and the Skool link. All values live in `data/links.json` and the text is generated by `scripts/11_make_publish.py` (1,972 of 5,000 characters). The video's own YouTube description must be pasted in by hand (YouTube Studio).
- **Decisions on wording:** the guest is shown as "Erdem Sahin" exactly as the user supplied it (elsewhere in the project he is "Rifat Erdem Sahin"; align if wanted). The Eventbrite link is the clean URL without the tracking parameters (`aff`, `utm_share_source`, `sg`) that were on the shared link; it opens the same event.
- **Open check:** the captions say "Cambridge Sixth-form college" (from correction rule 10), but the event location is Hills Road Sixth Form College. I do not know what the guest actually said, so I left the captions alone and added a checklist item; if the audio says Hills Road, add a rule and re-render.
- **X post** documented: https://x.com/rifaterdemsahin/status/2119868364722208900 (links.json, X page, overview, README, checklist).
- **Skool version:** the full `Combined` render with music and sound effects, exported as `~/Downloads/C1193_skool_v0.15.0.mp4` (25:49, 345 MB, 1280x720, -16.0 LUFS, peak -1.2 dBFS, 14 chapters, soft subtitle track). The LinkedIn cut with sound is `C1193_linkedin_sound_v0.15.0.mp4` (12:36) and the X cut is `C1193_x_v0.15.0.mp4` (1:22). The YouTube upload is the earlier Combined without sound. I verified duration, streams, chapters and loudness; I have not listened to the mix.
