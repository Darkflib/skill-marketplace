# merman-cli — full reference

Distilled from `merman-cli --help`. Where a flag is described as "mmdc compat",
it exists so existing `mmdc` command lines keep working; it may be a no-op under
merman, so don't depend on Puppeteer-specific semantics carrying through.

## Invocation modes

merman has a top-level render mode (the mmdc-compatible path) and a set of
developer subcommands.

```
merman-cli [OPTIONS] [INPUT] [COMMAND]
```

- **Top-level render**: `merman-cli -i input.mmd -o output.svg`. `[INPUT]` may be
  given positionally instead of `-i`; `-` means stdin.
- **Subcommands**: `detect`, `parse`, `layout`, `render`, `help`.

## Options (top-level render)

| Flag | Arg | Meaning |
|---|---|---|
| `-i, --input` | path or `-` | Input Mermaid file; `-` for stdin. |
| `-o, --output` | path or `-` | Output file; `-` for stdout. |
| `-a, --artefacts` | dir | Output artefacts directory for **Markdown** input (batch render of fenced mermaid blocks). |
| `-j, --jobs` | N | Parallel jobs for Markdown input (mmdc compat). |
| `-e, --outputFormat` | fmt | `svg`, `ascii`, `unicode`, `png`, `jpg`, `pdf`. Defaults to the `-o` extension, then SVG. |
| `-b, --backgroundColor` | colour | Background for SVG/PNG/JPG. `transparent` works for SVG/PNG (not JPG). |
| `-c, --configFile` | path | JSON Mermaid configuration (themeVariables, flowchart curve, etc.). |
| `-C, --cssFile` | path | CSS injected into SVG output before export. |
| `-I, --svgId` | id | Root SVG id and internal marker prefix. Use to avoid id collisions when embedding multiple SVGs in one document. |
| `-s, --scale` | float | Raster/PDF scale factor. |
| `--raster-fit-width` | px | Fit PNG/JPG to this CSS-pixel width *before* `--scale`. |
| `--raster-fit-height` | px | Fit PNG/JPG to this CSS-pixel height *before* `--scale`. |
| `--raster-max-width` | px | Max PNG/JPG width after scale+fit (default 8192). |
| `--raster-max-height` | px | Max PNG/JPG height after scale+fit (default 8192). |
| `--raster-max-pixels` | px | Max total PNG/JPG pixels after scale+fit (default 8192×8192). |
| `--raster-unbounded` | — | Disable raster size limits. Trusted oversized exports only. |
| `-f, --pdfFit` | — | Scale PDF to fit chart (mmdc compat). |
| `-q, --quiet` | — | Suppress non-error log output. |
| `-p, --puppeteerConfigFile` | path | mmdc compat (no browser under merman). |
| `--iconPacks` | names… | Iconify package names (mmdc compat). |
| `--iconPacksNamesAndUrls` | defs… | Iconify `prefix#url` definitions (mmdc compat). |
| `-t, --theme` | name | Mermaid theme override (`default`, `dark`, `forest`, `neutral`, `base`). |
| `-w, --width` | px | Viewport width for viewport-sensitive layouts. |
| `-H, --height` | px | Viewport height for viewport-sensitive layouts. |
| `--text-measurer` | strategy | `deterministic` or `vendored` (default `vendored`). See determinism below. |
| `--math-renderer` | engine | `none` (default) or `ratex` for `$$…$$` labels. |
| `--suppress-errors` | — | Emit an error diagram instead of failing on parse errors. |
| `--fixed-today` | date | Override local "today" for time-dependent diagrams (Gantt). |
| `--fixed-local-offset-minutes` | N | Override local timezone offset, in minutes. |
| `--sequence-mirror-actors` | — | Mirror sequence participants below lifelines for ASCII/Unicode output. |
| `--hand-drawn-seed` | N | Stabilise rough/hand-drawn rendering where supported. |
| `-h, --help` / `-V, --version` | — | Help / version. |

## Developer subcommands

