---
name: merman
description: >
  Render Mermaid diagrams to standalone images with merman-cli, a Rust port of
  Mermaid.js that needs no browser, no Node, and no Puppeteer/Chromium. Use
  whenever the user wants to turn Mermaid source — flowchart, sequence, class,
  state, ER, Gantt, C4, mindmap, gitgraph, etc. — into SVG, PNG, JPG or PDF,
  or (for most types, not C4) terminal ASCII/Unicode, or to render every
  Mermaid block in a Markdown file.
  Trigger on "render this mermaid", "make an SVG/PNG of this diagram", "draw a
  flowchart", "mmdc", "headless mermaid", or any request to produce a diagram
  image from Mermaid text locally. Prefer merman over a browser-based renderer
  or a network diagram service whenever the source is Mermaid and merman-cli is
  on PATH — it is faster, offline, deterministic, and keeps the source on the
  local machine.
---

# merman — headless Mermaid rendering

`merman-cli` is a self-contained Rust renderer for Mermaid.js. It does the same
job as `mmdc` (mermaid-cli) but with no headless browser underneath: no Node,
no Puppeteer, no Chromium download, no `/dev/shm` sizing dance in CI. It parses,
lays out, and rasterises in-process, which makes it fast, offline, and
reproducible. It is the right tool any time the source is Mermaid and the binary
is available locally.

Two things it does that a browser-based renderer cannot, and which are worth
reaching for:

- **Renders to the terminal** as ASCII or Unicode. Use this for a quick preview
  inline (no image file needed) or for diagrams in a text-only context such as a
  CI log or a README rendered in a pager. Coverage varies by type: flowchart,
  sequence, state, class and ER draw as diagrams; Gantt, gitgraph and mindmap
  come out as structured text; **C4 has no terminal output** — offer SVG
  instead.
- **Deterministic output.** With the deterministic text measurer and pinned
  time/seed, the same source produces byte-identical output across runs — golden-file
  testable, unlike a browser whose font rendering drifts.

## Check availability first

merman is a local binary, not a service. Confirm it is on PATH before the first
render of a session and capture the version (flag behaviour varies across
releases):

```bash
command -v merman-cli >/dev/null 2>&1 \
  && merman-cli --version \
  || echo "merman-cli not on PATH"
```

If it is missing, say so and stop — do not silently fall back to a browser-based
renderer or a public diagram service, which changes the privacy and dependency
profile the user chose merman to avoid. Offer to help install it (it builds from
the merman project with `cargo`) or to wire it into PATH, but let the user
decide.

## Output formats

`-e/--outputFormat` takes one of: `svg`, `png`, `jpg`, `pdf`, `ascii`,
`unicode`. If `-e` is omitted, the format is inferred from the `-o` extension,
falling back to SVG. So `-o diagram.png` gives PNG without an explicit `-e`.

| Format | Use for | Notes |
|---|---|---|
| `svg` | Default. Docs, web, anything that should scale. | Vector; renderable inline. Picks up `-C` CSS. |
| `png` | Raster for slides, GitHub, chat. | Honours `-b transparent`. Sized via `--scale`/`--raster-fit-*`. |
| `jpg` | Photos/large flat fills where size matters. | **No alpha** — `transparent` collapses to a solid fill. |
| `pdf` | Print, vector embed in LaTeX/docs. | `-s` scales; `-f/--pdfFit` fits page to chart. |
| `unicode` | Inline preview, richer box-drawing. | Text output. Best terminal fidelity. |
| `ascii` | Inline preview, 7-bit only. | Text output for the most constrained contexts. |

SVG is the safe default. Reach for `unicode` when you just want to *show* the
diagram in the reply without producing a binary.

## Common invocations

Drop-in mmdc-style render (format from extension):

```bash
merman-cli -i input.mmd -o diagram.svg
```

PNG, dark theme, transparent background, 2× scale:

```bash
merman-cli -i input.mmd -o diagram.png -t dark -b transparent -s 2
```

Unicode straight to the terminal via stdin/stdout (no temp files):

```bash
echo 'flowchart LR; A[Start]-->B{OK?}; B-->|yes| C[Ship]; B-->|no| A' \
  | merman-cli -i - -o - -e unicode
```

Detect the diagram type of some source:

```bash
merman-cli detect input.mmd
```

Render every Mermaid block in a Markdown file to an artefacts directory
(mmdc-compatible batch mode — this is how you'd process a chapter or a doc full
of diagrams):

```bash
merman-cli -i chapter.md -a ./diagrams -j 4
```

## Workflow

