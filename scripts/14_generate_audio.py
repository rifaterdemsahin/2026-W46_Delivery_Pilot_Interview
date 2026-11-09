#!/usr/bin/env python3
"""Sound effects and music with fal.ai (cheap audio models), levelled with ffmpeg, saved to public/audio/*.mp3.
SFX: cassetteai/sound-effects-generator. Music: cassetteai/music-generator (fallback fal-ai/stable-audio, max 47 s).
Cached (skip if the file exists); `--force --only <id>` redoes one. Key from .env, never printed.
Levels: SFX peak-normalised to -3 dBFS, music loudnorm -20 LUFS, so Remotion volume numbers mean the same for every file.
Costs are ASSUMED list prices (not returned by the API): check the fal.ai dashboard."""
import json, os, re, subprocess, sys, urllib.request, urllib.error

SFX_MODEL, MUSIC_MODEL, FALLBACK = "cassetteai/sound-effects-generator", "cassetteai/music-generator", "fal-ai/stable-audio"
SFX_COST, MUSIC_COST_PER_MIN = 0.01, 0.02
CLIPS = [  # id, kind, duration s, prompt
    ("sfx_whoosh", "sfx", 2, "soft smooth whoosh swipe transition, short and clean, no music"),
    ("sfx_pop", "sfx", 1, "single soft subtle UI pop click, very short, no music"),
    ("sfx_ding", "sfx", 2, "pleasant soft success chime ding, short, clean, no music"),
    ("sfx_buzz", "sfx", 1, "short soft low error buzz, brief, gentle, no music"),
    ("sfx_impact", "sfx", 3, "cinematic subtle impact hit with a short reverb tail, trailer boom, no music"),
    ("music_hook", "music", 45, "energetic modern technology documentary intro, driving pulse, optimistic, instrumental, no vocals"),
    ("music_bed1", "music", 90, "calm minimal ambient electronic background, soft pads and a gentle pulse, unobtrusive, instrumental, no vocals"),
    ("music_bed2", "music", 90, "warm minimal piano and soft synth background, thoughtful, unobtrusive, instrumental, no vocals"),
]

def key():
    k = os.environ.get("FAL_KEY") or next((l.split("=", 1)[1].strip() for l in open(".env") if l.startswith("FAL_KEY=")), None)
    if not k or k.startswith("your-"): sys.exit("FAL_KEY missing (put it in .env, git-ignored)")
    return k

def call(k, model, payload):
    req = urllib.request.Request(f"https://fal.run/{model}", data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Key {k}", "Content-Type": "application/json"})
    try: return json.load(urllib.request.urlopen(req, timeout=300)), None
    except urllib.error.HTTPError as e: return None, f"HTTP {e.code}: {e.read().decode()[:160]}"

def sh(*a): return subprocess.run(a, capture_output=True, text=True)

force = "--force" in sys.argv
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
mp = "data/audio_manifest.json"; manifest = json.load(open(mp)) if os.path.exists(mp) else {}
k, spent = key(), 0.0
for cid, kind, dur, prompt in CLIPS:
    out = f"public/audio/{cid}.mp3"
    if (only and cid != only) or (os.path.exists(out) and not force): continue
    model = SFX_MODEL if kind == "sfx" else MUSIC_MODEL
    res, err = call(k, model, {"prompt": prompt, "duration": dur})
    if err and kind == "music":  # fallback model has a 47 s cap
        model = FALLBACK; res, err = call(k, model, {"prompt": prompt, "seconds_total": min(dur, 47)})
    if err: print(f"{cid}: FAILED {err}"); continue
    url = res["audio_file"]["url"]; raw = f"work/{cid}.raw"
    open(raw, "wb").write(urllib.request.urlopen(url, timeout=300).read())
    if kind == "sfx":  # peak-normalise to -3 dBFS
        mx = float(re.search(r"max_volume: (-?[\d.]+)", sh("ffmpeg", "-hide_banner", "-i", raw, "-af", "volumedetect", "-f", "null", "-").stderr).group(1))
        af = f"volume={-3 - mx:.2f}dB,afade=t=out:st=0:d=0.001"
    else:
        af = "loudnorm=I=-20:TP=-2:LRA=7"
    r = sh("ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", raw, "-af", af, "-ar", "44100", "-ac", "2", "-b:a", "160k", out)
    if r.returncode: print(f"{cid}: ffmpeg failed {r.stderr[:120]}"); continue
    length = float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out).stdout)
    cost = SFX_COST if kind == "sfx" else MUSIC_COST_PER_MIN * length / 60; spent += cost
    manifest[cid] = {"kind": kind, "model": model, "prompt": prompt, "seconds": round(length, 1), "bytes": os.path.getsize(out), "est_cost_usd": round(cost, 4)}
    print(f"{cid}: {model} {length:.1f}s {os.path.getsize(out)//1024} KB")
json.dump(manifest, open(mp, "w"), indent=1)
print(f"estimated spend this run: ${spent:.3f} (assumed list prices)")