These expose merman's pipeline stages. Each takes Mermaid input the same way as
top-level mode (`[INPUT]` positionally or `-i`, `-` for stdin) and prints JSON
to stdout. `--pretty` pretty-prints it.

**stdin warning goes to stderr.** Reading from stdin prints `No input file
specified, reading from stdin…` — even when you passed `-i -`. It lands on
**stderr**, so captured/piped stdout JSON stays clean; silence it with
`2>/dev/null` if it clutters a log.

The field shapes below are confirmed against a `stateDiagram` v2. The generic
envelope (`type`, `nodes`, `edges`, `config`, `direction`, `accTitle`,
`accDescr`) is stable across types; the **per-type semantic block** (here
`states`/`relations`) and the **layout key** (here `StateDiagramV2`) vary by
diagram type. Don't hardcode the layout key — see the jq recipe below.

### `detect`

Identify the diagram type. Cheap validation that source parses as the kind you
expect before committing to a full render.

```bash
merman-cli detect input.mmd
```

### `parse`

Parse source into the semantic model as JSON, before geometry is assigned. Top
level:

- `type` — diagram type, e.g. `"stateDiagram"`.
- `nodes[]` — generic dagre-style nodes: `id`, `label`, `shape` (e.g.
  `stateStart`, `rect`, `stateEnd`), `domId`, `parentId`, `isGroup`, `padding`,
  `rx`/`ry`, `look`, the `cssClasses`/`cssStyles`/`cssCompiledStyles` triple,
  `centerLabel`, `dir`.
- `edges[]` — `id` (`edge0`…), `start`, `end`, `label`, `arrowhead`,
  `arrowTypeEnd`, `arrowheadStyle`, `style`, `thickness`, `labelpos`,
  `labelType`, `classes`, `look`.
- `config` — the **fully resolved** Mermaid config (theme, `themeVariables`,
  per-diagram blocks). This dwarfs everything else; ignore it unless you're
  inspecting theming (see "trimming output" below).
- `direction` — e.g. `"TB"`. `accTitle` / `accDescr` — accessibility
  title/description, `null` if unset.
- **Per-type semantic block.** For state diagrams: `states{}` keyed by id (each
  with `type`, `descriptions`, `doc`, `note`, `classes`, `styles`,
  `textStyles`, and a **tri-state `start`**: `true` = start pseudostate,
  `false` = end, `null` = neither), `relations[]` (`id1`, `id2`,
  `relationTitle`), plus `styleClasses{}` and `links{}`. Other diagram types
  carry their own block here.

Use when a render looks structurally wrong and you want to see what merman
*understood* the source to mean, independent of layout.

### `layout`

Parse **and** lay out, emitting positioned geometry. Three top-level keys:

- `meta` — `diagram_type`, `title`, `config` (just the user-supplied
  overrides — `{}` if none), and `effective_config` (the full resolved config,
  same shape as `parse`'s `config`).
- `semantic` — the **entire `parse` output** nested verbatim.
- `layout` — keyed by an internal renderer name that varies by diagram type
  (`StateDiagramV2`, etc.). The value holds:
  - `nodes[]` — `id`, `x`, `y`, `width`, `height`, `is_cluster`. **`x`/`y` are
    box centres**, not top-left corners.
  - `edges[]` — `id`, `from`, `to`, `from_cluster`, `to_cluster`, `points[]`
    (the routed polyline as `{x, y}` vertices), `label` (`{x, y, width,
    height}` or `null`), the `start_label_*`/`end_label_*` and
    `start_marker`/`end_marker` slots, and `stroke_dasharray`.
  - `clusters[]` — subgraph/composite boxes (empty for a flat diagram).
  - `bounds` — `min_x`, `min_y`, `max_x`, `max_y`: the overall canvas extent.

Use when positioning or overlap is the problem rather than the parse — to read
computed boxes, drive overlap/regression checks, or feed merman's geometry into
your own renderer.

### Consuming parse/layout JSON

The resolved `config`/`effective_config` blob is the bulk of the output. Strip
it when you only want structure or geometry:

```bash
# parse, minus the theme/config noise
merman-cli -i diagram.mmd parse | jq 'del(.config)'

# positioned boxes + canvas bounds, without hardcoding the renderer key
merman-cli -i diagram.mmd layout \
  | jq '.layout | to_entries[0].value
        | {bounds, nodes: [.nodes[] | {id, x, y, width, height}]}'
```

`to_entries[0].value` sidesteps the type-varying layout key (`StateDiagramV2`
and friends) so the same recipe works for any diagram.

### `render`

The explicit form of top-level render, with a format flag:

```bash
merman-cli render --format unicode input.mmd
```

`--format` accepts the same set as `-e` (`svg`, `ascii`, `unicode`, `png`,
`jpg`, `pdf`).

## Raster sizing model

For PNG/JPG, the output dimensions are computed in this order:

1. **Natural size** from layout, or the fitted size if `--raster-fit-width` /
   `--raster-fit-height` is given (the diagram is scaled to fit that CSS-pixel
   box).
2. **Multiply by `--scale`** (`-s`). `-s 2` doubles linear dimensions.
3. **Clamp** to `--raster-max-width`, `--raster-max-height`, and
   `--raster-max-pixels` (defaults 8192, 8192, 8192²). `--raster-unbounded`
   removes the clamp.

So a crisp 2× PNG at a known width is `--raster-fit-width 1200 -s 2`. If output
silently hits a wall at 8192 px, you're clamping — raise the relevant
`--raster-max-*` or pass `--raster-unbounded` for a trusted export.

`--scale` also applies to PDF. `-f/--pdfFit` fits the PDF page to the chart
bounds (mmdc compat).

## Determinism recipe

A browser renderer's font metrics drift between versions and platforms, so
mermaid-cli output is not byte-stable — awkward for golden-file tests. merman can
be pinned:

```bash
merman-cli -i diagram.mmd -o diagram.svg \
  --text-measurer deterministic \
  --fixed-today 2026-01-01 \
  --fixed-local-offset-minutes 0 \
  --hand-drawn-seed 42
```

- `--text-measurer deterministic` — fixed, reproducible text measurement.
  Trades a little visual fidelity for stability. `vendored` (default) uses
  bundled font metrics and looks better but is the variable to remove when
  chasing byte-identical output.
- `--fixed-today` / `--fixed-local-offset-minutes` — freeze the clock so Gantt
  "today" markers and any date maths don't move between runs.
- `--hand-drawn-seed` — fix the RNG for rough/sketch styles so the jitter is
  repeatable.

SVG tends to be the most stable target for golden files; rasterising adds an
encoder in the path.

## stdin / stdout piping

Both ends take `-`:

```bash
# source on stdin, unicode to stdout
cat diagram.mmd | merman-cli -i - -o - -e unicode

# generate source on the fly, capture SVG
printf 'stateDiagram-v2\n[*] --> Idle\nIdle --> Busy\nBusy --> Idle\n' \
  | merman-cli -i - -o out.svg
```

Pair stdout (`-o -`) with `-q/--quiet` if you're capturing the artefact and
don't want log lines mixed into it.

## Mermaid diagram-type cheat-sheet

merman renders standard Mermaid. First non-comment token usually selects the
type. Common headers:

| Type | Header keyword |
|---|---|
| Flowchart | `flowchart TD` / `graph LR` |
| Sequence | `sequenceDiagram` |
| Class | `classDiagram` |
| State | `stateDiagram-v2` |
| Entity-relationship | `erDiagram` |
| Gantt | `gantt` |
| Pie | `pie` |
| Mindmap | `mindmap` |
| Timeline | `timeline` |
| Git graph | `gitGraph` |
| User journey | `journey` |
| Quadrant | `quadrantChart` |
| C4 | `C4Context` / `C4Container` / `C4Component` |
| Requirement | `requirementDiagram` |
| Block | `block-beta` |
| Sankey | `sankey-beta` |

If a specific type or newer Mermaid feature fails to parse, fall back to
`detect`/`parse` to see what merman's grammar accepts in the installed version
rather than assuming parity with the latest mermaid.js.