1. **Check availability** (above) on the first render of a session.
2. **Locate or write the source.** If the user gave Mermaid, use it. If not,
   write it now — Claude knows Mermaid; see `references/cli-reference.md` for the
   type cheat-sheet if a reminder helps. Save it to a `.mmd` file (e.g.
   `diagram.mmd`) alongside the output so iteration is cheap and the user can
   keep the source. Use `detect`/`parse` if unsure the source is valid.
3. **Pick the format** from the table above. Default SVG; `unicode` for a
   throwaway inline preview; PNG/PDF when the user names them or the target
   demands raster/print.
4. **Render.** Write the image with a descriptive stem, not `output.svg`, to
   a destination that exists in the current environment: the path the user
   named, else the current workspace (or a temp directory for throwaway
   previews). Don't assume a sandbox path such as `/mnt/user-data/outputs/` —
   it exists on claude.ai, not in a local Claude Code session.
5. **Surface the result:**
   - **SVG** → render inline if the environment has a tool for it (e.g.
     `show_widget` on claude.ai), and always give the file path — or hand the
     file over with whatever file-sharing tool the host provides
     (`present_files` on claude.ai). Mermaid SVGs carry their own palette, so
     they will not pick up the host theme's CSS variables — that is expected.
   - **ASCII/Unicode** → put it straight in the reply inside a fenced code
     block. It is text; no file or image tool needed.
   - **PNG/JPG/PDF** → give the file path (or share it via the host's file
     tool); binary cannot render inline.
6. **Iterate** on theme, scale, or layout — change `-t`, `-c`, `-C`, `-s`, or
   the source and re-render.

## Output file naming

Descriptive stems, mirroring the diagram's subject:

- `flowchart-oauth-rs-mode.svg`
- `sequence-appkey-mint.png`
- `er-gateway-primitives.pdf`

## Differentiators worth using

- **mmdc migration.** merman accepts the mmdc flags people already have in
  scripts (`-p/--puppeteerConfigFile`, `--iconPacks*`, `-f/--pdfFit`,
  `-j/--jobs`) as compatibility shims, so swapping `mmdc` → `merman-cli` in an
  existing CI step usually Just Works and drops the Chromium dependency. The
  compat flags are accepted but may be no-ops; don't rely on Puppeteer-specific
  behaviour carrying over.
- **Determinism for golden files / CI.** `--text-measurer deterministic`
  combined with `--fixed-today YYYY-MM-DD`, `--fixed-local-offset-minutes N`,
  and (for rough/hand-drawn styles) `--hand-drawn-seed N` makes output
  reproducible. The default `vendored` measurer is more visually accurate but is
  the one to drop if a render needs to be byte-stable across machines.
- **Multiple SVGs on one page.** Mermaid SVGs define arrowhead `<marker>`s and
  reference them by id; inlining two diagrams in one HTML document collides those
  ids and breaks arrowheads. Give each render a unique `-I/--svgId` prefix to
  keep them isolated. Relevant whenever Claude embeds more than one diagram in a
  single artifact or doc.
- **Math in labels** without MathJax: `--math-renderer ratex` renders `$$…$$`
  in node labels via a Rust math engine. Off by default.
- **Batch tolerance.** In Markdown/batch mode, `--suppress-errors` emits an
  error diagram in place of a failed block instead of aborting the whole run —
  good for "render what you can" passes, bad for CI where you want a non-zero
  exit. Choose deliberately.

## Gotchas and errors

| Symptom | Cause | Action |
|---|---|---|
| `merman-cli: command not found` | Not on PATH | Stop; offer to install/build or fix PATH. Don't fall back to a browser renderer silently. |
| Parse/layout error, non-zero exit | Invalid Mermaid source | Surface the error text **verbatim** — merman reports the offending construct more usefully than a paraphrase. Or run `parse`/`layout` to localise it. |
| Transparent background ignored on JPG | JPEG has no alpha channel | Use PNG or SVG if transparency matters. |
| Arrowheads vanish with two inline SVGs | Duplicate marker ids across diagrams | Render each with a distinct `-I/--svgId`. |
| Raster looks tiny / huge | `--scale` and `--raster-fit-*` interaction | Natural (or fit) size is multiplied by `--scale`, then clamped by `--raster-max-*` (default 8192 px / 8192² total). See reference. |
| Gantt/"today" marker moves between runs | Time-dependent diagram reads the real clock | Pin it: `--fixed-today` and `--fixed-local-offset-minutes`. |
| Output is SVG when you wanted PNG | No `-e`, and `-o` had no/.svg extension | Set `-e png` or give `-o` a `.png` name. |

## Reference

- `references/cli-reference.md` — full flag reference, the `detect`/`parse`/
  `layout`/`render` developer subcommands with JSON output, raster-sizing maths,
  determinism recipe, and a Mermaid diagram-type cheat-sheet. Read it when you
  need a flag you don't have memorised or want the subcommand JSON shapes.
