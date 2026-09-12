#!/bin/zsh
# Mix a scare sting over a room-tone bed and mux to the silent sequence.
#
# Two layers plus a synthesised sub: a short IMPACT for the hit, and a WAIL that
# sustains under it. Delays are derived from each file's leading silence so both
# onsets land together - run analyze_audio.py --onset to get those numbers.

set -e
cd "$(dirname "$0")"

VID="scare.mp4"            # silent sequence from make_sequence.sh
BED="bed.wav"              # room tone, already the full length of VID
IMPACT="impact.mp3"        # fast-attack layer - the hit
WAIL="wail.mp3"            # slower layer - sustains underneath
OUT="scare_mixed.mp4"

HITT=21.100                # video cut to the scare, in seconds
LEAD=0.067                 # audio leads picture by ~2 frames at 30fps.
                           # Landing on the same frame reads as LATE.
DROP_START=21.000          # black frames: bed goes to true silence across them
DROP_END=21.100

# From analyze_audio.py --onset on each file:
IMPACT_SIL=0.104           # leading silence in IMPACT
WAIL_TRIM=0.30             # seconds to trim INTO the wail's attack, so it
                           # arrives at full level instead of swelling in late

IMPACT_DB=-5               # most scream samples are brickwalled; check for
WAIL_DB=7                  # clipping in analyze_audio.py and attenuate
SUB_DB=-3                  # generous on real speakers, ~-8 for phones
BUS_DB=-5                  # trim BEFORE the limiter. Without it the sum can hit
                           # +7dB and the limiter does ~8dB of reduction, which
                           # re-crushes the very transient the sting depends on.
                           # Check gain reduction, not just the output ceiling.

T=$((HITT-LEAD))
DI=$(printf %.0f $(( (T-IMPACT_SIL)*1000 )))
DW=$(printf %.0f $(( T*1000 )))

# Mono -> stereo, without the 3.01 dB loss.
# aformat=channel_layouts=stereo applies ffmpeg's POWER-PRESERVING rematrix to a
# mono source: it divides by sqrt(2), so the layer arrives 3 dB under where the
# volume= you wrote suggests. Measured: a mono file reading -3.6 dB peak reads
# -6.6 dB after aformat. pan= duplicates the channel instead, at unity.
# Already-stereo sources must NOT go through the pan form or the right channel
# is replaced by the left, so probe rather than assume.
tostereo() {
  local ch=$(ffprobe -v error -select_streams a:0 -show_entries stream=channels -of csv=p=0 "$1")
  if [ "$ch" = "1" ]; then print -r -- "pan=stereo|c0=c0|c1=c0"
  else print -r -- "aformat=channel_layouts=stereo"; fi
}
BED_ST=$(tostereo "$BED"); IMP_ST=$(tostereo "$IMPACT"); WAIL_ST=$(tostereo "$WAIL")

ffmpeg -y -v error -i "$VID" -i "$BED" -i "$IMPACT" -i "$WAIL" \
 -filter_complex "
  aevalsrc='sin(2*PI*(55*t+(28-55)*t*t/(2*0.9)))*exp(-t*3.2)':s=48000:d=1.0,
    pan=stereo|c0=c0|c1=c0,volume=${SUB_DB}dB,adelay=${DW}|${DW}[sub];

  [1:a]${BED_ST},
       volume=0:enable='between(t,${DROP_START},${DROP_END})'[bed];

  [2:a]aresample=48000,${IMP_ST},
       atrim=end=0.75,asetpts=PTS-STARTPTS,
       highpass=f=400:poles=2,
       afade=t=out:st=0.45:d=0.30,
       volume=${IMPACT_DB}dB,adelay=${DI}|${DI}[hit];

  [3:a]aresample=48000,${WAIL_ST},
       atrim=start=${WAIL_TRIM},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,
       acompressor=threshold=0.05:ratio=6:attack=5:release=250:makeup=2,
       aecho=0.8:0.9:230|520|950|1500:0.40|0.28|0.18|0.10,
       volume=${WAIL_DB}dB,afade=t=out:st=3.2:d=0.8,
       adelay=${DW}|${DW}[wail];

  [bed][hit][wail][sub]amix=inputs=4:duration=first:normalize=0,
    volume=${BUS_DB}dB,
    alimiter=limit=0.80:level=disabled:attack=1:release=60[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 "$OUT"

echo "Wrote $OUT  (impact ${DI}ms, wail ${DW}ms, both onsets at ${T}s)"

# Verify rather than trusting the arithmetic:
#   ffmpeg -hide_banner -nostats -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | tail -14
#   ffmpeg -hide_banner -nostats -ss 0 -t 20 -i "$OUT" -af volumedetect -f null - 2>&1 | grep mean
# Expect roughly: lull -47dB, impact -10dB, sustain -17..-22dB, aftermath -48dB,
# integrated ~-12 LUFS, LRA ~22 LU, true peak under -1 dBFS.
#
# Three settings that will otherwise cost an hour:
#
# - normalize=0 on amix. Default normalisation divides by input count, so the
#   bed drops ~6dB the instant the sting lands. It sounds like ducking.
# - level=disabled on alimiter. Auto-level is ON by default and renormalises
#   output back up to the ceiling, so lowering `limit` can make it LOUDER.
# - alimiter caps SAMPLE peaks; true peaks run ~1.5dB higher. limit=0.80 lands
#   around -1.7 dBTP. Leave headroom rather than tightening the ceiling.
#
# If the wail is inaudible until the impact decays, the two are colliding in
# 1-4kHz and no EQ separates them - shorten the impact (atrim=end) and raise
# WAIL_DB instead. See references/sting-design.md.
