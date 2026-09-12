# Choosing and vetting source audio

Recipes for deciding which of several source clips is usable, finding a clean stretch inside one, and catching content you don't want. `scripts/analyze_audio.py` automates most of this; the commands below are for one-off checks and for understanding what the script reports.

## Loudness and dynamics

```bash
ffmpeg -hide_banner -nostats -i in.wav -af ebur128=peak=true -f null - 2>&1 | tail -14
```

Two numbers matter and they answer different questions:

- **Integrated (LUFS)** — how loud it is
- **LRA (LU)** — whether anything *happens* in it

**LRA is the one that picks a room-tone bed.** A usable bed measures 1–2 LU across its length. A clip measuring 20+ LU contains events however quiet it sounds overall. Real comparison:

```
source_38   -43.9 LUFS   peak -20.8 dBFS   LRA 23.9 LU   ← near-empty, one event
take_64     -22.3 LUFS   peak  -7.8 dBFS   LRA 14.8 LU   ← continuous activity
take_68     -22.0 LUFS   peak  -7.7 dBFS   LRA 21.3 LU   ← continuous activity
```

A 22 LU gap in integrated loudness between clips from the same camera is not a gain difference to be matched — it means they're recordings of different things.

## See it before trusting it

Spectrograms and waveforms answer "what is in this" faster than any statistic. Gain-match for a content comparison; leave levels raw to show the level difference:

```bash
ffmpeg -i in.wav -filter_complex \
  "[0:a]volume=22dB,showspectrumpic=s=1100x260:legend=1:scale=log:color=intensity[v]" \
  -map "[v]" -frames:v 1 spec.png
```

Note these need `-filter_complex`, not `-af` (see gotchas). Broad horizontal bands mean continuous noise like wind; vertical striations are transients; **stacked harmonic ladders are voices**.

## Read the burned-in clock first

Most CCTV footage carries the camera's own on-screen timestamp, and it is the **only** trustworthy record of when a clip was shot. Extract a frame and look before reaching for any statistic:

```bash
ffmpeg -v error -ss 2 -i in.mp4 -frames:v 1 -vf "crop=iw:60:0:0" osd.png
```

Everything else about the file lies. Measured on three clips from one camera:

```
file                    filename epoch (UTC)   burned-in OSD      picture
1789209049738_0.mp4     10:30:49               04:11:44           monochrome (IR)
1789217114464_0.mp4     12:45:14               13:45:12           colour
1789217184668_0.mp4     12:46:24               13:42:27           colour
```

The epoch in the filename is ~6 hours off the night clip, and it orders the two daytime clips **backwards** — the higher-numbered file is the earlier recording. `creation_time` is mux-finalisation time and is no better. Neither tells you anything about capture.

A frame also gives you the time of day directly, which saturation only infers. Reach for SATAVG below when there's no OSD, or to confirm what you read.

## Day vs night

When the plate is IR night footage, daytime ambience under it is an instant tell. Brightness won't distinguish them — IR illuminators make night footage as bright as day. **Saturation does**, because night mode swings the IR-cut filter out and the sensor produces exactly monochrome:

```bash
ffmpeg -v error -ss 5 -t 40 -i in.mp4 \
  -vf "fps=1/4,scale=320:-1,signalstats,metadata=print:file=-" -f null - 2>/dev/null \
  | awk -F= '/SATAVG/{s+=$2;n++} END {printf "SATAVG %.2f\n", s/n}'
```

```
source_38   SATAVG 0.00   YAVG 105.0   ← IR night
take_64     SATAVG 7.59   YAVG 102.2   ← daylight
take_68     SATAVG 7.65   YAVG  99.4   ← daylight
```

The YAVG column shows why luma is useless here — all three are within 6 points.

Note that `creation_time` in a camera export is usually the *export* time, not capture time, so it won't corroborate this.

## Finding events

Window size determines what you can see, and a single pass will miss things:

- **0.25s RMS windows** find sustained events but average away sharp transients
- **20ms peak windows** resolve individual footsteps, clicks and codec artefacts

Flag windows exceeding a **local** median (say ±2s) rather than a global threshold, so a gradual level drift doesn't swamp the result. `scripts/analyze_audio.py` does both passes.

Beware of threshold choice: at +3 dB over local median a natural hiss wander registers as an event and you'll wrongly conclude a file is unusable. +6 dB over the local median is a reasonable default for RMS; +8 dB for the 20ms peak pass.

## Reading what an event is

Before describing an event, look at its shape — and be willing to contradict an assumption about it, including the user's:

- **Broadband thud, no harmonic structure** → impact, footstep, door
- **Harmonic ladder up through the band** → a voice
- **Continuous energy concentrated below ~600 Hz** → wind on the mic
- **Isolated 20–40ms blips at very low level** → codec artefacts, not real sound

