#!/usr/bin/env python3
"""
Verify a rendered scare sequence by measuring it, since you cannot watch it.

  verify_sequence.py FILE                 report the structure it detects
  verify_sequence.py FILE --audio-cut 21.1  also check audio onset vs that cut

Reports beat boundaries, black dropouts, whether grain is present, whether the
film returns to its opening shot, and - if the file has audio - the level arc
and where the sting lands relative to the cut.

Stdlib + ffmpeg/ffprobe only.
"""

import argparse, json, math, os, re, struct, subprocess, sys, tempfile, wave


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    out = sh(["ffprobe", "-v", "error", "-show_entries",
              "format=duration:stream=codec_type,width,height,r_frame_rate",
              "-of", "json", path]).stdout
    d = json.loads(out or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    fps = 30.0
    if v.get("r_frame_rate", "0/0") != "0/0":
        n, _, den = v["r_frame_rate"].partition("/")
        try: fps = float(n) / float(den or 1)
        except ZeroDivisionError: pass
    return {"duration": float(d.get("format", {}).get("duration", 0) or 0),
            "w": v.get("width"), "h": v.get("height"), "fps": fps, "has_audio": a is not None}


def frame_stats(path):
    """Per-frame mean luma (YAVG) and mean inter-frame difference (YDIF).

    YDIF is what detects grain. Spatial noise barely moves a frame's MEAN luma,
    so measuring variance of YAVG reports a grained clip as frozen. YDIF
    compares corresponding pixels between consecutive frames and goes to ~0
    only when the frame is genuinely static.

    Measured at full resolution - downscaling averages grain away too.
    """
    r = sh(["ffmpeg", "-v", "error", "-i", path, "-vf",
            "signalstats,metadata=print:file=-", "-f", "null", "-"])
    ys, ds = [], []
    for line in r.stdout.splitlines():
        m = re.search(r"lavfi\.signalstats\.YAVG=([\d.]+)", line)
        if m: ys.append(float(m.group(1)))
        m = re.search(r"lavfi\.signalstats\.YDIF=([\d.]+)", line)
        if m: ds.append(float(m.group(1)))
    return ys, ds


def black_spans(path):
    r = sh(["ffmpeg", "-v", "info", "-i", path, "-vf",
            "blackdetect=d=0.02:pic_th=0.98:pix_th=0.10", "-f", "null", "-"])
    out = []
    for m in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr):
        out.append((float(m.group(1)), float(m.group(2))))
    return out


def cuts(ys, fps, thresh=8.0):
    """Frames where mean luma jumps - approximates hard cuts."""
    return [(i / fps, abs(ys[i] - ys[i - 1]))
            for i in range(1, len(ys)) if abs(ys[i] - ys[i - 1]) > thresh]


def grain_present(ds, fps, span):
    """A held shot should still differ frame to frame. A dead-flat run means a
    frozen still, which silently tells the viewer nothing will happen here."""
    a, b = int(span[0] * fps), int(span[1] * fps)
    seg = [x for x in ds[a:b]]
    if len(seg) < 5:
        return None
    return sum(seg) / len(seg)


def returns_to_open(path, dur):
    """Compare an early frame with a late one. A scare that ends on the payoff
    skips the aftermath beat, which is where most of the unease lives."""
    tmp = tempfile.mkdtemp()
    a, b = f"{tmp}/a.png", f"{tmp}/b.png"
    sh(["ffmpeg", "-v", "error", "-y", "-ss", "0.5", "-i", path, "-frames:v", "1",
        "-vf", "scale=64:36,format=gray", a])
    sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.6, dur - 0.6):.2f}", "-i", path,
        "-frames:v", "1", "-vf", "scale=64:36,format=gray", b])
    def raw(p):
        # binary out - must not go through sh(), which decodes as text
        return subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo",
                               "-pix_fmt", "gray", "-"], capture_output=True).stdout
    ra, rb = raw(a), raw(b)
    if not ra or not rb or len(ra) != len(rb):
        return None
    diff = sum(abs(x - y) for x, y in zip(ra, rb)) / len(ra)
    for p in (a, b):
        try: os.unlink(p)
        except OSError: pass
    return diff


