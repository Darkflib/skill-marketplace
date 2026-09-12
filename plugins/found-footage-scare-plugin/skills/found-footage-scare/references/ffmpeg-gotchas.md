# ffmpeg, zsh and ImageMagick traps

Each of these produced a confusing failure or a silently wrong result. Read before writing a filter graph — several fail in ways that don't look like their cause.

## Contents

- [zsh eats your filter graph](#zsh-eats-your-filter-graph)
- [Odd dimensions break H.264](#odd-dimensions-break-h264)
- [Which expressions are evaluated per frame](#which-expressions-are-evaluated-per-frame)
- [Filters that output video from audio](#filters-that-output-video-from-audio)
- [drawtext may not exist](#drawtext-may-not-exist)
- [ImageMagick has no default font](#imagemagick-has-no-default-font)
- [alimiter has auto-level on](#alimiter-has-auto-level-on)
- [Sample peak vs true peak](#sample-peak-vs-true-peak)
- [amix normalises by default](#amix-normalises-by-default)
- [Mono to stereo costs 3 dB](#mono-to-stereo-costs-3-db)
- [Trim before the limiter, not after](#trim-before-the-limiter-not-after)
- [aecho attenuates everything](#aecho-attenuates-everything)
- [adeclick can make things worse](#adeclick-can-make-things-worse)
- [Cutting audio from a container comes out short](#cutting-audio-from-a-container-comes-out-short)
- [concat demuxer overshoots duration](#concat-demuxer-overshoots-duration)
- [Geometry pops between segments](#geometry-pops-between-segments)
- [Low bitrates eat your grain](#low-bitrates-eat-your-grain)
- [Stripping ffmpeg's signature](#stripping-ffmpegs-signature)

---

## zsh eats your filter graph

Two separate zsh behaviours mangle filter strings, both silently producing a *different valid-looking string* rather than an error at the shell level.

**Array subscripts.** `$VAR[name]` is subscript syntax:

```bash
# broken — zsh reads $HOLD1[intro] as a subscript
xfade=transition=fade:duration=$FADE:offset=$HOLD1[intro]
# correct
xfade=transition=fade:duration=$FADE:offset=${HOLD1}[intro]
```

**History modifiers.** `$VAR:e` applies the "extension" modifier, eating the character:

```bash
# broken — $POS_Y:e is a modifier; ffmpeg receives "of_action=repeat"
overlay=x=$POS_X:y=$POS_Y:eof_action=repeat
# correct
overlay=x=${POS_X}:y=${POS_Y}:eof_action=repeat
```

The symptom is an ffmpeg error about a parameter you didn't write. **Brace every variable inside a filter graph** and neither can bite.

## Odd dimensions break H.264

`yuv420p` chroma subsampling needs even width and height. A still that is 1672×941 fails to encode. Scale or crop to even numbers — and if you're going to crop anyway for camera-shake slack, do both in one step:

```bash
scale=1932:1088,crop=1920:1080
```

## Which expressions are evaluated per frame

Not all filter parameters accept time-varying expressions, and the ones that don't will silently evaluate once at initialisation:

| filter | per-frame | evaluated once |
|---|---|---|
| `crop` | `x`, `y` | `w`, `h` |
| `scale` | only with `eval=frame` | default |
| `overlay` | `x`, `y` | — |

So a zoom implemented as `crop=w='iw/(1+0.05*t)'` does nothing. Use `scale` with `eval=frame` and crop to a fixed size afterwards:

```bash
scale=w='trunc(1932*(1+0.12*t/3)/2)*2':h='trunc(1088*(1+0.12*t/3)/2)*2':eval=frame,
crop=1920:1080
```

The `trunc(…/2)*2` keeps the intermediate dimensions even at every frame. `zoompan` is the other option but tends to jitter on small increments.

## Filters that output video from audio

`showspectrumpic`, `showwavespic` and `showvolume` take audio and emit video. Passing them via `-af` fails with *"Output file does not contain any stream"*, which doesn't hint at the cause:

```bash
# broken
ffmpeg -i in.wav -af "showspectrumpic=s=1100x260" out.png
# correct
ffmpeg -i in.wav -filter_complex "[0:a]showspectrumpic=s=1100x260[v]" -map "[v]" -frames:v 1 out.png
```

## drawtext may not exist

Current homebrew-core ffmpeg **dropped freetype from its dependencies entirely** — there's no build flag to flip and no `--with-freetype` option. Check before planning any burned-in text:

```bash
ffmpeg -hide_banner -filters | grep -q ' drawtext ' && echo OK || echo MISSING
```

When it's missing, the practical route is to render text to transparent PNGs with ImageMagick and composite them with `overlay`. For a clock that only changes once per second you need one PNG per second, not per frame — feed them through the concat demuxer with explicit durations, which also lets you make the clock stutter or skip:

```bash
# list.txt:  file 'ts000.png'
#            duration 1.000
#            ...
#            file 'ts024.png'      <- last entry repeated, no duration
ffmpeg -i video.mp4 -f concat -safe 0 -i list.txt \
  -filter_complex "[1:v]fps=30,format=rgba[osd];[0:v][osd]overlay=x=${X}:y=${Y}:eof_action=repeat[v]" \
  -map "[v]" ...
```

This is more control than `drawtext` gives you, so it's worth doing even where `drawtext` exists.

Docker is the alternative if you need `drawtext` specifically — `jrottenberg/ffmpeg:7-ubuntu` has it, entrypoint is ffmpeg itself. Check the architecture; some images are amd64-only and crawl under emulation on Apple Silicon.

## ImageMagick has no default font

ImageMagick 7 on macOS fails with ``unable to read font `' `` when you use `-annotate` or `-draw` without an explicit font. Pass a path:

```bash
magick -size 760x44 xc:none \
  -font "/System/Library/Fonts/Supplemental/Courier New Bold.ttf" -pointsize 28 \
  -fill black -annotate +11+33 "$TXT" \
  -fill white -annotate +9+31 "$TXT" \
  out.png
```

Drawing the text twice at a small offset is a cheap drop shadow, which is what keeps an overlay legible over varying backgrounds.

## alimiter has auto-level on

`alimiter`'s `level` option defaults to **true**, which renormalises output back up to the ceiling. The consequence is that lowering `limit` does not lower your output — it can *raise* it. Pass `level=disabled` for it to behave like a limiter:

```bash
alimiter=limit=0.80:level=disabled:attack=1:release=60
```

With auto-level off the behaviour is linear and predictable. Measured on one dense mix:

```
limit=0.90 → -0.7 dBTP      limit=0.80 → -1.7 dBTP      limit=0.70 → -2.9 dBTP
```

## Sample peak vs true peak

`alimiter` caps **sample** peaks. `ebur128=peak=true` reports **true** (intersample) peaks, which on dense limited material run ~1.5 dB higher. A file can read +0.1 dBFS while the limiter is nominally holding −1.4.

The fix is real headroom, not a tighter ceiling — and note this is exactly the case where tightening `limit` without `level=disabled` makes things worse, not better.

## amix normalises by default

`amix` divides by the number of inputs, so a quiet bed drops ~6 dB the instant a loud layer arrives — it sounds like ducking and it's easy to misdiagnose as a compressor problem:

```bash
amix=inputs=4:duration=first:normalize=0
```

## Mono to stereo costs 3 dB

`aformat=channel_layouts=stereo` on a **mono** source applies ffmpeg's power-preserving rematrix — it divides by √2, so the layer lands 3.01 dB below where the `volume=` you wrote implies. Measured on one mono file:

```
no conversion                     max -3.6 dB
aformat=channel_layouts=stereo    max -6.6 dB      <- 3.0 dB gone
pan=stereo|c0=c0|c1=c0            max -3.6 dB      <- unity
```

It's silent and it only hits some of your layers — mono sources lose 3 dB while already-stereo ones don't — so it quietly skews the balance between them.

Use `pan=stereo|c0=c0|c1=c0` for mono. Do **not** apply it to a stereo source: `c1=c0` replaces the right channel with the left. Probe rather than assume:

```bash
ch=$(ffprobe -v error -select_streams a:0 -show_entries stream=channels -of csv=p=0 in.wav)
[ "$ch" = 1 ] && F="pan=stereo|c0=c0|c1=c0" || F="aformat=channel_layouts=stereo"
```

## Trim before the limiter, not after

A limiter holding your ceiling is not the same as a mix that fits. Summed sting layers can hit **+7 dBFS** pre-limiter, which means ~8 dB of gain reduction — and a limiter working that hard flattens the transient the sting exists to deliver, reproducing the brickwalled sound of the source sample you were trying to avoid.

Put a bus trim of a few dB *before* the limiter and the reduction drops to ~2 dB. Judge it by the gain reduction being applied, not by the output peak, which looks fine either way.

Crest factor is the quick check: a crushed master runs ~7 dB, one with its transient intact ~13 dB.

## aecho attenuates everything

`aecho=in_gain:out_gain:delays:decays` — `out_gain` scales the **whole output**, not just the echoes. `aecho=0.9:0.45:…` costs you 7 dB across the entire branch. Either keep `out_gain` near 1.0 and control the tail with `decays`, or put a compensating `volume` after it.

## adeclick can make things worse

On low-bitrate lossy sources (32 kbps AAC, say) `adeclick`'s autoregressive interpolator misreads the noise floor as damage and patches in discontinuities. Measured on one 29s bed: **3 transients before, 7 after**.

Always measure before and after any restoration filter rather than assuming it helped. On genuinely noisy low-bitrate material, leaving faint artefacts alone usually beats any available repair.

## Cutting audio from a container comes out short

Seeking into an mp4/mkv and asking for N seconds of audio gives you slightly less than N. A 29.1s bed cut from a camera mp4 came out **29.077s — 23 ms short**.

The cause is the container's audio stream carrying a non-zero `start_time` (AAC encoder priming delay), which the seek-and-duration arithmetic works against:

```bash
ffprobe -v error -select_streams a -show_entries stream=start_time -of default=nw=1 in.mp4
# start_time=0.139000
```

Three things worth knowing, because two obvious fixes don't work:

- It is **not** about which side `-t` is on. Input-side and output-side `-t` both produce 29.077s.
- `apad=whole_dur=29.1` does **not** fix it (still 29.077), because `whole_dur` measures against the same offset timeline.
- `asetpts=PTS-STARTPTS,atrim=0:29.1` does **not** fix it either.

What works is decoding to WAV first, which normalises `start_time` to 0, then cutting from that:

```bash
ffmpeg -i in.mp4 -vn -ac 1 -c:a pcm_s16le full.wav
ffmpeg -ss 7.9 -t 29.1 -i full.wav -af "afade=t=out:st=27.1:d=2" bed.wav   # exactly 29.100
```

Tens of milliseconds sounds negligible until you remember the sting is aligned to two frames (66 ms) — a bed that ends 23 ms early against picture is a quarter of that budget spent on nothing. Extract first, cut second, and the problem disappears for every downstream step.

## concat demuxer overshoots duration

The concat demuxer's final entry (repeated without a `duration` line) gets extended, and rounding across many short entries accumulates. A graph that should produce 24.1s produced 25.13s. Set the output length explicitly with `-t`, or `-shortest`.

## Geometry pops between segments

If one segment goes through `scale=1932:1088,crop=1920:1080` and another through plain `scale=1920:1080`, there's a ~0.6% scale difference that shows as a visible pop at the cut. Put **every** segment through the same geometry chain even when only one of them needs the slack.

Similarly, put shared grain or grading *after* concatenation, not per-segment, or the segments won't match.

## Low bitrates eat your grain

Deliberate grain and a camera-matching bitrate pull against each other. At ~1 Mbps for 720p, x264 spends nothing on a static shot and quantises light grain to zero, then restores it at the next refresh — the viewer sees the picture freeze and un-freeze. It's subtle and it undoes the one thing grain was there to do.

Measured on the same 20s source at 1 Mbps 720p, counting frames whose inter-frame difference (`signalstats` YDIF) fell below 0.01:

```
default                    25 dead (8%)   max YDIF 9.44
-tune grain                31 dead (9%)   max YDIF 2.03   <- best
-tune grain + aq-mode=3    10 dead (3%)   max YDIF 9.77
```

**Judge this by the restore spike, not the dead-frame count** — they point at different options. `-tune grain` leaves slightly *more* still frames but cuts the pop by 4.6x, and the pop is the part you see. Optimising the dead-frame count picks `aq-mode=3`, which looks best on that metric and still jumps.

If you need both heavy grain and a low bitrate, raise the noise strength so more of it survives quantisation, or accept a higher bitrate and lose some provenance realism. You cannot have all three.

## Stripping ffmpeg's signature

ffmpeg writes `encoder=Lavf…` into mp4 metadata. To remove it and control the container identity:

```bash
-brand mp42 -movflags +faststart \
-metadata creation_time="2026-09-12T02:14:41.000000Z" \
-fflags +bitexact -flags:v +bitexact -flags:a +bitexact
```

`creation_time` is UTC and is displayed converted to **local** time, so it rarely equals the clock you burned into the picture. Don't reason about the offset — compute it, because DST boundaries are exactly where this goes wrong:

```bash
python3 -c "import datetime,zoneinfo; print(datetime.datetime(2026,10,31,3,14,7,
  tzinfo=zoneinfo.ZoneInfo('Europe/London')).astimezone(datetime.timezone.utc)
  .strftime('%Y-%m-%dT%H:%M:%S.000000Z'))"
```

The trap worth naming: UK clocks go back on the **last Sunday in October**, so a Halloween-dated file is GMT (offset 0) while a file dated a week earlier is BST (offset +1). Halloween is when this technique gets used, and applying a remembered "+1 for British Summer Time" on 31 October puts the metadata an hour out of step with the burned-in clock — which is the precise tell the whole section exists to avoid.
