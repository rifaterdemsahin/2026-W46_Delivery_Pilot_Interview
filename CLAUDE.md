# CLAUDE.md - project rules for C1193.MP4 (Delivery Pilot interview)

AI pipeline: transcribe an English interview, add subtitles, chapters, cuts, animated captions and explainer visuals in Remotion, then publish. Read `README.md` (flow + steps), `docs/DECISIONS.md` (why), `docs/TIMELINE.md` (the edit), `CHANGELOG.md` (versions).

## Hard rules (never break)
1. **No media in git.** Never commit the raw video, renders, audio or the proxy (`work/`, `out/`, `*.mp4`, `*.wav`, `public/proxy.mp4`, `public/thumb_frame.jpg` are ignored). Small generated images and metadata are fine. The raw video is `~/Downloads/C1193.MP4` (20.9 GB, 4K); read it, never copy it in.
2. **Never commit secrets.** Keys live only in `.env` (git-ignored). `.githooks/pre-commit` blocks key-like text; enable with `git config core.hooksPath .githooks`. Never print or echo a key. Treat any key pasted in chat as exposed and say so.
3. **Document the rationale** of every step in `docs/DECISIONS.md` (numbered, dated, with the why and what was measured).
4. **Commit and push at every step** (small, one concern each). Do not leave work uncommitted.

## Always do (standing instructions from the user)
- **Keep `README.md` current:** emoji style, the Mermaid flow diagram, the status table and the steps table. Update on every step.
- **Always create the timeline:** `scripts/07_plan_cuts.py` regenerates `docs/TIMELINE.md` (and chapters, subtitles) whenever cuts change. Run it after any edit change; link stays in the README.
- **Always version what you create:** after a meaningful change run `scripts/version.py bump minor|patch "notes"`, commit, then `git tag -a vX.Y.Z` and push the tag. Keep earlier versions (e.g. `assets/thumbnails/v1-...jpg`, `versions/v*/`). Add the change to `CHANGELOG.md` and the artifact table at its top.
- **Record the user's prompts and stages** in `docs/WORKFLOW.md`.
- **Show an estimated completion time** for long jobs (transcription prints one; do the same for renders).
- **Preview in Google Chrome:** `open -a "Google Chrome" http://localhost:3000` for Remotion Studio.
- **Cost-effective fal.ai models** (e.g. `fal-ai/flux/schnell`), cache results, log cost in `data/visuals_manifest.json`, and record spend in the costs page. Image models garble text, so ask for text-free art and draw words in Remotion.
- **Measure, do not guess** (audio SNR, durations, frame counts). Verify visuals by rendering stills and looking at them. Proofread every cut join.

## Edit conventions
- Edits are an **edit decision list** (`data/cuts.json`) in source time; Remotion plays it back. Change the planner, not the video.
- Anchor everything by **exact phrases** found at word level and asserted unique (chapters, highlights, duplicates, explainers) so a re-transcription still lines up.
- Cut points are **snapped to the 25 fps grid** so Python and Remotion agree to the frame.
- Keep the first and fullest statement of an idea; remove restatements; never cut a sentence whose meaning is not said elsewhere.
- Corrections to the transcript go in `data/corrections.json` (rules with `active` flags); `transcript.raw.json` stays untouched.
- Speakers: Marianna asks the questions; Rifat Erdem Sahin answers.
- Look: white captions, spoken word red; red accent `#ff2b2b`; left-side explainer panel; footer section bar in the Combined composition.

## Pipeline (run order)
`01_extract_audio.sh` > `02_transcribe.py` > `02b_apply_corrections.py` > `03_make_subtitles.py` > `04_make_chapters.py` > `05_make_proxy.sh` > `05b_clean_audio.py` > `07_plan_cuts.py` > `08_plan_explainers.py` > `09_generate_visuals.py` > `10_make_thumbnail.sh` / `12_generate_thumbnail_art.py` > `11_make_publish.py` > `06_render_and_embed.sh`. Python runs as `.venv/bin/python -I scripts/<name>.py`.

## Gotchas found the hard way
- Remotion's bundler ignores symlinks in `public/`: `public/proxy.mp4` must be a **hard link** (done by `05_make_proxy.sh` / `05b_clean_audio.py`).
- `OffthreadVideo startFrom` is ignored in a single-frame `Still`: extract the frame with ffmpeg and use an image (thumbnail).
- Whisper splits tokens like `20-30%`, `desk-based`, `1.30`; matchers skip punctuation-only tokens and captions glue them back.
- macOS: BSD `sed` needs `sed -i ''`; zsh does not word-split unquoted variables.
- A compressor lifts pauses and cancels denoise; use a gate and measure the speech-to-noise gap.
- Image models add fake text even when told not to; reword prompts and regenerate (cheap).
- Pull before pushing: the user also edits the repo (e.g. the Pages workflow on GitHub).

## Where things live
`scripts/` pipeline | `data/` transcript, subtitles, chapters, cuts, explainers, corrections | `src/` Remotion (Main, Subtitles, Explainer, SectionBar, Thumbnail, edit) | `public/visuals/` fal.ai art | `assets/` thumbnail(s) | `versions/` snapshots | `docs/` plan, decisions, workflow, timeline, publish copy | `site/` GitHub Pages site (when present).
