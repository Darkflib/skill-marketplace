#!/bin/zsh
# Six-beat found-footage scare sequence from three stills, with optional
# burned-in CCTV timestamp that skips time across the dropout.
#
# Copy into the project directory and edit the variables. Renders silent video;
# use mix_sting.sh afterwards for audio.
#
# Requires: ffmpeg. For the timestamp also ImageMagick + python3 (this route
# avoids drawtext, which current homebrew ffmpeg does not build).

set -e
cd "$(dirname "$0")"

# ---- source stills (any size; they get normalised below) ----
PLATE="plate.png"      # the empty scene - opens and closes the film
REVEAL="reveal.png"    # something subtle present in the frame
SCARE="scare.png"      # the payoff

OUT="scare.mp4"

# ---- the arc, in seconds ----
HOLD1=10     # lull. Must feel boring - that is the product. Under 8 is too short.
FADE=8       # slow crossfade bringing the reveal in
CREEP=3      # hold on the reveal so they squint and doubt themselves
DROP=0.1     # black. Reads as dropped frames and masks the cut.
HIT=3        # the scare, hard cut
HOLD2=5      # back to the empty plate. Do not skip this beat.

# Camera drift during the creep, in pixels. 0 = dead still, which is correct:
# any shake before the hit warns the viewer and they brace. If you want a hint
# of life, 2 gives a 0.17Hz sway (one cycle per 6s) with no high-frequency
# component - drift, not shake.
DRIFT=0

# ---- output geometry ----
W=1920; H=1080
OW=$((W+12)); OH=$((H+8))   # oversize before cropping, to give drift/shake room
FPS=30

# ---- on-screen display ----
STAMP=1                              # 0 to disable
CAM="CAM 03  REAR GARDEN"
CLOCK="2026-10-31 03:14:07"          # clip start, LOCAL time. Keep it plausible - see below.
LOST=5                               # seconds the clock skips across the dropout
POS_X="W-w-26"; POS_Y="20"           # top-right; pick a spot that stays legible
FONT="/System/Library/Fonts/Supplemental/Courier New Bold.ttf"

# If the file is meant to pass as a real export, CLOCK must agree with both the
# filename and the embedded creation_time - and must not be in the future.
#
# CLOCK is LOCAL time; creation_time is UTC. Derive one from the other rather
# than applying a remembered offset. UK clocks go back on the last Sunday in
# October, so a Halloween date is GMT (+0) while late-October dates are BST (+1):
#
#   python3 -c "import datetime,zoneinfo; print(datetime.datetime(2026,10,31,3,14,7,
#     tzinfo=zoneinfo.ZoneInfo('Europe/London')).astimezone(datetime.timezone.utc))"

FADE_IN=$((HOLD1+FADE))
TOTAL=$((HOLD1+FADE+CREEP+DROP+HIT+HOLD2))
TSDIR=".ts"

# ---------- timestamp strips: one PNG per displayed second ----------
if (( STAMP )); then
python3 - "$TSDIR" "$FONT" "$CAM" "$CLOCK" "$FADE_IN" "$CREEP" "$DROP" "$TOTAL" "$LOST" <<'PY'
import sys, subprocess, datetime, os, shutil
TSDIR, FONT, CAM, CLOCK = sys.argv[1:5]
FADE_IN, CREEP, DROP, TOTAL, LOST = (float(x) for x in sys.argv[5:10])
shutil.rmtree(TSDIR, ignore_errors=True); os.makedirs(TSDIR)
START = datetime.datetime.strptime(CLOCK, "%Y-%m-%d %H:%M:%S")
CUT = FADE_IN + CREEP                       # the dropout

segs, t, off = [], 0.0, 0
while t < CUT - 1e-6:                       # clock runs normally
    d = min(1.0, CUT - t); segs.append((off, d)); t += d; off += 1
segs.append((off - 1, DROP))                # stays lit, frozen, through the black
off += LOST                                 # ...and time goes missing
while t + DROP < TOTAL - 1e-6:
    d = min(1.0, TOTAL - DROP - t); segs.append((off, d)); t += d; off += 1

lines = []
for n, (o, d) in enumerate(segs):
    txt = f"{CAM}    " + (START + datetime.timedelta(seconds=o)).strftime("%Y-%m-%d  %H:%M:%S")
    png = f"{TSDIR}/ts{n:03d}.png"
    # drawn twice at an offset - a cheap drop shadow keeps it legible over anything
    subprocess.run(["magick", "-size", "760x44", "xc:none", "-font", FONT, "-pointsize", "28",
                    "-fill", "black", "-annotate", "+11+33", txt,
                    "-fill", "white", "-annotate", "+9+31", txt,
                    "-blur", "0x0.4", png], check=True)
    lines.append(f"file '{os.path.basename(png)}'\nduration {d:.3f}")
