# Designing and mixing the sting

The sting is the payload. This covers getting layers to sit together, aligning them to picture, and gain staging so the result isn't clipped mush.

## Align onsets, not peaks

Sound files carry arbitrary leading silence, and different sources have wildly different attack shapes. Two measurements decide everything:

- **onset** — first sample reaching ~10% of peak
- **time to peak** — how long the attack takes

From two real scream samples:

```
stalker-scream.mp3   onset 0.104s → peak 0.138s     34 ms attack — instant hit
scream.mp3           onset 0.025s → peak 0.550s    525 ms attack — slow swell
```

To make both *start* at time T, the delay for each is `T − its_own_leading_silence`. That's why delays end up as odd numbers like `20929` and `21008` rather than a round figure — they're compensating for 104ms and 25ms of silence respectively.

**Don't align peaks instead.** Pulling a slow-swell sample earlier so its peak coincides with the cut means it starts before the cut, which telegraphs. Align onsets and accept that a slow layer peaks slightly late — or trim into its attack (below).

## Audio leads picture by two frames

Landing audio on exactly the same frame as the visual cut reads as *late*. About 66ms of lead at 30fps reads as simultaneous and hits harder. So for a cut at 21.100s, target 21.033s and derive the per-file delays from there.

Verify afterwards by measuring the onset of the rendered mix rather than trusting the arithmetic.

## When layers collide, separate in time not frequency

Two sources that peak in the same band cannot be EQ'd apart. Measure band energy before planning any EQ move:

```
                 0-200   200-1k    1k-4k   4k-12k     12k+
stalker          -28.8    -13.0     -7.8    -17.3    -31.1
scream           -27.3    -24.5    -20.8    -31.5    -50.9
```

Both peak in 1–4 kHz. No highpass or shelf separates them; the louder one simply masks the other, and the symptom is *"I only hear the second one once the first decays"*.

The fix is **time separation**. Make the fast-attack source a short impact and let the other carry the sustain:

```bash
# impact: first 0.75s only, fading out from 0.45s, highpassed to clear the sub
atrim=end=0.75,asetpts=PTS-STARTPTS,
highpass=f=400:poles=2,
afade=t=out:st=0.45:d=0.30,
volume=-5dB

# sustain: trimmed INTO its own swell so it arrives fast, compressed to hold level
atrim=start=0.30,asetpts=PTS-STARTPTS,afade=t=in:d=0.01,
acompressor=threshold=0.05:ratio=6:attack=5:release=250:makeup=2,
volume=6dB
```

Trimming into the swell is what fixes "we only hear the tail" — it removes the slow ramp so the layer is at full level from the first instant instead of arriving after the impact has already peaked.

The 10ms fade-in avoids a click from starting mid-waveform. It's masked by the impact anyway, but costs nothing.

## Compress the sustaining layer

A raw scream swells and decays. Under an impact that means it's only audible in the middle. Compression flattens it so it holds:

Measured on one branch after `acompressor=threshold=0.05:ratio=6:attack=5:release=250:makeup=2`:

```
0.00s -18.3   0.25s -18.3   0.50s -18.3   0.75s -18.4   1.00s -18.9
1.25s -19.3   1.50s -20.7   1.75s -20.9   2.00s -25.5   2.25s -29.6
```

Flat for 1.75s, then the source material genuinely runs out. **Measure the branch in isolation** rather than trying to tune it inside the full mix — it's much faster to see what's happening.

## Samples are shorter than you think

A 2.9s file trimmed 0.3s into its attack gives ~2.1s of usable material against a 3s hold. Options, in order of preference:

1. **Let it end.** A scream that stops while the face is still on screen is more disturbing than one that runs continuously. Silence with the threat still visible is a strong beat.
2. **Add a reverb tail** so it rings past the cut into the next shot — the empty plate returning with the scream still decaying over it is very effective.
3. Shorten the visual hold to match.

For the tail, `aecho` with several taps approximates a room. Watch `out_gain` (see gotchas — it scales the whole branch):

```bash
aecho=0.8:0.9:230|520|950|1500:0.40|0.28|0.18|0.10
```

## Synthesise the sub

Most scream samples have nothing below 200 Hz. Measured: two samples at −28.5 and −27.3 dB in 0–200 Hz, which is 20 dB below their own mid peaks. That's why they sound thin no matter how loud you make them.

A descending sine supplies the body. Sweep ~55→25 Hz with exponential decay:

```bash
aevalsrc='sin(2*PI*(55*t+(28-55)*t*t/(2*0.9)))*exp(-t*3.2)':s=48000:d=1.0
```

The phase term is the integral of a linear frequency ramp — instantaneous frequency is `55 − 30t`, so it stays positive across the 1s duration. Adding this lifted 0–200 Hz from −28 dB to −21 dB in the mix.

Judge the level for the target playback: generous on anything with real bass, restrained for phone speakers which reproduce nothing below ~40 Hz and will just eat headroom.

## Target level arc

```
lull              -49 dB
impact            -12 dB      ← ~37 dB jump, this is the mechanism
sustain           -17 to -24
falling           -31 dB
tail over cut     -42 dB
aftermath         -50 dB      ← quieter than the lull
```

Integrated ≈ −15 LUFS with LRA ≈ 22 LU. The large LRA is the point, not a defect — normalising it away destroys the scare.

Keep the bed quiet enough that people reach for the volume control. That's what makes the hit loud; the sting is only the payload.

## Cutting the bed at the dropout

Killing the bed to true digital silence across the black frames is worth doing. The ear registers hiss *disappearing* far more sharply than a sound starting, so a tenth of a second of real nothing does disproportionate work:

```bash
[1:a]volume=0:enable='between(t,21.0,21.1)'[bed]
```

## Gain staging checklist

- `amix=…:normalize=0` — otherwise the bed ducks 6 dB when the sting lands
- `alimiter=…:level=disabled` — otherwise `limit` renormalises instead of limiting
- A bus trim of ~5 dB **before** the limiter, so it does ~2 dB of reduction rather than ~8. Crest factor is the check: ~7 dB is crushed, ~13 dB has its transient intact
- `pan=stereo|c0=c0|c1=c0` for mono layers, not `aformat=channel_layouts=stereo`, which costs them 3.01 dB
- Leave ~1.5 dB for intersample overshoot; `limit=0.80` lands around −1.7 dBTP
- Mix at 48 kHz even when a source is band-limited — resampling restores nothing, but it stops a full-bandwidth sting being dragged down to the bed's ceiling