def audio_arc(path, cut):
    segs = [("lull", 0, max(1, cut - 1)), ("impact", cut - 0.07, 0.45),
            ("sustain", cut + 0.5, 1.5), ("aftermath", cut + 3.2, 1.0)]
    out = []
    for name, ss, t in segs:
        if ss < 0:
            continue
        r = sh(["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{ss}", "-t", f"{t}",
                "-i", path, "-af", "volumedetect", "-f", "null", "-"])
        m = re.search(r"mean_volume:\s*(-?[\d.]+)", r.stderr)
        out.append((name, float(m.group(1)) if m else None))
    return out


def audio_onset(path, cut, fps):
    """Where does the sting actually start relative to the cut?"""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    ss = max(0, cut - 0.6)
    r = sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", "1.2", "-i", path,
            "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", tmp])
    try:
        with wave.open(tmp, "rb") as w:
            n, sr = w.getnframes(), w.getframerate()
            d = struct.unpack(f"<{n}h", w.readframes(n))
    except Exception:
        return None
    finally:
        try: os.unlink(tmp)
        except OSError: pass
    pk = max(abs(x) for x in d) if d else 0
    if pk == 0:
        return None
    on = next(i for i, x in enumerate(d) if abs(x) >= pk * 0.10) / sr + ss
    return on, (cut - on) * 1000, (cut - on) * fps


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--audio-cut", type=float, help="time of the visual cut to the scare")
    args = p.parse_args()

    info = probe(args.file)
    print(f"\n=== {os.path.basename(args.file)} ===")
    print(f"  {info['duration']:.2f}s  {info['w']}x{info['h']}  {info['fps']:.2f}fps"
          f"  audio: {'yes' if info['has_audio'] else 'NONE'}")
    if info["w"] and (info["w"] % 2 or info["h"] % 2):
        print("  !! odd dimensions - yuv420p cannot encode this")

    ys, ds = frame_stats(args.file)
    if not ys:
        print("  could not read frame statistics")
        return

    bl = black_spans(args.file)
    print(f"  black spans: {len(bl)}" + ("" if bl else "   <- no dropout before the hit"))
    for s, e in bl:
        print(f"     {s:.2f}s - {e:.2f}s  ({(e-s)*info['fps']:.1f} frames)")

    cs = cuts(ys, info["fps"])
    print(f"  hard cuts detected: {len(cs)}")
    for t, mag in cs[:8]:
        print(f"     {t:6.2f}s   luma jump {mag:.1f}")

    g = grain_present(ds, info["fps"], (0.3, min(3.0, info["duration"] * 0.2)))
    if g is not None:
        verdict = "FROZEN still - no grain" if g < 0.15 else "live (grain present)"
        print(f"  opening-shot inter-frame diff: {g:.3f}  <- {verdict}")

    d = returns_to_open(args.file, info["duration"])
    if d is not None:
        verdict = "returns to the opening shot" if d < 12 else "ends on a different shot - no aftermath beat"
        print(f"  first vs last frame difference: {d:.1f}  <- {verdict}")

    if args.audio_cut and info["has_audio"]:
        print(f"  audio arc around the {args.audio_cut}s cut:")
        for name, v in audio_arc(args.file, args.audio_cut):
            print(f"     {name:10s} {v if v is not None else float('nan'):7.1f} dB")
        o = audio_onset(args.file, args.audio_cut, info["fps"])
        if o:
            on, ms, fr = o
            note = "leads picture" if ms > 10 else ("LATE - lands after the cut" if ms < -10 else "on the frame")
            print(f"     onset at {on:.3f}s -> {ms:+.0f} ms ({fr:+.1f} frames)  <- {note}")
    print()


if __name__ == "__main__":
    main()