lines.append(f"file 'ts{len(segs)-1:03d}.png'")   # concat demuxer wants the last repeated
open(f"{TSDIR}/list.txt", "w").write("\n".join(lines) + "\n")
PY
  STAMP_IN=(-f concat -safe 0 -i "$TSDIR/list.txt")
  STAMP_FC="[6:v]fps=$FPS,format=rgba[osd];[grain][osd]overlay=x=${POS_X}:y=${POS_Y}:eof_action=repeat,format=yuv420p[vout]"
else
  STAMP_IN=(); STAMP_FC="[grain]null[vout]"
fi

# Note every ${VAR} is braced. Unbraced, zsh reads $VAR[label] as an array
# subscript and $VAR:eof_action as an ":e" modifier, silently corrupting the graph.

ffmpeg -y \
 -loop 1 -t $FADE_IN -i "$PLATE" \
 -loop 1 -t $FADE    -i "$REVEAL" \
 -loop 1 -t $CREEP   -i "$REVEAL" \
 -f lavfi -t $DROP   -i "color=black:s=${W}x${H}:r=$FPS" \
 -loop 1 -t $HIT     -i "$SCARE" \
 -loop 1 -t $HOLD2   -i "$PLATE" \
 "${STAMP_IN[@]}" \
 -filter_complex "
 [0:v]fps=$FPS,scale=${OW}:${OH},setsar=1,crop=${W}:${H},settb=AVTB,format=yuv420p[plate];
 [1:v]fps=$FPS,scale=${OW}:${OH},setsar=1,crop=${W}:${H},settb=AVTB,format=yuv420p[reveal];
 [2:v]fps=$FPS,scale=${OW}:${OH},setsar=1,
      crop=${W}:${H}:'(in_w-out_w)/2+${DRIFT}*sin(2*PI*t*0.17)':'(in_h-out_h)/2',
      settb=AVTB,format=yuv420p[creep];
 [3:v]settb=AVTB,format=yuv420p[drop];
 [4:v]fps=$FPS,scale=${OW}:${OH},setsar=1,
      scale=w='trunc(${OW}*(1+0.12*t/${HIT})/2)*2':h='trunc(${OH}*(1+0.12*t/${HIT})/2)*2':eval=frame,
      crop=${W}:${H}:'(in_w-out_w)/2+5*sin(2*PI*t*11)':'(in_h-out_h)/2+3*sin(2*PI*t*8.3)',
      noise=alls=30:allf=t+u,
      chromashift=cbh=-6:crh=6,
      eq=contrast=1.15:brightness=-0.02:saturation=0.85,
      settb=AVTB,format=yuv420p[hit];
 [5:v]fps=$FPS,scale=${OW}:${OH},setsar=1,crop=${W}:${H},settb=AVTB,format=yuv420p[plate2];
 [plate][reveal]xfade=transition=fade:duration=$FADE:offset=${HOLD1}[intro];
 [intro][creep][drop][hit][plate2]concat=n=5:v=1:a=0[cat];
 [cat]noise=alls=7:allf=t+u[grain];
 $STAMP_FC
 " \
 -map "[vout]" -t $TOTAL \
 -c:v libx264 -preset slow -crf 20 -tune grain -pix_fmt yuv420p -movflags +faststart "$OUT"

echo "\nWrote $OUT"
echo "  cut to the scare at $((HOLD1+FADE+CREEP+DROP))s of ${TOTAL}s"
echo "  aim the audio onset ~0.067s earlier (2 frames) - see mix_sting.sh"

# Notes on the filter graph, so edits don't reintroduce fixed bugs:
#
# - Every beat goes through the SAME scale/crop pair even though only [creep]
#   and [hit] need the slack. Mixing geometries produces a visible pop at cuts.
# - Grain is applied AFTER concat so it is uniform. Per-segment grain does not
#   match across cuts and reads as a change of shot.
# - The zoom on [hit] uses scale with eval=frame, not crop. crop evaluates w/h
#   once at init, so a crop-based zoom silently does nothing.
# - trunc(.../2)*2 keeps intermediate dimensions even at every frame; yuv420p
#   rejects odd ones.
# - The distortion is on [hit] only. Putting it before the hit warns the viewer.
# - -tune grain keeps x264 from quantising the grain to nothing on static shots
#   and then restoring it with a visible pop. Matters most if you later re-encode
#   to a camera-like ~1Mbps; check with scripts/verify_sequence.py.
