#!/usr/bin/env python3
"""Clean the dialogue and swap it into the proxy (video stream is copied, no re-encode).

Chain: high-pass 70 Hz (rumble) -> afftdn FFT denoise (one conservative pass, tracks the noise floor)
       -> soft downward gate (pauses -12 dB or more, speech untouched) -> two-pass EBU R128 loudnorm to -16 LUFS, TP -1.5 dB.
Why a gate and no compressor: a compressor lifts the quiet pauses and cancelled the denoise gain (gap stayed at 28 dB).
Why one denoise pass: a second pass lowers the floor a further 2 dB but risks warbly 'underwater' artefacts.
Source audio already has a low room-noise floor (about -53 dB vs speech about -25 dB).
Input : the source video's audio (48 kHz stereo PCM) and work/proxy.mp4
Output: work/audio_clean.wav and work/proxy.mp4 (cleaned audio, AAC 192k), public/proxy.mp4 re-linked.
"""
import json, os, re, subprocess, sys

SRC = os.environ.get("SOURCE_VIDEO", os.path.expanduser("~/Downloads/C1193.MP4"))
RAW, CLEAN = "work/audio_48k.wav", "work/audio_clean.wav"
BASE = "highpass=f=70,afftdn=nr=20:nf=-50:tn=1,agate=threshold=0.006:ratio=2.5:range=0.25:attack=10:release=300"
TARGET = "I=-16:TP=-1.5:LRA=11"

def run(*a): return subprocess.run(a, capture_output=True, text=True)

if not os.path.exists(RAW):
    run("ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", SRC, "-map", "0:a:0", "-vn", "-c:a", "pcm_s16le", RAW)

# pass 1: measure
p1 = run("ffmpeg", "-hide_banner", "-i", RAW, "-af", f"{BASE},loudnorm={TARGET}:print_format=json", "-f", "null", "-")
m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p1.stderr, re.S).group(0))
meas = f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}"
# pass 2: apply (linear)
run("ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", RAW,
    "-af", f"{BASE},loudnorm={TARGET}:{meas}:linear=true", "-ar", "48000", CLEAN)

def lufs(f):
    t = run("ffmpeg", "-hide_banner", "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-").stderr
    return re.findall(r"I:\s+(-?[\d.]+) LUFS", t)[-1], re.findall(r"Peak:\s+(-?[\d.]+) dBFS", t)[-1]
def vol(f, ss, d):
    t = run("ffmpeg", "-hide_banner", "-ss", str(ss), "-t", str(d), "-i", f, "-af", "volumedetect", "-f", "null", "-").stderr
    return re.search(r"mean_volume: (-?[\d.]+)", t).group(1)

print("loudness  before: %s LUFS, peak %s dBFS | after: %s LUFS, peak %s dBFS" % (*lufs(RAW), *lufs(CLEAN)))
nb, sb, na, sa = (float(vol(RAW, 647.7, 0.7)), float(vol(RAW, 630, 40)), float(vol(CLEAN, 647.7, 0.7)), float(vol(CLEAN, 630, 40)))
print("room noise in silence (647.6 s): %.1f -> %.1f dB | speech-to-noise gap: %.1f -> %.1f dB (bigger is cleaner)" % (nb, na, sb - nb, sa - na))

# swap audio into the proxy, copy video
if "--no-remux" not in sys.argv:
    r = run("ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", "work/proxy.mp4", "-i", CLEAN,
            "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
            "-movflags", "+faststart", "work/proxy_clean.mp4")
    if r.returncode: sys.exit(r.stderr)
    os.replace("work/proxy_clean.mp4", "work/proxy.mp4")
    if os.path.lexists("public/proxy.mp4"): os.remove("public/proxy.mp4")
    os.link("work/proxy.mp4", "public/proxy.mp4")
    print("proxy.mp4 now carries the cleaned audio")
