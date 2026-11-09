# Workflow record: prompts and stages

A reusable record of how this video was processed with AI. Reuse the prompts (swap the file name) to repeat it on another video.
Rule that applies to every stage: **document the rationale, commit and push at each step, never commit raw or output video** (only metadata and code).

## Prompts (in the order given) and what each produced

| # | Prompt (condensed, my words kept) | Stage it started | Result / commit |
|---|-----------------------------------|------------------|-----------------|
| 1 | "we are working with C1193.MP4 this is in english install the libraries to this project to transcribe it first then we would use remotion to edit it. create me a plan... We would have subtitles and chapter markers in this video. Current video is in downloads folder. always document your rationale and commit and push at every step. Don't add video files to this project use it for metadata and processing. This is an ai based processing flow." | Plan, `.gitignore`, library install (mlx-whisper venv, Remotion) | `docs/PLAN.md`, `docs/DECISIONS.md` #1-2 |
| 2 | "install the components and get the transcript and set up the remotion and have all the code in this repo. in readme.md have a flow diagram in mermaid and always update it." | Audio extract, transcription, subtitles, chapters, proxy, Remotion scaffold, README Mermaid flow | scripts 01-05, `src/`, `README.md` |
| 3 | "save transcript and commit push" | Transcript saved as JSON and readable text | `data/transcript.json`, `data/transcript.txt` |
| 4 | "when transcribing in the future show the estimated completion time" | ETA in the transcription script | `scripts/02_transcribe.py` |
| 5 | "and have all the code recorded here and steps. just not input raw video and output video" | Steps table in README, media kept out of git | `README.md` Steps, `.gitignore` |
| 6 | "have a code on how to cut to have the best impact and decide on how the cut should happen. Place the footage to remotion and have the animated white red subtitles" | Cut planner (EDL), Remotion timeline, animated white/red captions | `scripts/07_plan_cuts.py`, `data/cuts.json`, `src/Subtitles.tsx` |
| 7 | "open this in remotion and record these prompts and stages as well for my workflow" | Remotion Studio opened in Chrome; this file | `docs/WORKFLOW.md` |
| 8 | "there are type issues. Such as the person asking questions is Marianna, person answering is Rifat Erdem Sahin > do these updates: [17 before/after corrections, plus 5 unconfirmed left switched off]" | Transcript corrections as data + script, speakers recorded | `data/corrections.json`, `scripts/02b_apply_corrections.py`, `data/speakers.json` |
| 9 | "create one more timeline where the highlights are at the start and then the Main goes in / at the bottom have an indicator how long one section is for. Use Fal.ai for the complex parts to be explained with visuals and graphics [key given] > use simple graphics on the left with animations explaining the subject, and if it is a complex one use an infographic. Use cost effective models. Never commit push my ai keys" | `Combined` timeline + section bar, explainers (simple animated graphics, fal.ai infographics), secret guard | `src/SectionBar.tsx`, `src/Explainer.tsx`, `scripts/08`, `scripts/09`, `.githooks/pre-commit` |

| 10 | "zoom in a little bit" / "zoom in a bit more" / "make the bottom footer a bit bigger" | Footage zoom 1.12 then 1.22, footer 48 px | `src/config.ts`, `src/SectionBar.tsx` |
| 11 | "create a thumbnail and title and description" | Thumbnail v1, title, description with chapters | `scripts/10_make_thumbnail.sh`, `scripts/11_make_publish.py`, `docs/PUBLISH.md` |
| 12 | "remove the topics that are getting duplicated in the video, keep the meaning" and "always create a timeline" | 8 documented duplicate cuts; `docs/TIMELINE.md` generated every run | `scripts/07_plan_cuts.py`, `docs/TIMELINE.md` |
| 13 | "make the audio better if you can, clean background noise" | Denoise + gate + loudness, measured | `scripts/05b_clean_audio.py` |
| 14 | "make the thumbnail curiosity triggering, use the fal.ai" | Thumbnail v2 | `scripts/12_generate_thumbnail_art.py`, `src/Thumbnail.tsx` |
| 15 | "always have versions on what you create. add a claude.md" | Versioning system and CLAUDE.md | `scripts/version.py`, `CHANGELOG.md`, `CLAUDE.md`, `versions/` |
| 16 (queued) | "use sound effects wherever it makes sense and music, use fal.ai" | next | |
| 17 (queued) | "include the costs in a page, create a page and deploy to GitHub Pages with the yaml, link at top of README" and "a YouTube metadata page, a LinkedIn page and one for X to copy and publish" | after sound | |

