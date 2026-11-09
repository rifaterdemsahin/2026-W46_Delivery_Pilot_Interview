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
