# Changelog

Every deliverable is versioned. Scheme: `0.MINOR.PATCH` for the whole project, one git tag per version, a snapshot of the
small deliverables in `versions/v<version>/` (with `manifest.json`), and an entry here. New version: `scripts/version.py bump minor "notes"`.

## v0.12.0 - 2026-11-09
Versioning system (VERSION, CHANGELOG, versions/ snapshots, tags) and CLAUDE.md project rules

## Current artifact versions

| Artifact | Current | Earlier |
|----------|---------|---------|
| Transcript | corrected, 17 rules (v0.6.0) | raw Whisper (v0.2.0, kept as `transcript.raw.json`) |
| Main edit (cuts) | 24:56, duplicates removed (v0.10.0) | 27:38 (v0.5.0 to v0.9.0) |
| Dialogue audio | denoise + gate, -16 LUFS (v0.9.0) | original (-20.9 LUFS) |
| Thumbnail | v2 curiosity "300 bots / 1 pilot" (v0.11.0) | v1 generic "Become a Delivery Pilot" (v0.8.0), in `assets/thumbnails/` |
| Publish copy | chapters after dedupe (v0.10.0) | first draft (v0.8.0) |
| Footage zoom | 1.22x (v0.9.0) | 1.12x (v0.8.0) |

## v0.11.0 - 2026-11-09
Curiosity thumbnail v2: fal.ai art, "300 bots / 1 pilot" hook, open question, framed speaker card.

## v0.10.0 - 2026-11-09
Removed 159 s of duplicated ideas from the main edit (8 documented cuts, 27:38 to 24:56). `docs/TIMELINE.md` is now generated on every cut run.

## v0.9.0 - 2026-11-09
Dialogue audio v2 (denoise + soft gate + loudness -16 LUFS, speech-to-noise gap 28 to 44 dB). Bigger footer, zoom 1.22x. GitHub Pages starter workflow added.

## v0.8.0 - 2026-11-09
Zoom 1.12x, README with emojis, thumbnail v1, title/description/tags v1.

## v0.7.0 - 2026-11-09
`Combined` timeline (highlights first) with section-length bar. Explainer visuals: 6 animated graphics plus 3 fal.ai infographics. Secret guard (`.env`, pre-commit hook).

## v0.6.0 - 2026-11-09
Transcript corrections as data (`data/corrections.json`), speakers recorded (Marianna asks, Rifat Erdem Sahin answers).

## v0.5.0 - 2026-11-09
Cut planner (edit decision list), highlights reel, animated white/red captions, readable transcript, ETA while transcribing, workflow record, captions lowered.

## v0.4.0 - 2026-11-09
Remotion composition (captions, chapter cards, progress bar) and render script.

## v0.3.0 - 2026-11-09
Subtitles (SRT/VTT), 13 AI chapters, proxy script.

## v0.2.0 - 2026-11-09
Audio extraction and Whisper transcript (283 segments, 4,494 words).

## v0.1.0 - 2026-11-09
Plan, `.gitignore` (no media), library install (mlx-whisper, Remotion).
