#!/usr/bin/env python3
"""Versioning for everything this project creates.

  scripts/version.py bump minor|patch "what changed"   snapshot the working tree as the next version
  scripts/version.py snapshot <git-ref> <version> "notes"   snapshot an OLD commit (recovers earlier versions)

A snapshot copies the small deliverables (cuts, chapters, subtitles, explainers, corrections, description,
transcript text, timeline, publish copy, thumbnail) into versions/v<version>/ with a manifest.json.
Large/generated media is never snapshotted (it is git-ignored and reproducible from the scripts).
After `bump`: commit, then `git tag -a v<version> -m "<notes>"` and `git push origin v<version>`.
"""
import datetime, json, os, shutil, subprocess, sys

FILES = ["data/cuts.json", "data/chapters.json", "data/chapters.main.json", "data/chapters.combined.json",
         "data/explainers.json", "data/corrections.json", "data/description.txt", "data/subtitles.combined.srt",
         "data/subtitles.main.srt", "data/transcript.txt", "docs/TIMELINE.md", "docs/PUBLISH.md", "assets/thumbnail.jpg"]

def sh(*a): return subprocess.run(a, capture_output=True)

def snapshot(ver, notes, ref=None):
    d = f"versions/v{ver}"; os.makedirs(d, exist_ok=True); got = []
    for f in FILES:
        dst = f"{d}/{os.path.basename(f)}"
        if ref:
            r = sh("git", "show", f"{ref}:{f}")
            if r.returncode: continue
            open(dst, "wb").write(r.stdout)
        elif os.path.exists(f):
            shutil.copy(f, dst)
        else: continue
        got.append(f)
    commit = sh("git", "rev-parse", "--short", ref or "HEAD").stdout.decode().strip()
    stats = {}
    try: stats = json.load(open(f"{d}/cuts.json"))["stats"]
    except Exception: pass
    json.dump({"version": ver, "date": datetime.date.today().isoformat(), "based_on_commit": commit,
               "notes": notes, "files": got, "stats": stats}, open(f"{d}/manifest.json", "w"), indent=1)
    return d, len(got)

def changelog(ver, notes):
    p = "CHANGELOG.md"; old = open(p).read() if os.path.exists(p) else "# Changelog\n"
    head, _, rest = old.partition("\n## ")
    entry = f"\n## v{ver} - {datetime.date.today().isoformat()}\n{notes}\n"
    open(p, "w").write(head + entry + ("\n## " + rest if rest else ""))

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["bump"]:
        kind, notes = a[1], a[2]
        mj, mn, pa = map(int, open("VERSION").read().strip().split("."))
        mn, pa = (mn + 1, 0) if kind == "minor" else (mn, pa + 1)
        ver = f"{mj}.{mn}.{pa}"; open("VERSION", "w").write(ver + "\n")
        d, n = snapshot(ver, notes); changelog(ver, notes)
        print(f"v{ver}: {n} files in {d}. Now commit, then: git tag -a v{ver} -m \"{notes}\" && git push origin v{ver}")
    elif a[:1] == ["snapshot"]:
        d, n = snapshot(a[2], a[3], ref=a[1]); print(f"{n} files from {a[1]} -> {d}")
    else: sys.exit(__doc__)
