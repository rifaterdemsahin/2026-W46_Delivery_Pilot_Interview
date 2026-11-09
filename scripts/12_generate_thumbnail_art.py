#!/usr/bin/env python3
"""Thumbnail background art with fal.ai (fal-ai/flux/schnell, cheap). Makes N variants (different prompts/seeds)
into work/thumb_art_<n>.jpg; pick one with --use N, which copies it to public/visuals/thumb_bg.jpg (committed).
Text-free on purpose: the headline is drawn by Remotion. Key comes from .env (never printed)."""
import json, os, shutil, sys, urllib.request, urllib.error

MODEL, SIZE, PRICE_PER_MP = "fal-ai/flux/schnell", "landscape_16_9", 0.003
STYLE = "cinematic, dramatic lighting, high contrast, deep navy and vivid red palette, dark moody background, no text, no letters, no words"
PROMPTS = [
    f"view from an airplane cockpit looking out at a huge swarm of hundreds of tiny glowing red robots flying in formation like a flock of birds across a stormy navy sky, {STYLE}",
    f"a lone pilot silhouette seen from behind in a dark control room facing a giant wall of hundreds of small glowing red robot screens, {STYLE}",
    f"a giant glowing red airplane-shaped constellation made of hundreds of tiny robots over a dark navy city at night, {STYLE}",
]

def key():
    k = os.environ.get("FAL_KEY")
    if not k and os.path.exists(".env"):
        k = next((l.split("=", 1)[1].strip() for l in open(".env") if l.startswith("FAL_KEY=")), None)
    if not k or k.startswith("your-"): sys.exit("FAL_KEY missing: put it in .env (git-ignored)")
    return k

if "--use" in sys.argv:
    n = int(sys.argv[sys.argv.index("--use") + 1])
    shutil.copy(f"work/thumb_art_{n}.jpg", "public/visuals/thumb_bg.jpg"); print(f"using variant {n}"); sys.exit()

k, spent, manifest = key(), 0.0, {}
for n, prompt in enumerate(PROMPTS, 1):
    req = urllib.request.Request(f"https://fal.run/{MODEL}", headers={"Authorization": f"Key {k}", "Content-Type": "application/json"},
        data=json.dumps({"prompt": prompt, "image_size": SIZE, "num_inference_steps": 4, "num_images": 1, "output_format": "jpeg"}).encode())
    try: res = json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e: sys.exit(f"fal.ai HTTP {e.code}: {e.read().decode()[:300]}")
    img = res["images"][0]
    open(f"work/thumb_art_{n}.jpg", "wb").write(urllib.request.urlopen(img["url"], timeout=120).read())
    cost = img["width"] * img["height"] / 1e6 * PRICE_PER_MP; spent += cost
    manifest[f"thumb_art_{n}"] = {"model": MODEL, "prompt": prompt, "seed": res.get("seed"), "est_cost_usd": round(cost, 4)}
    print(f"variant {n}: {img['width']}x{img['height']}")
mp = "data/visuals_manifest.json"; m = json.load(open(mp)) if os.path.exists(mp) else {}
m.update(manifest); json.dump(m, open(mp, "w"), indent=1)
print(f"estimated spend: ${spent:.3f}")
