#!/usr/bin/env python3
"""
Audio source vetting for found-footage work: is this clip usable as a bed,
what's in it, and where is the quietest stretch?

Stdlib + ffmpeg/ffprobe only. Accepts anything ffmpeg can decode.

  analyze_audio.py FILE [FILE...]              report on each file
  analyze_audio.py FILE --window 29.1          also scan for the best N-second window
  analyze_audio.py FILE --exclude 43.8 47.2    hard-exclude a span from that scan
  analyze_audio.py FILE --onset                onset + attack shape (for sting layers)

Why the two transient passes: 0.25s RMS windows find sustained events but average
away sharp transients; 20ms peak windows resolve individual clicks and footsteps.
A single pass will miss one kind or the other.
"""

import argparse, json, math, os, re, struct, subprocess, sys, tempfile, wave

SR = 48000


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stderr


def decode(path):
    """Decode to mono 16-bit PCM at SR. Returns (samples, sample_rate)."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", path, "-vn",
         "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", tmp],
        check=True, capture_output=True)
    with wave.open(tmp, "rb") as w:
        n, sr = w.getnframes(), w.getframerate()
        data = struct.unpack(f"<{n}h", w.readframes(n))
    os.unlink(tmp)
    return data, sr


def db(x, ref=32768.0):
    return 20 * math.log10(x / ref) if x > 0 else -120.0


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,codec_name,sample_rate,channels,bit_rate",
         "-of", "json", path], capture_output=True, text=True).stdout
    d = json.loads(out or "{}")
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), {})
    return {
        "duration": float(d.get("format", {}).get("duration", 0) or 0),
        "codec": a.get("codec_name", "?"),
        "sample_rate": a.get("sample_rate", "?"),
        "channels": a.get("channels", "?"),
        "bit_rate": a.get("bit_rate", "?"),
    }


def loudness(path):
    """Integrated LUFS, loudness range, true peak. LRA is what picks a bed."""
    err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path,
               "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = err[-3000:]
    def grab(pat):
        m = re.findall(pat, tail)
        return float(m[-1]) if m else None
    return grab(r"I:\s*(-?[\d.]+)\s*LUFS"), grab(r"LRA:\s*([\d.]+)\s*LU"), grab(r"Peak:\s*(-?[\d.]+)\s*dBFS")


BANDS = [(20, 200), (200, 1000), (1000, 4000), (4000, 12000), (12000, 23000)]


def band_energy(path, sample_rate):
    """Mean dB per band. Two sources peaking in the same band cannot be EQ'd apart.

    Bands above the file's Nyquist are skipped - a highpass above Nyquist produces
    nonsense coefficients and reports a plausible-looking level for a band that
    physically cannot contain anything.
    """
    try:
        nyq = int(sample_rate) / 2
    except (TypeError, ValueError):
        nyq = float("inf")
    out = []
    for lo, hi in BANDS:
        if lo >= nyq:
            out.append(None)
            continue
        err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                   f"highpass=f={lo}:poles=2,lowpass=f={min(hi, nyq * 0.98):.0f}:poles=2,volumedetect",
                   "-f", "null", "-"])
        m = re.search(r"mean_volume:\s*(-?[\d.]+)", err)
        out.append(float(m.group(1)) if m else None)
    return out


def envelope(d, sr, win):
    step = max(1, int(sr * win))
    return [(i / sr, db(math.sqrt(sum(x * x for x in d[i:i + step]) / step)))
            for i in range(0, len(d) - step, step)]


def peaks(d, sr, win):
    step = max(1, int(sr * win))
    return [(i / sr, db(max(abs(x) for x in d[i:i + step])))
            for i in range(0, len(d) - step, step)]


def flag(series, win, excess, local=2.0):
    """Flag windows exceeding the LOCAL median, so slow drift doesn't swamp it."""
    half = max(1, int(local / win))
    hits = []
    for j, (t, v) in enumerate(series):
        lo, hi = max(0, j - half), min(len(series), j + half)
        med = sorted(x for _, x in series[lo:hi])[(hi - lo) // 2]
        if v - med > excess:
            hits.append((t, v, v - med))
    return hits


def cluster(hits, gap=0.3):
    out = []
    for t, v, e in hits:
        if out and t - out[-1][1] <= gap:
            out[-1][1] = t
            out[-1][2] = max(out[-1][2], v)
            out[-1][3] = max(out[-1][3], e)
        else:
            out.append([t, t, v, e])
    return out


def best_window(hits, total, dur, fade=2.0, exclude=None):
    """Score every start position, weighting each transient by the fade envelope."""
    def gain(rel):
        if rel < fade:       return rel / fade
        if rel > dur - fade: return (dur - rel) / fade
        return 1.0
    # hits are clusters: (start, end, peak_db, excess_db)
    cands, s = [], 0.0
    while s + dur <= total:
        if not (exclude and s < exclude[1] and s + dur > exclude[0]):
            inside = [(a, e) for a, b, _, e in hits if s <= a <= s + dur]
            cost = sum(e * gain(a - s) for a, e in inside)
            cands.append((cost, s, len(inside)))
        s += 0.1
    return sorted(cands)


def onset_report(d, sr):
    """Onset and attack shape - what you need to align sting layers."""
    pk = max(abs(x) for x in d)
    if pk == 0:
        return None
    on = next(i for i, x in enumerate(d) if abs(x) >= pk * 0.10) / sr
    at = d.index(max(d, key=abs)) / sr
    off = max(i for i, x in enumerate(d) if abs(x) >= pk * 0.05) / sr
    return on, at, off


def report(path, args):
    print(f"\n=== {os.path.basename(path)} ===")
    info = probe(path)
    print(f"  {info['duration']:.2f}s  {info['codec']}  "
          f"{info['sample_rate']}Hz  {info['channels']}ch  {info['bit_rate']}bps")

    I, lra, peak = loudness(path)
    if I is not None:
        notes = []
        # LRA needs a reasonable span to mean anything - it reads 0.0 on short
        # one-shots, which is "too short to measure", not "flat as room tone".
        if lra is not None and info["duration"] >= 10:
            if lra <= 3:    notes.append("flat enough for a bed")
            elif lra >= 10: notes.append("events present")
        elif lra is not None:
            notes.append("too short for LRA to mean anything")
        if peak is not None and peak > -0.1:
            notes.append(f"CLIPPING at {peak:+.1f} dBFS - attenuate before layering")
        lra_s = f"{lra:>5.1f}" if lra is not None else "  n/a"
        peak_s = f"{peak:>6.1f}" if peak is not None else "   n/a"
        suffix = ("  <- " + "; ".join(notes)) if notes else ""
        print(f"  integrated {I:>6.1f} LUFS   LRA {lra_s} LU   true peak {peak_s} dBFS{suffix}")

    be = band_energy(path, info['sample_rate'])
    print("  band dB:  " + "  ".join(
        f"{lo}-{hi}:{v:.1f}" if v is not None else f"{lo}-{hi}:n/a"
        for (lo, hi), v in zip(BANDS, be)))

    d, sr = decode(path)
    total = len(d) / sr

    if args.onset:
        o = onset_report(d, sr)
        if o:
            on, at, off = o
            print(f"  onset {on:.3f}s -> peak {at:.3f}s  ({(at-on)*1000:.0f} ms attack)"
                  f"   decays by {off:.2f}s")
            print(f"  to land its onset at time T, delay by (T - {on:.3f})s")

    rms = cluster(flag(envelope(d, sr, 0.25), 0.25, 6.0))
    shp = cluster(flag(peaks(d, sr, 0.020), 0.020, 8.0))
    print(f"  events   (0.25s RMS, >6dB over local median): {len(rms)}")
    for a, b, v, e in rms[:12]:
        print(f"     {a:6.2f}s - {b:6.2f}s   peak {v:6.1f} dBFS  +{e:4.1f}dB")
    print(f"  transients (20ms peak, >8dB over local median): {len(shp)}")
    for a, b, v, e in shp[:12]:
        print(f"     {a:6.2f}s - {b:6.2f}s   peak {v:6.1f} dBFS  +{e:4.1f}dB")
    if len(shp) > 12:
        print(f"     ... and {len(shp)-12} more")

    if args.window:
        ex = tuple(args.exclude) if args.exclude else None
        cands = best_window(shp, total, args.window, args.fade, ex)
        if not cands:
            print(f"  no {args.window}s window fits"
                  + (" clear of the exclusion" if ex else ""))
        else:
            print(f"  best {args.window}s windows"
                  + (f" (excluding {ex[0]}-{ex[1]}s)" if ex else "") + ":")
            for c, s, n in cands[:5]:
                print(f"     start {s:6.2f}s -> {s+args.window:6.2f}s   cost {c:6.1f}   {n} transient(s)")
            print(f"  -> ffmpeg -ss {cands[0][1]:.2f} -t {args.window} -i {os.path.basename(path)} ...")


def main():
    p = argparse.ArgumentParser(description="Vet audio sources for found-footage work")
    p.add_argument("files", nargs="+")
    p.add_argument("--window", type=float, help="scan for the quietest window of this length")
    p.add_argument("--fade", type=float, default=2.0, help="fade length used when scoring windows")
    p.add_argument("--exclude", type=float, nargs=2, metavar=("START", "END"),
                   help="span the window scan must avoid entirely")
    p.add_argument("--onset", action="store_true", help="report onset and attack shape")
    args = p.parse_args()
    for f in args.files:
        if not os.path.exists(f):
            print(f"\n=== {f} ===\n  NOT FOUND", file=sys.stderr)
            continue
        report(f, args)
    print()


if __name__ == "__main__":
    main()
