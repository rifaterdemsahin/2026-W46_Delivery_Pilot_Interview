#!/usr/bin/env python3
"""Generate infographic art for the 'infographic' explainers with fal.ai.

Model: fal-ai/flux/schnell (4 steps) - among the cheapest image models (about $0.003 per megapixel
at the time of writing; check fal.ai pricing). 1 image per infographic, text-free art; Remotion adds
the labels. Cached: existing files are skipped unless --force.
The key is read from .env (FAL_KEY), git-ignored. It is never printed or written anywhere else.
Output: public/visuals/<id>.jpg (committed, small) + data/visuals_manifest.json (prompt, seed, size).
"""
import json, os, sys, time, urllib.request, urllib.error

MODEL = "fal-ai/flux/schnell"
SIZE = "landscape_4_3"  # 1024x768 = 0.79 MP
PRICE_PER_MP = 0.003


def load_key():
    key = os.environ.get("FAL_KEY")
    if not key and os.path.exists(".env"):
        for line in open(".env"):
            if line.startswith("FAL_KEY="):
                key = line.split("=", 1)[1].strip()
    if not key or key.startswith("your-"):
        sys.exit("FAL_KEY missing: put it in .env (git-ignored). See .env.example")
    return key


def post(key, payload):
    req = urllib.request.Request(
        f"https://fal.run/{MODEL}", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        sys.exit(f"fal.ai HTTP {e.code}: {e.read().decode()[:300]}")


force = "--force" in sys.argv
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
beats = [b for b in json.load(open("data/explainers.json")) if b["kind"] == "infographic" and (only is None or b["id"] == only)]
manifest_path = "data/visuals_manifest.json"
manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
key = load_key()
spent = 0.0
for b in beats:
    path = f"public/{b['image']}"
    if os.path.exists(path) and not force:
        print(f"skip {b['id']} (exists)"); continue
    t0 = time.time()
    res = post(key, {"prompt": b["prompt"], "image_size": SIZE, "num_inference_steps": 4,
                     "num_images": 1, "output_format": "jpeg", "enable_safety_checker": True})
    img = res["images"][0]
    with urllib.request.urlopen(img["url"], timeout=120) as r, open(path, "wb") as f:
        f.write(r.read())
    mp = img["width"] * img["height"] / 1e6
    spent += mp * PRICE_PER_MP
    manifest[b["id"]] = {"model": MODEL, "prompt": b["prompt"], "seed": res.get("seed"),
                         "width": img["width"], "height": img["height"], "bytes": os.path.getsize(path),
                         "est_cost_usd": round(mp * PRICE_PER_MP, 4)}
    print(f"{b['id']}: {img['width']}x{img['height']} {os.path.getsize(path)//1024} KB in {time.time()-t0:.1f}s")
json.dump(manifest, open(manifest_path, "w"), indent=1)
print(f"estimated spend this run: ${spent:.3f}")
