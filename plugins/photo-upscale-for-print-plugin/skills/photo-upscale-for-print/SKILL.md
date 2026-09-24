---
name: photo-upscale-for-print
description: "Upscale a scanned or low-resolution photograph for large-format print using Real-ESRGAN plus a measured finishing chain. Use when asked to enlarge, upscale, or print-prep a scan, press photo, or old image at poster or mural size."
---

# Upscaling a photograph for print

For turning a limited scan into a file that holds up at poster or mural size. The
model is one stage of six; most of the perceived quality comes from the finishing
chain and from not committing compute before you know it will pay.

## Check this first

A better scan beats every technique here. A flatbed at 1200 dpi on an original
8x10 print gives ~9600 px on the long edge of genuinely measured detail; no model
competes with that. Ask whether the original is obtainable before starting.

Compute the honest ppi table before any processing and show it, so the size
decision is made on numbers:

    ppi = pixel_width / (print_width_mm / 25.4)

Rough guide for a viewed-at-arm's-length print: 150+ comfortable, 100-150 fine,
90-100 mural territory, below 80 visibly soft. Wall murals viewed from metres
away survive 35-50.

## 1. Measure the source

- Crop to the actual image area first. Scans of prints carry white borders,
  credit lines and logos; detect the photo rectangle rather than eyeballing it.
- Estimate grain sigma: sample several hundred small patches, high-pass each
  (subtract a Gaussian blur), take the standard deviation, and use the **lower
  tail** of that distribution. Sampling the flattest patches measures grain
  rather than accidentally measuring detail. You need this number in stage 4.
- Note any colour cast. Monochrome scans usually carry one from the paper base.

## 2. Bake off on a crop before committing

Never start a full-frame run on an unproven model. Take a ~384px crop containing
the hardest content (a face, fine hair, text) and run every candidate on it.
Report seconds-per-megapixel so the full-frame cost extrapolates, and build a
side-by-side comparison sheet of a detail region at 1:1 to actually look at.

Candidates worth including:

| Model | Params | Character |
|---|---|---|
| Lanczos + unsharp | - | Baseline. Keeps grain, stays soft. Sometimes wins on simple images |
| RealESRGAN_x2plus | 16.7M | Usually best for photographic detail at 2x |
| RealESRGAN_x4plus | 16.7M | Same body, 4x the cost per input pixel |
| realesr-general-x4v3 | 1.2M | Fast, but denoises grain into plastic. Rarely right for film |

## 3. Pick the model on evidence, not defaults

- **Prefer the native scale.** Running x4 and downsampling to 2x discards three
  quarters of what the model synthesised and adds a resampling step on top.
- **x2plus costs ~1/4 of x4plus per input megapixel.** Same 23-block body; the
  x2 weights apply `pixel_unshuffle` first so `conv_first` takes 12 channels and
  the body runs at quarter the pixel count. If your measured ratio isn't near
  4.0, something is wrong with the setup.
- **Compact models treat film grain as noise.** They are trained against
  degradations weighted towards compressed web imagery. Correct behaviour, wrong
  assumption about a scan.

## 4. Finishing chain — the order is load-bearing

1. **Neutral greyscale** (monochrome sources) via Rec. 709 luma, so the printer's
   colour management finds no cast to correct.
2. **Grain restoration.** GAN output is locally smooth and reads as plastic. Add
   monochrome Gaussian noise, blurred to match clump size at the new scale, at
   the sigma measured in stage 1. Modulate by luminance on a triangular weight
   peaking at mid-grey — photographic granularity genuinely peaks at mid-density.
   Flat additive noise reads as digital hiss because it ignores this.
3. **Local contrast:** unsharp at a large radius (~18px), small amount (~0.15).
4. **Print sharpen:** unsharp at edge radius (~1.1px), threshold-gated. The gate
   exists because of stage 2 — ungated sharpening amplifies the grain you just
   added. Feather the mask so sharpening doesn't switch on and off along an edge.
5. **Dust removal, last, on the 16-bit master.** See the trap below.

Cache the super-resolution output to disk and expose a `--skip-sr` flag. The
expensive stage runs once; the finishing passes are seconds and need tuning.

## 5. Verify numerically

Cheap checks that each catch a specific failure:

- **Seam energy ratio.** Mean absolute gradient per row and column, sampled at
  the tile pitch, compared with the local neighbourhood. Near 1.0 means no seams.
- **Clipping.** Percentage at 0 and at max. Above ~0.5% either end, pull back.
- **Power above source Nyquist.** Radially averaged PSD versus a Lanczos
  baseline quantifies what the model actually added (expect 15-20 dB).
- **Pixels altered** by any repair pass. A dust filter touching more than ~0.1%
  is eating real detail.

## Traps

- **Do not use `basicsr` / `realesrgan`.** They pin old torchvision APIs and
  break on torch 2.x. Reimplement RRDBNet and SRVGGNetCompact directly (~120
  lines) and load official weights with `strict=True` so structural errors fail
  loudly. Infer architecture from the checkpoint: `conv_first` input channels
  give the scale (3 -> x4, 12 -> x2, 48 -> x1); the highest `body.N` index gives
  the block count. Weights live under `params_ema` or `params`.
- **Residual scaling is 0.2** in both the RDB and the RRDB. Getting it wrong
  raises no exception and silently degrades output.
- **Tiled inference must divide by accumulated weight,** not average. Keep two
  buffers at output resolution: `sum += tile * window` and `weight += window`,
  then divide. Raised-cosine ramps are C-1 continuous, unlike linear ones, but
  with `step = tile - 2*overlap` they do *not* form a partition of unity — the
  accumulated weight can reach ~1.5, and the division is what makes it exact.
- **OpenCV's `medianBlur` only accepts ksize <= 5 above 8-bit depth.** For 16-bit
  repair, iterate a 5x5 median and combine with a greyscale opening.
- **A morphological top-hat finds eyelashes as readily as dust.** Both are bright
  structures smaller than the structuring element. Gate on local standard
  deviation over a ~21x21 window and accept specks only where the neighbourhood
  is flat: dust sits on smooth tone, eyelashes sit in hair. Expect this to cut
  candidates by two orders of magnitude. Always render the mask and inspect it
  before applying.
- **CPU cost.** ~500 s/MP for x4plus on two cores. Split long runs across
  background invocations rather than blocking a single tool call.

## Honesty rules

State these when presenting results; they are not optional caveats.

- Everything above the source Nyquist is **synthesised, not recovered**. It is
  constrained by surrounding pixels and by what photographs look like, but no
  measurement establishes that a particular detail was there.
- Never present an upscale as evidential or forensic material.
- Restored grain is pseudorandom and seeded — reproducible, not the emulsion's.
- **Faces are the worst case.** Below roughly 150px across, the model invents
  structure rather than interpolating texture, and will confidently produce
  someone else. Flag this rather than shipping it.
- Check who holds copyright before recommending a printer. A photograph being
  public domain in the US says nothing about the UK or EU, where it is the
  photographer's life plus 70. Commercial premises need a different licence from
  a print at home.

## Delivery

- 16-bit TIFF as the master for the printer; 8-bit JPEG for preview and ordering.
- Stamp DPI metadata for the intended width — the same pixels serve every size,
  the DPI tag just tells the printer which one you meant.
- Deflate- or LZW-compress the TIFF and verify it round-trips bit-identical;
  uncompressed 16-bit masters routinely exceed upload limits.
- Give the ppi table alongside, so the size decision stays with the user.