(The API key was supplied in the chat; it is stored only in the git-ignored `.env` and is deliberately not recorded here.)

## Stages (pipeline)

| Stage | What happens | Tool / script | Output (committed) | Output (not committed) |
|-------|--------------|---------------|--------------------|------------------------|
| 0 Plan | Probe video, decide pipeline and rules | ffprobe | `docs/PLAN.md` | |
| 1 Audio | 16 kHz mono WAV from the 4K file | `scripts/01_extract_audio.sh` | | `work/audio.wav` |
| 2 Transcribe | Whisper large-v3-turbo on Apple GPU, word timestamps, ETA shown | `scripts/02_transcribe.py` | `data/transcript.raw.json` | |
| 2b Correct | Apply reviewed before/after rules (names, products, jargon) | `scripts/02b_apply_corrections.py` | `data/transcript.json`, `.txt`, `corrections.json` | |
| 3 Subtitles | Readable cues from word timing | `scripts/03_make_subtitles.py` | `subtitles.srt/.vtt`, `cues.json` | |
| 4 Chapters | AI (Claude) topic segmentation, anchored to phrases | `scripts/04_make_chapters.py` | `chapters.json`, `.ffmetadata`, `.youtube.txt` | |
| 5 Proxy | 720p proxy for fast preview/render | `scripts/05_make_proxy.sh` | | `work/proxy.mp4` |
| 6a Explainers | Pick concept moments; simple animated graphics or fal.ai infographic art | `scripts/08_plan_explainers.py`, `scripts/09_generate_visuals.py` | `data/explainers.json`, `public/visuals/*.jpg`, `visuals_manifest.json` | |
| 6 Cuts | Decide cuts for impact, write edit decision list | `scripts/07_plan_cuts.py` | `cuts.json`, `subtitles.main.srt`, `chapters.main.*` | |
| 7 Edit | Play cuts in Remotion with animated captions, chapter cards | `src/*.tsx`, `npm run studio` | the code | |
| 8 Render | Render, mux chapters and soft subs | `scripts/06_render_and_embed.sh` | | `out/*.mp4` |

## AI roles at each stage
- **Whisper (local model):** speech to text and word timing.
- **Claude:** reads the transcript to choose chapter boundaries/titles and highlight quotes; writes the code and logs the rationale.
- **Deterministic code:** everything else (subtitle cueing, cut tightening, frame snapping, remapping), so the result is reproducible.

## Reusable prompt templates
1. *Plan:* "We are working with `<FILE>` (language `<LANG>`). Install libraries to transcribe it, then edit with Remotion. Make a plan with subtitles and chapter markers. Document rationale, commit and push at every step. Never add video files to the repo; metadata and code only."
2. *Build:* "Install the components, get the transcript, set up Remotion, keep all code in this repo. Keep a Mermaid flow diagram in README.md and update it every step."
3. *Transcribe:* "Show the estimated completion time while transcribing. Save the transcript and commit/push."
4. *Cut:* "Write code that decides the cuts for best impact (tighten pauses, drop pre/post-roll, hook-first highlights), place the footage in Remotion, with animated white and red subtitles."
5. *Fix:* "Here are before/after corrections (some unconfirmed, keep those switched off). Names: interviewer is X, guest is Y." (Rules live in `data/corrections.json`; re-run 02b, 03, 04, 07.)
6. *Visuals:* "Use simple animated graphics on the left for easy ideas and a fal.ai infographic for complex ones. Cheap models. Never commit my API keys." (Key goes in `.env` only.)
7. *Combined:* "Add a timeline with the highlights first, then the main edit, with a bottom indicator of how long each section is."
8. *Review:* "Open it in Remotion Studio in Chrome."