Duration is a strong cue: a 20–40ms blip is click-length. A footstep is 50–150ms. A spoken phrase runs to seconds and comes in clusters — an approach followed by a louder pass is a person moving past.

## Picking the best window

Rather than eyeballing gaps, score every candidate start position. Weight each transient by the fade envelope that will be applied, since something inside a fade-out matters less than something in the middle, and hard-exclude any window overlapping content you must avoid:

```python
def gain(rel, dur, fade):           # linear fade envelope
    if rel < fade:        return rel / fade
    if rel > dur - fade:  return (dur - rel) / fade
    return 1.0

cost = sum(excess_db * gain(t - start, dur, fade)
           for t, excess_db in transients
           if start <= t <= start + dur)
```

Pick the minimum cost. In one 64s source this found a window with roughly half the audible transient content of a hand-picked guess, and reliably avoided clipping the leading edge of an event the human eye missed.

Check the *tail* of the chosen window explicitly. A window ending 0.06s before a voice starts will still catch its first breath.

## Mains hum

Cameras near household wiring pick up mains hum, and a highpass placed to remove rumble usually sits *below* it — a 40 Hz highpass does nothing to 50 Hz. Probe the mains frequency and its neighbours before deciding:

```bash
for f in 40 48 50 52 60 80; do
  printf "%3dHz " $f
  ffmpeg -hide_banner -nostats -i in.wav -af "bandpass=f=$f:width_type=h:w=3,volumedetect" \
    -f null - 2>&1 | grep -m1 mean_volume
done
```

A real reading from a UK camera — 50 Hz standing ~7 dB above its neighbours:

```
40Hz -72.1   48Hz -69.7   50Hz -67.7   52Hz -71.3   60Hz -75.0   80Hz -80.3
```

A narrow notch removes it surgically. High Q matters: this took 50 Hz down 14.5 dB while costing only 2.8 dB broadband.

```bash
equalizer=f=50:width_type=q:w=12:g=-18      # 60 for North America
```

Check the neighbours as well as the fundamental — if 48 and 52 are also raised, it's broadband rumble rather than hum and a notch won't help.

## Building the bed

Prefer a single continuous pass over a looped shorter cell — a repeating hiss cell pulses audibly over 20+ seconds. Only loop if the source genuinely can't cover the duration.

```bash
ffmpeg -i source.mp4 -vn -ac 1 -c:a pcm_s16le source.wav          # decode FIRST
ffmpeg -ss 14.7 -t 29.1 -i source.wav \
  -af "highpass=f=40,volume=20dB,aresample=48000:filter_size=64:phase_shift=10,
       afade=t=in:d=2,afade=t=out:st=27.1:d=2" \
  -c:a pcm_s24le -ar 48000 bed.wav
```

Note the two steps. Cutting straight from the source container gives you a file tens of milliseconds short, because the container's audio stream carries a non-zero `start_time` — decode to WAV first and the length comes out exact. See `ffmpeg-gotchas.md`.

The 40 Hz highpass removes DC and handling rumble. `filter_size=64:phase_shift=10` is a high-quality swresample setting for when libsoxr isn't compiled in — check with `ffmpeg -version | grep -o enable-libsoxr`.

Verify the result measures 1–2 LU. If it doesn't, the window still contains something.

### If you must loop

Measure whether the head and tail match *before* reaching for a crossfade, because a crossfade fixes the discontinuity at the splice and nothing else:

```bash
ffmpeg -hide_banner -nostats -t 1 -i bed.wav -af volumedetect -f null - 2>&1 | grep mean
ffmpeg -hide_banner -nostats -sseof -1 -i bed.wav -af volumedetect -f null - 2>&1 | grep mean
```

Fold the tail over the head with equal-power curves (`qsin`, not `tri` — `tri` is constant-gain and dips through the middle of the overlap):

```bash
D=0.5; BODY=$(python3 -c "print(29.1-$D)")
ffmpeg -i bed.wav -i bed.wav -filter_complex \
  "[0:a]atrim=start=${BODY},asetpts=PTS-STARTPTS[tail];
   [1:a]atrim=start=0:end=${BODY},asetpts=PTS-STARTPTS[body];
   [tail][body]acrossfade=d=${D}:c1=qsin:c2=qsin[out]" -map "[out]" loop.wav
```

Measured on one bed this took the head-to-tail gap from 4.41 dB to 2.89 dB — better, not solved. The residue is the source drifting in level across the window, which no splice can fix. **If head and tail differ by more than ~2 dB, choose a different window rather than trusting the crossfade.**

## Incidental voices

Security audio catches passers-by. When a voice turns up, say so, keep it out of the deliverable, and note which working files still contain it. Don't suggest using it as atmosphere — a real person's voice captured incidentally is not ambience, whatever it sounds like. State it once and move on.
